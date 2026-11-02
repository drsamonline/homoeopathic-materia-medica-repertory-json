#!/usr/bin/env python3
"""Book-specific grammars for repertories the generic omm_pipeline modes cannot
parse.

Why this file exists
--------------------
`omm_pipeline.py` handles the ':' + comma-separated remedy grammar (Hering 1889,
Jahr, Clarke) and the trailing '. ' grammar (Drake). The 1883-1896 sources added
in session 2026-11-02 print their remedy lists differently:

  * Allen, Intermittent Fever (1883)   -- 'Text: Rem. Rem. Rem.'  space-separated,
                                          lists wrap; ', sub-text:' refines.
  * Bryant, Pocket Manual (1851)       -- 'Heading: rem. rem. rem.'  lower-case
                                          Kent-style abbreviations, '--' sub-entries.
  * Gentry, Concordance (1893)         -- 'Word. -- text  Rem. Rem.'  remedy run
                                          trails the entry, space-separated.
  * Knerr, Repertory to Hering (1896)  -- 'Abdomen, aching: entry; entry; ...'
                                          entries separated by ';', each ending in
                                          grade-marked remedies (I / II).

Forcing those through the generic parser scrambles them, so each book gets a
dedicated grammar here. Nothing is invented: every rubric string is a slice of
the source after light OCR cleanup, and every remedy token is a token of the
source. A token that cannot be matched to the shared remedy tables keeps no name
(the schema's "unresolved token" state).

Usage
-----
  python3 pipeline/omm_extract_extra.py fever  --src ... --out ... --qc ...
  python3 pipeline/omm_extract_extra.py bryant --src ... --out ... --qc ...
  python3 pipeline/omm_extract_extra.py gentry --src ... --out ... --qc ...
  python3 pipeline/omm_extract_extra.py knerr  --src ... --out ... --qc ...
"""

import argparse
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import omm_pipeline as P  # noqa: E402


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #

MARK = re.compile(r"^[I1li|!\[\]{}()%^&*_~\\/<>=+\u2022\u00b0\u00a7\u00b6\u201c\u201d\u25a0]+")

ENGLISH_STOP = set("""
a an the and or but if of to in on at by for with from into over under as is are was were be
been being it its his her their them they he she we you this that these those there here when
then than so not no nor also see compare same both all any each other such very more most
less least only just even still yet once again about above after against before below between
during through until while without within upon toward towards like near off out up down away
back can could may might must shall should will would do does did done have has had
one two three four five six times day night morning evening afternoon week month year hours
hour minutes left right side sides upper lower middle part parts whole general symptom
symptoms sensation sensations pain pains case cases form forms state states patient patients
heat wanting location mercurial chill chilliness sweat sweating fever apyrexia
general during times time want wants desire desires longing longing-for
""".split())


def clean_line(s):
    s = P.fix_ligatures(s)
    s = re.sub(r"[\u00ac\u00ad\u2010\u2011]", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def tok_key(t):
    """Matching key for a printed remedy token: lower-case, marks/punct gone."""
    t = MARK.sub("", (t or "").strip())
    t = re.sub(r"[.,;:'\"`^*\-_/]", "", t)
    return re.sub(r"\s+", "", t).lower()


def load_master(path):
    """abbrev-key -> canonical name, from remedy_master.csv + remedy_aliases.csv."""
    out = {}
    for p in path:
        if not p or not os.path.exists(p):
            continue
        with open(p, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                a = (row.get("abbrev") or "").strip()
                n = (row.get("name") or "").strip()
                if a and n:
                    out.setdefault(tok_key(a), n)
                    out.setdefault(tok_key(n), n)
                    out.setdefault(tok_key(n.split()[0]), n)
    return out


_PREFIX_CACHE = {}


def remedy_entry(abbrev, master, grade=None):
    if hasattr(master, "name_of"):
        return {"abbrev": abbrev, "grade": grade, "polarity": "+",
                "name": master.name_of(abbrev)}
    key = tok_key(abbrev)
    nm = master.get(key)
    if nm is None and len(key) >= 4:
        # unique prefix match, e.g. 'calc' -> Calcarea carbonica
        hits = {v for k, v in master.items() if k.startswith(key)}
        if len(hits) == 1:
            nm = hits.pop()
    return {"abbrev": abbrev, "grade": grade, "polarity": "+", "name": nm}


def is_running_head(s, words):
    if not s or not s.isupper():
        return False
    if not any(w in s for w in words):
        return False
    return bool(re.match(r"^\d{1,4}\b", s) or re.search(r"\b\d{1,4}$", s))


def strip_page_no(s):
    return re.sub(r"^\s*\d{1,4}\s+|\s+\d{1,4}\s*$", "", s)


# --------------------------------------------------------------------------- #
# Allen -- Repertory to the Symptoms of Intermittent Fever (1883)
# --------------------------------------------------------------------------- #

FEVER_TOKEN = re.compile(r"[A-Z][A-Za-z'\u2019]{0,10}\.?(?:\s+[a-z]{1,6}\.?)?")


def fever_tokenize(run):
    """Split a remedy run into tokens, keeping each verbatim as printed."""
    toks, i = [], 0
    while i < len(run):
        m = FEVER_TOKEN.match(run, i)
        if not m:
            i += 1
            continue
        t = m.group(0).strip()
        if t:
            toks.append(t)
        i = m.end()
        while i < len(run) and run[i] in " ,;.":
            i += 1
    return toks


def fever_plausible(tok):
    t = tok.strip().rstrip(".")
    if not t or len(t) > 14:
        return False
    if t.split()[0].lower() in ENGLISH_STOP:
        return False
    if " " not in t and not tok.strip().endswith("."):
        return False
    return True


def fever_lines(src, words):
    raw = P.read_lines(src)
    start = 0
    for i, l in enumerate(raw):
        if re.match(r"^\s*APYREXIA, SYMPTOMS DURING", clean_line(l), re.I):
            start = i
            break
    out = []
    for l in raw[start:]:
        c = clean_line(l)
        if not c or re.fullmatch(r"\d{1,4}", c):
            continue
        if is_running_head(c, words):
            continue
        out.append(c)
    return out, raw


SINGLE_HEADINGS = {"chill", "heat", "sweat", "apyrexia", "pyrexia", "fever",
                   "mind", "head", "stomach", "sleep", "skin"}

SMALL_WORDS = {"of", "to", "the", "and", "from", "with", "for", "in", "on", "by",
               "a", "an", "or", "as", "at", "into", "during"}


def heading_title(s):
    """Title-case an ALL-CAPS heading without truncating it."""
    s = strip_page_no(s).strip().rstrip(".,;:")
    s = re.sub(r"[^A-Za-z' ]+", " ", s)
    words = [w for w in s.split() if w]
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i and lw in SMALL_WORDS:
            out.append(lw)
        else:
            out.append(lw.capitalize())
    return " ".join(out)


def caps_heading(line, keywords):
    """An ALL-CAPS chapter/running-head line, or None."""
    s = strip_page_no(line).strip()
    if not s or not s.isupper():
        return None
    if not re.search(r"[A-Z]{3}", s):
        return None
    words = s.split()
    if not (1 <= len(words) <= 8):
        return None
    if len(words) == 1 and s.rstrip(".").lower() not in SINGLE_HEADINGS:
        return None
    if not any(k in s for k in keywords):
        return None
    return heading_title(s)


def chapter_titles(lines, keywords, min_hits=3):
    """Canonical chapters = the ALL-CAPS headings that recur (running heads).
    OCR fragments of a heading occur once and are snapped onto these later."""
    counts, order = collections.Counter(), {}
    for i, l in enumerate(lines):
        t = caps_heading(l, keywords)
        if t:
            counts[t] += 1
            order.setdefault(t, i)
    canon = [t for t, n in counts.items() if n >= min_hits]
    return sorted(canon, key=lambda t: order[t])


def fever_sections(lines, keywords):
    """Split the cleaned body into (heading, [lines]) blocks."""
    canon = chapter_titles(lines, keywords)
    blocks, cur = [], None
    for l in lines:
        t = caps_heading(l, keywords)
        if t:
            snapped = P.snap_to_contents(t, canon) if canon else t
            if len(t.split()) == 1:
                snapped = t                      # a bare 'CHILL.' chapter
            elif snapped == t and canon:
                # not a canonical chapter: an OCR fragment unless it is close
                import difflib
                best = max(canon, key=lambda c: difflib.SequenceMatcher(
                    None, t.lower(), c.lower()).ratio())
                if difflib.SequenceMatcher(None, t.lower(), best.lower()).ratio() < 0.7:
                    continue                     # running-head debris
                snapped = best
            if cur is None:
                same = False
            elif len(snapped.split()) == 1 or len(cur[0].split()) == 1:
                same = snapped == cur[0]        # bare 'HEAT.' never absorbs
            else:
                same = P.same_section(snapped, cur[0])
            if not same:
                cur = (snapped, [])
                blocks.append(cur)
            continue
        if cur is None:
            continue                       # front matter before the first chapter
        cur[1].append(l)
    return blocks, canon


def fever_records(block_lines):
    """Yield (text, remedy_run) records for one section block."""
    cur_text, cur_run = None, []
    for line in block_lines:
        m = re.match(r"^(.*?):\s*(.*)$", line)
        if m:
            if cur_text is not None:
                yield cur_text, " ".join(cur_run)
            cur_text, cur_run = m.group(1).strip(), [m.group(2).strip()]
        elif cur_text is None:
            cur_text, cur_run = "", [line]     # a bare remedy list under a heading
        else:
            cur_run.append(line)
    if cur_text is not None:
        yield cur_text, " ".join(cur_run)


def parse_fever(a):
    words = ("APYREXIA", "FEVER", "CHILL", "HEAT", "SWEAT", "INTERMITTENT",
             "SYMPTOMS", "REMEDIES", "SEASON", "PAROXYSM", "PYREXIA")
    lines, raw = fever_lines(a.src, words)
    blocks, canon = fever_sections(lines, words)

    # pass 1 -- vocabulary from repeated tail tokens
    counts = collections.Counter()
    for title, blines in blocks:
        for text, run in fever_records(blines):
            for t in fever_tokenize(run):
                if fever_plausible(t):
                    counts[tok_key(t)] += 1
    vocab = {k for k, n in counts.items() if n >= 3}

    master = load_master([a.master, a.aliases])
    sections, seen, n = [], set(), 0
    for title, blines in blocks:
        if not any(P.same_section(title, t) for t in seen):
            seen.add(title)
            sec = {"id": f"{a.slug}-s{len(sections)+1}", "title": title,
                   "rubrics": []}
            sections.append(sec)
        else:
            sec = [s for s in sections if P.same_section(title, s["title"])][0]
        parent = ""
        for text, run in fever_records(blines):
            toks = [t for t in fever_tokenize(run) if tok_key(t) in vocab]
            # a 'record' that is itself only remedy tokens is a wrapped remedy
            # list directly under the chapter heading: its text is the heading
            bare = fever_tokenize(text)
            if not text.strip():
                text = title                        # heading carries the list
            elif bare and all(tok_key(t) in vocab for t in bare):
                toks = [t for t in bare if tok_key(t) in vocab] + toks
                text = title
            if not text or not (toks or len(text) > 3):
                continue
            is_sub = bool(re.match(r"^[,;\u2014\u2013-]", text))
            n += 1
            rub = {"id": f"{a.slug}-r{n:05d}", "text": text, "parent": None,
                   "remedies": [remedy_entry(t, master) for t in toks]}
            if is_sub and parent:
                rub["parent"] = parent
            elif not is_sub:
                parent = re.sub(r"^[^A-Za-z]+", "", text).strip()
            sec["rubrics"].append(rub)
    return sections, raw, counts, vocab


def cmd_fever(a):
    sections, raw, counts, vocab = parse_fever(a)
    finish(a, sections, raw, notes={"tail tokens seen": len(counts),
                                    "accepted vocabulary": len(vocab)})


# --------------------------------------------------------------------------- #
# shared space-separated-remedy machinery (Bryant, Gentry)
# --------------------------------------------------------------------------- #

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'\-]{0,14}[.,]?")


def tail_remedies(text, vocab):
    """Take the run of remedy tokens at the END of `text` (space separated).

    Returns (leading_text, [tokens]) - the tokens keep their printed form.
    Walking right-to-left stops at the first token that is not in the vocabulary,
    so ordinary prose is never mistaken for a remedy list.
    """
    body = re.sub(r"\([^)]*\)", " ", text)          # drop parenthetical glosses
    toks = [(m.start(), m.group(0)) for m in TOKEN_RE.finditer(body)]
    keep = []
    cut = len(body)
    for pos, tok in reversed(toks):
        if vocab_has(vocab, tok):
            keep.append(tok)
            cut = pos
        else:
            break
    if not keep:
        return text.strip(), []
    lead = body[:cut].strip()
    lead = re.sub(r"[\s,;:.\u2014\u2013-]+$", "", lead).strip()
    return lead, list(reversed(keep))


def parse_printed_gentry(src):
    """The book's own LIST OF ABBREVIATIONS -> {key: canonical name}."""
    raw = P.read_lines(src)
    out = {}
    for l in raw[:1400]:
        c = re.sub(r"[ \t]+", " ", clean_line(l))
        m = re.match(r"^([A-Za-z][A-Za-z0-9\-']{1,12})[.,]? "
                     r"([A-Z][a-z][A-Za-z \-]{2,40})[.,]?$", c)
        if m:
            out.setdefault(tok_key(m.group(1)), m.group(2).strip())
    return out


def parse_printed_bryant(src):
    """Bryant prints 'N. Full name.' followed by the abbreviation on its own
    line -> pair them into {key: canonical name}."""
    raw = P.read_lines(src)
    out, pending = {}, None
    on = False
    for l in raw:
        c = clean_line(l)
        if re.search(r"ABDOMEN\.\s+Anguish", c):
            break
        if not on and not re.match(r"^ABBREVIATIONS", c, re.I):
            continue
        on = True
        m = re.match(r"^\d{1,3}\.\s+([A-Z][A-Za-z .\-]{2,40}?)\.?$", c)
        if m:
            pending = m.group(1).strip()
            continue
        if pending and re.fullmatch(r"[A-Z][A-Za-z\-]{0,10}\.?", c):
            out.setdefault(tok_key(c), pending)
            pending = None
    return out


def abbrev_shaped(tok):
    """True if a token looks like a printed remedy abbreviation rather than an
    English word or a cross-reference target."""
    t = tok.strip()
    core = t.rstrip(".,;:")
    if not core or len(core) > 12:
        return False
    if core.isupper():                     # cross-reference target (SEE: GLANDS.)
        return False
    if tok_key(core) in ENGLISH_STOP:
        return False
    if "-" in core or core.islower():
        return True
    return len(core) <= 7                  # 'Aeon.' 'Phos.' but not 'Flatulence'


class Resolver:
    """Printed-vocabulary resolver: exact key, then a single close OCR variant."""

    def __init__(self, printed, master, caps_only=False):
        self.caps_only = caps_only
        self.name = dict(master)
        self.name.update({k: v for k, v in printed.items() if v})
        self.keys = set(printed) | set(master)
        self._close = {}
        self._has = {}

    def has(self, tok):
        """Accept only an exact printed abbreviation that is also punctuated like
        one ('Stram.' 'Nux-v.' 'Aeon,'). No fuzzy acceptance: a fuzzy match on a
        short word turns 'alone' into 'Aloe'."""
        t = tok.strip()
        if not (t.endswith((".", ",")) or "-" in t):
            return False
        k = tok_key(t)
        if k in self.keys:
            return True
        # a punctuated token that is one OCR step from a printed abbreviation
        # ('earb-v.' for 'carb-v.') is still that remedy - but only when it is
        # punctuated like an abbreviation, so English words are never admitted
        core = t.rstrip(".,;:")
        if core.endswith("-"):
            return False            # an OCR line-break fragment, not an abbrev
        if self.caps_only and not (core[:1].isupper() or "-" in core):
            return False
        if not (t.endswith(".") or "-" in core):
            return False
        if len(core) > 8:
            return False
        if len(k) >= 4:
            if self.close(k) is not None:
                return True
            # a printed abbreviation the OCR cut short ('Agn' for 'Agnus')
            hits = [c for c in self.keys if c.startswith(k) and len(k) >= 4]
            if len(hits) == 1:
                return True
        return False

    def close(self, k):
        if k in self._close:
            return self._close[k]
        self._close[k] = self._close_of(k)
        return self._close[k]

    def _close_of(self, k):
        if len(k) < 4:
            return None
        import difflib
        best, score = None, 0.0
        for c in self.keys:
            if abs(len(c) - len(k)) > 3:
                continue
            r = difflib.SequenceMatcher(None, k, c).ratio()
            if r > score:
                best, score = c, r
        return best if score >= 0.72 else None

    def name_of(self, tok):
        k = tok_key(tok)
        if k in self.name:
            return self.name[k]
        c = self.close(k)
        return self.name.get(c) if c else None


def vocab_has(vocab, tok):
    if hasattr(vocab, "has"):
        return vocab.has(tok)
    return tok_key(tok) in vocab


def leading_remedies(text, vocab):
    """The contiguous run of remedy tokens at the START of `text` (a colon's
    right side). Stops at the first token that is not a printed abbreviation, so
    'Diagnosis: Dropsical swelling ...' yields nothing."""
    out = []
    for m in TOKEN_RE.finditer(re.sub(r"\([^)]*\)", " ", text)):
        tok = m.group(0)
        if abbrev_shaped(tok) and vocab_has(vocab, tok):
            out.append(tok)
        else:
            break
    return out


def remedy_runs(text, vocab):
    """Every maximal run of remedy tokens in `text`, with its character span.

    A run ends an entry: the prose before it is that entry's text. This splits
    the entries the OCR glued onto one line ('... a. of mind. Agn. Uneasiness ...')
    without inventing anything.
    """
    body = re.sub(r"\([^)]*\)", " ", text)
    runs, cur, start, last_end = [], [], None, None
    for m in TOKEN_RE.finditer(body):
        tok = m.group(0)
        between = body[last_end:m.start()] if last_end is not None else ""
        if abbrev_shaped(tok) and vocab_has(vocab, tok):
            if cur and not re.fullmatch(r"[\s,;.]*", between):
                runs.append((start, last_end, cur))
                cur, start = [], m.start()
            if not cur:
                start = m.start()
            cur.append(tok)
            last_end = m.end()
        elif cur and not re.fullmatch(r"[\s,;.]*", between):
            runs.append((start, last_end, cur))
            cur, start, last_end = [], None, None
    if cur:
        runs.append((start, last_end, cur))
    return runs


def space_vocab(lines, min_hits=3, extra=()):
    """Empirical remedy vocabulary: tokens that recur at the end of an entry."""
    counts = collections.Counter()
    for line in lines:
        body = re.sub(r"\([^)]*\)", " ", line)
        toks = [m.group(0) for m in TOKEN_RE.finditer(body)]
        for tok in reversed(toks):
            k = tok_key(tok)
            if not abbrev_shaped(tok) or len(k) < 2:
                break
            counts[k] += 1
        # only the first few from the end are trusted as 'remedy position'
    vocab = {k for k, n in counts.items() if n >= min_hits}
    return vocab, counts


# --------------------------------------------------------------------------- #
# Bryant -- Pocket Manual, Repertory of Homoeopathic Medicine (3rd ed., 1851)
# --------------------------------------------------------------------------- #

BRYANT_HEAD = re.compile(
    r"^(?:[A-Z0-9]{2,6}\s+|\d{1,3}\s+)?[A-Z][A-Za-z ,'\-]{3,40}\.\s*"
    r"(?:[A-Za-z0-9^]{0,5}|\d{0,4})\s*$")


def bryant_lines(src):
    raw = P.read_lines(src)
    start = 0
    for i, l in enumerate(raw):
        if re.search(r"ABDOMEN\.\s+Anguish", clean_line(l)):
            start = i
            break
    out = []
    for l in raw[start:]:
        c = clean_line(l)
        if not c:
            continue
        c = re.sub(r"^POCKET MANUAL\.\s*", "", c)
        if re.fullmatch(r"[\d*\W]{0,4}", c):
            continue
        if BRYANT_HEAD.match(c) and not ":" in c:
            continue
        out.append(c)
    return out, raw


def parse_bryant(a):
    lines, raw = bryant_lines(a.src)
    counts = collections.Counter()
    printed = parse_printed_bryant(a.src)
    res = Resolver(printed, load_master([a.master, a.aliases]))
    vocab = res

    sec = {"id": f"{a.slug}-s1", "title": "General", "rubrics": []}
    n, parent = 0, ""
    cur_text, cur_toks = None, []

    def flush():
        nonlocal cur_text, cur_toks, n, parent
        if cur_text is None:
            return
        txt = re.sub(r"\s+", " ", cur_text).strip(" .;:")
        if txt:
            is_sub = bool(re.match(r"^[\u2014\u2013-]", txt))
            frag = re.sub(r"^[\u2014\u2013-]+\s*", "", txt) if is_sub else txt
            n += 1
            rub = {"id": f"{a.slug}-r{n:05d}", "text": frag, "parent": None,
                   "remedies": [remedy_entry(t, res) for t in cur_toks]}
            if is_sub and parent:
                rub["parent"] = parent
            elif not is_sub:
                parent = frag
            sec["rubrics"].append(rub)
        cur_text, cur_toks = None, []

    for line in lines:
        m = re.match(r"^(.*?):\s*(.*)$", line)
        if m:
            flush()
            cur_text = m.group(1).strip()
            cur_toks = leading_remedies(m.group(2), vocab)
            continue
        if cur_text is None:
            continue
        all_toks = TOKEN_RE.findall(re.sub(r"\([^)]*\)", " ", line))
        toks = [t for t in all_toks if abbrev_shaped(t) and vocab_has(vocab, t)]
        if toks and len(toks) == len(all_toks):
            cur_toks.extend(toks)          # a wrapped remedy list
        # else: prose (the nosological part's Diagnosis paragraphs) -> ignored
    flush()
    return [sec], raw, counts, vocab


def cmd_bryant(a):
    sections, raw, counts, vocab = parse_bryant(a)
    finish(a, sections, raw, notes={"printed abbreviations": len(vocab.keys)}, res=vocab)


# --------------------------------------------------------------------------- #
# Gentry -- The Concordance Repertory (2nd ed., 1893), volume I
# --------------------------------------------------------------------------- #

GENTRY_HEAD = re.compile(
    r"^([A-Z][A-Za-z'\u2019\-]{1,28}(?:\s+[a-z][A-Za-z'\u2019\-]{1,28})?)\.\s*"
    r"[\u2014\u2013-]\s*(.*)$")
GENTRY_RUNHEAD = re.compile(
    r"^(?:[A-Z0-9]{2,6}|\d{1,3})\s+[A-Z][A-Za-z ,'\-]{4,44}\.\s*\S{0,6}\s*$")


def gentry_lines(src):
    raw = P.read_lines(src)
    # the abbreviation list is printed in the front matter and looks exactly like
    # body text, so the body starts after the last 'ABBREVIATIONS' heading
    last_abbrev = 0
    for i, l in enumerate(raw):
        if re.search(r"ABBREVIATIONS|LIST OF MEDICINES", clean_line(l), re.I):
            last_abbrev = i
    start = 0
    for i, l in enumerate(raw):
        if i > last_abbrev and GENTRY_HEAD.match(clean_line(l)):
            start = i
            break
    out = []
    for l in raw[start:]:
        c = clean_line(l)
        if not c or re.fullmatch(r"[\d*\W]{0,4}", c):
            continue
        if GENTRY_RUNHEAD.match(c):
            continue
        out.append(c)
    return out, raw


def parse_gentry(a):
    lines, raw = gentry_lines(a.src)
    counts = collections.Counter()
    printed = parse_printed_gentry(a.src)
    res = Resolver(printed, load_master([a.master, a.aliases]), caps_only=True)
    vocab = res

    sec = {"id": f"{a.slug}-s1", "title": "General", "rubrics": []}
    n, keyword = 0, ""
    carry = ""

    def emit(text, toks):
        nonlocal n
        txt = re.sub(r"\s+", " ", text).strip(" .;:")
        if not txt:
            return
        if len(re.findall(r"[A-Za-z]{2,}", txt)) < 1 or len(txt) < 4:
            # an OCR fragment with no wording: its remedies belong to the entry
            # before it (a wrapped continuation), so fold them in
            if sec["rubrics"] and toks:
                sec["rubrics"][-1]["remedies"].extend(
                    remedy_entry(t, res) for t in toks)
            return
        n += 1
        sec["rubrics"].append({
            "id": f"{a.slug}-r{n:05d}", "text": txt,
            "parent": keyword or None,
            "remedies": [remedy_entry(t, res) for t in toks]})

    for line in lines:
        m = GENTRY_HEAD.match(line)
        if m:
            if carry:
                emit(carry, [])
                carry = ""
            keyword = m.group(1).strip()
            line = m.group(2).strip()
        runs = remedy_runs(line, vocab)
        if not runs:
            carry = (carry + " " + line).strip()
            continue
        pos = 0
        for start, end, toks in runs:
            emit((carry + " " + line[pos:start]).strip(), toks)
            carry = ""
            pos = end
        carry = line[pos:].strip()
    if carry:
        emit(carry, [])
    return [sec], raw, counts, vocab


def cmd_gentry(a):
    sections, raw, counts, vocab = parse_gentry(a)
    finish(a, sections, raw, notes={"printed abbreviations": len(vocab.keys)}, res=vocab)


# --------------------------------------------------------------------------- #
# Knerr -- Repertory to Hering's Guiding Symptoms (1896)
# --------------------------------------------------------------------------- #

KNERR_MARK = "I1l|![]{}"
KNERR_TOKEN = re.compile(
    r"(?P<marks>[" + KNERR_MARK + r"]{1,4}[ \t]*)?"
    r"(?P<name>[A-Z][A-Za-z'\u2019]{1,14}\.?)(?:\s+(?P<sub>[a-z]{1,6})\.?)?")
# a rubric heading starts a line and is closed by ':':  'APOPLEXY:' or
# 'Abdomen, aching:'  (the sub-heading may be lower case or small caps)
KNERR_HEAD = re.compile(
    r"^(?P<text>[A-Z][A-Za-z'\u2019 \-]{1,40}"
    r"(?:,\s*[A-Za-z'\u2019 ,()\-]{0,60})?)\s*:")
KNERR_CHAPTER = re.compile(r"^\d{1,2}\.\s+([A-Z][A-Z ,'\u2019\-]{2,40})\.?$")


def parse_printed_knerr(src, body_start):
    """The book's ABBREVIATIONS list ('Abies,    Abies  nigra.') -> {key: name}."""
    raw = P.read_lines(src)
    out, on = {}, False
    for l in raw[:body_start]:
        if re.match(r"^ABBREVIATIONS", clean_line(l), re.I):
            on = True
            continue
        if not on:
            continue
        parts = re.split(r"[ \t]{2,}", P.fix_ligatures(l).strip())
        if len(parts) < 2:
            continue
        # a printed abbreviation can itself contain a space ('Ars.  h.,')
        i = 1
        while i < len(parts) - 1 and re.fullmatch(r"[a-z]{1,6}[.,]?", parts[i]):
            i += 1
        ab = re.sub(r"\s+", " ", " ".join(parts[:i])).strip().rstrip(".,")
        nm = re.sub(r"\s+", " ", " ".join(parts[i:])).strip().rstrip(".,")
        if not (2 <= len(ab) <= 16) or ab.isupper() or not re.match(r"^[A-Za-z]", ab):
            continue
        if not re.match(r"^[A-Z][a-z]", nm):
            continue
        out.setdefault(tok_key(ab), nm)
    return out


def knerr_body(src):
    """Cleaned body lines + the raw lines, body starting at the first chapter
    heading ('1. MIND.' style) after the abbreviation list."""
    raw = P.read_lines(src)
    # the body opens with '1.  MIND AND DISPOSITION.' right after the
    # abbreviation list; the index at the end also names chapters, so take the
    # first numbered chapter heading past the front matter
    start = 0
    for i, l in enumerate(raw):
        if i > 500 and re.match(r"^1\.", clean_line(l)) and \
                KNERR_CHAPTER.match(strip_page_no(clean_line(l)).strip()):
            start = i
            break
    lines, chapters, seen = [], collections.Counter(), {}
    for i, l in enumerate(raw[start:], start):
        c = clean_line(l)
        if not c or re.fullmatch(r"\d{1,4}", c):
            continue
        m = KNERR_CHAPTER.match(strip_page_no(c).strip())
        if m:
            title = heading_title(m.group(1))
            chapters[title] += 1
            seen.setdefault(title, len(lines))
            continue                      # a running head, not content
        lines.append(c)
    canon = [t for t, n in chapters.items() if n >= 3]
    canon.sort(key=lambda t: seen[t])
    return lines, canon, start


KNERR_LEAD = "I1l|!B[]{}MN"


def knerr_resolve(name, res):
    """Resolve a Knerr remedy token, whose OCR often glues the degree mark onto
    the name ('IIAgnus' -> 'Agnus'). Returns (token, marks_stripped) or (None, 0).
    Only strips when the stripped form actually resolves, so 'Bell.' stays whole."""
    if tok_key(name) in res.keys:
        return name, 0
    t = name
    for k in range(1, 4):
        if not t or t[0] not in KNERR_LEAD:
            break
        t = t[1:]
        if len(t) >= 3 and tok_key(t) in res.keys:
            return t, k
    return None, 0


def knerr_entry_remedies(piece, res):
    """(text, [remedy entries]) for one ';'-separated entry."""
    toks = []
    cut = len(piece)
    for m in KNERR_TOKEN.finditer(piece):
        marks = (m.group("marks") or "").replace(" ", "")
        name = m.group("name") + ((" " + m.group("sub")) if m.group("sub") else "")
        grade = len(marks) or None
        if grade and grade > 3:
            grade = 3
        toks.append((m.start(), name, grade))
    # keep only the trailing run that resolves to printed abbreviations
    keep = []
    for start, name, grade in reversed(toks):
        nm, extra = knerr_resolve(name, res)
        if nm is not None:
            keep.append((start, nm, grade or (extra if extra else None)))
            cut = start
            continue
        # inside a remedy list, a capitalised abbreviation that is not in the
        # printed list is still a remedy (an OCR variant): keep it verbatim,
        # without a name, rather than cutting the list short
        if re.fullmatch(r"[A-Z][A-Za-z]{2,10}\.(?: [a-z]{1,3}\.?)?", name):
            keep.append((start, name, grade))
            cut = start
            continue
        break
    keep.reverse()
    text = piece[:cut].strip()
    text = re.sub(r"[\s,;.\u2014\u2013-]+$", "", text).strip()
    text = re.sub(r"[\s,;.]*\s[I1l|!B]{1,3}$", "", text).strip()
    return text, [remedy_entry(n, res, g) for _, n, g in keep]


def parse_knerr(a):
    lines, canon, body_start = knerr_body(a.src)
    printed = parse_printed_knerr(a.src, body_start)
    res = Resolver(printed, load_master([a.master, a.aliases]))
    res.has = lambda tok: tok_key(tok) in res.keys      # exact only (see Resolver)

    # one continuous string per chapter, with OCR hyphen breaks rejoined
    chapters, cur = [], None
    for l in lines:
        t = KNERR_CHAPTER.match(strip_page_no(l).strip())
        if t:
            continue
        if cur is None:
            cur = {"title": "General", "buf": []}
            chapters.append(cur)
        cur["buf"].append(l)
    # chapters are delimited by the running heads we dropped; recover the order
    # by walking the raw stream again
    raw_lines = a.src and P.read_lines(a.src)
    sections, seen, cur_sec = [], set(), None
    for l in raw_lines[body_start:]:
        c = clean_line(l)
        if not c or re.fullmatch(r"\d{1,4}", c):
            continue
        m = KNERR_CHAPTER.match(strip_page_no(c).strip())
        if m:
            title = P.snap_to_contents(heading_title(m.group(1)), canon)
            # OCR gives one chapter two spellings ('Respiration'/'Kespiration'):
            # fold a near-identical title onto the one already open
            if not any(P.same_section(title, t) for t in seen):
                import difflib
                def twin_of(t):
                    a, b = title.lower(), t.lower()
                    if difflib.SequenceMatcher(None, a, b).ratio() < 0.9:
                        return False
                    wa, wb = a.split(), b.split()
                    if len(wa) == len(wb):
                        # same shape: every word must be a near-match, so
                        # 'Female Sexual Organs' never collapses into 'Male ...'
                        return all(difflib.SequenceMatcher(None, x, y).ratio() >= 0.8
                                   for x, y in zip(wa, wb))
                    return True
                twin = next((t for t in seen if twin_of(t)), None)
                if twin:
                    title = twin
            if not any(P.same_section(title, t) for t in seen):
                seen.add(title)
                cur_sec = {"id": f"{a.slug}-s{len(sections)+1}",
                           "title": title, "rubrics": [], "buf": []}
                sections.append(cur_sec)
            continue
        if cur_sec is None:
            continue
        cur_sec["buf"].append(c)

    # line-level state machine: a heading starts a line and ends with ':'
    n = 0
    for sec in sections:
        blocks, cur = [], None
        for l in sec["buf"]:
            m = KNERR_HEAD.match(l)
            if m:
                cur = {"head": m.group("text").strip(), "lines": [l[m.end():].strip()]}
                blocks.append(cur)
            elif cur is not None:
                cur["lines"].append(l)
        sec.pop("buf")
        for blk in blocks:
            body = " ".join(x for x in blk["lines"] if x)
            body = re.sub(r"(\w)- (\w)", r"\1\2", body)      # OCR hyphen break
            body = re.sub(r"\s+", " ", body).strip()
            head = blk["head"]
            first = True
            for piece in body.split(";"):
                piece = piece.strip()
                if not piece:
                    continue
                txt, rems = knerr_entry_remedies(piece, res)
                if first and not txt:
                    txt = head                       # heading carries the list
                elif txt:
                    txt = head + ", " + txt if False else txt
                if not txt or len(re.findall(r"[A-Za-z]{2,}", txt)) == 0:
                    continue
                n += 1
                sec["rubrics"].append({
                    "id": f"{a.slug}-r{n:05d}", "text": txt,
                    "parent": None if first else head,
                    "remedies": rems})
                first = False
    return sections, P.read_lines(a.src), {}, res


def cmd_knerr(a):
    sections, raw, _, res = parse_knerr(a)
    finish(a, sections, raw, notes={"printed abbreviations": len(res.keys)})


# --------------------------------------------------------------------------- #
# emit + QC
# --------------------------------------------------------------------------- #

def finish(a, sections, raw, notes=None, res=None):
    if res is not None:
        sections, d2, f2 = clean_rubrics(sections, res)
        notes = dict(notes or {})
        notes["rubrics dropped (no wording left)"] = d2
        notes["remedy fragments folded into the previous rubric"] = f2
    # a rubric with no remedy list carries no repertory information: those are
    # cross-reference fragments ('Compare', 'Contraction') and OCR debris
    dropped = 0
    for s in sections:
        keep = [r for r in s["rubrics"] if r["remedies"]]
        dropped += len(s["rubrics"]) - len(keep)
        s["rubrics"] = keep
    sections = [s for s in sections if s["rubrics"]]
    if dropped:
        notes = dict(notes or {})
        notes["rubrics dropped (no remedy list)"] = dropped
    alias = P.load_aliases(a.aliases)
    index = {}
    for sec in sections:
        for rub in sec["rubrics"]:
            for r in rub["remedies"]:
                k = r["abbrev"]
                if k not in index:
                    nm = r.get("name") or alias.get(k.lower().rstrip("."))
                    index[k] = {"name": nm, "resolved": bool(nm)}
    data = {"schema_version": P.SCHEMA_VERSION, "type": "repertory",
            "book": P.book_block(a), "sections": sections,
            "remedy_index": index}
    errs, warns = P.validate(data, "repertory")

    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    nsrc = norm(" ".join(raw))
    allr = [r for sec in sections for r in sec["rubrics"]]
    vb_ok = sum(1 for r in allr if len(norm(r["text"])) < 6 or norm(r["text"]) in nsrc)
    vb = 100 * vb_ok / max(1, len(allr))
    if vb < 90:
        warns.append(f"verbatim rate below 90% ({vb:.1f}%)")

    P.write_json(a.out, data)
    size = os.path.getsize(a.out)
    qc = [f"# QC report - {a.slug}",
          f"- source: {a.src}",
          f"- output: {P._human(size) if hasattr(P, '_human') else size}",
          f"- sections: {len(sections)}",
          f"- rubrics: {data['book']['counts']['rubrics']}",
          f"- remedy links: {data['book']['counts']['remedy_links']}",
          f"- unique remedy tokens: {len(index)}",
          f"- resolved to a canonical name: "
          f"{sum(1 for v in index.values() if v['resolved'])}",
          f"- verbatim text found in source: {vb_ok}/{len(allr)} ({vb:.1f}%)",
          f"- validation errors: {len(errs)} {errs[:5]}",
          f"- warnings: {len(warns)} {warns[:5]}"]
    for k, v in (notes or {}).items():
        qc.insert(-2, f"- {k}: {v}")
    os.makedirs(os.path.dirname(os.path.abspath(a.qc)), exist_ok=True)
    with open(a.qc, "w", encoding="utf-8") as f:
        f.write("\n".join(qc) + "\n")
    print("\n".join(qc))


# --------------------------------------------------------------------------- #
# split a large book into per-chapter files + index.json (the kent-1897 layout)
# --------------------------------------------------------------------------- #

def split_book(json_path, out_dir):
    import json as _json
    data = _json.load(open(json_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    chapters = []
    for i, sec in enumerate(data["sections"], 1):
        slug = re.sub(r"[^a-z0-9]+", "-", sec["title"].lower()).strip("-") or f"s{i}"
        fname = f"{slug}.json"
        n = 1
        while os.path.exists(os.path.join(out_dir, fname)):
            n += 1
            fname = f"{slug}-{n}.json"
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            _json.dump({"schema_version": data["schema_version"],
                        "type": "repertory", "book": data["book"],
                        "section": sec}, f, ensure_ascii=False,
                       separators=(",", ":"))
        chapters.append({"title": sec["title"], "file": fname,
                         "rubrics": len(sec["rubrics"])})
    index = {"schema_version": data["schema_version"],
             "type": "repertory_index", "book": data["book"],
             "remedy_index": data.get("remedy_index", {}),
             "chapters": chapters}
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        _json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    return len(chapters), out_dir


def split_by_letter(json_path, out_dir, key_field="parent"):
    """Split a one-section concordance into A-Z files + index.json.

    Gentry is arranged by concordance keyword, so the keyword's first letter is
    the book's own division. Used when a single file is too large to serve.
    """
    import json as _json
    data = _json.load(open(json_path, encoding="utf-8"))
    sec = data["sections"][0]
    buckets = {}
    for rub in sec["rubrics"]:
        key = (rub.get(key_field) or rub.get("text") or "")[:1].upper()
        b = key if key.isalpha() else "_"
        buckets.setdefault(b, []).append(rub)
    os.makedirs(out_dir, exist_ok=True)
    chapters, total = [], 0
    for b in sorted(buckets):
        fname = f"{b.lower()}.json" if b != "_" else "other.json"
        part = {"schema_version": data["schema_version"], "type": "repertory",
                "book": data["book"],
                "section": {"id": f"{data['book']['id']}-{fname[:-5]}",
                            "title": f"Concordance {b}" if b != "_" else "Other",
                            "rubrics": buckets[b]}}
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            _json.dump(part, f, ensure_ascii=False, separators=(",", ":"))
        chapters.append({"title": part["section"]["title"], "file": fname,
                         "rubrics": len(buckets[b])})
        total += len(buckets[b])
    index = {"schema_version": data["schema_version"],
             "type": "repertory_index", "book": data["book"],
             "remedy_index": data.get("remedy_index", {}),
             "chapters": chapters}
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        _json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    return len(chapters), total


# --------------------------------------------------------------------------- #
# Kent -- Repertory of the Homoeopathic Materia Medica (1897), new OCR source
# --------------------------------------------------------------------------- #

KENT_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9'\-\.,:]{0,14}")
KENT_CHAPTER_RE = re.compile(r"^([A-Z][A-Z ,'\-]{2,30})[.,;:]?$")

# Kent's own chapters, in the book's order (used to tell a chapter head from an
# all-caps rubric head like 'ANGER.')
KENT_CHAPTERS = [
    "Mind", "Vertigo", "Sleep", "Head", "Vision", "Hearing", "Nose", "Face",
    "Mouth", "Teeth", "Throat", "External Throat", "Stomach", "Abdomen",
    "Rectum", "Stool", "Bladder", "Kidneys", "Prostate Gland", "Urethra",
    "Urine", "Genitalia", "Larynx And Trachea", "Respiration", "Cough",
    "Expectoration", "Chest", "Back", "Extremities", "Chill", "Fever",
    "Perspiration", "Skin", "Generalities"]


def parse_printed_kent(src, body_start):
    """Kent prints 'Abbrev.,  Full name.' one pair per line."""
    raw = P.read_lines(src)
    out, on = {}, False
    for l in raw[:body_start]:
        c = re.sub(r"[ \t]+", " ", clean_line(l))
        if re.search(r"ABBREVIATIONS", c, re.I):
            on = True
            continue
        if not on:
            continue
        m = re.match(r"^([A-Za-z][A-Za-z0-9\-]{0,12})[.,]*,? "
                     r"([A-Z][a-z][A-Za-z .\-]{2,40})[.,]?$", c)
        if m:
            out.setdefault(tok_key(m.group(1)), m.group(2).strip())
    return out


def kent_body(src):
    raw = P.read_lines(src)
    # body starts at the first all-caps chapter head that follows the
    # abbreviation list
    last_abbrev = 0
    for i, l in enumerate(raw):
        if re.search(r"ABBREVIATIONS", clean_line(l), re.I):
            last_abbrev = i
    start = None
    for i, l in enumerate(raw):
        if i <= last_abbrev:
            continue
        c = clean_line(l)
        if KENT_CHAPTER_RE.match(strip_page_no(c).strip()) and len(c.split()) == 1:
            start = i
            break
    return raw, (start if start is not None else last_abbrev), last_abbrev


def parse_kent(a):
    raw, start, last_abbrev = kent_body(a.src)
    printed = parse_printed_kent(a.src, last_abbrev + 1)
    res = Resolver(printed, load_master([a.master, a.aliases]))

    sections, seen, cur = [], {}, None
    for l in raw[start:]:
        c = clean_line(l)
        if not c or re.fullmatch(r"[\d\W]{0,4}", c):
            continue
        s = strip_page_no(c).strip()
        m = KENT_CHAPTER_RE.match(s)
        if m and len(s.split()) <= 4 and s == s.upper() and not s.endswith(":"):
            cand = heading_title(m.group(1))
            title = P.snap_to_contents(cand, KENT_CHAPTERS)
            if tok_key(title) not in {tok_key(t) for t in KENT_CHAPTERS}:
                continue                      # an all-caps rubric head, not a chapter
            if title and not any(P.same_section(title, t) for t in seen):
                seen[title] = 1
                cur = {"id": f"{a.slug}-s{len(sections)+1}", "title": title,
                       "rubrics": [], "lines": []}
                sections.append(cur)
            continue
        if cur is None:
            continue
        cur["lines"].append(c)

    n = 0
    for sec in sections:
        text = " ".join(sec.pop("lines"))
        text = re.sub(r"(\w)- (\w)", r"\1\2", text)
        text = re.sub(r"\s+", " ", text)
        toks = KENT_TOKEN.findall(text)
        i, parent = 0, ""
        while i < len(toks):
            head, rems, is_caps = [], [], False
            while i < len(toks):
                t = toks[i]
                i += 1
                head.append(t)
                if t.endswith(":"):
                    break
            if not head or not head[-1].endswith(":"):
                break
            htxt = " ".join(head)[:-1].strip(" .,;")
            is_caps = bool(htxt) and htxt.upper() == htxt and len(htxt) > 2
            while i < len(toks):
                t = toks[i]
                core = t.rstrip(".,;:")
                if len(core) < 2:
                    i += 1
                    continue
                if kent_is_remedy(core, res):
                    rems.append(core)
                    i += 1
                else:
                    break
            if not htxt:
                continue
            n += 1
            sec["rubrics"].append({
                "id": f"{a.slug}-r{n:05d}", "text": htxt,
                "parent": None if is_caps else (parent or None),
                "remedies": [remedy_entry(t, res) for t in rems]})
            if is_caps:
                parent = htxt
    return sections, raw, {}, res


def kent_is_remedy(core, res):
    k = tok_key(core)
    if k in res.keys:
        return True
    if len(k) < 3:
        return False
    if len(k) >= 4 and res.close(k) is not None:
        return True
    return False


def cmd_kent(a):
    sections, raw, _, res = parse_kent(a)
    finish(a, sections, raw, notes={"printed abbreviations": len(res.keys)})


# --------------------------------------------------------------------------- #
# Kimball -- Repertory of Gonorrhoea (1888)
# --------------------------------------------------------------------------- #

KIM_HEAD = re.compile(r"^([A-Z][A-Za-z' ,()\-]{2,60})\.$")


def kimball_lines(src):
    raw = P.read_lines(src)
    start = 0
    for i, l in enumerate(raw):
        if re.search(r"REPERTORY OF GONORRHOEA", clean_line(l), re.I):
            start = i
    # the body proper begins at the first mixed-case heading followed by entries
    for i, l in enumerate(raw):
        if i > start and KIM_HEAD.match(clean_line(l)) and i + 3 < len(raw):
            if ":" in clean_line(raw[i + 1]) or ":" in clean_line(raw[i + 2]):
                start = i
                break
    out = []
    for l in raw[start:]:
        c = clean_line(l)
        if not c or re.fullmatch(r"[\d\W]{0,4}", c):
            continue
        out.append(c)
    return out, raw


def parse_kimball(a):
    lines, raw = kimball_lines(a.src)
    master = load_master([a.master, a.aliases])
    res = Resolver({}, master)
    res.has = lambda tok: tok_key(tok) in res.keys or (
        len(tok_key(tok)) >= 4 and res.close(tok_key(tok)) is not None)

    sec = {"id": f"{a.slug}-s1", "title": "General", "rubrics": []}
    n, parent = 0, ""
    cur_text = None

    def emit(text, run):
        nonlocal n, parent
        txt = re.sub(r"\s+", " ", text).strip(" .,;:")
        toks = leading_remedies(run, res) if run else []
        if not txt:
            return
        is_sub = bool(re.match(r"^[\u2014\u2013,-]", txt))
        frag = re.sub(r"^[\u2014\u2013-]+[\s,]*", "", txt) if is_sub else txt
        if not frag:
            return
        n += 1
        sec["rubrics"].append({
            "id": f"{a.slug}-r{n:05d}", "text": frag,
            "parent": (parent or None) if is_sub else None,
            "remedies": [remedy_entry(t, res) for t in toks]})
        if not is_sub:
            parent = frag

    for line in lines:
        m = re.match(r"^(.*?):\s*(.*)$", line)
        if m:
            if cur_text is not None:
                emit(cur_text, "")
            cur_text = m.group(1).strip()
            run = m.group(2).strip()
            toks = leading_remedies(run, res) if run else []
            if toks or run == "":
                emit(cur_text, run)
                cur_text = None
            continue
        if cur_text is not None:
            lead, toks = tail_remedies(line, res)
            if toks:
                emit((cur_text + " " + lead).strip(), " ".join(toks))
                cur_text = None
                continue
            cur_text = (cur_text + " " + line).strip()
        elif KIM_HEAD.match(line) and len(line.split()) <= 8:
            parent = line.rstrip(".")
        else:
            cur_text = line
    if cur_text:
        emit(cur_text, "")
    return [sec], raw, {}, res


def cmd_kimball(a):
    sections, raw, _, res = parse_kimball(a)
    finish(a, sections, raw, notes={"remedy keys available": len(res.keys)})


# --------------------------------------------------------------------------- #
# Worcester -- Repertory to the Modalities (1880)
# --------------------------------------------------------------------------- #

WORC_CHAP = re.compile(r"^(?:[A-Z]{1,4}\s+)?([A-Z][A-Z '\-]{3,40})[.,]?\s*(?:\d{1,3})?$")


def parse_worcester(a):
    raw = P.read_lines(a.src)
    start = 0
    for i, l in enumerate(raw):
        if re.search(r"REPERTORY TO THE MODALITIES", clean_line(l), re.I):
            start = i
    res = Resolver({}, load_master([a.master, a.aliases]), caps_only=True)
    res.has = lambda tok: tok_key(tok) in res.keys or (
        tok.strip().endswith(".") and len(tok_key(tok)) >= 4
        and res.close(tok_key(tok)) is not None)

    sections, seen, cur = [], set(), None
    n, carry = 0, ""
    for l in raw[start:]:
        c = clean_line(l)
        if not c or re.fullmatch(r"[\d\W]{0,4}", c):
            continue
        m = WORC_CHAP.match(strip_page_no(c).strip())
        if m and c == c.upper() and 2 <= len(c.split()) <= 8:
            title = heading_title(m.group(1))
            if title and not any(P.same_section(title, t) for t in seen):
                seen.add(title)
                cur = {"id": f"{a.slug}-s{len(sections)+1}", "title": title,
                       "rubrics": []}
                sections.append(cur)
                carry = ""
            continue
        if cur is None:
            continue
        lead, toks = tail_remedies(c, res)
        if toks:
            txt = re.sub(r"\s+", " ", (carry + " " + lead)).strip(" .,;:")
            carry = ""
            if txt:
                n += 1
                cur["rubrics"].append({
                    "id": f"{a.slug}-r{n:05d}", "text": txt, "parent": None,
                    "remedies": [remedy_entry(t, res) for t in toks]})
        else:
            carry = (carry + " " + c).strip()
    return sections, raw, {}, res


def cmd_worcester(a):
    sections, raw, _, res = parse_worcester(a)
    finish(a, sections, raw, notes={"remedy keys available": len(res.keys)})


# --------------------------------------------------------------------------- #
# Boenninghausen -- Therapeutic Pocket Book (6th American ed., Allen, 1891)
# --------------------------------------------------------------------------- #

# 'Gentleness.— Aeon., Ambr., ...'  the separator always carries a dash, which
# is what tells a rubric head from a wrapped remedy list.
TPB_RUB = re.compile(r"^(?P<head>[A-Z][A-Za-z' ,()\-]{1,58}?)\s*\.?\s*[\u2014\u2013-]{1,2}\s*(?P<run>.+)$")
TPB_CAPS = re.compile(r"^[A-Z][A-Z ,'\-]{2,24}\.?$")

TPB_CHAPTERS = [
    "Mind", "Sensorium", "Head", "Eyes", "Vision", "Ears", "Hearing", "Nose",
    "Face", "Mouth", "Teeth", "Tongue", "Throat", "Stomach", "Abdomen",
    "Rectum", "Stool", "Bladder", "Urine", "Genitals", "Respiration",
    "Cough", "Chest", "Back", "Extremities", "Sleep", "Chill", "Fever",
    "Perspiration", "Skin", "Generalities", "Relationships Of Remedies"]


TPB_JUNK = re.compile(r"[^A-Za-z0-9.\- ]")


def tpb_is_remedy(tok, res):
    core = tok.strip(" .,;:")
    if not core or len(core) < 2 or TPB_JUNK.search(core):
        return False
    if not (tok.strip().endswith(".") or core.isupper() or "." in tok.strip()):
        return False
    k = tok_key(core)
    if k in res.keys:
        return True
    if len(k) >= 4 and res.close(k) is not None:
        return True
    if len(k) >= 3:
        hits = [c for c in res.keys if c.startswith(k)]
        if len(hits) == 1:
            return True
    return False


def tpb_run(run, res):
    """Split a printed remedy list into (token, grade) pairs.

    Boenninghausen's higher degrees are printed in capitals; the OCR preserves
    that, so an ALL-CAPS token is recorded as grade 3 and everything else as
    null. Two-word abbreviations ('Am. carb.', 'Calc. ph.', 'Nux m.') are
    re-joined from the split parts.
    """
    parts = [p.strip() for p in re.split(r"[,;]", run) if p.strip()]
    merged = []
    for p in parts:
        toks = p.split()
        if not toks:
            continue
        if merged and re.fullmatch(r"[a-z]{1,3}\.?", toks[0]) and \
                re.fullmatch(r"[A-Za-z]{1,5}\.?", merged[-1].split()[-1]):
            merged[-1] = merged[-1] + " " + toks[0]
            merged.extend(toks[1:])
        else:
            merged.extend(toks)
    out = []
    for t in merged:
        core = t.strip(" .,;:")
        if not core:
            continue
        if tpb_is_remedy(t, res):
            out.append((core, 3 if core.isupper() and len(core) > 3 else None))
    return out


def parse_tpb(a):
    raw = P.read_lines(a.src)
    res = Resolver({}, load_master([a.master, a.aliases]))

    sections = [{"id": f"{a.slug}-s1", "title": "General", "rubrics": []}]
    cur = sections[0]
    n, parent, pending = 0, "", None

    def flush():
        nonlocal n, pending
        if pending is None:
            return
        head, rems = pending
        pending = None
        if cur is None or not head:
            return
        n += 1
        cur["rubrics"].append({
            "id": f"{a.slug}-r{n:05d}", "text": head,
            "parent": parent or None,
            "remedies": [remedy_entry(t, res, g) for t, g in rems]})

    for l in raw:
        c = clean_line(l)
        if not c or re.fullmatch(r"[\d\W]{0,5}", c):
            continue
        s = strip_page_no(c).strip()
        if n > 500 and re.search(r"RELATIONSHIPS\s+OF\s+REMEDIES", s, re.I):
            break                          # the closing relationship tables
        if re.search(r"[\[\]|]", s):
            continue                       # OCR'd running head ('M [ND — INTELLECT.')
        # This OCR merges the two columns' running heads ('EXTERNAL HEAD - EYES'),
        # so chapter boundaries are not recoverable: the book ships as one
        # section and the printed sub-heading ('Intellect', 'Internal Head')
        # is carried as each rubric's parent instead.
        if TPB_CAPS.match(s) and s == s.upper():
            continue
        m = TPB_RUB.match(c)
        if m:
            rems = tpb_run(m.group("run"), res)
            if rems:
                flush()
                pending = (m.group("head").strip(" .,;:"), rems)
                continue
        # a continuation line is a bare remedy list: every token must resolve
        rems = tpb_run(c, res)
        all_toks = [t for t in re.split(r"[\s,;]+", c) if t]
        if pending and rems and len(rems) >= 2 and len(rems) >= 0.5 * len(all_toks):
            pending[1].extend(rems)
            continue
        # otherwise a short mixed-case line may be a printed sub-heading
        # ('Intellect.', 'Internal Head.') - never a remedy list or a cross-ref
        words = c.rstrip(".").split()
        if (1 <= len(words) <= 3 and c.endswith(".") and "," not in c
                and not re.search(r"\bSee\b", c)
                and all(w[:1].isupper() and len(w) >= 3 for w in words)
                and all(not tpb_is_remedy(w + ".", res) for w in words)
                and all(not any(c.startswith(tok_key(w)) for c in res.keys)
                        for w in words)):
            flush()
            parent = c.rstrip(".").strip()
    flush()
    return sections, raw, {}, res


def cmd_tpb(a):
    sections, raw, _, res = parse_tpb(a)
    finish(a, sections, raw, notes={"remedy keys available": len(res.keys)})


# --------------------------------------------------------------------------- #
# post-pass: remedy tokens that leaked into the rubric text
# --------------------------------------------------------------------------- #

def clean_rubrics(sections, res):
    """Move remedy tokens that ended up inside a rubric's text back where they
    belong, and fold rubrics whose whole text is a remedy list into the one
    before them.

    Two OCR failures put remedies in the text: a remedy list that begins a line
    ('Paris. Laziness, with slowness of a') and a wrapped list that lost its
    rubric ('kali-n., kreos., lach.'). Both are repaired here, without touching
    the wording of any real symptom.
    """
    dropped = folded = 0
    for sec in sections:
        out = []
        for rub in sec["rubrics"]:
            txt = rub.get("text", "")
            toks = txt.split()
            lead, rest = [], list(toks)
            while rest and vocab_has(res, rest[0]) and abbrev_shaped(rest[0]):
                lead.append(rest.pop(0))
            if lead:
                rub["remedies"] = [remedy_entry(t.strip(" .,;:"), res) for t in lead] \
                    + rub["remedies"]
                txt = " ".join(rest).lstrip(" ,;.-")
                rub["text"] = txt
            if not txt or len(re.findall(r"[A-Za-z]{2,}", txt)) == 0:
                dropped += 1
                continue
            # the whole text is a remedy list -> fold into the previous rubric
            parts = [x for x in re.split(r"[\s,;]+", txt) if x]
            if len(parts) >= 2 and all(vocab_has(res, x) or not abbrev_shaped(x)
                                       for x in parts) and \
                    sum(1 for x in parts if vocab_has(res, x)) >= 2:
                folded += 1
                if out:
                    out[-1]["remedies"].extend(
                        remedy_entry(x.strip(" .,;:"), res) for x in parts
                        if vocab_has(res, x))
                continue
            out.append(rub)
        sec["rubrics"] = out
    return sections, dropped, folded


def main():
    ap = argparse.ArgumentParser(description="book-specific repertory grammars")
    sub = ap.add_subparsers(dest="book", required=True)
    for name in ("fever", "bryant", "gentry", "knerr", "kent", "tpb", "kimball", "worcester"):
        p = sub.add_parser(name)
        p.add_argument("--src", required=True)
        p.add_argument("--slug", required=True)
        p.add_argument("--title", default="")
        p.add_argument("--author", default="")
        p.add_argument("--year", type=int, default=None)
        p.add_argument("--publisher", default="")
        p.add_argument("--out", required=True)
        p.add_argument("--qc", required=True)
        p.add_argument("--aliases", default=os.path.join(HERE, "remedy_aliases.csv"))
        p.add_argument("--master", default=os.path.join(HERE, "remedy_master.csv"))
        p.add_argument("--indent", action="store_true")
    a = ap.parse_args()
    P.COMPACT = not a.indent
    {"fever": cmd_fever, "bryant": cmd_bryant, "gentry": cmd_gentry,
     "knerr": cmd_knerr, "kent": cmd_kent, "kimball": cmd_kimball, "worcester": cmd_worcester, "tpb": cmd_tpb}[a.book](a)


if __name__ == "__main__":
    main()
