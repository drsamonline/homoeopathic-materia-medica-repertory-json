# homoeopathic-materia-medica-repertory-json

[![License: Free to use, attribution required](https://img.shields.io/badge/license-Free%20to%20use,%20attribution%20required-yellowgreen)](LICENSE)

## Repertorium Publicum (2008) — complete, graded

`repertory/repertorium-publicum-2008/` holds a **complete, fully graded** open
repertory: **74,480 rubrics**, **735,460 remedy links**, **669 remedies**, 41 chapters.

Unlike the `kent-1897/` extraction, every remedy link carries a grade (1–3):

| grade | links |
|---|---|
| 1 | 465,287 |
| 2 | 198,591 |
| 3 | 71,582 |

Sourced from the [OOReP](https://github.com/nondeterministic/oorep) open repertory
database (repertory token `publicum`).

**Please note:** this is *not* Kent's 1897 first edition. It is *Repertorium Publicum*
by Vladimir Polony (2008), a Kent-derived repertory with its own chapter structure
(separate *Clinical*, *Appetite*, *Blood* and *Heart & Circulation* chapters) and its
own additions. It is licensed **GPL v3** as part of the OpenRep source code — not
public domain. See the dataset README for details.

## The Organon, in two editions

`treatise/` holds the *Organon of Medicine* as a **treatise** — numbered paragraphs, no
rubrics, no remedies — in both public-domain English translations:

| file | edition | translation | paragraphs |
|---|---|---|---|
| `organon-6th-1922.json` | sixth (completed 1842) | William Boericke, 1922 | 291 |
| `organon-5th-1849.json` | fifth (1833) | R. E. Dudgeon, 1849 | 294 |

Each paragraph carries its text, its printed footnotes, the source it was read from and
the fraction of its 12-letter sequences found verbatim in OCR scans of **that edition**
(median 0.976 for the sixth, 0.979 for the fifth; floor 0.60). The two are different
books — 74 paragraphs are worded differently and §292–§294 exist only in the fifth — and
they are kept as separate volumes, never merged.

## The public-domain collection

**55 volumes (1847–1932)** — 16 repertories, 6 materia medicas and 33 treatises:
**307,998 repertory rubrics**, **1,359,069 remedy links** of which **751,907 carry a
grade**, 39,770 materia medica symptoms and 5,375 sections of prose, every string verbatim
from its source.

Knerr's 1896 repertory (131,685 rubrics, 43 chapters) and Kent's 1897 are split by chapter
with an `index.json`; Gentry's concordance is split A-Z by concordance keyword, 25 files
plus `index.json`; the rest are single files. Each book carries a QC report under
`data/processed/<slug>/qc_report.md` with its verbatim-fidelity rate.

Two figures worth reading carefully, because they are not what they look like. **Kent's
1897 repertory is entirely ungraded** — 59,114 rubrics and 353,000 links, every grade null
— while the graded links come from Knerr and from Repertorium Publicum. And the totals in
`catalog.json` were recounted from the files themselves on 2026-11-04, having previously
omitted every split volume: remedy links were 613,588 short and rubrics 34,531 short.

## Licensing — two licences, one per folder

- **Compiled public-domain datasets** (everything except the folder below) — **CC0 1.0**.
  Compilations of source texts published before 1929.
- **`repertory/repertorium-publicum-2008/`** — **GNU GPL v3**, *not* CC0. It is
  third-party material (Repertorium Publicum, 2008, Vladimir Polony; part of the
  OpenRep source code) and cannot be relicensed here. Use of those files must comply
  with GPL v3, including its copyleft terms.

The CC0 dedication in `LICENSE` does not apply to that folder. See `LICENSE` and
`LICENSE-GPL-3.0.txt`.
