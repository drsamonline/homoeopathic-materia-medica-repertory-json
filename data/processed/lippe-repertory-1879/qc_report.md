# QC — Lippe, Repertory to the More Characteristic Symptoms (1879)

| | |
|---|---|
| Source | `lippe-repertory-1879` — DjVu XML of the NLM scan (101303591) |
| Chapters | 33 |
| Rubrics | 38,309 |
| Remedy links | 40,217 |
| Licence of the TEXT | Public domain — Lippe died 1861; this is the 1879 printing |

## This replaces a broken extraction

The volume was previously marked **damaged**: one section, 452 rubrics and 2,824 links.
The book has thirty-three chapters and some thirty-eight thousand rubrics. The old parse
had collapsed the entire repertory into a single section.

## How it was rebuilt

Two sources of structure were needed, because neither works alone:

1. **The chapter titles come from the book's own CONTENTS page**, which is legible —
   "3. Head interior, headache, congestion of blood, heaviness, fulness".
2. **The chapter breaks come from the running heads in the body**, which print only the
   number and a short title — "3. HEAD." — repeated on every page.

Joining them gives thirty-three chapters with real titles. Splitting on the body heads
alone had produced ninety chapters, because every page repeats the head.

Rubrics are one per printed line, with the remedy citations at the end of the line
resolved against the library's own vocabulary by the word-wise matcher.

## Known limitations

- **No grades.** Lippe prints grades as superscripts and this scan's OCR does not preserve
  them, so `grade` is null throughout rather than invented.
- **Chapter 7 (Nose and smell) is thin** — six lines — and chapter 10 is absent; their
  headings survived poorly in this scan. Their rubrics are not lost, but they sit inside
  the neighbouring chapter rather than under their own head.
- **OCR damage in remedy citations** is carried through, not corrected.
