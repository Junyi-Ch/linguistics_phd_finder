#!/usr/bin/env python
"""Write research summaries and labels with a local model (Ollama), free and offline.

  ollama pull qwen2.5:7b                              # once (about 5 GB)
  python pipeline/label_local.py                      # all data/raw/*.json -> data/labels/<slug>.json
  python pipeline/label_local.py --only ucla          # some universities (slug prefixes)
  python pipeline/label_local.py --model qwen2.5:14b  # a bigger model if your Mac has the memory (slower, better)
  python pipeline/label_local.py --redo               # relabel people already done

It resumes where it stopped: people already in data/labels/<slug>.json are skipped, and the file is saved after
each person. The model sees only the public profile text, research areas and paper titles. The output is checked
against pipeline/taxonomy.json (the label codes are given to Ollama as fixed choices, so it cannot invent codes).
"""
import argparse, json, re, sys, time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAX = json.load(open(ROOT / "pipeline" / "taxonomy.json", encoding="utf-8"))
DIMS = list(TAX["dimensions"])
OLLAMA = "http://localhost:11434/api/chat"
NAMES = {"topic": "subfields", "approach": "methods", "data": "data", "setting": "populations", "region": "languages"}

def codebook():
    lines = []
    for d in DIMS:
        dim = TAX["dimensions"][d]
        lines.append(f"\n{d} ({dim['label']}: {dim['description']})")
        for c, l in dim["labels"].items():
            lines.append(f"  {c}: {l}")
    return "\n".join(lines)

SYSTEM = f"""You describe a university researcher's work for a website that helps PhD applicants in linguistics find advisors.
Use ONLY the profile text given. Do not use outside knowledge about the person. If the profile says little, say little.

Return JSON with:
- summary: ONE sentence, at most 200 characters, present tense, without the person's name, saying what they study and how.
  Example: "Studies tone and intonation in Bantu languages through fieldwork and acoustic analysis."
- summary_zh: the same sentence in natural Chinese.
- keywords: 5 to 10 specific lowercase terms from the profile (phenomena, languages, methods), e.g. "tone sandhi", "visual world paradigm", "quechua".
- confidence: "high" if the profile describes their research in detail, "medium" if briefly, "low" if almost not at all.
- labels: for each dimension below, 0 to 4 codes that the profile clearly supports. Mark primary=true only for their main emphasis
  (at least one primary subfield). Leave a dimension empty rather than guess.
  For "region" (languages): only languages the research is actually about; English only when English itself is studied.
Codes:{codebook()}
"""

def schema():
    lab = lambda d: {"type": "array", "maxItems": 4, "items": {"type": "object", "required": ["code", "primary"],
            "properties": {"code": {"type": "string", "enum": list(TAX["dimensions"][d]["labels"])}, "primary": {"type": "boolean"}}}}
    return {"type": "object", "required": ["summary", "summary_zh", "keywords", "confidence", "labels"],
            "properties": {"summary": {"type": "string"}, "summary_zh": {"type": "string"},
                           "keywords": {"type": "array", "items": {"type": "string"}},
                           "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                           "labels": {"type": "object", "required": DIMS, "properties": {d: lab(d) for d in DIMS}}}}

def person_prompt(f):
    parts = [f"Name: {f['name']}", f"Title: {f.get('title') or f['rank']}", f"Department: {f.get('department','')}"]
    if f.get("research_areas"):
        parts.append("Research areas listed by the department: " + "; ".join(f["research_areas"]))
    bio = re.sub(r"\s+", " ", f.get("bio") or "").strip()
    parts.append("Profile text: " + (bio[:3500] or "(none)"))
    works = f.get("works") or []
    if works:
        parts.append("Recent paper titles: " + "; ".join(w["title"] for w in works[:15]))
    return "\n".join(parts)

def shorten(s, n=200):
    s = re.sub(r"\s+", " ", s or "").strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    return (cut[: cut.rfind(" ")] if " " in cut else cut).rstrip(",;: ") + "."

def call(model, f, timeout=300):
    import requests
    body = {"model": model, "stream": False, "format": schema(),
            "options": {"temperature": 0.2, "num_ctx": 8192},
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": person_prompt(f)}]}
    r = requests.post(OLLAMA, json=body, timeout=timeout)
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])

def clean(out, f):
    srcs = ["department_profile"] + (["publications"] if f.get("works") else [])
    labels = {}
    for d in DIMS:
        items, seen = [], set()
        for it in (out.get("labels", {}).get(d) or []):
            c = it.get("code")
            if c in TAX["dimensions"][d]["labels"] and c not in seen:
                seen.add(c); items.append({"code": c, "primary": bool(it.get("primary")), "sources": srcs})
        labels[d] = items[:4]
    if labels["topic"] and not any(x["primary"] for x in labels["topic"]):
        labels["topic"][0]["primary"] = True
    kw = [k.strip().lower() for k in out.get("keywords") or [] if 1 < len(k.strip()) < 50][:10]
    return {"name": f["name"], "summary": shorten(out.get("summary")), "summary_zh": (out.get("summary_zh") or "").strip()[:120],
            "confidence": out.get("confidence") if out.get("confidence") in ("high", "medium", "low") else "low",
            "labels": labels, "keywords": kw}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--only")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    try:
        import requests
        requests.get("http://localhost:11434/api/tags", timeout=5).raise_for_status()
    except Exception:
        sys.exit("Ollama is not running. Open the Ollama app (or run `ollama serve`), then `ollama pull " + a.model + "`.")
    files = sorted((ROOT / "data" / "raw").glob("*.json"))
    if a.only:
        files = [f for f in files if any(f.stem.startswith(k) for k in a.only.split(","))]
    todo_total = sum(len(json.load(open(f, encoding="utf-8"))["faculty"]) for f in files)
    done, t0 = 0, time.time()
    out_dir = ROOT / "data" / "labels"; out_dir.mkdir(parents=True, exist_ok=True)
    for fp in files:
        raw = json.load(open(fp, encoding="utf-8"))
        lp = out_dir / f"{raw['slug']}.json"
        have = json.load(open(lp, encoding="utf-8")) if lp.exists() and not a.redo else {"faculty": []}
        by_name = {x["name"]: x for x in have["faculty"]}
        result = {"slug": raw["slug"], "labeled_at": date.today().isoformat(), "faculty": []}
        for f in raw["faculty"]:
            done += 1
            if f["name"] in by_name:
                result["faculty"].append(by_name[f["name"]]); continue
            rec = None
            for attempt in range(2):
                try:
                    rec = clean(call(a.model, f), f)
                    if len(rec["summary"]) >= 20:
                        break
                except Exception as e:
                    print(f"  retry {f['name']}: {str(e)[:100]}")
            if not rec or len(rec["summary"]) < 20:
                rec = {"name": f["name"], "summary": shorten(f"{f.get('rank','Faculty')} in the {f.get('department') or 'department'}; the public profile gives little detail."), "summary_zh": "",
                       "confidence": "low", "labels": {d: [] for d in DIMS}, "keywords": []}
            result["faculty"].append(rec)
            json.dump(result, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            el = time.time() - t0
            print(f"[{done}/{todo_total}] {raw['slug']}: {f['name']} — {rec['summary'][:70]}  ({el/60:.0f} min)")
        json.dump(result, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Done. Check with: python pipeline/validate_labels.py data/labels/*.json")

if __name__ == "__main__":
    main()
