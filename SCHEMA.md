# Schema

Every file is self-describing: the top-level `type` is either `repertory` or
`materia_medica`.

## Common — `book`

| field | type | notes |
|---|---|---|
| `id` | string | slug, e.g. `kent-repertory-1897` |
| `title` | string | full title |
| `author` | string | author(s) |
| `year` | integer | year of the edition used |
| `publisher` | string | where known, else `""` |
| `source_file` | string | the OCR text file it was built from |
| `counts` | object | `{ sections, rubrics, remedy_links }` or `{ remedies, symptoms }` |

## Repertory — `repertory/*.json`

```json
{
  "schema_version": "1.0",
  "type": "repertory",
  "book": { ... },
  "sections": [
    {
      "id": "kent-repertory-1897-s1",
      "title": "Mind",
      "rubrics": [
        {
          "id": "kent-repertory-1897-r00001",
          "text": "Fear of death",
          "parent": null,
          "remedies": [
            { "abbrev": "Acon", "grade": null, "polarity": "+", "name": "Aconitum napellus" }
          ]
        }
      ]
    }
  ],
  "remedy_index": {
    "Acon": { "name": "Aconitum napellus", "resolved": true }
  }
}
```

- `sections[].title` — a chapter (e.g. `Mind`, `Stomach`), or `General` when the
  source has no chapter structure.
- `rubrics[].text` — the symptom string, **verbatim** from the source.
- `rubrics[].parent` — for sub-rubrics (e.g. Drake, Lippe), the heading this
  entry refines; `null` for a top-level rubric.
- `rubrics[].remedies[].abbrev` — the remedy exactly as printed.
- `rubrics[].remedies[].grade` — integer 1–3 **only if the source prints a
  grade**, otherwise `null`. Never defaulted.
- `rubrics[].remedies[].name` — canonical remedy name, resolved where possible,
  else `null`.
- `rubrics[].note` — verbatim prose attached to a rubric (Jahr Part II), else `null`.
- `remedy_index` — every printed remedy token → `{ name, resolved }`.

## Materia Medica — `materia_medica/*.json`

```json
{
  "schema_version": "1.0",
  "type": "materia_medica",
  "book": { ... },
  "remedies": [
    {
      "name": "Aconitum Napellus",
      "abbrev": "Acon",
      "canonical_name": "Aconitum napellus",
      "symptoms": [
        { "chapter": "Mind", "text": "Anxiety, with fear of death", "grade": null }
      ]
    }
  ]
}
```

- `remedies[].name` — the remedy as printed (may be OCR-damaged in some books).
- `remedies[].canonical_name` — best-effort resolved name, else `null`.
- `symptoms[].chapter` — the labelled group the symptom belongs to (e.g.
  `Stools`, `Aggravation`), or `General`.
- `symptoms[].text` — the symptom string, **verbatim**.

## Rules

1. **Verbatim.** Every `text` is copied from the source, not rewritten.
2. **No invention.** Unknown values are `null`. Grades are never assumed.
3. **Validation.** Each file passes schema validation with zero errors, and
   reports a verbatim-fidelity rate in its QC report.
