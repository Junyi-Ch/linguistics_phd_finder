#!/usr/bin/env python3
"""Academic family: where each faculty member did their PhD, and advisor -> student links.

Sources
  1. Department profiles we already scraped (data/raw/*.json, kept on your Mac only): the PhD school and year,
     and the advisor when the profile names one ("... dissertation was supervised by X").
  2. Wikidata (open data, CC0): "doctoral advisor" (P184) and "doctoral student" (P185).
     Needs internet; run on your Mac:  python3 pipeline/tree.py
     Without internet it reuses what was fetched before, or skips Wikidata.

Output: src/data/tree.json  (only short facts: PhD school, year, advisor names; no profile text is published)
"""
import json, os, re, sys, glob, time, unicodedata, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
CACHE = os.path.join(ROOT, "data", "cache", "wikidata")
OUT = os.path.join(ROOT, "src", "data", "tree.json")

# ---------- names ----------
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s)

def key(name):
    """first + last name, lower-case, accents removed: 'Edward A. Gibson' -> 'edward gibson'"""
    toks = norm(re.sub(r"\(.*?\)|,.*$|\b(Prof(essor)?|Dr)\.?\s", " ", name or "")).split()
    return f"{toks[0]} {toks[-1]}" if len(toks) >= 2 else ""

# ---------- 1. profiles ----------
PHD = re.compile(r"\b(Ph\.?\s?D\.?|PhD|Doctorate|doctoral degree|D\.\s?Phil\.?|DPhil|Doctor of Philosophy)", re.I)
CAMPUS = r"(?:,?\s(?:at\s)?(?:Berkeley|Los Angeles|San Diego|Santa Cruz|Santa Barbara|Davis|Irvine|Amherst|College Park|Austin|Arlington|El Paso|Twin Cities|Chapel Hill|Urbana[\- ]Champaign|Madison|Milwaukee|Ann Arbor|Seattle|Buffalo|M[aā]noa|Bloomington|Boulder|Tucson|Pittsburgh|New Brunswick))?"
CAP = r"[A-Z][A-Za-zÀ-ÿ\-’‘'ʻ]*"
INST = re.compile(
    r"((?:[Tt]he )?(?:University of (?:" + CAP + r" ?){1,3}" + CAMPUS +
    r"|(?:" + CAP + r" ){1,3}University(?: of (?:" + CAP + r" ?){1,3})?" + CAMPUS +
    r"|Universit(?:é|at|ät|à|ad|ade|eit|y) (?:[A-Za-zÀ-ÿ\-’‘'ʻ]+ ?){1,4}" +
    r"|(?:" + CAP + r" ){1,3}(?:College|Institute(?: of Technology)?)" +
    r"|MIT|UCLA|UCSD|UCSC|UCSB|UC\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?|USC|NYU|CUNY(?: Graduate Center)?|UMass(?: Amherst)?|UConn|UIUC|UT[\s\-]Austin|UW[\s\-–]Madison"
    r"|Stanford|Harvard|Yale|Princeton|Cornell|Rutgers|Georgetown|Northwestern|Berkeley|Oxford|Cambridge|Edinburgh|Johns Hopkins|Stony Brook|Brown|Penn State|Ohio State|Michigan State|Leiden|Utrecht|McGill|Brandeis|Columbia|Carnegie Mellon)\b)")
YEAR = re.compile(r"(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)")
NEXT_DEGREE = re.compile(r"\b(M\.?A\.?|B\.?A\.?|M\.?S\.?c?|B\.?S\.?c?|MSt|MPhil|M\.Phil|Postdoc|Post-doc|Licenciatura|Diploma)\b|\n| - |[.;]\s")
ADV = re.compile(r"(?:supervis(?:ed|ion|or)|advis(?:ed|or|er)|under the (?:direction|guidance|mentorship|supervision) of|direct(?:ed|ion) of|co-advised)\s(?:by\s|of\s|was\s)?((?:Prof(?:essor)?\.?\s|Dr\.?\s)?[A-Z][a-zà-ÿ\-]+(?:\s[A-Z]\.)?(?:\s(?:de|van|von|di|da)?\s?[A-Z][a-zà-ÿ\-]+){1,2}(?:\s(?:and|&)\s[A-Z][a-zà-ÿ\-]+(?:\s[A-Z]\.)?(?:\s[A-Z][a-zà-ÿ\-]+){1,2})?)")

# school names written in many ways -> one name
ALIASES = [
    (r"^(mit|massachusetts institute of technology)$", "Massachusetts Institute of Technology"),
    (r"^(ucla|university of california,? (at )?los angeles|uc los angeles)$", "University of California, Los Angeles"),
    (r"^(uc berkeley|berkeley|university of california,? (at )?berkeley)$", "University of California, Berkeley"),
    (r"^(ucsd|uc san diego|university of california,? (at )?san diego)$", "University of California, San Diego"),
    (r"^(ucsc|uc santa cruz|university of california,? (at )?santa cruz)$", "University of California, Santa Cruz"),
    (r"^(ucsb|uc santa barbara|university of california,? (at )?santa barbara)$", "University of California, Santa Barbara"),
    (r"^(uc davis|university of california,? (at )?davis)$", "University of California, Davis"),
    (r"^(uc irvine|university of california,? (at )?irvine)$", "University of California, Irvine"),
    (r"^(ut austin|ut-austin|university of texas( at austin)?)$", "University of Texas at Austin"),
    (r"^(uiuc|university of illinois(,? (at )?urbana[\- ]champaign)?)$", "University of Illinois Urbana-Champaign"),
    (r"^(umass( amherst)?|university (of )?massachusetts(,? (at )?amherst)?)$", "University of Massachusetts Amherst"),
    (r"^(uw[\s\-–]madison|university of wisconsin(,? (at )?madison)?)$", "University of Wisconsin–Madison"),
    (r"^(university of maryland(,? college park)?)$", "University of Maryland, College Park"),
    (r"^(university of minnesota(,? twin cities)?)$", "University of Minnesota, Twin Cities"),
    (r"^(university of michigan(,? ann arbor)?)$", "University of Michigan"),
    (r"^(university of washington(,? seattle)?)$", "University of Washington"),
    (r"^(university of hawai.?i(,? (at )?m[aā]noa)?)$", "University of Hawaii at Manoa"),
    (r"^(university of north carolina(,? (at )?chapel hill)?|unc chapel hill)$", "University of North Carolina at Chapel Hill"),
    (r"^(usc|university of southern california)$", "University of Southern California"),
    (r"^(nyu|new york university)$", "New York University"),
    (r"^(cuny( graduate center)?|city university of new york( graduate center)?|graduate center,? cuny)$", "City University of New York Graduate Center"),
    (r"^(uconn|university of connecticut)$", "University of Connecticut"),
    (r"^(penn|university of pennsylvania)$", "University of Pennsylvania"),
    (r"^(penn state( university)?|pennsylvania state university)$", "Pennsylvania State University"),
    (r"^(ohio state( university)?)$", "Ohio State University"),
    (r"^(stony brook( university)?|suny stony brook)$", "Stony Brook University"),
    (r"^(rutgers( university)?)$", "Rutgers University–New Brunswick"),
    (r"^(indiana university( bloomington)?)$", "Indiana University Bloomington"),
    (r"^(cambridge( university)?|university of cambridge)$", "University of Cambridge"),
    (r"^(oxford( university)?|university of oxford)$", "University of Oxford"),
    (r"^(edinburgh|university of edinburgh)$", "University of Edinburgh"),
    (r"^(university at buffalo|suny buffalo|university at buffalo, suny)$", "University at Buffalo, SUNY"),
    (r"^(university of colorado(,? (at )?boulder)?|cu boulder)$", "University of Colorado Boulder"),
]
for short in ["Stanford", "Harvard", "Yale", "Princeton", "Cornell", "Georgetown", "Northwestern", "Johns Hopkins", "Brown", "Michigan State",
              "Brandeis", "Columbia", "Carnegie Mellon", "Boston", "Purdue", "Rice", "Tulane", "Syracuse", "Vanderbilt", "Arizona State", "Georgia State", "Northern Arizona"]:
    ALIASES.append((rf"^({short.lower()}( university)?)$", f"{short} University"))
# every university on the site, by its own name
for _p in json.load(open(os.path.join(ROOT, "src", "data", "programs.json"), encoding="utf8")):
    ALIASES.append(("^" + re.sub(r"\s+", " ", re.sub(r"\bat\b", " ", norm(_p["name"]))).strip() + "$", _p["name"]))
ALIASES = [(re.compile(a.replace(",? (at )?", " ").replace(",? ", " ").replace("( at ", "( ")), b) for a, b in ALIASES]
STOP = set("while sciences science linguistics psychology her his she he their they not contact email personal website research i as in from and at ph the my our after before since then where with".split())
BAD = re.compile(r"^(the )?(university|college|institute)$|department|school of|faculty of|program|calendar|\bhall\b|cum laude|beckman|rehabilitation|language technologies|^graduate college$|^national institute$", re.I)

def _low(s):
    low = norm(s)
    low = re.sub(r"\bat\b", " ", low)
    return re.sub(r"\s+", " ", low).strip()

def canon(inst):
    """clean a school name found in a profile; None when unsure"""
    s = re.sub(r"\s+", " ", inst.strip(" ,.;:-"))
    toks = s.replace(",", " ,").split()
    # 1. any stretch of words that is a known school
    for i in range(len(toks)):
        for j in range(len(toks), i, -1):
            low = _low(" ".join(toks[i:j]))
            for rx, name in ALIASES:
                if rx.match(low):
                    return name
    # 2. otherwise trim stray words at both ends
    toks = [t for t in toks if t != ","]
    for i, t in enumerate(toks):
        if t.endswith((".", ";", ":")) and i > 0:
            toks = toks[:i] + [t.rstrip(".;:")]
            break
    while toks and (toks[0].lower() in STOP or toks[0].lower() == "the"):
        toks = toks[1:]
    k = next((i for i, t in enumerate(toks) if i > 0 and (t.lower().strip("’'s") in STOP or t.endswith(("’s", "'s")))), len(toks))
    toks = toks[:k]
    s = " ".join(toks)
    if not re.search(r"(Universit|College|Institute)", s) or BAD.search(s) or len(toks) < 2:
        return None
    if re.fullmatch(r"University of California", s):
        return None  # campus not given
    if toks[-1] == "of":
        return None
    return s

def from_profile(bio):
    phd = None
    for m in PHD.finditer(bio or ""):
        after = bio[m.end():m.end() + 160]
        before = bio[max(0, m.start() - 120):m.start()]
        im = INST.search(after)
        if not im:
            # "University of X, PhD" written just before the degree
            ims = [x for x in INST.finditer(before) if len(before) - x.end() <= 25 and "\n" not in before[x.end():]]
            im = ims[-1] if ims else None
        if not im:
            continue
        name = canon(im.group(1))
        if not name:
            continue
        # the year: "2012 PhD ..." or "PhD ..., 2012" (stopping at the next degree, line or sentence)
        y = None
        pre = re.search(r"(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)[\s,:\-–]*$", bio[max(0, m.start() - 12):m.start()])
        if pre:
            y = pre
        else:
            stop = NEXT_DEGREE.search(after)
            y = YEAR.search(after[: stop.start() if stop else 120])
        year = int(y.group(1)) if y else None
        if year and year > 2026:
            year = None
        phd = {"inst": name, "year": year}
        break
    advisors = []
    for m in ADV.finditer(bio or ""):
        ctx = bio[max(0, m.start() - 220):m.end()]
        if not re.search(r"dissertation|thesis|Ph\.?\s?D|doctoral|doctorate", ctx, re.I):
            continue
        for part in re.split(r"\s(?:and|&)\s", m.group(1)):
            part = re.sub(r"^(Prof(essor)?|Dr)\.?\s", "", part).strip()
            if len(part.split()) >= 2 and part not in advisors:
                advisors.append(part)
        break
    return phd, advisors

# ---------- 2. Wikidata ----------
SPARQL = "https://query.wikidata.org/sparql"
LANGY = re.compile(r"lingu|language|speech|phon|psycholog|cognitive|computer scien|philosoph|anthropolog|professor|researcher|academic|scholar", re.I)

def sparql(q, cache_name):
    cp = os.path.join(CACHE, cache_name + ".json")
    if os.path.exists(cp):
        return json.load(open(cp, encoding="utf8"))
    url = SPARQL + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "linguistics-phd-explorer/1.0 (academic family links; https://github.com/Junyi-Ch/linguistics_phd_finder)", "Accept": "application/sparql-results+json"})
    for attempt in range(5):
        try:
            time.sleep(1.0)
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)
            os.makedirs(CACHE, exist_ok=True)
            json.dump(d, open(cp, "w", encoding="utf8"))
            return d
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    raise last

def wikidata(fac):
    """for each faculty member: Wikidata item (if a confident match) with doctoral advisors and students"""
    out = {}
    names = {}
    for f in fac:
        variants = {re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", f["name"])).strip()}
        k = key(f["name"])
        toks = re.sub(r"\(.*?\)", "", f["name"]).split()
        if len(toks) >= 2:
            variants.add(f"{toks[0]} {toks[-1]}")
        for v in variants:
            names.setdefault(v, []).append(f)
    allnames = sorted(names)
    rows = []
    for b in range(0, len(allnames), 60):
        chunk = allnames[b:b + 60]
        values = " ".join('"' + n.replace('"', '') + '"@en' for n in chunk)
        q = f"""SELECT ?name ?item ?desc ?adv ?advLabel ?stu ?stuLabel ?empLabel WHERE {{
  VALUES ?name {{ {values} }}
  ?item rdfs:label ?name ; wdt:P31 wd:Q5 .
  OPTIONAL {{ ?item schema:description ?desc FILTER(LANG(?desc)="en") }}
  OPTIONAL {{ ?item wdt:P184 ?adv }}
  OPTIONAL {{ ?item wdt:P185 ?stu }}
  OPTIONAL {{ ?item wdt:P108 ?emp }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}"""
        d = sparql(q, f"names-{b // 60:03d}")
        rows += d["results"]["bindings"]
        print(f"  Wikidata: {min(b + 60, len(allnames))}/{len(allnames)} names checked")
    items = {}
    for r in rows:
        v = lambda k: r.get(k, {}).get("value")
        it = items.setdefault(v("item"), {"name": v("name"), "desc": v("desc") or "", "adv": {}, "stu": {}, "emp": set()})
        if v("adv"): it["adv"][v("adv")] = v("advLabel")
        if v("stu"): it["stu"][v("stu")] = v("stuLabel")
        if v("empLabel"): it["emp"].add(v("empLabel"))
    progs = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "src", "data", "programs.json"), encoding="utf8"))}
    for qid, it in items.items():
        if not (it["adv"] or it["stu"]):
            continue
        for f in names.get(it["name"], []):
            uni = progs.get(f["u"], {}).get("name", "")
            emp_ok = any(norm(uni).split()[-1:] and set(norm(uni).split()) & set(norm(e).split()) - {"university", "of", "the", "at", "college"} for e in it["emp"])
            desc_ok = bool(LANGY.search(it["desc"]))
            if not (emp_ok or desc_ok):
                continue
            prev = out.get(f["id"])
            if prev and prev["qid"] != qid:
                out[f["id"]] = None  # two different Wikidata people with this name: too unsure, skip
                continue
            out[f["id"]] = {"qid": qid.rsplit("/", 1)[-1], "adv": sorted(set(it["adv"].values())), "stu": sorted(set(it["stu"].values()))}
    return {k: v for k, v in out.items() if v}

# ---------- main ----------
# ---------- 3. Academic Family Tree (academictree.org data export, CC BY) ----------
AT_DIR = os.path.join(ROOT, "data", "academictree")
AT_RECORD = "https://zenodo.org/api/records/13953546/versions/latest"
AT_FILES = ["people.csv.gz", "connect.csv.gz", "locations.csv.gz"]

def at_download():
    """fetch the newest Academic Family Tree export from Zenodo (about 90 MB, once)"""
    os.makedirs(AT_DIR, exist_ok=True)
    if all(os.path.exists(os.path.join(AT_DIR, f)) for f in AT_FILES):
        return True
    req = urllib.request.Request(AT_RECORD, headers={"User-Agent": "linguistics-phd-explorer/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        rec = json.load(r)
    links = {f["key"]: f["links"]["self"] for f in rec.get("files", [])}
    print(f"  Academic Family Tree export: version {rec.get('metadata', {}).get('version', '?')}")
    for name in AT_FILES:
        dest = os.path.join(AT_DIR, name)
        if os.path.exists(dest) or name not in links:
            continue
        print(f"  downloading {name} ...")
        tmp = dest + ".part"
        with urllib.request.urlopen(urllib.request.Request(links[name], headers={"User-Agent": "linguistics-phd-explorer/1.0"}), timeout=600) as r, open(tmp, "wb") as out:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                out.write(chunk)
        os.replace(tmp, dest)
    return all(os.path.exists(os.path.join(AT_DIR, f)) for f in AT_FILES)

def at_rows(name):
    import csv, gzip
    csv.field_size_limit(10 ** 8)
    with gzip.open(os.path.join(AT_DIR, name), "rt", encoding="utf8", errors="replace", newline="") as fh:
        rd = csv.DictReader(fh)
        print(f"  {name} columns: {rd.fieldnames}")
        for r in rd:
            yield {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}

def at_name(r):
    if r.get("name"):
        return r["name"]
    first = r.get("fname") or r.get("firstname") or r.get("first") or ""
    last = r.get("lname") or r.get("lastname") or r.get("last") or ""
    return f"{first} {last}".strip()

AT_AREAS = re.compile(r"ling|psych|neuro|cogsci|computerscience|anthro|education|philosophy|speech|commsci|hearing|language", re.I)

def academictree(fac):
    """advisor (grad-student mentor) links for faculty on the site, from the Academic Family Tree export"""
    if not at_download():
        raise RuntimeError("export files missing")
    progs = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "src", "data", "programs.json"), encoding="utf8"))}
    want = {}
    for f in fac:
        want.setdefault(key(f["name"]), []).append(f)
    # people whose first+last name matches someone on the site
    people, cand = {}, {}
    for r in at_rows("people.csv.gz"):
        pid = r.get("pid")
        if not pid:
            continue
        nm = at_name(r)
        people[pid] = (nm, r.get("majorarea", ""))
        k = key(nm)
        if k in want:
            cand.setdefault(k, []).append(pid)
    locs = {}
    for r in at_rows("locations.csv.gz"):
        locs[r.get("locid")] = r.get("location") or r.get("name") or r.get("locname") or ""
    conns, places = [], {}
    for r in at_rows("connect.csv.gz"):
        p1, p2, rel, loc = r.get("pid1"), r.get("pid2"), r.get("relation"), r.get("locid")
        places.setdefault(p1, set()).add(loc)
        if p2 and p2 != "0":
            places.setdefault(p2, set()).add(loc)
        if rel == "1" and p2 and p2 != "0":
            conns.append((p1, p2))
    def uni_words(s):
        return set(norm(s).split()) - {"university", "of", "the", "at", "college", "state", "institute", "and", "school", "department", "linguistics"}
    # choose one Academic Family Tree person per faculty member
    match = {}
    for k, fs in want.items():
        pids = cand.get(k, [])
        for f in fs:
            uw = uni_words(progs.get(f["u"], {}).get("name", ""))
            scored = []
            for pid in pids:
                area = people[pid][1]
                at_uni = any(uw and uw <= uni_words(locs.get(l, "")) for l in places.get(pid, ()))
                score = (2 if at_uni else 0) + (1 if AT_AREAS.search(area) else 0)
                if score:
                    scored.append((score, pid))
            scored.sort(reverse=True)
            if scored and (len(scored) == 1 or scored[0][0] > scored[1][0]):
                match[f["id"]] = scored[0][1]
    by_pid = {pid: fid for fid, pid in match.items()}
    edges = []
    for s, a in conns:
        if s in by_pid or a in by_pid:
            edges.append({"student": by_pid.get(s), "student_name": None if s in by_pid else people.get(s, ("",))[0],
                          "advisor": by_pid.get(a), "advisor_name": None if a in by_pid else people.get(a, ("",))[0], "src": "academictree"})
    print(f"Academic Family Tree: {len(match)} faculty matched, {len(edges)} PhD advisor links")
    return match, edges


def main():
    fac = json.load(open(os.path.join(ROOT, "src", "data", "faculty.json"), encoding="utf8"))
    site = {f["id"] for f in fac}
    bykey = {}
    for f in fac:
        bykey.setdefault(key(f["name"]), []).append(f["id"])
    # 1. profiles
    bios = {}
    for fn in glob.glob(os.path.join(RAW, "*.json")):
        d = json.load(open(fn, encoding="utf8"))
        for r in d.get("faculty", []):
            bios[(d.get("slug"), key(r.get("name")))] = r.get("bio") or ""
    phd, adv_edges = {}, []
    for f in fac:
        bio = bios.get((f["u"], key(f["name"])), "")
        p, advs = from_profile(bio)
        if p:
            phd[f["id"]] = p
        for a in advs:
            adv_edges.append({"student": f["id"], "advisor_name": a, "src": "profile"})
    print(f"Profiles: PhD school found for {len(phd)} of {len(fac)}; advisors named in {len({e['student'] for e in adv_edges})} profiles")
    # 2. Wikidata
    wd = {}
    try:
        wd = wikidata(fac)
        print(f"Wikidata: {len(wd)} faculty matched with advisor/student information")
    except Exception as e:
        print("Wikidata skipped (no internet here?):", str(e)[:120])
    for fid, w in wd.items():
        for a in w["adv"]:
            adv_edges.append({"student": fid, "advisor_name": a, "src": "wikidata"})
        for s in w["stu"]:
            adv_edges.append({"student_name": s, "advisor": fid, "src": "wikidata"})
    # 3. Academic Family Tree
    at = {}
    try:
        at, at_edges = academictree(fac)
        adv_edges = at_edges + adv_edges   # listed first, so its spelling of names wins
    except Exception as e:
        print("Academic Family Tree skipped:", str(e)[:160])
    # resolve names to people on the site; drop duplicates
    def resolve(name):
        ids = bykey.get(key(name), [])
        return ids[0] if len(ids) == 1 else None
    edges, seen = [], set()
    for e in adv_edges:
        s = e.get("student") or resolve(e.get("student_name", ""))
        a = e.get("advisor") or resolve(e.get("advisor_name", ""))
        if not (s or e.get("student_name")) or not (a or e.get("advisor_name")):
            continue
        sname = e.get("student_name") or next(f["name"] for f in fac if f["id"] == s)
        aname = e.get("advisor_name") or next(f["name"] for f in fac if f["id"] == a)
        k = (s or key(sname), a or key(aname))
        if k in seen:
            continue
        seen.add(k)
        if re.fullmatch(r"Q\d+", sname or "") or re.fullmatch(r"Q\d+", aname or ""):
            continue  # Wikidata item without an English name
        if s in site or a in site:
            edges.append([s, sname if s is None else None, a, aname if a is None else None, e["src"]])
    out = {
        "built": time.strftime("%Y-%m-%d"),
        "sources": ["department profiles"] + (["Wikidata (CC0)"] if wd else []) + (["Academic Family Tree (academictree.org, CC BY)"] if at else []),
        "academictree": at,
        "phd": phd,
        "wikidata": {k: v["qid"] for k, v in wd.items()},
        "advising": edges,  # [student_id|null, student_name_if_not_on_site, advisor_id|null, advisor_name_if_not_on_site, source]
    }
    json.dump(out, open(OUT, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
    both = sum(1 for e in edges if e[0] and e[2])
    print(f"Done: {len(phd)} PhD schools, {len(edges)} advisor links ({both} between two people on the site) -> src/data/tree.json")

if __name__ == "__main__":
    main()
