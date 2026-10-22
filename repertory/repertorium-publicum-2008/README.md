# Repertorium Publicum (2008)

An open, **Kent-derived** repertory — complete and graded — as distributed with the
[OpenRep](https://github.com/nondeterministic/oorep) source code and published in the
OOReP database under the repertory token `publicum`.

**It is not Kent's 1897 first edition.** It has its own chapter structure (41 chapters,
including *Clinical*, *Appetite*, *Blood* and *Heart & Circulation*, which are not
separate chapters in Kent) and its own additions.

| | |
|---|---|
| Rubrics | **74,480** |
| Remedy links | **735,460** |
| Remedies | **669** |
| Chapters | **41** |

## Grades

`remedies[].grade` is an integer **1–3** and is populated for every link
(1 → 465,287 · 2 → 198,591 · 3 → 71,582). This is the field the Kent 1897 extraction in
this repo could not provide.

## Files

`index.json` holds the book record, the section index and the `remedy_index`
(abbrev → canonical name). One file per chapter; `extremities` is split into parts
because of size.

## Licence

**GPL v3**, as part of the OpenRep source code — *not* public domain. Reuse of this
data must comply with the GPL. The Kent 1897 material elsewhere in this repository is
public domain; this dataset is not.
