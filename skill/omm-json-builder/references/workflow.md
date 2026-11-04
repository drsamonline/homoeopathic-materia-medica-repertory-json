# Workflow — one book at a time

Each source `.txt` goes through the same seven phases. Do **not** batch-generate
JSON from templates — every output must come from a real parse of a real file.

## Phase 0 — Intake & identity
- **Check `catalog.json` first.** Search the title and the author for an existing
  entry. Two duplicate Clarke repertories were built into this library because this
  was skipped; one had to be reverted.
- Confirm the file is a genuine source text; record line/byte counts.
- **Choose the medium** before parsing: `_djvu.txt`, DjVu XML, a typed transcription,
  or EPUB. If the text gives headings like `BTMPTOHS`, go to XML — see
  `djvu_xml.md`.
- Read the title page, CONTENTS and PREFACE. Extract: exact title, author (person
  **or** corporate body), edition year, publisher. Confirm the year against a
  catalogue (archive.org / HathiTrust) — the OCR title page is usually garbled.
- Classify: **repertory** (chapter → rubric → remedies) vs **materia medica**
  (remedy → symptoms). If unclear, ask the user.
- Public-domain check: read the **title page**, not the item metadata. A scan can be
  an old book behind a modern reprint — a 1993 B. Jain issue and a 1981 Boenninghausen
  were both refused that way. If the term differs by country, record
  `public_domain_note` and `copyright_jurisdictions` in the book block.

## Phase 1 — Structure mapping
- Sample head / middle / tail. Identify the heading grammar, the separator
  (`:` / `;`), how remedies are graded (usually not in these texts), and the
  CONTENTS list of chapters.
- Run `omm_pipeline.py classify --src <file>` for a first guess.

## Phase 2 — Extraction
- Run `extract-repertory` or `extract-mm`. Output goes to the final folder.
- Never hand-edit the JSON. If the parse is wrong, fix the parser and re-run.

## Phase 3 — Normalisation
- Remedy abbreviations resolved through `scripts/remedy_aliases.csv`
  (grow this file as new tokens appear). Grades → int 1–3 only if printed.
- OCR cleanup per `ocr_playbook.md`.

## Phase 4 — Validation gates
- `omm_pipeline.py validate --json <file>` → must report zero errors.
- Verbatim rate ≥ 90 % (printed in the QC report).
- Spot-check ≥ 5 random rubrics against the source.
- Zero placeholder fingerprints (`grep -c 'Remedy_[0-9]'` must be 0).

## Phase 5 — Promotion
- Final file lives in `repertory/` or `materia_medica/`, named
  `{author-last}-{title-slug}-{year}.json`, and its `book` block carries the full
  provenance (source file, date, counts, public-domain flag).

## Phase 6 — Documentation
- Append a dated entry to `docs/SESSION_LOG.md`; update `docs/BOOK_REGISTRY.csv`.
- **Recount the catalogue totals from the files** (`catalog.json.totals`) rather than
  incrementing them by hand: split volumes are the usual casualty, and this library's
  remedy-link total was once 613,588 short for exactly that reason. Put how the number
  was obtained in `totals_note`.
- Record coverage honestly in `quality` / `quality_note` — "52 % of rubrics carry a
  remedy link" belongs on the shelf, not in a footnote.
- Commit with `feat(<slug>): extracted final json`.

## Adding a new book (checklist)
1. Drop the `.txt` into `data/source_txt/`.
2. `python3 scripts/omm_pipeline.py classify --src "data/source_txt/<file>"`
3. Run the right extractor with `--slug --title --author --year --publisher`.
4. Read the QC report; if the verbatim rate is low, inspect the parse and adapt
   the heuristics (see `ocr_playbook.md`), then re-run.
5. Add any new remedy tokens to `remedy_aliases.csv` and re-run so the index resolves.
