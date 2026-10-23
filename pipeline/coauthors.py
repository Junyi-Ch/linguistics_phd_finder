#!/usr/bin/env python3
"""Find which faculty on the site have published together, using OpenAlex (free, open scholarly data).

Run on your Mac from the project folder:
    python3 pipeline/coauthors.py

Needs a free OpenAlex API key in a file called .env in the project folder:
    OPENALEX_KEY=your-key
Only the Python standard library is used. Results are cached in data/cache/openalex/, so if the run stops
(for example when the daily free budget runs out) just run the same command again later and it continues.

Output: src/data/coauthors.json, which the site build reads. It holds only public publication metadata:
which pairs of faculty share papers, how many, the latest year and one example title.
"""
import hashlib, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request, urllib.error
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "cache", "openalex")
OUT = os.path.join(ROOT, "src", "data", "coauthors.json")
API = "https://api.openalex.org"
MAX_AUTHORS = 25        # ignore huge consortium papers: sharing one doesn't mean two people worked together
MAX_PROFILES = 5        # OpenAlex sometimes splits one person into several author profiles; merge up to this many

def load_key():
    k = os.environ.get("OPENALEX_KEY")
    p = os.path.join(ROOT, ".env")
    if not k and os.path.exists(p):
        for line in open(p, encoding="utf8"):
            if line.strip().startswith("OPENALEX_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        sys.exit("No OpenAlex key found. Put a line OPENALEX_KEY=your-key in a file called .env in the project folder.")
    return k

KEY = load_key()
os.makedirs(CACHE, exist_ok=True)

class OutOfBudget(Exception):
    pass

calls = 0
def get(path, params, cache_name=None):
    """GET with cache, polite pacing and retries. The key is never written to the cache or printed."""
    global calls
    if cache_name:
        cp = os.path.join(CACHE, cache_name + ".json")
        if os.path.exists(cp):
            return json.load(open(cp, encoding="utf8"))
    q = dict(params); q["api_key"] = KEY
    url = f"{API}/{path}?{urllib.parse.urlencode(q)}"
    for attempt in range(6):
        try:
            time.sleep(0.12)
            calls += 1
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "linguistics-phd-explorer (coauthor map)"}), timeout=60) as r:
                data = json.load(r)
            if cache_name:
                json.dump(data, open(os.path.join(CACHE, cache_name + ".json"), "w", encoding="utf8"))
            return data
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf8", "ignore")[:300]
            if e.code == 429 and ("budget" in body.lower() or "limit" in body.lower()) and attempt >= 2:
                raise OutOfBudget(body)
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt); continue
            if e.code in (401, 403):
                sys.exit(f"OpenAlex refused the key ({e.code}). Check the key in .env. Details: {body}")
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    raise OutOfBudget("too many failed requests")

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s)

def name_parts(name):
    name = re.sub(r"\(.*?\)", " ", name)
    name = re.sub(r",.*$", "", name)
    toks = [t for t in norm(name).split() if t]
    return (toks[0], toks[-1]) if toks else ("", "")

def name_score(fac_name, cand):
    f1, l1 = name_parts(fac_name)
    names = [cand.get("display_name", "")] + list(cand.get("display_name_alternatives") or [])
    best = 0
    for n in names:
        f2, l2 = name_parts(n)
        if not l2 or l1 != l2:
            continue
        if f1 == f2: best = max(best, 2)
        elif f1 and f2 and f1[0] == f2[0]: best = max(best, 1)
    return best

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")[:80]

INST_FALLBACK = {
    "city-university-of-new-york-graduate-center": ["Graduate Center CUNY", "CUNY Graduate Center", "City University of New York"],
    "rutgers-universitynew-brunswick": ["Rutgers University New Brunswick", "Rutgers, The State University of New Jersey", "Rutgers"],
}
LANGY = re.compile(r"lingu|language|speech|phon|semantic|syntax|grammar|discourse|bilingual|literacy|reading|translation|dialect|lexic|morpholog|pragmatic|prosod|natural language|psycholing|cognitive|acquisition|vocabulary|word|hearing|communication", re.I)

def inst_id(p):
    for k, q in enumerate([p["name"]] + INST_FALLBACK.get(p["slug"], [])):
        d = get("institutions", {"search": q, "per-page": 5, "select": "id,display_name,country_code"}, f"inst-{p['slug']}" + (f"-{k}" if k else ""))
        res = [r for r in d.get("results", []) if r.get("country_code") in (None, "US")]
        if res:
            return res[0]["id"].rsplit("/", 1)[-1]
    return None

def disp_score(fac_name, c):
    """name match on the profile's main display name only (alternative names in OpenAlex are noisy)"""
    f1, l1 = name_parts(fac_name)
    f2, l2 = name_parts(c.get("display_name", ""))
    if not l2 or l1 != l2:
        return 0
    if f1 == f2:
        return 2
    return 1 if f1 and f2 and f1[0] == f2[0] else 0

def middles(n):
    toks = norm(re.sub(r"\(.*?\)|,.*$", " ", n)).split()
    return {t[0] for t in toks[1:-1]}

def compatible(a, b):
    """'Robert D. Hawkins' and 'Robert P. Hawkins' are different people; 'Robert Hawkins' fits either"""
    ma, mb = middles(a), middles(b)
    return not ma or not mb or ma <= mb or mb <= ma

def langy(c):
    n = 0
    for t in (c.get("topics") or [])[:10]:
        text = " ".join([t.get("display_name") or "", (t.get("subfield") or {}).get("display_name") or "", (t.get("field") or {}).get("display_name") or ""])
        if LANGY.search(text):
            n += t.get("count") or 1
    return n

SEL = "id,display_name,display_name_alternatives,works_count"

def find_author(f, iid):
    first, last = name_parts(f["name"])
    full = re.sub(r"\(.*?\)|,.*$", " ", f["name"]).strip()
    params = {"search": f"{first} {last}", "filter": f"affiliations.institution.id:{iid}", "per-page": 10, "select": SEL}
    key = f"author-{f['id']}"
    res = get("authors", params, key).get("results", [])
    if not any(disp_score(f["name"], c) for c in res) and norm(full).split() != [first, last]:
        params = dict(params, search=full); key = f"author2-{f['id']}"
        res = get("authors", params, key).get("results", [])
    cands = [c for c in res if disp_score(f["name"], c) > 0 and compatible(c["display_name"], f["name"])]
    if not cands:
        # last resort: an alternative name that matches first and last name exactly; take only the biggest such profile
        alt = [c for c in res if name_score(f["name"], c) == 2]
        return [max(alt, key=lambda c: c.get("works_count", 0))["id"].rsplit("/", 1)[-1]] if alt else None
    top = max(disp_score(f["name"], c) for c in cands)
    cands = sorted([c for c in cands if disp_score(f["name"], c) == top], key=lambda c: -c.get("works_count", 0))
    best = cands[0]
    group = [best]
    if len(cands) > 1:
        # several profiles with this name at the university: they may be one person split up, or different people.
        # Keep the profile that publishes on language, plus only those other profiles that also publish on language.
        tres = get("authors", dict(params, select=SEL + ",topics"), key + "-topics").get("results", [])
        score = {c["id"]: langy(c) for c in tres}
        best = max(cands, key=lambda c: (score.get(c["id"], 0), c.get("works_count", 0)))
        group = [c for c in cands if c is best or (score.get(c["id"], 0) > 0 and compatible(c["display_name"], best["display_name"]))]
    group.sort(key=lambda c: c is not best)
    return [c["id"].rsplit("/", 1)[-1] for c in group[:MAX_PROFILES]]

def main():
    fac = json.load(open(os.path.join(ROOT, "src", "data", "faculty.json"), encoding="utf8"))
    progs = json.load(open(os.path.join(ROOT, "src", "data", "programs.json"), encoding="utf8"))
    matched, unmatched = {}, []
    try:
        # 1. each university's OpenAlex id
        inst = {}
        for p in progs:
            iid = inst_id(p)
            if iid:
                inst[p["slug"]] = iid
            else:
                print("  ! no OpenAlex institution for", p["name"])
        print(f"Universities found in OpenAlex: {len(inst)} of {len(progs)}")

        # 2. each person's OpenAlex author profile(s), restricted to people affiliated with their university
        for i, f in enumerate(fac, 1):
            iid = inst.get(f["u"])
            if not iid:
                unmatched.append(f["id"]); continue
            ids = find_author(f, iid)
            if ids:
                matched[f["id"]] = ids
            else:
                unmatched.append(f["id"])
            if i % 50 == 0:
                print(f"  people looked up: {i}/{len(fac)} (matched {len(matched)}), API calls this run: {calls}")
        print(f"Faculty matched to OpenAlex: {len(matched)} of {len(fac)}")

        # 3. each matched person's works; keep co-authors who are also on the site
        owner = {a: fid for fid, ids in matched.items() for a in ids}
        pairs = {}
        for i, (fid, ids) in enumerate(matched.items(), 1):
            cursor, page = "*", 0
            while cursor:
                page += 1
                d = get("works", {"filter": "author.id:" + "|".join(ids), "per-page": 200, "cursor": cursor,
                                  "select": "id,title,publication_year,authorships"}, f"works-{fid}-{hashlib.md5('|'.join(ids).encode()).hexdigest()[:8]}-{page}")
                for w in d.get("results", []):
                    au = w.get("authorships") or []
                    if len(au) > MAX_AUTHORS:
                        continue
                    others = {owner.get(((a.get("author") or {}).get("id") or "").rsplit("/", 1)[-1]) for a in au} - {None, fid}
                    for o in others:
                        a, b = sorted((fid, o))
                        e = pairs.setdefault((a, b), {"works": set(), "year": 0, "title": ""})
                        if w["id"] in e["works"]:
                            continue
                        e["works"].add(w["id"])
                        y = w.get("publication_year") or 0
                        if y >= e["year"]:
                            e["year"], e["title"] = y, (w.get("title") or "")[:200]
                cursor = (d.get("meta") or {}).get("next_cursor") if d.get("results") else None
            if i % 50 == 0:
                print(f"  publication lists read: {i}/{len(matched)}, pairs so far: {len(pairs)}, API calls this run: {calls}")
    except OutOfBudget as e:
        print("\nOpenAlex says today's free budget is used up (or it keeps failing).")
        print("Everything fetched so far is saved. Run the same command again tomorrow and it will continue.")
        print("Details:", str(e)[:200])
        sys.exit(1)

    out = {
        "built": date.today().isoformat(),
        "source": "OpenAlex (https://openalex.org), CC0",
        "max_authors": MAX_AUTHORS,
        "matched": len(matched),
        "authors": matched,
        "pairs": sorted([[a, b, len(e["works"]), e["year"], e["title"]] for (a, b), e in pairs.items()], key=lambda r: (-r[2], r[0])),
    }
    json.dump(out, open(OUT, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
    print(f"\nDone. {len(out['pairs'])} co-author pairs among {len(matched)} matched faculty -> src/data/coauthors.json")
    print(f"API calls this run: {calls}")

if __name__ == "__main__":
    main()
