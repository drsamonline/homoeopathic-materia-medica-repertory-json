# OMM JSON Schema v1.0 — app-ready output format

Two document types, one shared envelope. Every file is a single JSON object.
Design goals: (a) trivial to load and search in a browser app, (b) every string
traces back to the printed source, (c) nothing invented.

## Shared envelope

```json
{
  "schema_version": "1.0",
  "type": "repertory" | "materia_medica",
  "book": {
    "id": "hering-repertory-1889",
    "title": "Repertory to Hering's Condensed Materia Medica",
    "author": "Homoeopathic Medical Society of the State of Pennsylvania",
    "year": 1889,
    "publisher": "Globe Printing House, Philadelphia",
    "language": "en",
    "public_domain": true,
    "source_file": "data/source_txt/hering.txt",
    "extraction_date": "2026-10-14",
    "pipeline_version": "omm_pipeline 1.0",
    "counts": { "...": "filled by the validator" }
  },
  "...": "type-specific payload below"
}
```

## type = "repertory"

```json
{
  "sections": [
    {
      "id": "hering-repertory-1889-s1",
      "title": "Repertory Of Symptoms Of The Lower Extremities",
      "rubrics": [
        {
          "id": "hering-repertory-1889-r00001",
          "text": "Abscess of knee, gouty, with pain and loss of sleep",
          "parent": null,
          "note": null,
          "remedies": [
            { "abbrev": "Guaiacum", "grade": null, "polarity": "+" }
          ]
        }
      ]
    }
  ],
  "remedy_index": {
    "Guaiacum": { "name": "Guaiacum", "resolved": true },
    "Natrum ars": { "name": "Natrum arsenicosum", "resolved": true }
  }
}
```

Field notes:
- `sections[]` mirrors the book's own chapters (taken from its CONTENTS page).
- `rubrics[].text` — the symptom string, **verbatim** from the source (light OCR cleanup only).
- `rubrics[].parent` — for repertories with sub-entries (Drake: `Sweat of the Feet,
  Constant` → `Morning`), the heading the entry refines; `null` for a top-level
  rubric. The app renders `parent ? parent + ', ' + text : text`.
- `rubrics[].note` — verbatim prose attached to the rubric (Jahr Part II: the
  clinical remarks). Where a source carries remedy lists inside prose, the note is
  authoritative; `remedies[]` holds only the tokens confidently matched to the
  curated alias table and may be an incomplete subset.
- `remedies[].abbrev` — the remedy exactly as printed.
- `remedies[].grade` — integer 1–3 **only if the source prints a grade**; otherwise `null`.
  Never default to 1.
- `remedies[].polarity` — `"+"` or `"-"`; `"+"` is the default when the source shows none.
- `remedy_index` maps every printed remedy token to a canonical name.
  `resolved:false` means the token is not in `remedy_aliases.csv` yet — the token is
  still shown, but no full name is asserted.

## type = "materia_medica"

```json
{
  "remedies": [
    {
      "id": "boericke-mm-1901-0001",
      "name": "Aconitum napellus",
      "abbrev": "Acon",
      "common_name": null,
      "kingdom": null,
      "family": null,
      "clinical_indications": ["Fever", "Inflammation"],
      "sections": {
        "relationships": [ { "kind": "complementary", "remedies": ["Ars", "Bell"] } ],
        "dosages": [],
        "antidotes": []
      },
      "symptoms": [
        {
          "id": "boericke-mm-1901-0001-s0001",
          "chapter": "Mind",
          "text": "<verbatim from source>",
          "grade": null,
          "modalities": [ { "dir": "worse", "text": "night" } ]
        }
      ]
    }
  ]
}
```

Field notes:
- `clinical_indications` — the disease/condition list a remedy is indicated in,
  when the source prints one (Jahr prints a semicolon-separated list before the
  symptoms). Empty list when absent.
- `chapter` is one of the body-system vocabulary (Mind, Head, Stomach, …) when the
  source prints section headers; otherwise `"General"`.
- `modalities[].dir` ∈ `worse | better | ws` (`ws` = unspecified).
- `kingdom` / `family` / `common_name` stay `null` unless the source states them.
  Do not fill them from outside knowledge.

## Size guidance for the app
- One JSON per book, named `{author-last}-{title-slug}-{year}.json`.
- A large book (e.g. 12k rubrics) is ~3 MB. If that is too heavy for the front end,
  split per section at load time or serve `sections[]` as separate files keyed by
  `section.id`. The pipeline can emit either; ask before splitting.

## Invariants the validator enforces
1. `schema_version` and `type` present and correct.
2. `book.id`, `book.title`, `book.source_file`, `book.extraction_date` present.
3. Repertory: at least one rubric; every rubric has non-empty `text`; ids unique;
   every remedy has an `abbrev`.
4. Materia medica: at least one remedy; every remedy has a `name`.
5. QC gate (not a hard error): ≥ 90 % of rubric texts must be findable verbatim
   in the source; below that the QC report flags a warning.

## Output formats and sizes (measured 2026-10-15)

A final book can be emitted three ways. Measured on the whole collection
(7 books, Kent is the big one):

| format | collection | Kent alone |
|---|---|---|
| JSON, indented (`indent=1`) | 50.5 MB | 38.3 MB |
| JSON, compact (`--compact`) | 30.5 MB | 21.5 MB |
| SQLite (`to-sqlite`) | 26.9 MB | 20.0 MB |

- **Compact JSON is the DEFAULT** (project decision 2026-10-15). Every extract
  command writes compact JSON; pass `--indent` only if you want it pretty-printed
  for eyeballing or hand-diffing. Both parse to identical data - indentation is
  insignificant whitespace between tokens, never inside a string value.
- **SQLite** (`python3 scripts/omm_pipeline.py to-sqlite --json <file> --db <db>`)
  is ~47 % smaller than indented JSON and slightly smaller than compact JSON.
  It is NOT smaller if you keep text keys and many indexes (a naive version came
  out at 41.7 MB — larger than the JSON). Use integer primary keys, keep only the
  indexes you need, and `VACUUM`.
- SQLite's real advantage is not size but **query speed and partial loading** — a
  browser app can ask "which remedies for `Stomach > pain`" without parsing 38 MB.

### SQLite schema produced by `to-sqlite`
```
book(id, type, schema_version, title, author, year, publisher, source_file,
     extraction_date, counts)
section(id INTEGER PK, book_id, ordinal, title)              -- repertory
rubric(id INTEGER PK, book_id, section_id, text, parent, note)
remedy_link(rubric_id, abbrev, grade, polarity, note)
remedy_index(book_id, abbrev, name, resolved)
mm_remedy(id INTEGER PK, book_id, name, abbrev, canonical_name, common_name,
          kingdom, family)                                    -- materia medica
mm_symptom(id INTEGER PK, remedy_id, chapter, text, grade)
```
Indexes: `rubric(section_id)`, `remedy_link(rubric_id)`, `remedy_link(abbrev)`,
`mm_symptom(remedy_id)`.
