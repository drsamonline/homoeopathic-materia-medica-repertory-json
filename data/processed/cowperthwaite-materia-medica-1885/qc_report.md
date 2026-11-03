# QC — A Text-Book of Materia Medica, Characteristic, Analytical and Comparative

| | |
|---|---|
| Source | `cowperthwaite-materia-medica-1885` — the 1885 third edition (Gross & Delbridge), text layer of the scan |
| Pages | 738 |
| Remedies | 252 |
| Symptoms | 2965 |
| Chapters | 133 |
| Licence of the TEXT | Public domain — Cowperthwaite's edition was published 1885 |

## What the parse found

- **252 remedies**, 238 of them with at least one symptom line.
- **2965 symptoms** across 133 chapter labels.
- **191 of 252** remedy names resolved to a canonical name
  (75.8%); the printed name is kept verbatim in every case.

Most-used chapter labels: Therapeutic Range (203), Generalities (149), Respiratory Organs (141), Stomach (133), Mouth (132), Eyes (125), Abdomen (119), Face (113), Head (107), Nose (106).

## Method

The book is rigidly laid out, and the parse leans on that: a remedy begins at an
all-capitals heading followed by `Natural order.`, `Common names.`, `General Analysis.`
or `CHARACTERISTIC SYMPTOMS.`; inside a remedy, a `Label. —` line opens a chapter and the
words that follow it are that chapter's symptom text. Chapter labels are read as printed
rather than snapped to a fixed list, which is why the book's own vocabulary ("Generalities",
"Ear", "Sensorium") survives instead of being flattened.

## Normalisation (nothing else was touched)

- runs of spaces collapsed — the OCR sets wide word gaps;
- a word broken by a line-end hyphen rejoined;
- running heads (`94 ARUM TRIPHYLLUM.`) and bare page numbers dropped.

No symptom was rewritten, reworded or invented. Grades are `null` throughout: this book
prints no grade marks, and the schema forbids defaulting them.

## Page-level check

Page 27 (Abies canadensis) was rendered and compared against the parsed record by eye:
heading, `Natural order`, `Common names`, `General Analysis`, `CHARACTERISTIC SYMPTOMS`
and the `Mind` / `Head` / `Eyes` / `Stomach` / `Abdomen` chapters all correspond, in order,
with no text added or lost.

The scan's own OCR damage is carried through rather than silently corrected — it reads
"Puls." as "Puis." and prints some parenthetical remedy lists with braces where the page
has round brackets. That is the text layer the PDF carries; correcting it would be
rewriting, which this library does not do.

## Known limitations

- **No second source.** This edition has one usable scan, so the text cannot be
  corroborated the way the Organon volumes were. The fidelity claim here is a parse
  claim, not a corroboration claim.
- 14 remedies parsed with no symptom lines (AURUM. I07, BADIAGA. I I I, I3O BERBERIS, BO VISTA. I37, BRYONIA. I4I, CARBO VEGETABILIS, I96 CAULOPHYLLUM, LACHNANTHES. 4OI, …).
  Their headings are real; their bodies are prose that the chapter grammar does not split.
- 61 printed names have no confident canonical match
  (ALETRIS FARINOSA, AMYL NITRITE, APIS MELLIFICA, ARANEA DIADEMA, ARUM TRIPHYLLUM, ASCLEPIAS CORNUTI, ASPARAGUS, AURUM. I07, I3O BERBERIS, BO VISTA. I37, …). None was guessed.
- The book's "Compare." and "Antidotes." lines are not carried: they name other remedies
  rather than symptoms, and no field in this schema holds them honestly.
