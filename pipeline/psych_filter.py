#!/usr/bin/env python
"""Psychology site: decide, before labelling, who is psychology-relevant.

  python pipeline/psych_filter.py          # data/psych/raw/*.json -> data/psych/relevance.json (+ a summary)

Rules (Junyi: "if the research is not relevant to psych, there's no need to include them"):
- Not a person (a research-area heading scraped as a name) or no profile text at all -> dropped.
- Psychology and cognitive science departments: kept, unless the profile is overwhelmingly cell/molecular biology.
- Neuroscience programs and institutes: kept with clear evidence of psychology relevance (a psychology or cognitive science
  appointment, or research about behavior, cognition or the mind that clearly outweighs cell/molecular biology); dropped when
  cell/molecular or medical research clearly dominates; anything in between ("keep": null) goes to the labeller to decide.
The labeller (label_local.py) skips dropped people and judges the rest again (psych_relevant).
"""
import json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "psych"

PSY = re.compile(r"\b(behavio\w*|cogniti\w*|psycholog\w*|memory|memories|learning|attention|perception|perceptual|decision\w*|"
                 r"emotion\w*|affective|social|language|speech|reading|reward|motivat\w*|fear|anxiety|stress|depression|addiction|"
                 r"habits?|sleep|conscious\w*|mind|thinking|reasoning|categor\w*|navigation|spatial|psychophysic\w*|vision|visual|"
                 r"auditory|hearing|olfact\w*|pain|motor control|movement|actions?|choice|executive|working memory|"
                 r"development\w*|infan\w*|child\w*|adolescen\w*|aging|human participants|humans|fmri|eeg|meg|neuroimaging|"
                 r"cognitive neuroscience|systems neuroscience|songbirds?|vocal\w*|courtship|aggression|parenting|maternal|"
                 r"personality|mental health|psychiatric|schizophrenia|autism|adhd|dyslexia)\b", re.I)
BIO = re.compile(r"\b(molecular|molecules?|proteins?|genes?|genetic|genomic\w*|transcription\w*|epigenetic\w*|rna|dna|crispr|"
                 r"cellular|cell biology|cells?|stem cells?|glia\w*|astrocyt\w*|microglia\w*|oligodendrocyt\w*|myelin\w*|axon\w*|"
                 r"ion channels?|channels?|receptors?|kinases?|signaling|signalling|pathways?|mitochondri\w*|metabolism|metabolic|"
                 r"neurodegenera\w*|alzheimer\w*|parkinson\w*|huntington\w*|ataxia|epilep\w*|seizures?|stroke|tumou?rs?|glioma|"
                 r"cancer|injury|regenerat\w*|inflammat\w*|neuroinflammat\w*|immune|immunolog\w*|vascular|retina\w*|"
                 r"photoreceptor\w*|hair cells?|cochlea\w*|zebrafish|drosophila|elegans|yeast|organoids?|biophysic\w*|"
                 r"structural biology|cryo-em|pharmacolog\w*|drugs?|therapeutic\w*|clinical trials?|surgery|surgical|"
                 r"anesthe\w*|biomaterial\w*|nanoparticle\w*|electrodes?|hormon\w*|endocrin\w*|obesity|diabet\w*|microbio\w*)\b", re.I)
HOME = re.compile(r"psycholog|cognitive science|cognitive sciences|brain (and|&) cognitive|psychological (and|&) brain|cognitive (and|&) psychological", re.I)
NOT_PERSON = re.compile(r"\b(disorders?|behavior|behaviour|neuroscience|research|areas?|program|faculty|systems|cognition|biology|health|"
                        r"development|imaging|disease|plasticity|circuits?)$", re.I)
DEAD = re.compile(r"can.t find that page|page not found|404|access denied", re.I)

def decide(x, field):
    name, bio = x["name"], x.get("bio") or ""
    head = " ".join([x.get("title") or "", x.get("department") or "", bio[:600]])
    text = " ".join([x.get("title") or "", " ".join(x.get("research_areas") or []), bio])
    if NOT_PERSON.search(name) or len(name.split()) < 2:
        return False, "not a person"
    p, b = len(PSY.findall(text)), len(BIO.findall(text))
    home = bool(HOME.search(head))
    if field in ("PSY", "COGSCI"):
        if b >= 12 and b > 3 * max(p, 1):
            return False, f"cell/molecular biology ({p} psych vs {b} bio terms)"
        return True, "psychology or cognitive science department"
    # neuroscience programs
    if len(bio) < 200 or DEAD.search(bio[:200]):
        return (True, "psychology appointment; profile thin") if home else (False, "no usable profile")
    if home and p >= b / 2:
        return True, "psychology appointment"
    if p >= 6 and p >= 2 * b:
        return True, f"behavior/cognition research ({p} psych vs {b} bio terms)"
    if b >= 6 and b >= 2 * max(p, 1):
        return False, f"mainly cell/molecular or medical ({p} psych vs {b} bio terms)"
    return None, f"unclear ({p} psych vs {b} bio terms): the labeller decides"

def main():
    P = json.load(open(D / "programs.json", encoding="utf-8"))
    field = {(p["slug"], u["name"]): u["field"] for p in P for u in p["units"]}
    out, stats = {}, collections.Counter()
    for fp in sorted((D / "raw").glob("*.json")):
        raw = json.load(open(fp, encoding="utf-8"))
        for x in raw["faculty"]:
            f = field.get((raw["slug"], x["unit"]), "NEURO")
            keep, why = decide(x, f)
            out.setdefault(raw["slug"], {})[x["name"]] = {"keep": keep, "why": why, "unit": x["unit"], "field": f}
            stats[(f, keep)] += 1
    json.dump(out, open(D / "relevance.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for f in ("PSY", "COGSCI", "NEURO"):
        k, d, u = stats[(f, True)], stats[(f, False)], stats[(f, None)]
        print(f"{f:7s} kept {k:5d}  dropped {d:5d}  for the labeller {u:5d}")
    print("kept", sum(v for (f, k), v in stats.items() if k is True), "| unclear", sum(v for (f, k), v in stats.items() if k is None))

if __name__ == "__main__":
    main()
