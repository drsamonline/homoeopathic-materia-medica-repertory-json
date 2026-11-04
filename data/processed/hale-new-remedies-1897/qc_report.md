# QC — Hale, Materia Medica and Special Therapeutics of the New Remedies

| | |
|---|---|
| Source | `hale-new-remedies-1897` — DjVu XML of the archive.org scan (789 pages) |
| Remedies | 204 |
| Words | ~230,000 |
| Licence of the TEXT | Public domain — Hale's 1897 edition |

## What the book is

Hale's "new remedies" are the drugs outside the classical materia medica — the American
plants and the recent chemicals: Acalypha indica, Ailanthus glandulosa, Apocynum
androsemifolium, Amyl nitrite. Each gets a prose chapter rather than a numbered schema.

## How it was read

A remedy opens with its name set in capitals and slightly larger than the body text,
which the DjVu XML makes visible as height. Front-matter headings are filtered out by name
("Materia Medica", "Special Therapeutics", "Preface", "Explanation of Symbols"), since they
are set in the same capitals.

## Known limitations

- **Symptoms are prose, not rows.** Each remedy's chapter is carried in `sections.general`
  as continuous text rather than being split into numbered symptoms, so this volume adds
  no `symptoms` count. Splitting Hale's prose into rows would mean inventing boundaries the
  page does not mark.
- **OCR damage in remedy names** is carried through — "Aoave Americana" for Agave,
  "Aletris Fabinosa" for Farinosa, "Amyl Nitritb" for Nitrite.
- **One front-matter entry was removed**: a chapter headed "New Eemedies" (the scan's
  rendering of "New Remedies") that the capitals rule had taken for a remedy.
- **No corroboration** beyond the scan.
