#!/usr/bin/env python
"""Add recent publications from OpenAlex (free, open) to each scraped faculty record.

  python pipeline/enrich_openalex.py                 # all data/raw/*.json
  python pipeline/enrich_openalex.py --only ucla     # some universities (slug prefixes)
  python pipeline/enrich_openalex.py --refresh       # redo people already enriched

For each person it looks for an OpenAlex author with the same name at the same university and keeps the match
only when it is unambiguous and their recent work is about language. It then stores up to 25 recent paper titles
(with abstracts) under "works" in data/raw/<slug>.json. build.py adds them to the profile view used for the
matching vectors and the labeller reads them; they are never published on the site. Responses are cached in
data/cache/openalex/.
"""
import argparse, hashlib, json, re, sys, time, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrape_local import LANG_WORDS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "openalex"
API = "https://api.openalex.org"

def get(path, params):
    import requests
    key = hashlib.sha1((path + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    cp = CACHE / f"{key}.json"
    if cp.exists():
        return json.loads(cp.read_text())
    for attempt in range(4):
        r = requests.get(API + path, params=params, timeout=30, headers={"User-Agent": "LingPhDExplorer/0.1"})
        if r.status_code == 429:
            time.sleep(2 + 3 * attempt); continue
        r.raise_for_status()
        CACHE.mkdir(parents=True, exist_ok=True)
        cp.write_text(r.text)
        time.sleep(0.12)
        return r.json()
    raise RuntimeError("OpenAlex rate limit")

def norm(s):
    return re.sub(r"[^a-z ]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()).strip()

def institution_ids(university):
    res = get("/institutions", {"search": university, "per-page": 5})["results"]
    want = norm(university)
    ids = [r["id"].rsplit("/", 1)[-1] for r in res if norm(r["display_name"]) == want]
    return ids or [r["id"].rsplit("/", 1)[-1] for r in res[:1]]

def abstract(inv):
    if not inv:
        return ""
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)

def find_author(name, inst_ids):
    parts = norm(name).split()
    if len(parts) < 2:
        return None
    res = get("/authors", {"search": name, "filter": "affiliations.institution.id:" + "|".join(inst_ids), "per-page": 5})["results"]
    last, first = parts[-1], parts[0]
    cands = []
    for r in res:
        dn = norm(r["display_name"]).split()
        alts = [norm(x).split() for x in r.get("display_name_alternatives", [])] + [dn]
        if any(a and a[-1] == last and (a[0] == first or a[0][:1] == first[:1]) for a in alts):
            cands.append(r)
    if not cands:
        return None
    cands.sort(key=lambda r: r.get("works_count", 0), reverse=True)
    if len(cands) > 1 and cands[1].get("works_count", 0) > 0.3 * cands[0].get("works_count", 1):
        return None  # two plausible people with this name: skip rather than guess
    return cands[0]

def recent_works(author_id, n=25):
    res = get("/works", {"filter": f"author.id:{author_id}", "sort": "publication_date:desc", "per-page": n,
                         "select": "title,publication_year,abstract_inverted_index,type"})["results"]
    out = []
    for w in res:
        t = re.sub(r"<[^>]+>", "", w.get("title") or "").strip()
        if not t or w.get("type") in ("erratum", "paratext", "peer-review"):
            continue
        out.append({"title": t, "year": w.get("publication_year"), "abstract": abstract(w.get("abstract_inverted_index"))[:1200]})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    files = sorted((ROOT / "data" / "raw").glob("*.json"))
    if a.only:
        files = [f for f in files if any(f.stem.startswith(k) for k in a.only.split(","))]
    tot = found = 0
    for fp in files:
        d = json.load(open(fp, encoding="utf-8"))
        try:
            inst = institution_ids(d["university"])
        except Exception as e:
            print(f"{d['slug']}: institution lookup failed ({e})"); continue
        n = 0
        for f in d["faculty"]:
            if "works" in f and not a.refresh:
                n += bool(f["works"]); continue
            tot += 1
            try:
                au = find_author(f["name"], inst)
                works = recent_works(au["id"].rsplit("/", 1)[-1]) if au else []
            except Exception as e:
                print(f"  {f['name']}: {e}"); works = []
            # wrong-person guard: in a non-linguistics unit, or with an odd record, most titles should be about language
            if works:
                lang = sum(1 for w in works if LANG_WORDS.search(w["title"] + " " + w["abstract"]))
                if lang < max(2, 0.25 * len(works)):
                    works = []
            f["works"] = works
            if works:
                found += 1; n += 1
        json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{d['slug']:45s} {n:3d}/{len(d['faculty'])} with publications")
    print(f"\nLooked up {tot} people; matched {found}.")

if __name__ == "__main__":
    main()
