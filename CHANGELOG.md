# Changelog

## 2026-11-03 — the Organon, in two editions

`treatise/` is a new type in this library: a prose work with numbered paragraphs, which a
repertory or materia medica file cannot honestly represent.

- **`organon-6th-1922.json`** — 291 paragraphs, Boericke's 1922 translation of the sixth
  edition, with its printed footnotes.
- **`organon-5th-1849.json`** — 294 paragraphs, Dudgeon's 1849 translation of the fifth.
- Every paragraph carries `from` and `corroboration`, measured the same way as every other
  book here: the fraction of its 12-letter sequences found verbatim in OCR scans of the
  same edition. Sixth: median 0.976, minimum 0.729. Fifth: median 0.979, minimum 0.745.
  Floor 0.60 in both; nothing was accepted below it.
- `catalog.json` gains two entries and a `treatise_sections` total (585).

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
- **`repertory/boenninghausen-pocket-book-1891.json`** — Boenninghausen,
  *Therapeutic Pocket Book*, sixth American edition by Timothy Field Allen
  (1891): **1,323 rubrics**, 38,314 remedy links, 100 % verbatim, 1,208 remedy
  tokens all resolved. Two deliberate limits, recorded in its QC report: the
  OCR merges the two columns' running heads (`EXTERNAL HEAD — EYES`), so the
  book ships as one section with the printed sub-heading (`AGGRAVATIONS`,
  `AMELIORATIONS`, `Internal Head`) carried as each rubric's `parent`; and the
  printed degree marks survive only as capitals, so an ALL-CAPS remedy token is
  recorded as grade 3 and every other token as `null`. Collection: 17 books,
  219,005 repertory rubrics.

## 1.1.1 — 2026-11-02

Audit pass over the published collection (`docs/AUDIT-2026-11-02.md`).

- **Jahr's Manual:** both part files claimed the whole book's counts
  (199 remedies / 26,734 symptoms). Each now reports its own half — 99 / 11,711
  and 100 / 15,023.
- **Kent:** `extremities.json` holds 6,666 rubrics, not the 13,333 the index
  claimed, and ends mid-remedy-list — the chapter is truncated and needs a
  rebuild. Kent's totals are corrected to **52,447 rubrics / 319,461 links**
  (was 59,114 / 353,000).
- **Landing page:** the rubric total had never included Kent's chapter files.
  Corrected to **271,421 repertory rubrics, 744,394 remedy links** across 17
  books.
- **Gentry:** a post-pass moves remedy tokens that leaked into rubric text back
  into the remedy list — +1,740 links (64,052 → 65,792), 31 non-symptom
  fragments removed.
- **Bryant:** same pass, +38 links, no rubric lost.
- **Provenance:** `data/source_txt/SOURCES.md` records the byte size and SHA-256
  prefix of every source text, so a verbatim claim can now be checked.
- Known and left alone: Kent Extremities (needs source), Hering 1889 (713
  no-remedy rubrics, 93.6% verbatim), Vilas (51% no-remedy rubrics), Jahr
  repertory (587 rubrics — rebuild from `JAHRII.XML`).

## 1.1.2 — 2026-11-02

- **Four volumes were shipping placeholder metadata** — `title: "x"`,
  `author: "x"`, and a year of 1900 for all four — which is what a reader saw in
  any catalogue built from the JSON. Each is now named from its own catalogue
  record:

  | id | title | author | year | publisher |
  |---|---|---|---|---|
  | `clarke-clinical-1900` | A Clinical Repertory to the Dictionary of Materia Medica | John Henry Clarke | **1904** | Homoeopathic Publishing Co., London |
  | `lippe-repertory-1879` | Repertory to the More Characteristic Symptoms of the Materia Medica | Constantine Lippe | **1879** | Steam Press of Bedell & Brother, New York |
  | `pulford-rheumatism-1898` | Repertory of the Symptoms of Rheumatism, Sciatica, et cetera | Alfred Pulford | **1898** | B. B. Krammes, Tiffin, Ohio |
  | `vilas-eye-ear-1890` | Therapeutics of the Eye and Ear, with a Repertory of the Eye | C. H. Vilas | **1883** | — |

  Sources: HathiTrust, Wellcome Collection and the Library of Congress for Clarke,
  Pulford and Lippe; the NLM copy for Vilas.
- **Years corrected.** Three of the four carried 1900 regardless of their own
  slug. Clarke is 1904, not 1900. Vilas is 1883, not 1890 — the slug still says
  1890, which is left in place so the file URL stays stable, and is flagged here
  rather than silently changed.
- **`catalog.json` regenerated**, so any reader built on it shows the real names.
  No rubric, remedy link or id was touched — only the `book` block.
