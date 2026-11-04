# QC — Clarke, A Dictionary of Practical Materia Medica, Vol. I (A–H)

| | |
|---|---|
| Source | `clarke-dictionary-materia-medica-v1` — the DjVu XML of the 1900 archive.org scan |
| Remedies | 435 |
| Words | 484,652 |
| Licence of the TEXT | Public domain — Clarke died 1931 |

## Why this worked when plain text did not

Three earlier attempts at Clarke failed on plain OCR text: the remedy headings come out as
"BTMPTOMS", and the CCRH scan gave no font signal at all. The DjVu XML carries a bounding
box for every word, so a heading can be found by **height** rather than by spelling: body
text on this scan sits at a median height of about 56–65, while a remedy heading such as
"Brucinum." sits at 116. Anything more than 1.6× the page's own median, and shaped like a
name, is a heading.

## How the parse works

- Pages are read in order and the median word height is computed **per page**, so a scan
  whose pages differ in scale still works.
- A line taller than 1.6× its page's median, matching a name shape, opens a remedy.
- Text is carried across page boundaries: an earlier version reset at each page and lost
  every line before the first heading, which is why it recovered only 96,000 of the
  volume's 485,000 words.
- Running heads repeat the remedy's name on later pages and are merged back onto the first
  occurrence by name similarity.

## Known limitations

- **Volume I only (Abies–Hypericum).** Volumes II and III are separate scans.
- **OCR damage in the names** — "Absinthiiim" for Absinthium, "Acajypha Indica" for
  Acalypha Indica — carried through, not corrected.
- **No corroboration** beyond the scan itself.
