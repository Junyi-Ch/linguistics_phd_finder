# Data workflows

> The current pipeline runs locally without AI agents: `scrape_local.py` (steps 1–2), `enrich_openalex.py`, `label_local.py` (step 3, Ollama). See `SETUP_MAC.md`. The scope rules below still define who is included; the agent instructions are kept for manual fixes.

Three agent workflows turn the seed list into site data. Each runs one agent per university, on the owner's machine (headless Chromium via `pipeline/fetch.py --render` is often needed), and writes one file per university. Run them in order; each output is validated before the next step.

```
data/programs_seed.json ──(1 discover)──▶ data/programs_discovered.json ──(review)──▶ data/programs.json
data/programs.json ──(2 scrape)──▶ data/raw/<slug>.json ──(3 label)──▶ data/labels/<slug>.json ──▶ python pipeline/build.py
```

## Scope rules (apply in every step)

A **unit** is in scope when it grants a research PhD (dissertation-based; not a professional doctorate, Ed.D., Au.D. or MFA) and its faculty work on language. Each included unit carries a `field`:

| field | Unit | Who counts as faculty |
|---|---|---|
| `LING` | A Linguistics department or program (incl. "Language Science", "Linguistics and Cognitive Science", MIT Linguistics & Philosophy, JHU Cognitive Science) | All tenure-line faculty. For joint departments (linguistics + philosophy, + cognitive science), only faculty whose research is on language. |
| `COMP` | Computational linguistics / NLP groups in CS, iSchools or institutes (e.g. CMU LTI, JHU CLSP, Stanford NLP) | **Only** tenure-line faculty whose primary research is NLP, speech technology or computational linguistics. Never a whole CS department. |
| `APPLIED` | Applied linguistics, second language studies/acquisition, TESOL with a research PhD (often in English, Education or its own department) | Tenure-line faculty in that program. Exclude literacy-only or general education faculty with no language research. |
| `LANG` | Linguistics PhDs or linguistics tracks inside language departments (Hispanic, East Asian, Slavic, Arabic, …) | **Only** the linguists in the department, not literature or culture faculty. |
| `SPEECH` | Speech, language and hearing sciences; communication sciences and disorders; cognitive science or psychology units with a language group | **Only** faculty whose research is on speech or language (production, perception, acquisition, disorders, processing). Exclude audiology-only, swallowing, vestibular and voice-medicine work unless it concerns language. |

Faculty: tenure-line assistant, associate and full professors only (endowed and distinguished titles count as Professor). Exclude lecturers, teaching/clinical/research/practice-track faculty, emeriti, visiting, adjunct, courtesy and affiliated faculty listed from other units. A person listed in two included units of one university is recorded once, in the unit that is their primary appointment.

## 1. Discover (per university, from `programs_seed.json`)

Input: one seed entry (`university`, `slug`, `guide_units` = expected core units, `adjacent_hints` = possible adjacent units with a suggested field).

Task: confirm from official pages which units grant a research PhD in scope, and for each find the PhD program page and the faculty directory URL. Hints are leads, not facts: drop a hinted unit if it grants no research PhD or has no language faculty, and add units the hints missed. If the university has no in-scope PhD, set `offers_linguistics_phd: false` and explain in `notes` (e.g. a department that offers only BA/MA).

Output: one object in the format of `data/programs.json` (see an existing entry): `slug, university, offers_linguistics_phd, city, state, latitude, longitude, domain, confidence, notes, guide_units` and `units[]` with `name, field, school, unit_url, phd_program_name, phd_program_url, directory_url, directory_verified, directory_notes, approx_faculty_count, include, reason`. `directory_notes` should say how the page is built (static or needs `--render`, pagination, which sections hold tenure-line faculty) so step 2 can scrape it without rediscovering that.

Review: merge into `programs_discovered.json`, read every `include: false` and every `confidence: medium/low` by hand, then copy to `programs.json`.

## 2. Scrape (per university, from `programs.json`)

For each included unit, read the directory and each in-scope person's profile page. Write `data/raw/<slug>.json` following `pipeline/schema_raw.json`. Set each person's `unit` to the unit name exactly as in `programs.json` (this sets their field on the site). `bio` is the profile's research text (it is used only to compute vectors and is never published). Check with `python pipeline/validate_raw.py data/raw/<slug>.json`.

## 3. Label (per university, from `data/raw/<slug>.json`)

For each person, using only their public profile, personal site and listed publications, write `data/labels/<slug>.json` following `pipeline/schema_labels.json` and the codes in `pipeline/taxonomy.json`:

- `summary`: one sentence, at most 200 characters, present tense, no name: what they study and how. `summary_zh`: the same in Chinese.
- Labels in all five dimensions (Subfields, Methods, Data, Populations, Languages), at most 4 per dimension, each with its `sources`. Mark `primary` only where the evidence is explicit; every person needs at least one primary subfield. Leave a dimension empty rather than guess.
- `region` here means **languages**: label the languages the research is actually about. Research on English counts as `R_ENGLISH` only when English is a subject of study, not merely the language of the paper.
- `keywords`: 5–10 specific lowercase terms, including language names and technical terms ("tone sandhi", "visual world paradigm", "quechua").
- `confidence`: high / medium / low, by how much public text there was.

Check with `python pipeline/validate_labels.py data/labels/<slug>.json`. After all universities, an independent agent re-checks a 5% random sample against the profile pages.

## Build

```bash
python pipeline/build.py          # → src/data, public/search, public/schools
python pipeline/report.py         # → docs/DATA_REPORT.md
npm run build
```
