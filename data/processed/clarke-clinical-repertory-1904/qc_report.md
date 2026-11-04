# QC — Clarke, A Clinical Repertory to the Dictionary of Materia Medica

| | |
|---|---|
| Source | `clarke-clinical-repertory-1904` — DjVu XML of the archive.org scan (368 pages) |
| Chapters | 35 (grouped by the rubric's initial letter) |
| Rubrics | 3,725 |
| Remedy links | 4,321 |
| Rubrics carrying at least one remedy | 2,293 of 3,725 (62%) |
| Licence of the TEXT | Public domain — Clarke died 1931 |

## How it was read

The scan's OCR is clean, which is unusual for this library's repertories: a rubric reads
"Exhausting Diseases, Children after. — Cb. v." and the abbreviations survive intact. The
parse splits each line at its em dash, takes the words before it as the rubric and the
citation run after it as remedies, and resolves each citation through the library's own
vocabulary with the word-wise matcher (an abbreviation may be a prefix of the name's first
word, and of its second).

Rubrics are grouped into chapters by their initial letter, because the book is a single
alphabetical sequence rather than a set of classical chapters. Sub-rubrics, printed with a
leading dash, are marked `sub` in the source and flattened into the same sequence here.

## Grades

**No grades are recorded.** Clarke's Clinical Repertory prints remedy abbreviations in
sequence without the superscript grades a classical repertory uses, and the scan's OCR does
not preserve any that exist. `grade` is null throughout rather than invented.

## Known limitations

- **Only 62% of rubrics carry a remedy link.** Clarke's abbreviations are two or three
  letters ("Cb. v.", "Stn.", "Lrs."), and short abbreviations are inherently ambiguous — the
  matcher resolves what it can and leaves the rest as text rather than guessing.
- **Some resolved names inherit OCR damage** from the library's own vocabulary, where a
  book stored a mangled name ("Phellan Duixjm Aquaticum" for Phellandrium aquaticum).
- **No corroboration** beyond the scan itself.
