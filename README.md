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

## The public-domain collection

16 books (1847–1906), **217,682 repertory rubrics** and 384,841 remedy links,
every string verbatim from its source. Knerr's 1896 repertory (131,685 rubrics,
43 chapters) and Kent's 1897 are split by chapter with an `index.json`; Gentry's
concordance is split A-Z by concordance keyword, 25 files plus `index.json`; the
rest are single files. Each book carries a QC report under
`data/processed/<slug>/qc_report.md` with its verbatim-fidelity rate.

Two extraction pipelines live in `pipeline/`:

- `omm_pipeline.py` — the generic repertory / materia medica grammar (`':'` +
  comma-separated remedy lists, the trailing `'. '` grammar, Jahr, Ruoff, Bell).
- `omm_extract_extra.py` — dedicated grammars for the books that print their
  remedy lists as a run of **space-separated** abbreviations, or that carry
  printed degree marks: Allen 1883 (`fever`), Bryant 1851 (`bryant`), Gentry
  1893 (`gentry`), Knerr 1896 (`knerr`). Each mode is documented at the top of
  the file, with the source sample it was written against.

## Licensing — two licences, one per folder

- **Compiled public-domain datasets** (everything except the folder below) — **CC0 1.0**.
  Compilations of source texts published before 1929.
- **`repertory/repertorium-publicum-2008/`** — **GNU GPL v3**, *not* CC0. It is
  third-party material (Repertorium Publicum, 2008, Vladimir Polony; part of the
  OpenRep source code) and cannot be relicensed here. Use of those files must comply
  with GPL v3, including its copyleft terms.

The CC0 dedication in `LICENSE` does not apply to that folder. See `LICENSE` and
`LICENSE-GPL-3.0.txt`.
