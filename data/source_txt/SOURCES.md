# Source texts

The OCR text each book was built from. They are not stored in this repository
(the largest is 8.7 MB, and every one is a public-domain scan already available
from the Internet Archive or the National Library of Medicine), so this file
records what each book's `book.source_file` points at, with a SHA-256 prefix so
a rebuild can be checked against the same input.

| file | bytes | sha256 (first 16) | book |
|---|---|---|---|
| `BRYANT.TXT` | 870,956 | `22904f2b2bed3eba` | Bryant, Pocket Manual (1851) |
| `FEVER.TXT` | 114,669 | `f0f86298977925ba` | Allen, Intermittent Fever (1883) |
| `GENTRY.TXT` | 3,363,024 | `5723e3f4f19a9f13` | Gentry, Concordance vol. I (1893) |
| `HERING.TXT` | 8,655,056 | `7c82b31160289022` | Knerr, Repertory to Hering's Guiding Symptoms (1896) |
| `HERING_CND.TXT` | 794,875 | `184a22672d0616f6` | Repertory to Hering's Condensed Materia Medica (1889) |
| `TPB.TXT` | 1,401,304 | `80f8c9064365d71a` | Boenninghausen, Therapeutic Pocket Book (1891) |

Sources for books extracted in earlier sessions (`kent-diff.txt`,
`clarke`, `lippe`, `pulford`, `vilas`, `humphreys`, `jahr`, `drake`,
`sensation-as-if`) are named in each book's `book.source_file`; those texts were
not part of this audit and are not checksummed here.

Sources received but not yet extracted are listed in
`data/processed/NEW_SOURCES_STATUS.md`.
