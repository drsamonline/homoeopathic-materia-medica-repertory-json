# QC — Clarke, Dictionary of Practical Materia Medica, Vol. II (I–P)

| | |
|---|---|
| Source | `clarke-dictionary-materia-medica-v2-i-p` — DjVu XML of two 1902 archive.org scans |
| Remedies | 323 |
| Words | 435,794 |
| Licence of the TEXT | Public domain — Clarke died 1931 |

## How it was built

The same height-based method that recovered Volume I: the DjVu XML gives every word a
bounding box, so a remedy heading is found by being taller than its page's median line
rather than by being spelled correctly — which OCR never manages for these headings.

Two scans of this volume exist and both were used. One carries far more text (400,001 words)
but stops a remedy short of the volume's end; the other reaches Pelargonium Reniforme but
recovers only 58,325 words because its page scale defeats the height test. The richer scan
is the base, and remedies it lacks are filled from the second.

## Known limitations

- **Volume II only (Iberis–Pelargonium).** Volumes I and III are separate scans.
- **323 entries** is more than the volume's true remedy count: two scans produce two
  spellings of the same remedy, and only those 94% alike on letters and within three
  characters of length were merged, deliberately, so that genuinely distinct remedies such
  as the several Calcareas are never collapsed into one.
- **OCR damage in names** — "Ictodes Fobtida", "Peoten" — carried through.
