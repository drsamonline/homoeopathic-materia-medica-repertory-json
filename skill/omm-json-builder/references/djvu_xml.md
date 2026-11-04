# The DjVu XML method

When OCR text gives you headings like `BTMPTOMS` and `STHPTOHS`, the text is not the
problem — the *spelling* is. DjVu XML carries a bounding box for every word, so a
heading can be found by **geometry**: it is set larger than the body around it.

This is how three volumes of Clarke's *Dictionary* were recovered after the plain text
of the same scans had defeated three attempts.

## Get the right file

```
https://archive.org/download/<identifier>/<identifier>_djvu.xml
```

Check `https://archive.org/metadata/<identifier>` first: some items are lending stock
and return **401** on the XML (the Wellcome volumes do), while their `_djvu.txt` may
still be readable. If the XML is refused, fall back to text and lower your ambitions.

## Two coordinate formats — the silent killer

Both appear in the wild, and a parser written for one reads **zero headings** on the
other and returns an empty book **without raising an error**.

```python
# four values:  x1,y1,x2,y2          -> height = y2 - y1  (or abs(y1 - y2))
# five values:  x1,y1,x2,y2,baseline -> height = y1 - y2
def heights(line):
    out = []
    for w in re.findall(r'coords="([\d,]+)"', line):
        p = [int(x) for x in w.split(",")]
        if len(p) == 5:   out.append(p[1] - p[3])
        elif len(p) == 4: out.append(abs(p[1] - p[3]))
    return out
```

Always assert a non-zero heading count before continuing. An empty result is a bug,
not a book with no chapters.

Watch the `<WORD>` tag too: some scans add attributes (`<WORD coords="…" x-confidence="20">`),
so match `<WORD coords="([\d,]+)"[^>]*>(.*?)</WORD>` rather than `<WORD coords="…">`.

## Finding headings by height

```python
lines = parse_page(chunk)                 # [(x, height, text), …]
med = statistics.median(h for _, h, _ in lines)
if h > med * 1.6 and re.fullmatch(r"[A-Z][A-Za-z'’\-\. ]{2,32}\.?", t):
    start_new_section(t)
```

- Compute the median **per page**, not for the whole book: scans differ in scale from
  page to page, and a global median starts calling body text a heading.
- `1.6×` is a good starting threshold. Check the density: headings should be roughly
  **1 % of lines**. At 1.45× and 1.8× the same book gave 1.1 % and 1.0 % — stable. If
  your threshold yields 10 %, you are cutting paragraphs in half.
- On a real Clarke page body text sits at 56–65 and `Brucinum.` at 116.

## Carry the open section across pages

The bug that produced a plausible-looking but crippled book: resetting the current
section at every page boundary, so **every line before the first heading on a page was
discarded**. That recovered 96,000 of a volume's 485,000 words while still reporting
435 remedies.

Keep `cur` outside the page loop. Sanity-check the result against the source's own
size: if a 500,000-word book yields 100,000, you have this bug.

## Two-column pages

Find the gutter from the x distribution rather than assuming a fixed one:

```python
xs = sorted(x for x, _, _ in lines)
gutter = xs[len(xs) // 2]
ordered = [t for _, _, t in [l for l in lines if l[0] <  gutter]] + \
          [t for _, _, t in [l for l in lines if l[0] >= gutter]]
```

Read the left column top-to-bottom, then the right. Without this, a two-column
repertory interleaves its columns and the rubrics are nonsense.

## Merging running heads

A remedy's name repeats as a running head on each of its pages, so the *first*
occurrence is the real heading. Collect first occurrences only, and merge later
repeats back by name similarity (≥ 0.93 on letters is a safe start).

Do not merge too eagerly: `Zincum cyanatum` and `Zincum muriaticum` are different
remedies. Require similarity **and** a length difference of two characters at most.

## Remedy abbreviations

Repertory citations drop vowels: `Magn. mur.` → Magnesia muriatica, `Eupator. perf.`
→ Eupatorium perfoliatum, `Natr. carb.` → Natrum carbonicum. Spelling similarity gets
`Natr. carb.` wrong (it lands on Natrum muriaticum, the more frequent remedy).

Match **word by word**:

```python
first, second = words(citation)[:2]          # normalised to letters
for cand in index[first[:3]]:
    cf, cs = words(display[cand])[:2]
    if not cf.startswith(first[:4]):         # first word is a prefix
        continue
    if second and not cs.startswith(second[:3]):
        continue
```

Verify against a hand-checked list before trusting it — that is how the wrong
`Natr. carb.` mapping was caught.

## Grades

Kent and the classical repertories print grades as **superscripts**: smaller and
raised. The XML carries what you need to find them — a digit word with height ~26
against body ~36.

But check feasibility before promising it. On a Kent 1897 scan, **64 grade digits
survived in an 8 MB slice** where the volume needs hundreds of thousands; the
superscripts were simply lost to OCR. Knerr's scan fuses the grade into the name
(`IMerc;`, `INatr.`). Worcester prints none at all.

If grades cannot be read, write `grade: null` and say so in the QC. An ungraded
repertory that admits it is useful; one that implies grades is not.

## What to record in the QC

- the medium and identifier used, and why others were rejected;
- the threshold and the heading density it produced;
- any bug found during the build, with the before/after counts;
- coverage: how many rubrics/sections resolved, as a fraction and a percentage;
- whether grades are present, null by design, or lost.
