# QC — Clarke, A Clinical Repertory to the Dictionary of Materia Medica

| | |
|---|---|
| Source | `clarke-clinical-1900` — the DLI scan's text |
| Chapters | 27 (A–Z, plus Other for entries beginning with punctuation) |
| Rubrics | 12,537 |
| Remedy links | 17,217 |
| Licence of the TEXT | Public domain — Clarke died 1931 |

## What was wrong, and what is still wrong

The volume was flagged **damaged** and carried sixteen sections that were not chapters
at all — they were front-matter headings: "List Of Remedies", "List Ot Remedies", "List
Op Abbreviation", "Introduction To The", "VIII", "The Materia Medica I", "Iii Animal
Kingdom", "The Same Author". None of them is a division of the book.

Clarke's Clinical Repertory is one alphabetical sequence, so its rubrics are now grouped
by initial letter, A–Z, with an `Other` group for the entries whose first character is
punctuation debris. Every rubric and every remedy is carried over unchanged: 12,537
rubrics and 17,217 links in, the same out.

## The defect that remains

**10,865 of the 12,537 rubrics carry exactly one remedy.** In Clarke's book a rubric
usually lists several. The source text split the citation run so that most remedies ended
up attached to the following entry, which is why the flag stays `damaged` rather than
being cleared by the re-chaptering.

Fixing it needs the citation run re-joined across the line break, and that needs the scan
itself — the text file no longer contains the information. A DjVu XML attempt on the 1904
scan recovered 3,725 rubrics and 4,321 links, which is a third of this, so it is not an
improvement either.

## Known limitations

- **No grades**, and the remedy-per-rubric defect described above.
- **OCR damage** in rubric text and remedy names carried through.
