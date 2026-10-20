# OCR playbook — the concrete things that break, and what fixes them

These are the patterns that actually cost time on archive.org / Google-Books
texts. The pipeline already implements the fixes below; read this when a new book
parses badly and you need to adapt the heuristics.

## 1. Light cleanup policy (agreed default)
- Collapse runs of spaces (`"Aconitum  napellus"` → `"Aconitum napellus"`).
- Fix ligatures / smart punctuation (`ﬁ ﬂ ¬ ’ “ ” —`).
- Rejoin words hyphen-broken across a line break **only when the next line starts
  lower-case** (`"Kreo-\nsotum"` → `"Kreosotum"`). Strip the line before testing
  `endswith("-")` — trailing spaces hide the hyphen.
- Drop standalone page numbers (`^\\s*\\d{1,4}\\s*$`) and running heads.
- **Keep the wording otherwise.** Do not modernise spelling.

## 2. Running heads and section titles
Running heads repeat the chapter title on every page, often with a page number
glued on either end, e.g. `"2  REPERTORY OF SYMPTOMS OF THE LOWER EXTREMITIES."`
or `"REPERTORY OF SYMPTOMS OF THE LOWER EXTREMITIES. 3"`.
Fix: all-caps lines are heading candidates; normalise them (drop digits/punct,
drop leading/trailing junk tokens like `I J`, `Io`, `Jj`), then **de-duplicate**:
a heading equal / prefix / token-Jaccard≥0.7 of a section already seen is a
running head, not a new section.

## 3. Snap headings to the CONTENTS
OCR garbles section titles (`"Disires"` for `"Desires"`). The book always prints a
CONTENTS page — parse it once, then snap each detected heading to the closest
canonical title (exact → prefix → token-Jaccard ≥ 0.7). This both fixes typos and
prevents two spellings of one chapter becoming two sections.
Watch out: the CONTENTS lists `"Preface  2"` as its first entry — don't let that
trip your "stop at PREFACE" guard before you have collected titles.

## 4. The rubric grammar (repertories)
A rubric is `symptom text : remedy, remedy.` — but the separator and the remedy
list both wander across lines:

```
Acetabulum to knee, shooting pains from, worse moving about:   <- ':' with NO remedy
                                                               <- blank
Natrum ars.                                                    <- remedy on next line
                                                               <- blank
Ache, in sacro-ischiatic foramen sharply defined, with tenderness  <- rubric text wraps
                                                               <- blank
on pressure : Podophyllum.                                     <- text continues, then ':'
```

So you need an explicit **`expect_remedies`** state: after a `:` whose right side
is empty or ends with `,` or `-`, the following line(s) are remedies until a line
that does not look like a remedy. A line with no separator while `expect_remedies`
is false starts a new rubric (flush the current one).

Other separators seen in the wild: `;` sometimes replaces `:`
(`"feel as if ; Ammonium mur., Psorinum."`) — accept `;` only when the right side
parses as remedies.

## 4b. Separator variants — the remedy list is not always after a colon
Some repertories put the remedy list AFTER the rubric text with no colon:

```
Sweat of the Feet, Constant. Sil., Thu.
- Morning. Euphm., Sul.
- , in bed. Bry., Lach., Merc-sol.
```

(Drake's Repertory of Foot-sweat.) Use `--trailing`: find the last `'. '` whose
remainder parses fully as remedies (`split_trailing_remedies`). Sub-entries start
with `'-'`; keep the verbatim fragment in `text` and the heading it refines in a
`parent` field, so the verbatim gate stays honest. Do NOT create a 'General'
section for lines before the first chapter — that is how preface prose gets
mistaken for rubrics.

## 4c. Kent's Repertory — known hard case (BLOCKED)
`kent.txt` looks like the colon grammar but is not parseable with the current
heuristics: remedy abbreviations are **lower-case** (`agar. alum. nux-v.`), remedy
lists **wrap across lines**, and the OCR **drops many colons**, so continuation
lines become bare remedy fragments. A first attempt reached only ~62 % verbatim
(54,883 rubrics) and was discarded. Fixing it needs a pass that (a) recognises
lower-case remedy tokens, (b) tracks the current rubric heading across wrapped
remedy lists, and (c) treats a line of only remedy tokens as a continuation, not
a new rubric. Also note: Kent's chapter headings are not reliably present as
standalone lines, so chapter segmentation is partial.

## 5. Cross-references
Repertories carry `(See "Bound." or "Bandaged.")` cross-refs. They may be glued to
the remedy list on the same line, or on their own line. Strip `\\(See.*$` from the
remedy side before parsing, and skip standalone `(See …)` lines so they don't
become rubric text.

## 6. Missing separators → the recovery pass
When OCR drops the `:`, a remedy name sits **inline** in the rubric text:
`"…tearing pains. Chamomilla. pains from right knee…"`. After the first pass,
build a remedy vocabulary from every token parsed so far, then split each rubric
text at embedded vocabulary tokens: text before the token belongs to a rubric whose
remedy is that token; text after starts the next rubric. This took embedded-leak
rate from ~9 % to 0 % on the Hering repertory. Guard against false positives: only
split on tokens that are in the vocabulary.

## 7. Remedy lists that break mid-word
`"…Podophyllum, Ru-"` / `"mex, Sabadilla."` — if a blank line sits between, the
hyphen-rejoin misses it. Residual; accept and record, or extend the rejoin to look
past a single blank line.

## 8. Honest metrics
Report, in the QC file: rubrics parsed, unique remedy tokens, alias-resolution rate,
and the **verbatim rate** (share of rubric texts found in the source after
normalisation). 92 % verbatim on a 400-page OCR'd repertory is a good result; do
not chase 100 % by editing text by hand — that is fabrication.

## 9. The remaining sources — what each needs (2026-10-14)

These were probed and are NOT yet cleanly parseable. Notes for the next pass:

- **bell.txt** (Bell, *Homoeopathic Therapeutics*, 1906) — DONE (session 8) via
  the `--bell` mode: numbered `N. REMEDY.` headings, labelled groups
  (`Stools:`/`Aggravation:`/`Before Stool:` …) with `;`/`:`-separated items.
  Caveat: the remedy NAMES are severely OCR-mangled and mostly unrecoverable
  (fuzzy matching resolved only 22/103). The `enrich_canonical_names` helper adds
  a best-effort `canonical_name`; the verbatim name is always kept. Do not assert
  a canonical below ~0.7 similarity.
- **Ruoff's repertory** (1840) — condition heading (mixed case, e.g. `Abortus
  molimina. Threatened abortion.`), then `Remedy — clinical note` entries whose
  notes wrap. A `--ruoff` mode exists but the condition/note boundary is ambiguous
  and output is scrambled; it needs a stronger heading rule (Latin+gloss pairs).
- **shantee.txt** (Santee, *Repertory of Convulsions*, 1890) — `symptom text,
  Remedy list.` with a COMMA separator and capitalised remedies. Adding a comma cut
  to `split_trailing_remedies` works for Shantee but over-splits Drake/Humphreys, so
  it must be gated behind a flag, and continuation fragments (`","`, `"small"`)
  still need folding.
- **hunting.txt / sherril.txt** (Sherrill, *A Repertory for Prescribing*, 1854) —
  `rubric — remedy1. remedy2.` with SPACE-separated remedies (multi-word names like
  `Nux V.` make the split ambiguous). Sections are OCR-garbled running heads
  (`Hom Eopathio Pbactice`) and cannot be dropped by frequency (each variant is
  unique). Needs a space-separated remedy parser and a running-head heuristic.
- **jahr 1.txt** (Jahr *Manual* Part II) — chapter/section headings, condition
  headings, and `label: remedy list` blocks with clinical remarks; a hybrid.
- **hering mind rep.txt** (Hering, *Analytical Repertory*, 1881) — attempted, NOT
  shipped. It is a large general repertory (not just the mind) whose body uses the
  colon grammar (`rubric text: Remedy.`), but the file also carries a long dotted
  TOC, a prose introduction, and mixed heading styles, and the body fragments badly
  (31% empty rubrics, 37% <=2 words) because remedy lists and rubrics wrap across
  lines. General helpers added while trying it: drop TOC dotted-leader lines in
  cleanup; `--caps-any` (any short ALL-CAPS line is a chapter); `--skip-to-rubric`
  (ignore front matter); `--min-rubrics N`. It still needs a dedicated pass like
  Bell's.

Lesson: for these, decide the exact separator and heading rule from a raw sample
first, then write a dedicated mode — do not force an existing mode and ship the
scrambled result.
