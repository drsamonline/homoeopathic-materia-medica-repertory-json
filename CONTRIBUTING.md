# Contributing

Thank you for helping improve this data set. **Corrections are genuinely
welcome** — the goal is accuracy.

This repository is a compilation of public-domain texts. The most valuable
contributions are **corrections that make the data match the original books more
faithfully**.

---

## Ways to contribute

### 1. Report a discrepancy (easiest)

Open an **issue** with:

- **Book** — e.g. `kent-repertory-1897`
- **Location** — chapter / rubric text, or the JSON path and an approximate line
- **Current value** — what the JSON says
- **Correct value** — what the source actually says
- **Evidence** — a page reference, or a scan/screenshot, or a link to the source

Please quote the source where you can. "I think this is wrong" is hard to act
on; "page 412 reads *…*, the JSON has *…*" is easy.

### 2. Fix it yourself (pull request)

1. Fork the repository.
2. Edit the JSON file(s) — keep them **compact JSON** (no indentation).
3. Make sure the file still parses:
   ```bash
   python3 -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8'))" repertory/your-book.json
   ```
4. Open a pull request describing the book, the change, and the evidence.

---

## Rules of the data

These are non-negotiable, because the value of the set is its honesty:

1. **Verbatim.** Every `text` string is copied from the source — never
   paraphrased, modernised, or "improved". OCR artefacts that change the meaning
   should be fixed; spelling of the era stays.
2. **No invention.** If a value is unknown, it is `null`. Never guess a remedy
   name, a grade, or an author. `grade` is an integer only if the source prints
   one.
3. **Remedy names.** `abbrev` is the token exactly as printed. `name` is a
   canonical resolution — only set it when you are confident, otherwise leave it
   `null`.
4. **Schema.** Follow [`SCHEMA.md`](SCHEMA.md). Do not add fields without
   discussing them in an issue first.

---

## Adding a new book

New books are welcome if they are **public domain** (published before 1929).

1. Add the JSON under `repertory/` or `materia_medica/`.
2. Fill the `book` block completely: `title`, `author`, `year`, `source_file`.
3. Add the author to [`CREDITS.md`](CREDITS.md) — **book authors must be
   credited.**
4. State the verbatim-fidelity rate in your pull request.

Large books may be split into parts (see the README) because of the per-file
upload limit.

---

## Credits

By contributing you agree that your contribution is released under the same
[CC0 1.0](LICENSE) public-domain dedication, and that the book authors and the
compiler are credited as described in [CREDITS.md](CREDITS.md).
