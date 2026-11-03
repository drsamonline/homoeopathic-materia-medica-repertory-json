# Schema

Every file is self-describing: the top-level `type` is `repertory`, `materia_medica` or
`treatise`.

## Common — `book`

| field | type | notes |
|---|---|---|
| `id` | string | slug, e.g. `kent-repertory-1897` |
| `title` | string | full title |
| `author` | string | author(s) |
| `year` | integer | year of the edition used |
| `publisher` | string | where known, else `""` |
| `source_file` | string | the OCR text file it was built from |
| `counts` | object | `{ sections, rubrics, remedy_links }`, `{ remedies, symptoms }` or `{ sections, notes }` |

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

## Treatise — `treatise/*.json`

A prose work with numbered paragraphs — the Organon, in either edition. It has no rubrics
and no remedies, so it is its own type rather than a repertory with empty fields.

```json
{
  "schema_version": "1.0",
  "type": "treatise",
  "book": { ... , "edition": "Fifth German edition (1833), English translation 1849",
                  "translator": "R. E. Dudgeon",
                  "verification": { "median": 0.979, "min": 0.745, "floor": 0.6 } },
  "sections": [
    {
      "id": "organon-5th-1849-s1",
      "n": 1,
      "text": "The physician's high and only mission is to restore the sick to health, to cure, as it is termed.",
      "notes": ["1 His mission is not, however, to construct so-called systems..."],
      "from": "MediT-shared",
      "corroboration": 1.0
    }
  ]
}
```

- `sections[].n` — the paragraph number as printed (§1, §2, …).
- `sections[].title` — **optional**, for a treatise that is chaptered rather than numbered
  (Allen's *Chronic Miasms*, Bradford's *Life and Letters*). When present, `n` is the
  section's ordinal position in the book and the reader shows the title instead of "§n".
  A numbered treatise like the Organon carries `n` and no `title`.
- `sections[].pages` — **optional**, the printed page range the section occupies.
- `sections[].text` — the paragraph, **verbatim**. A footnote never runs into it.
- `sections[].notes` — the footnotes printed with that paragraph, verbatim, in order.
- `sections[].from` — `MediT` (transcription), `MediT-5th` (a fifth-edition variant block) or
  `MediT-shared` (a heading the page prints without an edition label, because the text is
  the same in both).
- `sections[].corroboration` — the fraction of the paragraph's 12-letter sequences found
  verbatim in the OCR scans of **the same edition**. `null` means not yet checked.
- `book.verification` — median, minimum and the acceptance floor across the volume.
- `book.public_domain_note` — **optional**, when the public-domain claim differs by country.
  A bare `public_domain: true` is only used where the work is free everywhere this library
  is likely to be read.
- `book.copyright_jurisdictions` — **optional**, the year the term expires per country, e.g.
  `{"IN": 1996, "GB": 2007, "US": 2028}`. A consumer must show this before republishing a
  volume whose rights are not universal.

**The two editions are separate volumes and are never merged.** They are different books:
the fifth runs to 294 paragraphs against the sixth's 291, and 74 paragraphs are worded
differently. A consumer must show which edition it is reading, never blend the two.

## Rules

1. **Verbatim.** Every `text` is copied from the source, not rewritten.
2. **No invention.** Unknown values are `null`. Grades are never assumed.
3. **Validation.** Each file passes schema validation with zero errors, and
   reports a verbatim-fidelity rate in its QC report.
