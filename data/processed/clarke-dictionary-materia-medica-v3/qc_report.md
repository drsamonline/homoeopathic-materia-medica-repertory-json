# QC — Clarke, A Dictionary of Practical Materia Medica, Vol. III (P–Z)

| | |
|---|---|
| Source | `clarke-dictionary-materia-medica-v3` — the DjVu XML of the DLI scan |
| Remedies | 268 |
| Words | 473,969 |
| Licence of the TEXT | Public domain — Clarke died 1931 |

## This replaces an earlier partial

An earlier volume in this library, `clarke-dictionary-materia-medica-v2`, carried P–Z from
the same DLI scan but parsed from its plain OCR text: 192 remedies and 3,226 symptoms, with
coverage flagged unverified. This is the same book parsed from the same scan's **DjVu XML**,
where every word carries a bounding box, so headings are found by height instead of spelling
— 268 remedies and 473,969 words. The older partial has been retired from the catalogue and
its file removed; git history keeps it.

## A format difference worth recording

This scan's XML uses a **five-value** word coordinate (`x1,y1,x2,y2,baseline`) where the
Google scans use four (`x1,y1,x2,y2`). Height is `y1−y2` in the first form and `y2−y1` in the
second. A parser written only for the four-value form reads zero headings on this file and
returns an empty book without error — which is exactly what happened on the first attempt.

## Known limitations

- **Volume III only (P–Z).** Volumes I and II are separate scans, both in this library.
- **OCR damage in names** carried through.
- **No corroboration** beyond the scan itself.
