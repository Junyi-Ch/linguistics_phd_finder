#!/usr/bin/env python3
"""Re-read personal-website and Google Scholar links from the cached profile pages (no internet needed).

Earlier, a personal site was only kept when its link pointed to a different university domain, so links like
"Website -> www.acsu.buffalo.edu/~shimojo" or "Personal Website -> campuspress.yale.edu/jasonshaw" were dropped.
This script uses the improved rules in scrape_local.profile_links and updates data/raw/*.json and src/data/faculty.json.

    python3 pipeline/relink.py
"""
import json, os, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import fetch  # noqa: E402
from scrape_local import profile_links, clean_url, SOCIAL, PUBLISHER  # noqa: E402

def cached(url):
    for render in (False, True):
        p = fetch.cache_path(url, render)
        if p.exists():
            return p.read_text(errors="ignore")
    return None

def shared_old(f):
    return False

def main():
    fac_path = ROOT / "src" / "data" / "faculty.json"
    fac = json.loads(fac_path.read_text())
    shared = collections.Counter(f["profile"] for f in fac if f["profile"])
    before = sum(bool(f["site"]) for f in fac), sum(bool(f["scholar"]) for f in fac)
    found = {}
    for f in fac:
        url = f["profile"]
        if not url or shared[url] > 1:      # a list page shared by several people: links there are not this person's
            continue
        html = cached(url)
        if not html:
            continue
        site, scholar = profile_links(html, url, f["name"])
        found[url] = (site, scholar)
        f["site"] = site or (f["site"] if f["site"] and not shared_old(f) else None)
        if scholar: f["scholar"] = scholar
    # tidy every site link, and drop ones that are clearly not personal sites
    uses = collections.Counter(clean_url(f["site"]) for f in fac if f["site"])
    for f in fac:
        if f["site"]:
            u = clean_url(f["site"])
            f["site"] = None if (SOCIAL.search(u) or PUBLISHER.search(u) or uses[u] > 1) else u
    fac_path.write_text(json.dumps(fac, ensure_ascii=False, separators=(",", ":")))
    # keep the raw files in step so the next build keeps the links
    for rp in (ROOT / "data" / "raw").glob("*.json"):
        d = json.loads(rp.read_text())
        changed = False
        for r in d.get("faculty", []):
            if r.get("profile_url") in found:
                site, scholar = found[r["profile_url"]]
                if site and r.get("personal_url") != site: r["personal_url"] = site; changed = True
                if scholar and r.get("google_scholar_url") != scholar: r["google_scholar_url"] = scholar; changed = True
        if changed:
            rp.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    after = sum(bool(f["site"]) for f in fac), sum(bool(f["scholar"]) for f in fac)
    print(f"Personal sites: {before[0]} -> {after[0]};  Google Scholar: {before[1]} -> {after[1]}  (of {len(fac)})")

if __name__ == "__main__":
    main()
