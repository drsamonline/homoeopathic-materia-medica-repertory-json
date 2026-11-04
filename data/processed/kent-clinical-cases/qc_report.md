# QC — Kent, Clinical Cases

| | |
|---|---|
| Source | `kent-clinical-cases` — the Médi-T transcription, read through the Wayback Machine |
| Cases | 105 |
| Words | 41,735 |
| Licence of the TEXT | Public domain — Kent died 1916 |

## What it is

Kent's case records, each opening with `Case N`, a title, the remedy and the narrative of the
prescription and its result — "Case 1 — Abdominal pain and tumor suspicion", "Case 6 —
Aconite or Sulphur ?- Pneumonia". The transcription's own French page header calls them
"Les 111 observations du Professeur James Tyler Kent".

## Coverage

**105 cases are present** against the 111 the transcription advertises. The six absent are
cases whose heading the transcription itself does not carry as a `Case N` line; they are
missing rather than lost in parsing.

## Known limitations

- **Titles are the transcription's own** — some are the case's presenting complaint, some the
  remedy. They are kept as printed, not rewritten.
- **Prose cases, not structured records.** No attempt is made to split a case into symptoms,
  remedy and outcome as separate fields: the page does not mark those boundaries, and
  inventing them would be invention.
- **No corroboration** beyond the transcription.
