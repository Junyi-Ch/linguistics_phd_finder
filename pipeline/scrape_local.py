#!/usr/bin/env python
"""Scrape faculty directories and profile pages on your own computer (no AI needed).

  python pipeline/scrape_local.py --dir-only            # step 1: find each directory and count people (fast)
  python pipeline/scrape_local.py                       # step 2: also read every profile page -> data/raw/<slug>.json
  python pipeline/scrape_local.py --only ucla,mit       # just some universities (slugs or slug prefixes)
  python pipeline/scrape_local.py --workers 4           # universities scraped in parallel (default 4)

Reads data/programs.json. For each included unit it uses `directory_url` when given, otherwise finds the
faculty/people page from the unit homepage. It keeps tenure-line people (assistant, associate, full professors)
by reading the title text next to each name, then reads each profile page for research text.
For adjacent units (computer science, speech and hearing, language departments) it keeps only people whose
profile is about language.

Pages are cached under data/cache/, so re-runs are quick and only fetch what changed in programs.json.
A summary is written to data/cache/scrape_report.csv; anything marked CHECK needs a look.
"""
import argparse, csv, json, re, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch  # noqa: E402  (cached static fetch with headless-Chromium fallback)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "data" / "cache" / "scrape_report.csv"

# ---------- titles ----------
# titles that are not tenure-line even when they contain "professor"
NOT_TENURE = re.compile(r"emerit|lecturer|instructor|adjunct|visiting|clinical|of (the )?practice|professional practice|"
                        r"teaching (assistant |associate )?professor|professor of teaching|of instruction|in residence|"
                        r"research (assistant |associate )?professor|affiliate|courtesy|postdoc|post-doc|retired|collegiate|"
                        r"extension|\bvisitor\b|part-time", re.I)
# lines that mark someone as not faculty at all (no "professor" in them)
NOT_FACULTY = re.compile(r"\b(lecturer|instructor|emerit\w*|postdoc\w*|post-doctoral|graduate student|ph\.?d\.? (student|candidate)|"
                         r"staff|coordinator|manager|administrator|advisor|specialist|research (scientist|associate)|fellow)\b", re.I)
RANK_RE = re.compile(r"\b(assistant|associate|full|distinguished|university|regents'?|endowed|chair(ed)?)?\s*professor\b", re.I)

def classify_title(text):
    """Return (rank, title_line) for the first professor-like line in text, or (None, None)."""
    for line in re.split(r"[\n|•·;]+", text):
        line = re.sub(r"\s+", " ", line).strip(" ,:-–")
        if not line or len(line) > 160 or not RANK_RE.search(line):
            continue
        if NOT_TENURE.search(line):
            return "EXCLUDED", line
        l = line.lower()
        if "assistant professor" in l: return "Assistant Professor", line
        if "associate professor" in l: return "Associate Professor", line
        return "Professor", line
    for line in re.split(r"[\n|•·;]+", text):
        line = re.sub(r"\s+", " ", line).strip(" ,:-–")
        if line and len(line) <= 100 and NOT_FACULTY.search(line):
            return "EXCLUDED", line
    return None, None

# ---------- names ----------
NOT_NAME = set("""faculty people staff directory home about contact news events research graduate undergraduate program programs
department departments school college university more read view profile profiles email website site page pages menu search
login apply give support courses course students student alumni emeriti emeritus lecturers affiliated core all and of the for
in at our team labs lab center centre institute linguistics language languages science sciences studies phd ma ba
skip main content navigation calendar resources publications overview learn next previous back top cv pdf map""".split())
NAME_TOKEN = re.compile(r"^(?:[A-ZÀ-ÖØ-Þ][\w'’.\-À-ÿ]*|[A-Z]\.|de|da|del|della|der|van|von|le|la|du|di|dos|bin|al-\w+|y)$")

def clean_name(text):
    t = re.sub(r"\s+", " ", text or "").strip()
    t = re.sub(r",?\s*(ph\.?\s?d\.?|m\.?a\.?|ed\.?d\.?|jr\.?|sr\.?)$", "", t, flags=re.I).strip(" ,")
    t = re.sub(r"\s*\(.*?\)\s*", " ", t).strip()
    if "," in t:  # "Last, First"
        a, b = [x.strip() for x in t.split(",", 1)]
        if a and b and " " not in a.strip() or (a and b and len(a.split()) <= 2 and len(b.split()) <= 3):
            t = f"{b} {a}"
    return re.sub(r"\s+", " ", t).strip()

def looks_like_name(text):
    t = clean_name(text)
    if not (4 <= len(t) <= 45) or re.search(r"\d|@|http", t):
        return False
    toks = t.split()
    if not (2 <= len(toks) <= 5):
        return False
    if any(w.lower().strip(".") in NOT_NAME for w in toks):
        return False
    return all(NAME_TOKEN.match(w) for w in toks) and sum(1 for w in toks if w[0].isupper()) >= 2

# ---------- page structure ----------
def soup_of(html):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "lxml")
    for t in s(["script", "style", "noscript", "svg", "iframe", "header", "footer", "nav"]):
        t.decompose()
    return s

def same_site(a, b):
    ha, hb = urlparse(a).hostname or "", urlparse(b).hostname or ""
    base = lambda h: ".".join(h.split(".")[-2:])
    return base(ha) == base(hb)

def person_cards(html, page_url):
    """Find (name, profile_url, context_text) for each person link on a directory page."""
    s = soup_of(html)
    found, seen = [], set()
    for a in s.find_all("a", href=True):
        text = a.get_text(" ", strip=True) or a.get("title", "") or a.get("aria-label", "")
        text = re.sub(r"^(read more about|view profile( of| for)?|profile (of|for)|more about)\s+", "", text, flags=re.I)
        if not looks_like_name(text):
            continue
        url = urljoin(page_url, a["href"]).split("#")[0]
        if not url.startswith("http") or not same_site(url, page_url) or url.rstrip("/") == page_url.rstrip("/"):
            continue
        name = clean_name(text)
        key = re.sub(r"[^a-z]", "", name.lower())
        if key in seen:
            continue
        # smallest ancestor that holds this person's details but not another person's link
        ctx, node = a.get_text(" ", strip=True), a
        for _ in range(6):
            node = node.parent
            if node is None or node.name in ("body", "html"):
                break
            others = {urljoin(page_url, x["href"]).split("#")[0] for x in node.find_all("a", href=True)
                      if looks_like_name(x.get_text(" ", strip=True))} - {url}
            if others:
                break
            ctx = node.get_text("\n", strip=True)
            if len(ctx) > 1200:
                break
        seen.add(key)
        found.append((name, url, ctx[:1200]))
    return found

def next_pages(html, page_url, limit=12):
    s = soup_of(html)
    out = []
    for a in s.find_all("a", href=True):
        t = a.get_text(" ", strip=True).lower()
        href = urljoin(page_url, a["href"]).split("#")[0]
        if not same_site(href, page_url) or href == page_url:
            continue
        if t in ("next", "next ›", "›", "»", "next page", ">") or re.fullmatch(r"\d{1,2}", t):
            if re.search(r"(page[=/]\d+|[?&]p(g|age)?=\d+|/page/\d+)", href):
                out.append(href)
    return list(dict.fromkeys(out))[:limit]

DIR_WORDS = [("faculty", 5), ("people", 4), ("directory", 3), ("our team", 2), ("core faculty", 6), ("ladder faculty", 6)]
def discover_directory(unit_url):
    """Pick the most likely faculty-list link from a unit homepage."""
    html = fetch.get(unit_url)
    s = soup_of(fetch.get(unit_url)) if html else None
    best, score_best = None, 0
    for a in (s.find_all("a", href=True) if s else []):
        t = a.get_text(" ", strip=True).lower()
        href = urljoin(unit_url, a["href"]).split("#")[0]
        if not href.startswith("http") or not same_site(href, unit_url) or len(t) > 40:
            continue
        sc = sum(w for k, w in DIR_WORDS if k in t) + sum(1 for k in ("faculty", "people") if k in href.lower())
        if any(x in t for x in ("emerit", "student", "staff", "alumni", "lecturer", "affiliate")):
            sc -= 5
        if sc > score_best:
            best, score_best = href, sc
    return best

# ---------- profiles ----------
LANG_WORDS = re.compile(r"\b(linguist\w*|language|languages|speech|phonet\w*|phonolog\w*|syntax|syntactic|semantic\w*|pragmatic\w*|"
                        r"morpholog\w*|bilingual\w*|multilingual\w*|lexic\w*|grammar\w*|nlp|natural language|discourse|"
                        r"sociolinguist\w*|psycholinguist\w*|dialect\w*|sign language|aphasia|literacy|reading|second language|"
                        r"acquisition|prosod\w*|intonation|vowel\w*|translation|corpus|corpora|conversation)\b", re.I)

COMP_WORDS = re.compile(r"\b(natural language|nlp|computational linguistic\w*|linguist\w*|speech (recognition|processing|synthesis|technology)|"
                        r"spoken language|machine translation|language models?|dialog\w*|parsing|semantic parsing)\b", re.I)

def about_language(text, field):
    """Adjacent units keep only people whose profile is about language."""
    if field == "COMP":
        return len(COMP_WORDS.findall(text)) >= 2
    return len(LANG_WORDS.findall(text)) >= 3

def profile_text(html, url):
    text = None
    try:
        import trafilatura
        text = trafilatura.extract(html, url=url, include_comments=False, include_tables=False, favor_recall=True)
    except Exception:
        pass
    if not text or len(text) < 200:
        s = soup_of(html)
        main = s.find("main") or s.find("article") or s.body or s
        text = main.get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text or "").strip()

AREAS_HEAD = re.compile(r"^\s*(research (interests|areas|focus)|areas of (interest|research|expertise)|specializations?|expertise|interests)\s*:?\s*(.*)$", re.I)
def research_areas(text):
    """Items after a 'Research interests' heading: the rest of that line, or the short lines (a list) below it."""
    lines = text.split("\n")
    for k, line in enumerate(lines):
        m = AREAS_HEAD.match(line)
        if not m or len(line) > 300:
            continue
        chunk = [m.group(4)] if m.group(4).strip() else []
        if not chunk:
            for nxt in lines[k + 1:k + 12]:
                if not nxt.strip() or len(nxt) > 90:
                    break
                chunk.append(nxt)
        parts = re.split(r"[;,\n•·]| and (?=[^,;]*$)", " ; ".join(chunk))
        out = [re.sub(r"\s+", " ", x).strip(" .-–") for x in parts]
        out = [x for x in out if 2 < len(x) < 60]
        if out:
            return out[:8]
    return []

def profile_links(html, url):
    s = soup_of(html)
    scholar, site = None, None
    for a in s.find_all("a", href=True):
        h = urljoin(url, a["href"]); t = a.get_text(" ", strip=True).lower()
        if "scholar.google" in h and not scholar:
            scholar = h
        elif not site and h.startswith("http") and not same_site(h, url) and re.search(r"personal|website|homepage|lab site|home page", t):
            site = h
    return site, scholar

# ---------- per university ----------
def scrape_university(p, dir_only=False):
    rows, faculty, depts, seen = [], [], [], set()
    for u in p["units"]:
        if not u.get("include"):
            continue
        row = {"slug": p["slug"], "unit": u["name"], "field": u.get("field", "LING"), "directory": u.get("directory_url") or "",
               "candidates": 0, "tenure_line": 0, "excluded_titles": 0, "no_title": 0, "not_language": 0, "kept": 0, "status": "ok", "note": ""}
        try:
            d = u.get("directory_url") or (discover_directory(u["unit_url"]) if u.get("unit_url") else None)
            if not d:
                row.update(status="CHECK", note="no directory found from unit homepage"); rows.append(row); continue
            row["directory"] = d
            pages, cards = [d], []
            html = fetch.get(d)
            cards += person_cards(html, d)
            for nxt in next_pages(html, d):
                if nxt not in pages:
                    pages.append(nxt); cards += person_cards(fetch.get(nxt), nxt)
            if len(cards) < 3:  # maybe a JS-built list: try rendering
                html = fetch.get(d, render=True); cards = person_cards(html, d)
            row["candidates"] = len(cards)
            depts.append({"name": u["name"], "school": u.get("school"), "directory_url": d,
                          "phd_program_url": u.get("phd_program_url"), "phd_program_name": u.get("phd_program_name")})
            for name, url, ctx in cards:
                key = re.sub(r"[^a-z]", "", name.lower())
                if key in seen:
                    continue
                rank, title = classify_title(ctx)
                if rank == "EXCLUDED":
                    row["excluded_titles"] += 1; continue
                if dir_only:
                    if rank: row["tenure_line"] += 1
                    else: row["no_title"] += 1
                    continue
                try:
                    ph = fetch.get(url)
                except Exception as e:
                    row["note"] += f" profile failed: {name};"; continue
                text = profile_text(ph, url)
                if not rank:  # title not on the list page: read it from the top of the profile
                    rank, title = classify_title(text[:1500])
                    if rank in (None, "EXCLUDED"):
                        row["no_title" if rank is None else "excluded_titles"] += 1; continue
                row["tenure_line"] += 1
                if (u.get("field", "LING") != "LING" or u.get("filter_language")) and not about_language(text, u.get("field", "LING")):
                    row["not_language"] += 1; continue
                site, scholar = profile_links(ph, url)
                seen.add(key)
                faculty.append({"name": name, "title": title, "rank": rank, "department": u["name"], "unit": u["name"],
                                "profile_url": url, "personal_url": site, "google_scholar_url": scholar,
                                "research_areas": research_areas(text), "bio": text[:6000]})
                row["kept"] += 1
            n = row["tenure_line"] if dir_only else row["kept"]
            if n < 3 or (row["no_title"] > max(3, row["tenure_line"])):
                row["status"] = "CHECK"
                row["note"] += f" few tenure-line people found ({n}); titles missing for {row['no_title']}"
        except Exception as e:
            row.update(status="CHECK", note=f"error: {str(e)[:120]}")
        rows.append(row)
    if not dir_only and faculty:
        RAW.mkdir(parents=True, exist_ok=True)
        json.dump({"university": p["university"], "slug": p["slug"], "departments": depts,
                   "scraped_at": date.today().isoformat(), "faculty": faculty},
                  open(RAW / f"{p['slug']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated slugs or slug prefixes")
    ap.add_argument("--dir-only", action="store_true", help="only find directories and count tenure-line people")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    programs = [p for p in json.load(open(ROOT / "data" / "programs.json", encoding="utf-8")) if any(u.get("include") for u in p["units"])]
    if a.only:
        keys = a.only.split(",")
        programs = [p for p in programs if any(p["slug"].startswith(k) for k in keys)]
    print(f"{len(programs)} universities, {sum(1 for p in programs for u in p['units'] if u.get('include'))} units"
          f"{' (directories only)' if a.dir_only else ''}")
    rows, t0 = [], time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(scrape_university, p, a.dir_only): p for p in programs}
        for i, f in enumerate(as_completed(futs), 1):
            p = futs[f]
            try:
                r = f.result()
            except Exception as e:
                r = [{"slug": p["slug"], "unit": "*", "status": "CHECK", "note": f"crashed: {e}"}]
            rows += r
            n = sum(x.get("kept" if not a.dir_only else "tenure_line", 0) or 0 for x in r)
            flag = " CHECK" if any(x.get("status") == "CHECK" for x in r) else ""
            print(f"[{i:2d}/{len(programs)}] {p['slug']:45s} {n:3d} people{flag}  ({int(time.time()-t0)}s)")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["slug", "unit", "field", "status", "candidates", "tenure_line", "excluded_titles", "no_title", "not_language", "kept", "directory", "note"]
    with open(REPORT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in sorted(rows, key=lambda x: (x.get("status") != "CHECK", x["slug"])):
            w.writerow(r)
    bad = [r for r in rows if r.get("status") == "CHECK"]
    print(f"\nDone in {int(time.time()-t0)}s. {len(bad)} units need a look; see {REPORT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
