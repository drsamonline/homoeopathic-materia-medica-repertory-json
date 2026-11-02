# New sources, 2026-11-02 — survey and extraction status

Seven books arrived in this batch. This note records what each one is, the
grammar it prints, what the current parser produces, and what is still wrong.
Nothing here is published to the repository yet: a book ships only when its
rubric text and remedy lists are faithful, and four of these are not there.

## Published earlier today (for reference)

| book | rubrics | links | verbatim |
|---|---|---|---|
| Knerr 1896 (Hering's Guiding Symptoms) | 131,685 | 203,661 | 99.6% |
| Gentry 1893, Concordance vol. I | 40,524 | 64,052 | 99.8% |
| Bryant 1851, Pocket Manual | 4,965 | 39,045 | 100% |
| Allen 1883, Intermittent Fever | 1,708 | 9,044 | 99.9% |

## This batch

### 1. Kent, Repertory of the Homoeopathic Materia Medica (1897) — new OCR source
Lancaster, Pa.: Examiner Printing House, 1897. `KENTS_NEW_SOURCE.txt`, 89,226 lines.

Grammar: chapter heads in caps with page numbers; rubric heads are all-caps and
close with `:` (`ANGER, ailments after, with vehemence:`), sub-rubrics are
lower-case and also close with `:`; remedy lists are lower-case abbreviations
(`acon., bell., nux-v.`), often missing their final period and wrapping freely.

Draft parse: 22 of 34 chapters, 23,809 rubrics, 92,475 links, 97.3% verbatim.
**Why it is not published:** only 22 chapters were recognised — everything after
*Urine* (Genitalia through Generalities) has no recognisable chapter head in this
OCR — and 23,809 rubrics against the 59,114 in the existing `kent-1897/` means
this parse is currently the smaller, not the better, file. The existing Kent
extraction (94.1% verbatim) stays in place until the new one beats it.

### 2. Boenninghausen, Therapeutic Pocket Book (6th American ed., Allen, 1891) — PUBLISHED
`repertory/boenninghausen-pocket-book-1891.json`, 2.8 MB.

Grammar: `Heading.— Rem1., Rem2., ...`, the separator always carrying a dash,
with higher degrees printed in capitals and two-word abbreviations
(`Am. carb.`, `Calc. ph.`, `Nux m.`) split across the OCR.

Result: **1,323 rubrics, 38,314 remedy links, 1,208 remedy tokens (all
resolved), 100 % verbatim, zero validation errors.**

Two limits, both recorded in its QC report rather than papered over:

- **One section.** The OCR merges the two columns' running heads
  (`EXTERNAL HEAD — EYES`, `M [ND — INTELLECT`), so chapter boundaries are not
  recoverable. The book ships as a single section and the printed sub-heading
  (`AGGRAVATIONS`, `AMELIORATIONS`, `Internal Head`, `Glands`) is carried as each
  rubric's `parent`, which is what the book itself uses to distinguish, say, the
  *Walking* rubric under aggravations from the one under ameliorations. The
  parent strings keep their OCR damage (`AGGRAVAnONS`); they are printed text,
  not corrected.
- **Grades only at the top degree.** The printed degree marks survive as
  capitals, so an ALL-CAPS token is recorded as grade 3 and every other token as
  `null`. The intermediate degrees are not distinguishable in this scan.

### 3. Kimball, A Repertory of Gonorrhoea (1888)
Boston: Otis Clapp and Son, 1888. `KAMBAL.txt`, 8,882 lines.

Grammar: mixed-case headings (`Urging, or Desire, to Urinate.`), entries
`text : remedies`, sub-entries introduced by an em dash or a bare comma, heavy
line-wrapping and frequent dropped colons.

Draft parse: 2,894 rubrics, 4,082 links, 99.6% verbatim.
**Why it is not published:** the verbatim rate is good but the rubric *text* is
fragmentary — entries are split mid-sentence and the `parent` heading is often a
fragment (`cle`, `ward evening`) because wrapped heading lines are not being
rejoined. Needs a heading-rejoin pass before it ships.

### 4. Worcester, Repertory to the Modalities (1880)
New York: Boericke & Tafel, 1880. `MODALITY_RP.TXT`, 7,699 lines.

Grammar: modality chapters (Sun, Air, Water, Winds, Weather, Seasons); inside
them, region labels (`EYES. —`, `FACE. —`, `GENERALITIES. —`) and entries whose
remedy list trails the sentence, in full names (`Camphora.`, `Natr. mur.`).

Draft parse: 69 sections, 1,619 rubrics, 2,166 links, 96.4% verbatim.
**Why it is not published:** two defects — several entries merge into one rubric
when a region label interrupts them, and short capitalised English words
(`cold.`, `after.`) are being accepted as remedy names. Needs the label handling
plus a stricter rule for what may count as a remedy.

### 5. Ruoff, Repertory of Homoeopathic Medicine (2nd American ed., 1845)
New York: William Radde, 1845; translated by A. Howard Okie, additions by
Gideon Humphrey. `RUOFF.txt`, 17,998 lines.
Not started. The skill's playbook records the 1840 edition as blocked: the
condition heading and the `Remedy — clinical note` boundary is ambiguous. The
1845 edition prints the same shape and will need the same dedicated pass.

### 6. Lee (ed.), Repertory of Characteristic Symptoms, Clinical and Pathogenetic
Published as a supplement to *The Homoeopathic Physician*. `PATHO.TXT`, 30,350
lines. Not started — grammar not yet mapped.

### 7. Jahr, Manual of Homoeopathic Medicine, Part II (Curie trans., 1847)
`JAHR_II.txt` (75,413 lines) plus `JAHRII.XML`, a DjVu OCR file carrying
word-level coordinates and confidence.
The repository's `jahr-repertory-1847.json` holds only 587 rubrics, which is far
short of what this 1.9 MB book contains. The XML is the better source here: the
word coordinates let the two-column page be reassembled correctly instead of
being read line-by-line across the gutter. Not started.

## The CSV

`-Repertory-Archivesearchlink.csv` is not a source text — it is a numbered list
of repertories with archive.org search links (Boenninghausen's several
repertories, Boger, Hering's Analytical Repertory of the Mind, Morgan's urinary
repertory, Lee & Clark's Cough and Expectoration, and others). It reads as the
target list for what to extract next; none of its links were fetched.

## Method note

All five new parsers live in `pipeline/omm_extract_extra.py` alongside the four
that shipped (`fever`, `bryant`, `gentry`, `knerr`). Each mode names the grammar
it expects and the OCR failure it works around. Nothing is written to
`repertory/` until a mode clears zero validation errors, ≥ 90% verbatim, and a
manual spot-check of five rubrics against the source.
