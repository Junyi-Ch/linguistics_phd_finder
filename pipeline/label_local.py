#!/usr/bin/env python
"""Write research summaries and labels with a local model (Ollama), free and offline.

  ollama pull qwen2.5:7b                              # once (about 5 GB)
  python pipeline/label_local.py                      # all data/raw/*.json -> data/labels/<slug>.json
  python pipeline/label_local.py --only ucla          # some universities (slug prefixes)
  python pipeline/label_local.py --model qwen2.5:14b  # a bigger model if your Mac has the memory (slower, better)
  python pipeline/label_local.py --redo               # relabel people already done
  python pipeline/label_local.py --discipline psych   # psychology: data/psych/raw -> data/psych/labels

It resumes where it stopped: people already in data/labels/<slug>.json are skipped, and the file is saved after
each person. The model sees only the public profile text, research areas and paper titles. The output is checked
against pipeline/taxonomy.json (the label codes are given to Ollama as fixed choices, so it cannot invent codes).
"""
import argparse, json, os, re, sys, time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from disciplines import current  # noqa: E402
DISC, CFG = current()  # --discipline psych (or DISCIPLINE=psych) switches prompts, taxonomy and folders
TAX = json.load(open(CFG["taxonomy"], encoding="utf-8"))
DIMS = list(TAX["dimensions"])
OLLAMA = "http://localhost:11434/api/chat"
NAMES = {"topic": "subfields", "approach": "methods", "data": "data", "setting": "populations", "region": "languages"}

SUMMARY_SYSTEM = CFG["summary_system"]

def codebook(dims):
    lines = []
    for d in dims:
        dim = TAX["dimensions"][d]
        lines.append(f"\n{d} = {dim['label']}:")
        for c, l in dim["labels"].items():
            lines.append(f"  {c}: {l}")
    return "\n".join(lines)

LABEL_SYSTEM = CFG["label_intro"] + "Codes:" + codebook(DIMS) + "\n"

def summary_schema():
    extra = CFG["extra_summary_fields"]
    return {"type": "object", "required": ["summary", "summary_zh", "keywords", "confidence"] + list(extra),
            "properties": {"summary": {"type": "string"}, "summary_zh": {"type": "string"},
                           "keywords": {"type": "array", "items": {"type": "string"}},
                           "confidence": {"type": "string", "enum": ["high", "medium", "low"]}, **extra}}

def label_schema():
    codes = lambda d: list(TAX["dimensions"][d]["labels"])
    arr = lambda d, lo=0: {"type": "array", "minItems": lo, "maxItems": 4, "items": {"type": "string", "enum": codes(d)}}
    props = {d: arr(d, 1 if d == "topic" else 0) for d in DIMS}
    props["primary_topic"] = {"type": "string", "enum": codes("topic")}
    return {"type": "object", "required": ["topic", "primary_topic"] + [d for d in DIMS if d != "topic"], "properties": props}

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

def ask(model, system, user, schema, timeout=300):
    import requests
    body = {"model": model, "stream": False, "format": schema, "options": {"temperature": 0.1, "num_ctx": 8192},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    r = requests.post(OLLAMA, json=body, timeout=timeout)
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])

def call(model, f):
    prof = person_prompt(f)
    out = ask(model, SUMMARY_SYSTEM, prof, summary_schema())
    lab_in = prof + f"\nSummary: {out.get('summary','')}\nKeywords: {', '.join(out.get('keywords') or [])}"
    out["labels"] = ask(model, LABEL_SYSTEM, lab_in, label_schema())
    return out

# a language code is kept only when the profile names something from that group
REGION_EVIDENCE = {
    "R_ENGLISH": r"english|american (english|dialect)|aave|african american (vernacular )?english|southern us",
    "R_ROMANCE": r"spanish|portuguese|french|italian|romanian|catalan|romance|latin american|hispanic|galician|occitan",
    "R_GERMANIC": r"german|dutch|swedish|norwegian|danish|icelandic|yiddish|afrikaans|frisian|germanic|faroese",
    "R_SLAVIC_E_EUROPE": r"russian|polish|czech|slovak|ukrainian|serbian|croatian|bosnian|bulgarian|slovene|slavic|baltic|lithuanian|latvian|georgian|armenian|hungarian|finnish|estonian|albanian|romani|caucas",
    "R_CHINESE": r"chinese|mandarin|cantonese|sinitic|taiwanese|hokkien|wu |shanghainese",
    "R_JAPANESE_KOREAN": r"japanese|korean",
    "R_SE_ASIA_PACIFIC": r"austronesian|tagalog|filipino|indonesian|malay|javanese|thai|lao|vietnamese|khmer|burmese|tibet|hmong|maori|hawaiian|samoan|tongan|oceanic|papua|pacific|tai-kadai|austroasiatic|polynesian|micronesian|melanesian|new guinea|pahoturi|ende\b",
    "R_SOUTH_ASIA": r"hindi|urdu|bengali|bangla|punjabi|marathi|gujarati|tamil|telugu|kannada|malayalam|nepali|sinhala|indo-aryan|dravidian|south asia",
    "R_MIDDLE_EAST": r"arabic|hebrew|persian|farsi|turkish|kurdish|uzbek|kazakh|uyghur|turkic|semitic|aramaic|pashto|middle east|central asia",
    "R_AFRICA": r"africa|bantu|swahili|yoruba|igbo|zulu|xhosa|isixhosa|hausa|amharic|wolof|akan|twi|ewe|somali|niger-congo|nilo|khoisan|berber|shona|kinyarwanda|luganda|chichewa|setswana|sesotho",
    "R_AMERICAS_INDIGENOUS": r"indigenous|native american|quechua|aymara|maya|mayan|nahuatl|navajo|zapotec|mixtec|guarani|cherokee|ojibwe|lakota|inuit|yupik|salish|uto-aztecan|amazon|otomanguean|algonquian|athabaskan|iroquoian|k'iche|kaqchikel|tzotzil|mapudungun|american indian",
    "R_SIGN": r"sign language|\basl\b|signers?|deaf",
    "R_CROSSLING": r"cross-?linguistic|typolog|language universals|many languages|comparative",
    "R_CLASSICAL": r"latin|ancient greek|classical|sanskrit|old chinese|old english|old norse|hittite|indo-european|homeric|biblical|akkadian|egyptian|old irish|gothic",
}

EVIDENCE = CFG["evidence"] or REGION_EVIDENCE

def clean(out, f):
    srcs = ["department_profile"] + (["publications"] if f.get("works") else [])
    lab = out.get("labels") or {}
    evidence = " ".join([f.get("bio") or "", " ".join(f.get("research_areas") or []), " ".join(w["title"] for w in f.get("works") or []),
                         " ".join(out.get("keywords") or []), out.get("summary") or ""]).lower()
    primary = lab.get("primary_topic")
    labels = {}
    for d in DIMS:
        items, seen = [], set()
        for c in lab.get(d) or []:
            if c not in TAX["dimensions"][d]["labels"] or c in seen:
                continue
            if d == "region" and not re.search(EVIDENCE.get(c, "."), evidence):
                continue  # the model named a language group the profile never mentions
            seen.add(c); items.append({"code": c, "primary": False, "sources": srcs})
        labels[d] = items[:4]
    # languages named in the summary or keywords that the model left out (e.g. "isiXhosa" -> African languages)
    named = " ".join([out.get("summary") or ""] + list(out.get("keywords") or [])).lower()
    for c, rx in EVIDENCE.items():
        if c in ("R_CROSSLING", "R_ENGLISH", "R_HUMANS", "R_MACHINES") or len(labels["region"]) >= 4:
            continue
        if re.search(rx, named) and not any(x["code"] == c for x in labels["region"]):
            labels["region"].append({"code": c, "primary": False, "sources": srcs})
    if primary in TAX["dimensions"]["topic"]["labels"]:
        if not any(x["code"] == primary for x in labels["topic"]):
            labels["topic"] = [{"code": primary, "primary": True, "sources": srcs}] + labels["topic"][:3]
        for x in labels["topic"]:
            x["primary"] = x["code"] == primary
    elif labels["topic"]:
        labels["topic"][0]["primary"] = True
    for d in DIMS:  # first item of the other dimensions counts as their main one
        if d != "topic" and labels[d]:
            labels[d][0]["primary"] = True
    kw = [k.strip().lower() for k in out.get("keywords") or [] if 1 < len(k.strip()) < 50][:10]
    return {"name": f["name"], "summary": shorten(out.get("summary")), "summary_zh": (out.get("summary_zh") or "").strip()[:120],
            "confidence": out.get("confidence") if out.get("confidence") in ("high", "medium", "low") else "low",
            "labels": labels, "keywords": kw,
            **{k: bool(out.get(k)) for k in CFG["extra_summary_fields"]}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--only")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--discipline", default=None, help="e.g. psych: data/psych/raw -> data/psych/labels")
    a = ap.parse_args()
    if a.discipline and a.discipline != DISC:  # restart with the env var set so the prompts and taxonomy switch too
        os.environ["DISCIPLINE"] = a.discipline
        os.execv(sys.executable, [sys.executable] + sys.argv)
    try:
        import requests
        requests.get("http://localhost:11434/api/tags", timeout=5).raise_for_status()
    except Exception:
        sys.exit("Ollama is not running. Open the Ollama app (or run `ollama serve`), then `ollama pull " + a.model + "`.")
    files = sorted((CFG["data"] / "raw").glob("*.json"))
    if a.only:
        files = [f for f in files if any(f.stem.startswith(k) for k in a.only.split(","))]
    todo_total = sum(len(json.load(open(f, encoding="utf-8"))["faculty"]) for f in files)
    done, t0 = 0, time.time()
    out_dir = CFG["data"] / "labels"; out_dir.mkdir(parents=True, exist_ok=True)
    for fp in files:
        raw = json.load(open(fp, encoding="utf-8"))
        lp = out_dir / f"{raw['slug']}.json"
        have = json.load(open(lp, encoding="utf-8")) if lp.exists() and not a.redo else {"faculty": []}
        by_name = {x["name"]: x for x in have["faculty"]}
        # psychology: people the pre-filter (pipeline/psych_filter.py) already dropped are not labelled
        rel = json.load(open(CFG["data"] / "relevance.json", encoding="utf-8")).get(raw["slug"], {}) if (CFG["data"] / "relevance.json").exists() and DISC != "linguistics" else {}
        result = {"slug": raw["slug"], "labeled_at": date.today().isoformat(), "faculty": []}
        for f in raw["faculty"]:
            done += 1
            if rel.get(f["name"], {}).get("keep") is False:
                continue
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
