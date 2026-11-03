# QC — Boericke, Pocket Manual of Homoeopathic Materia Medica

| | |
|---|---|
| Source | `boericke-pocket-manual-1906` — the Google scan of the 1906 printing, text layer |
| Remedies | 379 |
| Symptoms | 3012 |
| Licence of the TEXT | Public domain — Boericke died 1929; a 1906 printing is long out of copyright |

## Why this scan

Three copies were tried. The Médi-T transcription is the cleanest but the Wayback Machine
would not serve 622 pages reliably. The DLI scan of the 1922 eighth edition OCRs badly
enough that the author's name comes out "IIOERK'KE". This 1906 Google scan reads
"ACONITUM NAPELLUS. (Monkshood.) A state of fear, anxiety…" and keeps the schema sections
("Mind. —", "Head. —"), so it is good enough to be the text rather than merely to check one.

## How the parse works

- A remedy opens with its name in capitals and a full stop; the common name follows in
  brackets and is lifted into `common_name`.
- The account before the first section is kept as `sections.general`.
- Each schema section keeps Boericke's own chapter word — `Mind`, `Head`, `Stomach` — with
  the words after the em dash as its text. Nothing is mapped onto a modern vocabulary.
- Names 94% alike and within two characters of length are merged onto the first spelling,
  which folds running heads and OCR variants without collapsing the Zincums into each other.

## Known limitations

- **Coverage is unverified.** This scan carries no usable list of remedies, so
  379 cannot be checked against the book's own index; a remedy whose heading the
  OCR destroyed is absent rather than reconstructed.
- **OCR damage is carried through** — "wtth" for with, and double spaces the scan produced.
- **One source, no corroboration** beyond the two other copies used to choose it.
- 18 remedies parsed with no schema sections.
