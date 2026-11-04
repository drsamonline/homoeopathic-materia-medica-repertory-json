---
name: omm-json-builder
description: >
  Convert raw homeopathic source texts — OCR text, DjVu XML, or a typed transcription
  — into clean, app-ready JSON, one file per book, for a materia medica / repertory
  reader app. Use when the user wants to extract a materia medica or repertory into
  structured JSON, add a new book to the OMM collection, rebuild a volume whose
  headings the OCR destroyed, validate or repair an extraction, or work with the
  homeopathy JSON schema. Covers repertories (chapter -> rubric -> remedies) and
  materia medicas (remedy -> symptoms), plus OCR cleanup, remedy-name normalisation,
  verbatim-fidelity validation, and the rights screen every public-domain library
  needs. Do NOT use for unrelated JSON or for generating homeopathic content — this
  skill only structures text that already exists in a source file.
---

# OMM JSON builder

Turn a homeopathic **source** into a **final JSON** an app can load, without ever
inventing a symptom, remedy, grade, author or year. Every string stays verbatim from
the source (after light OCR cleanup) and that claim is validated.

## The one rule that matters

**No fabricated data.** Every rubric/symptom string must trace back into the source.
Missing values are `null`, never guessed. This is where an earlier version of this
project failed: it generated template JSON (`Remedy_1`, `Symptom 0 of Remedy_1`) that
looked structured but contained none of the book. Never regenerate from templates;
always parse a real file.

## Before you build anything

Three checks that cost a minute and save a book.

1. **Does the collection already have it?** Search `catalog.json` for the title and
   the author *before* parsing. Two Clarke repertories were built into this library
   because this check was skipped; one was a third the size of the copy already on
   the shelf and had to be reverted.
2. **Is this printing public domain?** Read the title page, not the item's metadata.
   A scan can be an old book behind a modern reprint: a 1993 B. Jain issue of Allen's
   *Psora* and a 1981 Boenninghausen were both refused on their own title pages. The
   text underneath may be free; the file is not the source to cite.
3. **Which medium is best for this book?** See below — it decides whether the parse
   is easy or impossible.

## Choose the medium first

| Medium | Use when | Watch for |
|---|---|---|
| `_djvu.txt` | OCR is good and headings survive as capitals | headings fused into prose; running heads |
| **DjVu XML** | headings are OCR'd to rubble, or the page is two columns | two coordinate formats (below) |
| Typed transcription (Médi-T and similar) | the book is short enough to fetch page by page | fetch throttling; anchors per remedy |
| EPUB / plain text | neither of the above exists | reflowed, so pagination is gone |

The XML is the strong tool: every word carries a bounding box, so a heading can be
found **by height instead of by spelling**. Three volumes of Clarke's *Dictionary*
were unparseable from text and trivial from XML. Read `references/djvu_xml.md` before
using it — it has the method, the two coordinate formats, and the bugs that silently
return empty books.

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

Read `references/workflow.md` for the full procedure (intake → identity → structure →
extract → normalise → validate → promote → document). Always: confirm identity from
the title page, classify, extract, then **read the QC report before promoting**.

## Output format

Read `references/schema.md` for the exact contract. One JSON per book; a `book`
provenance block; repertory is `chapters[] → rubrics[] → remedies[]`; materia medica
is `remedies[] → symptoms[]`. Grades are `null` unless printed.

Two fields earn their keep on awkward volumes:
- `book.coverage_note` — when the count could not be checked against the book's own
  index, say so here rather than letting the number imply completeness.
- `book.public_domain_note` + `book.copyright_jurisdictions` — when the term differs
  by country (Bach is free in India and the UK but not the US until 2028).

## Remedy names

`scripts/remedy_aliases.csv` maps printed tokens → canonical names; grow it as new
tokens appear. Unresolved tokens stay verbatim with no asserted name.

**Repertory abbreviations drop vowels** — `Magn. mur.` is Magnesia muriatica and
`Eupator. perf.` is Eupatorium perfoliatum. No spelling comparison reaches those.
Match **word by word**: the first cited word may be a *prefix* of the name's first
word, the second a prefix of its second. On one repertory that change alone took
resolved links from 596 to 1,087. Details in `references/djvu_xml.md`.

**Clean the vocabulary before trusting it.** A vocabulary harvested from existing
books inherits their OCR junk — `BELl<.iDOX.\A` was indexed as a remedy name and
captured every token beginning `Bel`. Filter to `^[A-Za-z][A-Za-z .'\-]{2,40}$`.

## Quality bar

- Validator: **zero errors**.
- **Verbatim rate ≥ 90 %** (printed in the QC report).
- Spot-check ≥ 5 rubrics against the source, and at least one page image.
- Report honest metrics; never hand-edit JSON to raise a score.

**State coverage as found.** If only 52 % of rubrics resolved a remedy, that goes in
the QC and in `catalog.json.quality_note` — not into a footnote nobody reads. A
volume with an honest 62 % is worth having; one that implies 100 % is not.

## Count from the files, never by hand

Totals written by hand drift the moment a volume is added, and split volumes are the
usual casualty: this library's `catalog.json` once under-reported remedy links by
**613,588** because Kent's 353,000 and every other split volume were never counted.
Recount from the JSON itself before publishing figures:

```python
# walk repertory/**/*.json, sum chapters[].rubrics[] and section.rubrics[]
# also count graded links: sum(1 for x in remedies if x.get("grade") is not None)
```

Record how the number was obtained (`totals_note`) so the next reader knows whether
it was counted or inherited.

## Files in this skill

- `scripts/omm_pipeline.py` — classify / extract / validate / compress.
- `scripts/remedy_aliases.csv`, `scripts/remedy_master.csv` — name tables.
- `references/workflow.md` — the per-book procedure.
- `references/schema.md` — the JSON contract.
- `references/ocr_playbook.md` — OCR failure modes and fixes.
- `references/djvu_xml.md` — **the XML method**: height-based headings, coordinate
  formats, two-column pages, page-boundary carry, word-wise remedy matching, grades.
