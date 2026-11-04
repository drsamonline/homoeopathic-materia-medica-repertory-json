# QC — Hering, Index to the Remedies for Ague

| | |
|---|---|
| Source | `hering-ague-index` — the supplied PDF, a typed transcription |
| Chapters | 1 |
| Rubrics | 79 |
| Remedy links | 679 |
| Licence of the TEXT | Public domain — Hering died 1884 |

## What it is

A short clinical index: each rubric names a circumstance of the ague — "In marshy places",
"In damp, cold seasons", "An attack every two weeks", "Chill then heat", "First heat then
chill" — followed by the remedies Hering associated with it. No grades are printed and none
are recorded.

## How it was read

The printed form is `rubric. - Remedy, Remedy, Remedy.` The parse splits on that dash, takes
the words before it as the rubric and the comma-separated names after it as remedies. A name
longer than three words is rejected rather than kept, because at that length it is prose
that has leaked past the dash.

## Known limitations

- **One chapter only.** The index has no divisions of its own, so it is carried as a single
  "Ague" chapter rather than being given chapters it does not have.
- **No grades** — the book prints none.
- **A short work**: seven pages. It is a clinical index, not a full repertory, and the
  counts reflect that.
