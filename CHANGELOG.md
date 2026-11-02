# Changelog

## 1.0.0 — 2026-10-25

- **Licence: PolyForm Noncommercial 1.0.0.** Every repository now carries the canonical text
  from polyformproject.org with the Required Notice line, and the four places a repo states
  its licence agree: LICENSE, the SPDX headers, the README and package.json.
- **The public demo is the app.** A build now fails if `docs/play/index.html` is not the app,
  because a demo running older code is two code paths for one program.

## 1.1.0 — 2026-11-02

- **Four repertories added, one rebuilt.** New book-specific grammars
  (`pipeline/omm_extract_extra.py`) parse the space-separated remedy lists these
  sources print, which the generic `':'` + comma grammar scrambled:
  - `repertory/knerr-1896/` — Knerr, *Repertory to Hering's Guiding Symptoms*
    (1896): **131,685 rubrics**, 203,661 remedy links, 43 chapters, printed
    degree marks (I/II/III) carried as grades. Split by chapter + `index.json`,
    like Kent.
  - `repertory/gentry-concordance-1893.json` — Gentry, *Concordance Repertory*
    (1893), vol. I: **40,524 rubrics**, 64,052 links, 99.8 % verbatim.
  - `repertory/allen-intermittent-fever-1883.json` — Allen, *Repertory to the
    Symptoms of Intermittent Fever* (1883): **1,708 rubrics**, 9,044 links,
    30 chapters.
  - `repertory/bryant-pocket-1851.json` — Bryant, *Pocket Manual* (1851):
    **4,965 rubrics**, 39,045 links, 100 % verbatim. Replaces
    `bryant-pocket-1900.json`, whose title/author were placeholders (`"x"`) and
    whose first rubrics were the title page.
- **Collection totals:** 16 books, **217,682 repertory rubrics**, 384,841 remedy
  links. The landing page carries the new figures and the new file table.
- Every book ships a QC report under `data/processed/<slug>/qc_report.md` with
  its verbatim rate; all five report zero validation errors.
