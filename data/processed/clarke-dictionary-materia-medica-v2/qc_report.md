# QC — Clarke, A Dictionary of Practical Materia Medica, Vol. II

| | |
|---|---|
| Source | `clarke-dictionary-materia-medica-v2` — the DLI scan of the 1902 printing (text layer, not OCR'd here) |
| Remedies | 192 |
| Symptoms | 3226 |
| Licence of the TEXT | Public domain — Clarke died 1931 |

## Why this scan and not the other

A CCRH scan of the same volume was tried first and abandoned: its remedy headings carry no
font signal and its *List of Remedies* prints no page numbers for the I–J page, so no
anchor held. This DLI scan keeps the book's capitals and its numbered Schema sections, so
the structure survives.

## How the parse works

- A remedy begins at the **first** occurrence of its name in capitals. The name repeats as
  a running head on every page of its own entry, which is why first-occurrence is the right
  key.
- The scan mangles some names twice over ("PETROLEUM" / "PETTIOLEUM"), so names whose
  letters are 86% or more alike are merged onto the first spelling seen — 438
  variants were folded in rather than counted as separate remedies.
- Inside an entry, `23. Lower Limbs.—` opens a section and the words after it are that
  section's text. The section title is kept as printed.

## Coverage is unverified — read this

This scan has **no list of remedies**, so there is nothing to check the 192 recovered
entries against. Clarke's volume certainly carries more; the difference is entries whose
capitalised heading the OCR destroyed, and they are absent rather than reconstructed or
guessed at. Treat this as a partial volume, which is why the catalogue flags it.

## Known limitations

- **Volume II only (P–Z).** Volume I is not in this file.
- **No second source.** One scan, so the fidelity claim is "this is what the scan says".
- The scan's own OCR damage is carried through, not corrected.
- 14 remedies parsed with no sections, because their entries did not
  match the numbered-section pattern in this scan.
