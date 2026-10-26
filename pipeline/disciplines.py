"""Per-discipline settings shared by the pipeline scripts (scrape_local, label_local, build).

Pick one with --discipline <id> or the DISCIPLINE environment variable (default: linguistics).
Linguistics keeps its original file layout (data/, pipeline/taxonomy.json); other disciplines live in data/<id>/.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LING_SUMMARY = """You describe a university researcher's work for a website that helps PhD applicants in linguistics find advisors.
Use ONLY the profile text given. Do not use outside knowledge about the person. If the profile says little, say little.

Return JSON with:
- summary: ONE sentence, at most 200 characters, present tense, without the person's name, saying what they study and how.
  Example: "Studies tone and intonation in Bantu languages through fieldwork and acoustic analysis."
- summary_zh: the same sentence in natural Chinese (use standard linguistics terms, e.g. 音系学, 句法学, 语义学, 社会语言学).
- keywords: 5 to 10 specific lowercase terms from the profile (phenomena, languages, methods), e.g. "tone sandhi", "visual world paradigm", "quechua".
- confidence: "high" if the profile describes their research in detail, "medium" if briefly, "low" if almost not at all.
"""

LING_LABEL_INTRO = """You tag a linguistics researcher's profile with codes from a fixed list, for a search website.
Use ONLY what the profile, summary and keywords say. Choose the codes that clearly apply; most people get 1-3 per list.

- topic: 1 to 4 subfields they work in. primary_topic: the single main one.
- approach: methods they use. data: kinds of data they work with. setting: populations or settings they study (often none).
- region: languages they study. Only languages actually named or clearly implied (e.g. "Quechua" -> R_AMERICAS_INDIGENOUS,
  "Spanish" -> R_ROMANCE, "ASL" -> R_SIGN). R_ENGLISH only when English itself is studied. Leave empty if no language is named.

Example: profile about "variation in Boston Spanish, sociophonetics, interviews with speakers"
-> topic [T_SOCIOLING, T_PHONETICS], primary_topic T_SOCIOLING, approach [A_VARIATIONIST], data [D_SPOKEN_CORPORA, D_SPEECH_AUDIO],
   setting [S_SPEECH_COMMUNITIES, S_BILINGUAL_HERITAGE], region [R_ROMANCE]
"""

PSY_SUMMARY = """You describe a university researcher's work for a website that helps PhD applicants in psychology, cognitive science
and neuroscience find advisors. Use ONLY the profile text given. Do not use outside knowledge about the person.
If the profile says little, say little.

Return JSON with:
- summary: ONE sentence, at most 200 characters, present tense, without the person's name, saying what they study and how.
  Example: "Studies how children learn words from social cues, using eye-tracking and looking-time experiments with infants."
- summary_zh: the same sentence in natural Chinese (use standard psychology terms, e.g. 认知神经科学, 发展心理学, 社会认知, 工作记忆).
- keywords: 5 to 10 specific lowercase terms from the profile (phenomena, methods, populations, species), e.g. "working memory", "fmri", "zebra finch".
- confidence: "high" if the profile describes their research in detail, "medium" if briefly, "low" if almost not at all.
- psych_relevant: true if the research is about mind, brain or behavior in a way a psychology, cognitive science or neuroscience
  PhD applicant would study (perception, cognition, emotion, social behavior, development, brain systems for behavior, animal behavior).
  false for work only on molecules, cells, genes or disease biology with no link to behavior or cognition, and for work outside these fields.
- clinical_role: true if the person's research and training role is clinical psychology (therapy, assessment, treatment trials,
  clinical supervision, a clinical psychology program). false otherwise, including people who study mental health mechanisms
  without a clinical training role.
"""

PSY_LABEL_INTRO = """You tag a psychology, cognitive science or neuroscience researcher's profile with codes from a fixed list, for a search website.
Use ONLY what the profile, summary and keywords say. Choose the codes that clearly apply; most people get 1-3 per list.

- topic: 1 to 4 research areas. primary_topic: the single main one.
- approach: methods they use. data: real-world domains the work connects to (often none). setting: the people they study
  (leave empty for animal-only research). region: species and systems studied (R_HUMANS for human participants;
  animals only when named, e.g. "mice" -> R_RODENTS, "macaques" -> R_PRIMATES; R_MACHINES for neural-network or robot models).

Example: profile about "how stress in adolescence shapes reward learning, using fMRI and ecological momentary assessment"
-> topic [T_MOTIVATION, T_DEVELOPMENT, T_COG_NEURO], primary_topic T_MOTIVATION, approach [A_FMRI, A_DAILY_LIFE, A_COMP_MODEL],
   data [D_MENTAL_HEALTH], setting [S_ADOLESCENTS], region [R_HUMANS]
"""

LING_EVIDENCE = None  # label_local keeps its own language regexes for linguistics

PSY_EVIDENCE = {
    "R_HUMANS": r".",
    "R_PRIMATES": r"primate|monkey|macaque|marmoset|rhesus|chimpanzee|bonobo|apes?\b|baboon|lemur",
    "R_RODENTS": r"\bmice\b|\bmouse\b|\brats?\b|rodent|vole|hamster|gerbil",
    "R_BIRDS": r"\bbirds?\b|songbird|zebra finch|avian|pigeon|corvid|crows?\b|chick|starling|owl",
    "R_FISH_INVERT": r"zebrafish|\bfish\b|drosophila|fruit fl|\bflies\b|c\. ?elegans|worms?\b|\bbees?\b|honeybee|\bants?\b|octopus|cephalopod|insect|larva",
    "R_OTHER_ANIMALS": r"\bdogs?\b|canine|\bbats?\b|ferret|\bcats?\b|sheep|\bpigs?\b|horse|dolphin|whale|elephant|\bgoats?\b|lizard|frog|tadpole",
    "R_MACHINES": r"neural network|deep learning|robot|artificial agent|language model|\bllms?\b|\bai\b|artificial intelligence|machine learning",
}

CONFIG = {
    "linguistics": {"data": ROOT / "data", "taxonomy": ROOT / "pipeline" / "taxonomy.json",
                    "summary_system": LING_SUMMARY, "label_intro": LING_LABEL_INTRO, "evidence": LING_EVIDENCE,
                    "extra_summary_fields": {}},
    "psych": {"data": ROOT / "data" / "psych", "taxonomy": ROOT / "data" / "psych" / "taxonomy.json",
              "summary_system": PSY_SUMMARY, "label_intro": PSY_LABEL_INTRO, "evidence": PSY_EVIDENCE,
              "extra_summary_fields": {"psych_relevant": {"type": "boolean"}, "clinical_role": {"type": "boolean"}}},
}

def current():
    d = os.environ.get("DISCIPLINE", "linguistics")
    if d not in CONFIG:
        raise SystemExit(f"Unknown discipline {d!r}; choose one of {', '.join(CONFIG)}")
    return d, CONFIG[d]
