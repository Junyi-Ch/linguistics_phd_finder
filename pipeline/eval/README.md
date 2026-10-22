# Matcher evaluation

How the matcher's setup (model, fusion weights, reranker, translation) is checked, and how to re-check it after a change.

## Status

The matcher setup was chosen on a graded test set for the sister Communication explorer (nDCG@10 0.69 → 0.85 there). It has **not yet been measured on Linguistics**. Linguistics differs in ways that could change the answer:

- Queries lean on technical terms and language names ("Bantu tone", "visual world paradigm", "scalar implicature"), which may favour a larger keyword weight than the 15% carried over.
- Adjacent units (computer science, speech and hearing, education) write profiles in a different register from linguistics departments.
- The Chinese glossary (`pipeline/glossary_zh.json`) is new and untested.

Until the table below is filled in, the About page says the setup is being re-checked.

## Test set

- `queries.json`: 40 applicant-style descriptions: 30 statement-style covering the subfields, languages and methods; 6 short keyword queries; 4 in Chinese. They were written separately from `pipeline/probes.json` (used for score calibration) so the test set is not tuned on.
- `judgments.json`: query → {faculty id: grade 0–3} under `RUBRIC.md`. Empty until the first judging round.
  - Pool the top 10 of every system compared, so every system in the table is fully judged at depth 10.
  - Graders see only the published profile card (summary, keywords, research areas, labels, a short profile excerpt), with no system names and in shuffled order.

## Results (nDCG@10)

| System | all | statement | short | Chinese |
|---|---|---|---|---|
| arctic + fusion 85/15 + MiniLM rerank + translation (carried over) | — | — | — | — |
| same, keyword weight 25% | — | — | — | — |
| same, no rerank | — | — | — | — |
| bge-small baseline | — | — | — | — |

## Re-running

```bash
conda activate nlp
python pipeline/eval/run_systems.py                      # runs for the judging pool (cached under data/cache/eval/)
python pipeline/eval/make_packets.py 10 4 <system> ...   # blind packets for pairs not yet judged
python pipeline/eval/merge_judgments.py                  # fold graded packets into judgments.json
python pipeline/eval/experiments.py                      # metrics table for every cached run
```

`harness.py` replicates the browser scoring. The tokenizer, BM25 and published text come from `pipeline/textmatch.py`, which `src/lib/match.ts` mirrors; query detectors come from `pipeline/hints.json`, which both read. Profile excerpts in the packets come from the local raw files and are never committed.
