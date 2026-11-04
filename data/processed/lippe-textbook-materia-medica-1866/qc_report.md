# QC — Lippe, A Text Book of Materia Medica

| | |
|---|---|
| Source | `lippe-textbook-materia-medica-1866` — the supplied PDF (740 pages, with a text layer) |
| Remedies | 263 |
| Words | 176,825 |
| Licence of the TEXT | Public domain — Lippe's 1866 text |

## How it was read

A remedy opens with its name in capitals on its own line. The scan repeats the name as a
running head on every page of its entry, so 834 heading candidates reduce to 263 remedies
once repeats are merged back onto the first occurrence.

Two merges were applied, and only two:
- names within 92% similarity and two characters of length (OCR variants);
- **one name being a prefix of another** — "Agnus" onto "Agnus Castus", "Agaricus" onto
  "Agaricus Muscarius" — because the running head abbreviates and the full name appears at
  the entry.

## Known limitations

- **Prose chapters, not numbered symptoms.** Each remedy is carried whole in
  `sections.general`, so this volume adds no `symptoms` count.
- **OCR damage in names** is carried through — "Agaricus Muscahius" for Muscarius,
  "Aconit" for Aconitum — rather than corrected.
- **The printer's name was removed** rather than kept as a remedy: the title page sets
  "JAS. B. EODGEES, PRINTBE" in the same capitals as the entries.
- **No corroboration** beyond the scan.
