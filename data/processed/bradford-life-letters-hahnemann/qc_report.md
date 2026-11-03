# QC — The Life and Letters of Dr. Samuel Hahnemann

| | |
|---|---|
| Source | `bradford-life-letters-hahnemann` — the digital text layer of the scan (542 pages) |
| Chapters | 70 |
| Words | 192,792 |
| Licence of the TEXT | Public domain — "Copyrighted, 1894, by Boericke & Tafel"; Bradford died in 1918 |

## Structure

A chaptered biography, carried as a `treatise` whose sections have a `title` instead of a
paragraph number.

Chapter starts are read from the **body**, not from the OCR'd table of contents: each
chapter opens with `CHAPTER <roman>.` followed by its title in capitals, which gives the
exact page. The contents block in this scan is badly OCR'd ("IvXVI", "lyXXVII") and only
parsed 70 of the chapters, so it is used as a cross-check rather than as the source.

Printed page numbers run 20 behind the PDF pages; that offset was verified on 185 of 189
pages by reading the running head.

## Normalisation

- runs of spaces collapsed; a word broken by a line-end hyphen rejoined;
- running heads (`22 LIFE OF HAHNEMANN.`) and bare page numbers dropped.

The chapter heading the page prints — `CHAPTER I. MEISSEN, THE CAPlTAIv OF MISNIA.` — is
**kept** in the body. An earlier pass tried to strip it, and the OCR damages those
headings badly enough ("CAPlTAIv") that the strip sometimes ate the chapter's opening
sentence instead. Keeping the printed heading is the honest trade: a reader sees the
chapter open twice, rather than losing a paragraph of Bradford.

Nothing was summarised or reworded.

## Known limitations

- **No second source.** One scan of this printing is used, so there is nothing to
  corroborate the text against. The claim is that this is what the scan says.
- **OCR damage carried through**, including damaged chapter titles (`CAPlTAIv` for
  CAPITAL). Titles are title-cased for display but their words are not corrected.
- Chapter numbering is the book's own roman numerals as read; a numeral too damaged to
  read means that chapter merges into the one before it rather than being invented.
