# QC — Materia Medica Pura (A–I)

| | |
|---|---|
| Source | `hahnemann-materia-medica-pura` — the CCRH (Government of India, AYUSH) scan, 742 pages, with a text layer |
| Remedies | 36 |
| Words | 303,925 |
| Licence of the TEXT | Public domain — Hahnemann d. 1843; this translation 1880 |

## What this volume is, and what it is not

This scan covers **Aconitum to Ipecacuanha only** — 36 remedies, the A–I part of
Hahnemann's *Materia Medica Pura*. It is not the complete six-volume work. The rest of the
alphabet is not in this file.

It is a book of **provings**, not a clinical materia medica: each remedy has an
introduction and then numbered symptoms with the provers' initials. It is therefore carried
as a `treatise` with one section per remedy rather than as a `materia_medica` with invented
chapter labels — nothing is asserted about which organ a symptom belongs to, because the
book does not say.

## How the parse works

A remedy begins where its name is printed in capitals, followed either by a preparation
note in parentheses or by the volume number. The running head repeats the remedy's name on
every page and is followed by neither, which is what keeps it out of the parse.

The scan's text layer is set in very short lines, so most of the work is rejoining: words
broken across a line-end hyphen are rejoined, and lines are joined into paragraphs.

## Known limitations

- **No corroboration.** One scan, no second copy, so the fidelity claim is "this is what the
  scan's text layer says".
- **Fragmented text.** The extraction splits some sentences awkwardly; the words are the
  book's, the spacing is the scanner's.
- **A–I only**, as above. Do not present this as the whole *Materia Medica Pura*.
