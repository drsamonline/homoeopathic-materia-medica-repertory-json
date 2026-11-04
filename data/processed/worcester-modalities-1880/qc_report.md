# QC — Worcester, Repertory to the Modalities (1880)

| | |
|---|---|
| Source | `worcester-modalities-1880` — DjVu XML of the archive.org scan |
| Chapters | 111 |
| Rubrics | 2,046 |
| Remedy links | 1,087 |
| Rubrics carrying at least one remedy | 1,059 of 2,046 (52%) |
| Licence of the TEXT | Public domain — Worcester's 1880 text |

## What the geometry bought

The plain text of this scan defeated an earlier attempt: entries merged across the region
labels because nothing distinguished a heading from a rubric. The XML gives every word a
bounding box, so the page is split at its own gutter into two columns, and a region heading
is recognised by its capitals and closing dash — `COUGH. —`, `CHILL, FEVER, SWEAT.—`.
The book repeats the region name at the head of each rubric, so chapters merge by title
rather than opening one per line.

## The matcher, and why it is word-wise

Repertory abbreviations drop vowels, so "Magn. mur." has to reach Magnesia muriatica and
"Eupator. perf." Eupatorium perfoliatum — no spelling comparison gets there. The matcher
compares **word by word**, allowing the first word of the citation to be a prefix of the
first word of the name, and the second to be a prefix of the second. The vocabulary is
built from the library's own 271,421 rubrics and its materia medicas, cleaned of the OCR
junk some of those books carry as remedy names.

## Grades

**Worcester prints no grades.** `grade` is null on every link; the book does not supply one
and nothing was invented to fill it.

## Known limitations

- **Only 52% of rubrics carry a remedy link.** The other half are either continuations that
  did not join cleanly or citations the OCR damaged past recognition ("Puis." for
  Pulsatilla, "Kohalt" for Cobaltum). They are kept as rubric text rather than guessed at.
- **Page numbers bleed into some rubric text** ("relieved 14 TH").
- **No corroboration** beyond the scan itself.
