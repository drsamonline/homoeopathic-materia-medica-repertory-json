# QC — Ruoff, Repertory of Homoeopathic Medicine (1845)

| | |
|---|---|
| Source | `ruoff-repertory-1845` — archive.org text of the NLM scan (64330790R) |
| Remedies | 119 |
| Words | 60,525 |
| Licence of the TEXT | Public domain — Ruoff's 1845 text; Okie's translation |

## A repertory that reads remedy-first

The title says *Repertory*, and it is nosologically arranged, but the printed page runs
**remedy first, then the symptoms**: "Chamom. — Great restlessness, convulsive twitchings",
"Sabina — Threatening abortion in a female". So the book is shaped like a materia medica,
and that is how it is stored — one entry per remedy, its symptoms in prose beneath it.

Calling it a repertory of rubrics would have been a fiction about how the page is built.

## How it was read

A remedy opens with its name at the start of a line, followed by an em dash and the symptom
text. Names are resolved against the library's own vocabulary, which is why "Chamom." lands
on Chamomilla and "Ipecac." on Ipecacuanha.

## Known limitations

- **Prose symptoms, not rows.** Each remedy's symptoms are carried whole in
  `sections.general`, so this volume adds no `symptoms` count.
- **OCR damage** is heavy in this scan — the title page alone reads "HOKEOPATHIC MEDICINE"
  and the second editor's name as "B. LUDWXO, PUXTSK". Text is carried as the scan gives it.
- **119 remedies** is fewer than the book holds: names the OCR damaged past resolution were
  left in the running text rather than attached to a guessed remedy.
