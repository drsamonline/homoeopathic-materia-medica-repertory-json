<div align="center">

# 🏛️ Homoeopathic Materia Medica & Repertory — JSON

**Open-domain classical homoeopathy, compiled into clean, app-ready JSON.**

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](LICENSE)
[![Books](https://img.shields.io/badge/books-13-blue.svg)](#-the-library)
[![Rubrics](https://img.shields.io/badge/rubrics-~108k-green.svg)](#-the-library)
[![Format](https://img.shields.io/badge/format-JSON-orange.svg)](#-schema)

*Free to use. Credit the book authors and the JSON compiler. Corrections welcome.*

</div>

---

## ✨ What this is

A curated collection of **13 public-domain homoeopathic Materia Medica and
Repertory classics** (1840–1906), extracted from their scanned page images into
**structured JSON** ready for apps, search tools, study aids and AI projects.

Each remedy and rubric string is kept **verbatim** from the source — nothing is
invented, paraphrased or filled in. Where a field is unknown it is `null`, never a
guess. Extraction quality is reported per book so you know exactly what you are
working with.

> **Compiled by Dr Sohil Momin.** See [CREDITS.md](CREDITS.md) — the authors of
> every source text are acknowledged there and **must be credited wherever this
> data is used.**

---

## 📚 The Library

### Repertories

| Book | Author | Year | Rubrics | Verbatim |
|---|---|---:|---:|---:|
| [Kent's Repertory](repertory/kent-repertory-1897.json) | James Tyler Kent | 1897 | 59,114 | 94.1% |
| [Clarke's Clinical Repertory](repertory/clarke-clinical-1900.json) | John Henry Clarke | 1900 | 12,537 | 100% |
| [Hering's Repertory](repertory/hering-repertory-1889.json) | Hom. Med. Soc. of Pennsylvania | 1889 | 11,156 | 93.7% |
| [Bryant's Pocket Repertory](repertory/bryant-pocket-1900.json) | J. Bryant | 1900 | 8,892 | 90.2% |
| [Pulford — Rheumatism & Sciatica](repertory/pulford-rheumatism-1898.json) | Alfred Pulford | 1898 | 7,518 | 92.6% |
| [Sensation-as-if](repertory/sensation-as-if-1890.json) | A. W. Holcomb | 1890 | 2,721 | 100% |
| [Vilas — Eye & Ear](repertory/vilas-eye-ear-1890.json) | O. H. Vilas | 1890 | 2,465 | 80.3% |
| [Humphreys — Sexual System](repertory/humphreys-sexual-1860.json) | F. Humphreys | 1860 | 1,280 | 100% |
| [Jahr — Symptomatology](repertory/jahr-repertory-1847.json) | G. H. G. Jahr | 1847 | 587 | 100% |
| [Lippe's Repertory](repertory/lippe-repertory-1879.json) | Constantine Lippe | 1879 | 452 | 88.7% |
| [Drake — Foot-sweat](repertory/drake-foot-sweat-1894.json) | Olin M. Drake | 1894 | 84 | 100% |

### Materia Medica

| Book | Author | Year | Content | Verbatim |
|---|---|---:|---|---:|
| [Jahr's Manual, Part I](materia_medica/jahr-materia-medica-1847.json) | G. H. G. Jahr | 1847 | 199 remedies / 26,734 symptoms | 98.7% |
| [Bell's Therapeutics](materia_medica/bell-therapeutics-1906.json) | James B. Bell | 1906 | 103 remedies / 5,547 symptoms | 97.2% |

> **Kent is provided split by chapter** in [`repertory/kent-1897/`](repertory/kent-1897/)
> — 34 chapter files + `index.json` — so it loads one chapter at a time. (Its single
> 21 MB file and a couple of other large files exceed GitHub's per-file upload limit
> here, so they are shipped as parts: `extremities.json` + `extremities-2.json`, and
> `jahr-materia-medica-1847.json` + `jahr-materia-medica-1847-2.json`. Concatenate
> the parts. The complete single-file JSON for every book ships in the source
> library bundle.)

---

## 🗂️ Repository layout

```
.
├── repertory/            # Repertory books (rubric -> remedies)
│   ├── kent-1897/        # Kent, split into 34 chapters + index.json
│   ├── clarke-clinical-1900.json
│   └── ... (9 more)
├── materia_medica/       # Materia Medica books (remedy -> symptoms)
│   ├── jahr-materia-medica-1847.json   (+ -2.json, part 2)
│   └── bell-therapeutics-1906.json
├── pipeline/             # omm_pipeline.py + remedy lists (reproduce the data)
├── skill/omm-json-builder/   # the extraction skill (SKILL.md + references)
├── SCHEMA.md             # Field-by-field data model
├── CREDITS.md            # Book authors + compiler (please credit)
├── CONTRIBUTING.md       # How to report a discrepancy or send a fix
└── LICENSE               # CC0 1.0 — public domain dedication
```

---

## 🧩 Schema

Two shapes, both self-describing via `"type"`.

**Repertory** — `repertory/*.json`
```json
{
  "type": "repertory",
  "book": { "title": "...", "author": "...", "year": 1897, "source_file": "..." },
  "sections": [
    {
      "title": "Mind",
      "rubrics": [
        {
          "text": "Fear of death",
          "parent": null,
          "remedies": [
            { "abbrev": "Acon", "grade": null, "polarity": "+", "name": "Aconitum napellus" }
          ]
        }
      ]
    }
  ],
  "remedy_index": { "Acon": { "name": "Aconitum napellus", "resolved": true } }
}
```

**Materia Medica** — `materia_medica/*.json`
```json
{
  "type": "materia_medica",
  "book": { "title": "...", "author": "...", "year": 1847 },
  "remedies": [
    {
      "name": "Aconitum Napellus",
      "symptoms": [ { "chapter": "Mind", "text": "Anxiety, with fear of death" } ]
    }
  ]
}
```

See **[SCHEMA.md](SCHEMA.md)** for every field and its rules.

---

## 🚀 Quick start

```python
import json

rep = json.load(open("repertory/kent-repertory-1897.json", encoding="utf-8"))

# every rubric mentioning a remedy, across all chapters
for sec in rep["sections"]:
    for r in sec["rubrics"]:
        if any(x["abbrev"] == "Acon" for x in r["remedies"]):
            print(sec["title"], ">", r["text"])
```

```javascript
// In a browser / Node app
const rep = await fetch("repertory/kent-repertory-1897.json").then(r => r.json());
const stomach = rep.sections.find(s => s.title === "Stomach");
console.log(stomach.rubrics.length, "stomach rubrics");
```

**Files are compact JSON** (no indentation) — ~40% smaller than pretty-printed,
and they parse identically. Perfect for shipping inside an app.

---

## ⚠️ Data quality — read this

This is **honest, verbatim OCR data**, not hand-verified text.

- Every rubric/symptom string is **verbatim** from the source scan; the per-book
  *Verbatim* column above is the share of strings found character-for-character in
  the source.
- Some books carry **OCR fragments and garbled remedy abbreviations** (notably
  Vilas, Lippe, Clarke, Pulford, Bryant). The rubrics are real; a few remedy
  tokens are damaged. **Verify against the original text before clinical use.**
- **Bell's** remedy names are OCR-mangled (partly auto-resolved).
- Books not included because they did not parse cleanly: Hale (*New Remedies*),
  King (*American Dispensatory*), Sherrill, Ruoff, Hering's *Analytical
  Repertory*. They may be added as parsers improve.

> ⚕️ **Not medical advice.** These are historical texts for study and software.
> Always consult a qualified practitioner.

---

## 🔧 Reproducing the data

The extraction is fully reproducible. [`pipeline/omm_pipeline.py`](pipeline/omm_pipeline.py)
is the tool that produced every file here — it classifies a source text, applies
the right grammar parser, validates the output and reports a verbatim-fidelity
rate.

```bash
python3 pipeline/omm_pipeline.py extract-repertory \
  --src data/source_txt/kent-diff.txt --slug kent-repertory-1897 \
  --title "Repertory of the Homoeopathic Materia Medica" \
  --author "James Tyler Kent" --year 1897 \
  --out repertory/kent-repertory-1897.json --qc qc.md --caps-chapters
```

[`skill/omm-json-builder/`](skill/omm-json-builder/) packages this as an agent
**skill** (instructions + references + scripts) so the same pipeline can be
driven end-to-end. See [`pipeline/`](pipeline/) for the remedy alias and master
lists.

---

## 🤝 Contributing & corrections

Found a discrepancy, a bad OCR token, or a wrong remedy mapping? **Please fix it.**

- Open an **issue** describing the book, the rubric, and the correct reading.
- Or open a **pull request** with the correction.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for how to report a discrepancy, the
rules of the data (verbatim, no invention), and how to add a new book.
Corrections are genuinely welcome — the goal is accuracy.

---

## 📜 License & credits

- **Data:** [CC0 1.0 Universal](LICENSE) — public domain dedication. Free to use,
  modify and redistribute, including commercially.
- **Source texts:** all published before 1929 and in the public domain.
- **Please credit:** the **authors of each book** and the **JSON compiler
  (Dr Sohil Momin)** wherever this data is used. See [CREDITS.md](CREDITS.md).

<div align="center"><sub>Built with the <b>omm-json-builder</b> pipeline.</sub></div>
