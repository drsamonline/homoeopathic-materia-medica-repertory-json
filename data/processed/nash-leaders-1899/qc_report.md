# QC — Nash, Leaders in Homoeopathic Therapeutics

| | |
|---|---|
| Source | `nash-leaders-1899` — archive.org text layer of the Google scan |
| Remedies | 205 |
| Words | 117,070 |
| Licence of the TEXT | Public domain — Nash's 1899 text |

## Why the archive text, not the PDF

The supplied PDF of this title is **image-only**: every body page carries no text layer. The
same scan on archive.org has a DjVu text layer, which is what this volume was built from.
OCR of 501 pages would not have been practical here.

## How it was read

A remedy opens with its name in capitals on its own line. Running heads repeat the name on
later pages, so repeats are merged back onto the first occurrence, and the author's own name
from the title page is not treated as a remedy.

## Known limitations

- **Some remedies appear twice under OCR variants.** "Nttx Vomica" sits beside "Nux
  Vomica", "Brvunia Alba" beside "Bryonia Alba", "Mercttbixts" beside "Mercurius". The
  merge accepts names within 93% similarity and two characters of length; damage like
  `Nttx` for `Nux` falls outside that, and loosening it would start collapsing genuinely
  different remedies such as the several Mercuries. The duplicates are left visible rather
  than guessed away.
- **Prose chapters, not numbered symptoms** — each remedy is carried whole in
  `sections.general`, so this volume adds no `symptoms` count.
- **OCR damage** elsewhere in the text is carried through.
