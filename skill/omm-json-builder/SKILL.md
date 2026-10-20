---
name: omm-json-builder
description: >
  Convert raw OCR'd homeopathic source texts into clean, app-ready JSON — one file
  per book — for a materia medica / repertory reader app. Use when the user wants to
  extract a materia medica or repertory text (.txt) into structured JSON, add a new
  book to the OMM collection, validate or repair an extraction, or work with the
  homeopathy JSON schema. Covers repertories (chapter -> rubric -> graded remedies)
  and materia medicas (remedy -> symptoms), plus OCR cleanup, remedy-name
  normalisation, and verbatim-fidelity validation. Do NOT use for unrelated JSON or
  for generating homeopathic content — this skill only structures text that already
  exists in a source file.
---

# OMM JSON builder

Turn a homeopathic **source text** into a **final JSON** an app can load, without
ever inventing a symptom, remedy, grade, author or year. The pipeline keeps every
string verbatim from the source (after light OCR cleanup) and validates that claim.

## The one rule that matters

**No fabricated data.** Every rubric/symptom string must trace back into the
`.txt`. Missing values are `null`, never guessed. This is exactly where the earlier
version of this project failed: it generated template JSON (`Remedy_1`,
`Symptom 0 of Remedy_1`) that looked structured but contained none of the book.
Never regenerate from templates; always parse a real file.

## When to use
- "Extract this repertory / materia medica into JSON."
- "Add this new book to the collection."
- "The extraction looks wrong / has junk — fix it."
- "What's the JSON schema for the app?"

## Quick start

```bash
# 0. classify a new file (repertory vs materia medica)
python3 scripts/omm_pipeline.py classify --src "data/source_txt/<file>.txt"

# 1. extract a repertory
python3 scripts/omm_pipeline.py extract-repertory \
  --src "data/source_txt/hering.txt" \
  --slug hering-repertory-1889 \
  --title "Repertory to Hering's Condensed Materia Medica" \
  --author "Homoeopathic Medical Society of the State of Pennsylvania" \
  --year 1889 --publisher "Globe Printing House, Philadelphia" \
  --out "repertory/hering-repertory-1889.json" \
  --qc "data/processed/hering-repertory-1889/qc_report.md"

# 2. extract a materia medica
python3 scripts/omm_pipeline.py extract-mm --src ... --slug ... --out ...

# 3. validate the result (must report zero errors)
python3 scripts/omm_pipeline.py validate --json repertory/hering-repertory-1889.json
```

## Workflow

Read `references/workflow.md` for the full seven-phase procedure (intake →
identity → structure → extract → normalise → validate → promote → document).
Always: confirm the book's identity from its title page + a catalogue, classify it,
extract, then read the QC report before promoting.

## Output format

Read `references/schema.md` for the exact JSON contract (repertory and materia
medica). Key points: one JSON per book; `book` provenance block; repertory is
`sections[] → rubrics[] → remedies[]` with a `remedy_index`; grades are `null`
unless printed.

## OCR gotchas

Read `references/ocr_playbook.md` before adapting the parser. The high-value ones:
running heads repeat section titles (de-duplicate + snap to the CONTENTS page);
remedy lists wander onto the next line after a `:` (need an `expect_remedies`
state); OCR drops separators so remedies sit inline (the recovery pass splits on a
remedy vocabulary); cross-references `(See "…")` must be stripped.

## Remedy names

`scripts/remedy_aliases.csv` maps printed tokens → canonical names. Grow it as new
tokens appear; the QC report prints how many tokens resolved. Unresolved tokens are
kept verbatim with `resolved:false` — never assert a name you cannot justify.

## Quality bar
- Validator: **zero errors**.
- **Verbatim rate ≥ 90 %** (printed in the QC report).
- Spot-check ≥ 5 rubrics against the source.
- Report honest metrics; do not hand-edit JSON to raise the score.

## Files in this skill
- `scripts/omm_pipeline.py` — the whole pipeline (classify / extract / validate).
- `scripts/remedy_aliases.csv` — abbreviation → canonical-name table.
- `references/workflow.md` — the per-book procedure.
- `references/schema.md` — the JSON contract.
- `references/ocr_playbook.md` — OCR failure modes and fixes.
