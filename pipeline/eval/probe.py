#!/usr/bin/env python
"""Try a research description against the built index, the way the website scores it (before re-ranking).

  python pipeline/eval/probe.py "Language revitalization and pedagogy, fieldwork, language variation" --who Caballero

Prints the top matches with the old single-embedding score and with interest-by-interest ("facet") scoring,
and where the person named by --who lands in each.
"""
import argparse, json, math, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
M = json.load(open(ROOT / "public/search/manifest.json"))
IDS = json.load(open(ROOT / "public/search/index.json"))
VEC = np.frombuffer(open(ROOT / "public/search/vectors.i8.bin", "rb").read(), dtype=np.int8).reshape(-1, M["dimensions"]).astype(np.float32) / M["quantizationScale"]
F = json.load(open(ROOT / "src/data/faculty.json")); T = json.load(open(ROOT / "src/data/taxonomy.json"))
P = {p["slug"]: p for p in json.load(open(ROOT / "src/data/programs.json"))}
DIMS = ["topic", "approach", "data", "setting", "region"]
STOP = set("a an the and or of in on for to with from by at as is are be been being this that these those i my me we our you your it its their they them he she his her how what which who whom where when why while about into over under between among through during also both such than then there here very more most much many some any each other same so too not no nor only own just can could would should will shall may might must do does did doing have has had having using use used uses study studies studying research interested interest interests work works working want wants focus focused focusing especially particularly including include includes like well across within without via towards toward against around".split())

def stem(w):
    if len(w) <= 4: return w
    w = re.sub(r"(ization|isation)$", "ize", w); w = re.sub(r"(ational|ically)$", "al", w); w = re.sub(r"(ies)$", "y", w)
    w = re.sub(r"(ness|ment|ings?|ers?|ed|es|s)$", lambda m: "s" if m.group(0) == "s" and w.endswith("ss") else "", w)
    return re.sub(r"(ic|al|ive|ous)$", "", w)
def tok(t): return [x for x in (stem(w) for w in re.split(r"[^\w-]+", t.lower().replace("’", "").replace("'", ""))) if len(x) > 2 and x not in STOP]
def pub(f):
    parts = [f["summary"]]
    if f["kw"]: parts.append("Keywords: " + ", ".join(f["kw"]) + ".")
    if f["areas"]: parts.append("Research areas: " + "; ".join(f["areas"]) + ".")
    labs = [T["dimensions"][d]["labels_short"][l["c"]] for d in DIMS for l in f["labels"].get(d, [])]
    if labs: parts.append("Labels: " + ", ".join(labs) + ".")
    return " ".join(parts)
DOCS = [tok(pub(f)) for f in F]; TF = [{} for _ in F]
for i, d in enumerate(DOCS):
    for w in d: TF[i][w] = TF[i].get(w, 0) + 1
DF = {}
for tf in TF:
    for w in tf: DF[w] = DF.get(w, 0) + 1
N = len(F); AVG = sum(len(d) for d in DOCS) / N
def bm25(q):
    out = np.zeros(N, np.float32)
    for t in set(tok(q)):
        d = DF.get(t)
        if not d: continue
        w = math.log(1 + (N - d + 0.5) / (d + 0.5))
        for i in range(N):
            c = TF[i].get(t)
            if c: out[i] += w * (c * 2.2) / (c + 1.2 * (0.25 + 0.75 * len(DOCS[i]) / AVG))
    return out
z = lambda a: (a - a.mean()) / (a.std() or 1)
def split_facets(text):
    parts = re.split(r"\n|;|•|·|\.\s+|,(?![^()]*\))|\band/or\b", text)
    parts = [re.sub(r"^\s*(and|or|also|as well as)\s+", "", x, flags=re.I).strip().rstrip(".:") for x in parts]
    parts = [x for x in parts if len(x) >= 4 and tok(x)]
    seen, out = set(), []
    for x in parts:
        if x.lower() not in seen: seen.add(x.lower()); out.append(x)
    return out[:10] if len(out) >= 3 else []

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("query"); ap.add_argument("--who", default=""); ap.add_argument("-k", type=int, default=15)
    a = ap.parse_args()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(M["model"])
    emb = lambda t: model.encode([M.get("queryPrefix", "") + t], normalize_embeddings=True)[0]
    order = {fid: i for i, fid in enumerate(IDS)}
    def dense(t):
        cos = VEC @ emb(t); out = np.zeros(N, np.float32)
        for i, f in enumerate(F): out[i] = cos[order[f["id"]]]
        return out
    wl = M["fusion"]["lex"]; wd = 1 - wl
    old = wd * z(dense(a.query)) + wl * z(bm25(a.query))
    facets = split_facets(a.query)
    new = old
    if facets:
        per = np.stack([wd * z(dense(t)) + wl * z(bm25(t)) for t in facets])
        best2 = np.sort(per, axis=0)[-2:].mean(axis=0)
        new = z(0.45 * z(old) + 0.55 * z(best2))
    print("Interests found:", facets or "(none: scored as one description)")
    for name, s in [("one embedding (before)", old), ("interest by interest (now)", new)]:
        rk = np.argsort(-s)
        print(f"\n== {name}")
        for r, i in enumerate(rk[:a.k], 1):
            print(f"{r:3d}. {F[i]['name']} ({P[F[i]['u']]['short']}) — {F[i]['summary'][:80]}")
        if a.who:
            for r, i in enumerate(rk, 1):
                if a.who.lower() in F[i]["name"].lower(): print(f"   -> {F[i]['name']}: rank {r} of {N}"); break

if __name__ == "__main__":
    main()
