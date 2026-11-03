# QC — Kent, Lectures on Homoeopathic Materia Medica

| | |
|---|---|
| Source | `kent-lectures-materia-medica` — the DLI scan of a Calcutta reprint of the first edition (text layer) |
| Lectures recovered | 251 |
| Words | 439,808 |
| Licence of the TEXT | Public domain — Kent died 1916 |

## What this is

Kent's lecture course, one lecture per remedy, carried as a `treatise` with the remedy as
the section title. It is prose, not a rubric list and not a symptom schema, so nothing is
forced into chapter labels the lectures do not have.

## How the parse works

A lecture begins at the first occurrence of the remedy's name in capitals; the name repeats
as a running head on that lecture's pages, so first-occurrence is the right key. Names whose
letters are 93% alike (and whose length differs by two at most) are merged onto the first
spelling seen.

## Known limitations

- **Coverage is unverified.** The scan carries no list of lectures, so 251 cannot be checked
  against the book's own contents. A lecture whose heading the OCR destroyed is absent, not
  reconstructed.
- **OCR duplicates can survive.** A badly mangled name ("Aconttum Napellos") can slip past
  the merge rule and appear as its own lecture.
- **Running heads and page numbers are glued to some lecture openings**, which is why a
  lecture occasionally begins mid-word.
- **One source, so no corroboration.** The fidelity claim is "this is what the scan says".
