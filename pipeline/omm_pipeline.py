#!/usr/bin/env python3
"""
OMM pipeline — turn raw OCR'd homeopathic source texts into clean, app-ready JSON.

Subcommands
-----------
  extract-repertory   Parse a repertory text (rubric -> remedy list) into final JSON.
  extract-mm          Parse a materia medica text (remedy -> symptoms) into final JSON.
  validate            Validate a produced JSON against the OMM schema.
  classify            Heuristic guess: repertory vs materia_medica.

Design rules (non-negotiable):
  * Every rubric / symptom string is VERBATIM from the source (after light OCR cleanup).
  * Grades are only emitted when the source prints them; otherwise null.
  * Nothing is invented. Unknowns are recorded, not guessed.

Light OCR cleanup (agreed policy):
  * collapse runs of spaces, fix common ligatures / dashes,
  * rejoin words hyphen-broken across a line break,
  * drop running heads and standalone page numbers.
Wording is otherwise preserved exactly.
"""

import argparse
import csv
import difflib
import json
import os
import re
import sys
import unicodedata
from datetime import date

SCHEMA_VERSION = "1.0"

# --------------------------------------------------------------------------- #
# OCR cleanup
# --------------------------------------------------------------------------- #

LIGATURES = {
    "\ufb01": "fi", "\ufb02": "fl", "\ufb00": "ff", "\ufb03": "ffi", "\ufb04": "ffl",
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    # NOTE: em/en dashes are the symptom separator in chaptered materia medicas
    # (Jahr). Do NOT flatten them to '-'; keep them as separators.
    "\u00ad": "", "\u00ac": "",
    "\u00a0": " ",
}

# a line that is only a page number, e.g. "  139  " or "14"
PAGE_NO_RE = re.compile(r"^\s*\d{1,4}\s*$")
# a line that is a running head: leading page no then a mostly-uppercase phrase
RUNNING_HEAD_RE = re.compile(r"^\s*\d{1,4}\s+[A-Z][A-Z ,.'\-]{8,}\s*$")


def fix_ligatures(s: str) -> str:
    for a, b in LIGATURES.items():
        s = s.replace(a, b)
    return unicodedata.normalize("NFKC", s)


def collapse_spaces(s: str) -> str:
    return re.sub(r"[ \t]+", " ", s).strip()


def rejoin_hyphen_breaks(lines):
    """Join a line ending in '-' with the next when it looks like a split word."""
    out = []
    i = 0
    while i < len(lines):
        cur = lines[i].rstrip()
        if cur.endswith("-") and i + 1 < len(lines):
            nxt = lines[i + 1].lstrip()
            # only rejoin when the next line starts lower-case (mid-word split)
            if nxt and nxt[0].islower():
                out.append(cur[:-1] + nxt)
                i += 2
                continue
        out.append(cur)
        i += 1
    return out


def merge_caps_lines(lines):
    """Merge runs of consecutive ALL-CAPS lines into one (multi-line headings)."""
    out = []
    for l in lines:
        s = l.strip()
        if (s and s.isupper() and len(s.split()) >= 1
                and out and out[-1] and out[-1].strip().isupper()):
            out[-1] = out[-1].rstrip() + " " + s
        else:
            out.append(l)
    return out


def rejoin_lines(lines):
    """OCR line-rejoin: glue lines broken mid-sentence. A buffer stays open until
    it ends with terminal punctuation; a soft-hyphen ending joins tight."""
    out, buf = [], ""
    for raw in lines:
        s2 = raw.rstrip()
        if not s2.strip():
            if buf:
                out.append(buf); buf = ""
            out.append("")
            continue
        piece = s2.strip()
        if not buf:
            buf = piece
        elif buf.endswith(("-", "\u00ac", "\u2010")):
            buf = buf[:-1] + piece
        else:
            buf = buf + " " + piece
        if re.search(r"[.!?]\s*$", buf) and not buf.endswith("-"):
            out.append(buf); buf = ""
    if buf:
        out.append(buf)
    return out


def clean_lines(raw_lines):
    """Return cleaned lines with page numbers / running heads removed.

    Also returns the set of lines that were dropped (for the QC report).
    """
    if REJOIN:
        raw_lines = rejoin_lines(raw_lines)
    lines = [fix_ligatures(l) for l in raw_lines]
    lines = rejoin_hyphen_breaks(lines)
    lines = merge_caps_lines(lines)
    kept, dropped = [], []
    for l in lines:
        c = collapse_spaces(l)
        if c == "":
            kept.append("")
            continue
        if PAGE_NO_RE.match(c) or RUNNING_HEAD_RE.match(c) or re.search(r"\.{4,}", c):
            dropped.append(c)          # page no / running head / TOC dotted leader
            continue
        kept.append(c)
    return kept, dropped


# --------------------------------------------------------------------------- #
# Repertory parsing
# --------------------------------------------------------------------------- #

# a remedy token: starts uppercase, 1-4 words, optional trailing period
REMEDY_TOKEN_RE = re.compile(r"^[A-Z][a-zA-Z]+(?:[ .\-][a-zA-Z.]+){0,3}\.?$")
# a heading: all-caps line of >= 3 words
HEADING_RE = re.compile(r"^[A-Z][A-Z0-9 ,.'\-]{6,}$")
SECTION_HINT_RE = re.compile(r"REPERTORY|MATERIA MEDICA|GENERALITIES", re.I)


# Kent-style remedy abbreviation: lower-case, short, ending with a period
# (agar.  alum.  am-c.  nux-v.).
LOWER_REMEDY_RE = re.compile(r"^[a-z][a-z0-9-]{0,7}\.$")


_MASTER = None


def _nkey(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())


def _load_master():
    """abbrev/name -> canonical name, from scripts/remedy_master.csv."""
    global _MASTER
    if _MASTER is not None:
        return _MASTER
    m = {}
    path = "scripts/remedy_master.csv"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = (row.get("name") or "").strip()
                if not name:
                    continue
                for k in (row.get("abbrev"), name, name.split()[0]):
                    kk = _nkey(k)
                    if kk and kk not in m:
                        m[kk] = name
    _MASTER = m
    return m


def normalize_remedy(token):
    """Map an OCR'd remedy token to a canonical name, or None if it is not a
    known remedy. Exact match, then unique prefix (>=4 chars), then fuzzy."""
    k = _nkey(token)
    if len(k) < 2:
        return None
    m = _load_master()
    if k in m:
        return m[k]
    ko = k
    for a, b in (("0", "o"), ("1", "l"), ("8", "b"), ("5", "s")):
        ko = ko.replace(a, b)
    if ko in m:
        return m[ko]
    if len(ko) >= 4:
        pref = [v for kk, v in m.items() if kk.startswith(ko)]
        if pref and len(set(pref)) == 1:
            return pref[0]
    import difflib
    close = difflib.get_close_matches(ko, list(m), n=1, cutoff=0.82)
    return m[close[0]] if close else None


def _is_remedy_token(p: str) -> bool:
    """A remedy token is a capitalised name (Hering/Jahr), or a short token with
    no spaces (Kent uses lower-case, often OCR-garbled abbrevs like 'sz/.')."""
    p = p.strip()
    if not p or len(p) > 40:
        return False
    if REMEDY_TOKEN_RE.match(p) and len(p.split()) <= 4:
        return True
    return bool(re.fullmatch(r"[A-Za-z][^\s]{0,9}\.?", p))


def parse_remedy_list(text: str):
    """Split a 'remedy, remedy, remedy.' fragment into clean remedy tokens.

    Returns (remedies, leftover) where leftover is text that did not look like
    a remedy (so the caller can decide it was actually rubric prose).
    """
    text = text.strip()
    if text == "":
        return [], ""
    if SPACE_REMEDIES:
        toks = [t for t in re.split(r"[\s,;]+", text) if t]
        merged = []
        for t in toks:                      # re-join multi-word abbrevs: "Cb." + "v."
            if merged and re.fullmatch(r"[A-Za-z]{1,2}\.?", t) and \
                    re.fullmatch(r"[A-Za-z]{1,3}\.?", merged[-1]):
                merged[-1] = merged[-1] + " " + t
            else:
                merged.append(t)
        rem, left = [], []
        for t in merged:
            if t.lower() in ("and", "or", "with", "also", "see", "compare"):
                continue
            # in space mode a remedy token must look like an abbrev (end in '.')
            # or be a capitalised word; this rejects ordinary prose words
            looks = _is_remedy_token(t) and (t.endswith(".") or re.fullmatch(r"[A-Z][a-z]{2,}", t))
            (rem if looks else left).append(t.rstrip("."))
        return rem, " ".join(left)
    parts = [p.strip() for p in re.split(r"[;,]", text) if p.strip()]
    remedies, leftover = [], []
    for p in parts:
        if _is_remedy_token(p):
            remedies.append(p.rstrip("."))
        else:
            leftover.append(p)
    return remedies, " ".join(leftover)


def looks_like_remedies(text: str) -> bool:
    rems, leftover = parse_remedy_list(text)
    return bool(rems) and not leftover


HEADING_STOP = {"of", "to", "the", "and", "from", "with", "for", "in", "on", "a", "an"}


def normalize_heading(s: str) -> str:
    """Clean an OCR heading: drop digits/punct and leading/trailing junk tokens."""
    s = re.sub(r"[^A-Za-z ]+", " ", s)
    toks = s.split()
    while toks and len(toks[-1]) <= 3 and toks[-1].lower() not in HEADING_STOP:
        toks.pop()
    while toks and len(toks[0]) <= 2 and toks[0].lower() not in HEADING_STOP:
        toks.pop(0)
    return collapse_spaces(" ".join(toks)).title()


def parse_contents(lines):
    """Extract the ordered canonical section titles from the book's CONTENTS block."""
    titles, in_c = [], False
    for l in lines:
        s = collapse_spaces(l)
        if re.search(r"\bCONTENTS\b", s, re.I):
            in_c = True
            continue
        if titles and re.search(r"\bPREFACE\b", s, re.I):
            break
        if not in_c:
            continue
        if re.match(r"^Repertory\b", s, re.I):
            t = re.sub(r"\d.*$", "", s)          # cut at first digit (page range)
            t = normalize_heading(t)
            if t and len(t.split()) >= 2:
                titles.append(t)
    return titles


def snap_to_contents(title, canon):
    """Snap an OCR-garbled heading to the closest canonical CONTENTS title.

    Uses exact -> prefix -> token-overlap (Jaccard) so that 'Mental Symptoms'
    is NOT wrongly pulled onto 'Heart Symptoms' (which shares only stop-words).
    """
    tl = title.lower()
    for c in canon:
        if tl == c.lower():
            return c
    for c in canon:
        cl = c.lower()
        if tl.startswith(cl) or cl.startswith(tl):
            return c
    ta = set(tl.split())
    best, score = title, 0.0
    for c in canon:
        tb = set(c.lower().split())
        j = len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0
        if j > score:
            best, score = c, j
    return best if score >= 0.7 else title


def same_section(a: str, b: str) -> bool:
    """True if two normalized titles name the same section (running head vs body)."""
    a, b = a.lower(), b.lower()
    if a == b or a.startswith(b) or b.startswith(a):
        return True
    ta, tb = set(a.split()), set(b.split())
    if ta and tb and len(ta & tb) / len(ta | tb) >= 0.8:
        return True
    if FUZZY_SECTIONS and len(a) >= 5 and len(b) >= 5:
        return difflib.SequenceMatcher(None, a, b).ratio() >= 0.72
    return False


NOTE_RE = re.compile(r"ARRANGED BY|CONTENTS|PREFACE|INDEX|PAGE|COPYRIGHT|ENTERED", re.I)
FUZZY_SECTIONS = False   # opt-in: merge OCR-variant section titles (--fuzzy-sections)


def parse_repertory(cleaned_lines, slug, canon=(), hierarchy=False,
                    caps_chapters=False, caps_any=False, skip_to_rubric=False):
    """State machine: rubric prose (possibly multi-line) then ': remedies'.

    hierarchy=True  -> sub-rubrics that start lower-case are prefixed with the
                       last heading line, rebuilding paths like
                       'PAIN, ovaries, extending to knee' (Kent-style).
    caps_chapters=True -> a short ALL-CAPS line is taken as a chapter heading.
    """
    sections = []          # list of {"id","title","rubrics":[...]}
    seen_titles = set()
    cur_section = None
    buf_text = ""
    buf_remedies = []
    expect_remedies = False
    parent = ""
    body_started = not skip_to_rubric
    section_notes = []
    counter = {"n": 0}

    def ensure_section():
        nonlocal cur_section
        if cur_section is None:
            cur_section = {"id": f"{slug}-s1", "title": "General", "rubrics": []}
            sections.append(cur_section)

    def flush():
        nonlocal buf_text, buf_remedies, expect_remedies
        expect_remedies = False
        txt = collapse_spaces(buf_text)
        if cur_section is None:            # front matter -> discard
            buf_text = ""
            buf_remedies = []
            return
        if txt and (buf_remedies or len(txt) > 2):
            counter["n"] += 1
            rid = f"{slug}-r{counter['n']:05d}"
            cur_section["rubrics"].append({
                "id": rid,
                "text": txt,
                "remedies": [{"abbrev": r, "grade": None, "polarity": "+"}
                             for r in buf_remedies],
            })
        buf_text = ""
        buf_remedies = []

    for line in cleaned_lines:
        if line == "":
            continue

        # skip front matter / TOC until the first real rubric
        if not body_started:
            sep0 = ":" if ":" in line else None
            if sep0:
                l0, r0 = line.split(sep0, 1)
                rm0, lo0 = parse_remedy_list(r0.strip())
                if rm0 and not lo0:
                    body_started = True
                else:
                    continue
            else:
                continue

        # all-caps chapter heading (Kent-style): a short ALL-CAPS line
        if (caps_chapters and line == line.upper() and any(c.isalpha() for c in line)
                and 1 <= len(line.split()) <= (6 if caps_any else 4)
                and not NOTE_RE.search(line)
                and (caps_any or line.strip().rstrip(".").strip().lower() in KENT_CHAPTERS)):
            title = snap_to_contents(normalize_heading(line), canon)
            if title and not any(same_section(title, t) for t in seen_titles):
                flush()
                seen_titles.add(title)
                cur_section = {"id": f"{slug}-s{len(sections)+1}",
                               "title": title, "rubrics": []}
                sections.append(cur_section)
                parent = ""
            continue

        # heading? (all-caps, >=3 words, not front-matter note, has a hint word)
        if HEADING_RE.match(line) and len(line.split()) >= 3:
            if NOTE_RE.search(line):
                continue
            if SECTION_HINT_RE.search(line):
                title = snap_to_contents(normalize_heading(line), canon)
                is_repeat = any(same_section(title, t) for t in seen_titles)
                if title and not is_repeat:
                    flush()
                    seen_titles.add(title)
                    cur_section = {"id": f"{slug}-s{len(sections)+1}",
                                   "title": title, "rubrics": []}
                    sections.append(cur_section)
                    section_notes.append(title)
                continue
            continue

        if line.startswith("(See"):          # standalone cross-reference line
            continue
        sep = ":" if ":" in line else (";" if ";" in line else None)
        if sep is not None:
            left, right = line.split(sep, 1)
            left = left.strip()
            right = re.sub(r"\(See.*$", "", right).strip()   # drop glued cross-ref
            rems, leftover = parse_remedy_list(right)
            if sep == ":":
                # a real separator has remedies (and no prose left over), or is
                # empty / continues on the next line
                is_sep = (left or buf_text) and (
                    right == "" or right.endswith(",") or right.endswith("-")
                    or (bool(rems) and not leftover))
            else:                                   # ';' only separates when remedies follow
                is_sep = (left or buf_text) and bool(rems)
            if is_sep:
                if buf_remedies:            # previous record complete
                    flush()
                if left:
                    if hierarchy and not buf_text and parent and left[:1].islower():
                        buf_text = (parent + " " + left).strip()
                    else:
                        buf_text = (buf_text + " " + left).strip() if buf_text else left
                buf_remedies.extend(rems)
                # keep cross-references like (See "Bound.") out of the rubric text
                if leftover and not leftover.startswith("(See"):
                    buf_text = (buf_text + " " + leftover).strip()
                # if no remedy captured here, or the list ends with a comma,
                # more remedies may follow on the next line(s)
                expect_remedies = (len(rems) == 0) or right.endswith(",")
            else:
                buf_text = (buf_text + " " + line).strip() if buf_text else line
                expect_remedies = False
            continue

        # no colon
        # a line of pure remedy tokens continues the current remedy list
        # (Kent wraps long remedy lists across lines), whether or not we were
        # already expecting more
        if (expect_remedies or buf_remedies) and looks_like_remedies(line):
            rems, _ = parse_remedy_list(line)
            buf_remedies.extend(rems)
            expect_remedies = True
        else:
            if buf_text or buf_remedies:    # previous record done, new rubric
                flush()
            buf_text = line
            buf_remedies = []
            expect_remedies = False
            if hierarchy:
                parent = line.rstrip(".").strip()

    flush()
    return sections, section_notes


def split_trailing_remedies(line):
    """Split '<rubric text> <sep> Rem1, Rem2.' into (rubric text, remedies).

    The separator is an em/en dash (Humphreys) or '. ' (Drake); try each cut
    from the right and accept the first whose remainder parses as remedies.
    """
    cuts = [m.end() for m in re.finditer(r"[—–]", line)]
    cuts += [m.end() for m in re.finditer(r"\.\s", line)]
    for c in sorted(set(cuts), reverse=True):
        rems, leftover = parse_remedy_list(line[c:].strip())
        if rems and not leftover:
            text = re.sub(r"[\s—–.]+$", "", line[:c]).strip()
            return text, rems
    return line.strip(), []


def parse_repertory_trailing(cleaned_lines, slug, canon=(), flat=False):
    """Repertory whose separator is '. ' and whose remedy list trails the rubric
    text (Drake's Repertory of Foot-sweat). Sub-entries start with '-'."""
    sections, seen = [], set()
    cur = None
    parent = ""
    counter = {"n": 0}

    def new_section(title):
        nonlocal cur
        cur = {"id": f"{slug}-s{len(sections) + 1}", "title": title, "rubrics": []}
        sections.append(cur)

    for line in cleaned_lines:
        if not line:
            continue
        if (not flat and line == line.upper() and any(c.isalpha() for c in line)
                and 2 <= len(line.split()) <= 6 and not NOTE_RE.search(line)):
            title = normalize_heading(line)
            if title and not any(same_section(title, t) for t in seen):
                seen.add(title)
                new_section(title)
                parent = ""
            continue
        text, rems = split_trailing_remedies(line)
        if rems:
            if cur is None:          # front matter before the first chapter
                if flat:
                    new_section("General")
                else:
                    continue
            if text.startswith("-"):
                # a sub-entry: keep the verbatim fragment in `text`, the heading
                # it refines in `parent` (the app renders parent + ', ' + text)
                frag = text.lstrip("- ").strip().lstrip(",").strip().rstrip(".").strip()
                parent_field = parent or None
            else:
                frag = text.rstrip(".").strip()
                parent = frag
                parent_field = None
            counter["n"] += 1
            cur["rubrics"].append({
                "id": f"{slug}-r{counter['n']:05d}",
                "text": frag,
                "parent": parent_field,
                "remedies": [{"abbrev": r, "grade": None, "polarity": "+"}
                             for r in rems],
            })
        elif cur is not None and len(line.split()) <= 8:
            parent = line.rstrip(".").strip()
    return sections, []


# --------------------------------------------------------------------------- #
# Remedy index / aliases
# --------------------------------------------------------------------------- #

JAHR_STOP = set("the are in of and see for with from has its his her all not was were when then than that this they them their been have but or as at be by is it on to we you if no so up us do go an my me he she also else which may some most been often case cases more such very thus same other others".split())


def _jahr_remedy_vocab():
    import glob as _glob
    vocab = set()
    if os.path.exists("scripts/remedy_aliases.csv"):
        with open("scripts/remedy_aliases.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("abbrev"):
                    vocab.add(re.sub(r"[^a-z]", "", row["abbrev"].lower()))
    return {v for v in vocab if 2 < len(v) <= 10 and v not in JAHR_STOP}


def _split_text_remedies(line):
    """Lippe-style: '<text>, Rem1. Rem2. Rem3.' - split at the last comma whose
    right side parses entirely as a space-separated remedy list."""
    for m in reversed(list(re.finditer(r",", line))):
        right = line[m.end():].strip()
        rems, leftover = parse_remedy_list(right)
        if rems and not leftover:
            return line[:m.start()].strip(), rems
    return line.strip(), []


def _rems(lst):
    return [{"abbrev": a, "grade": None, "polarity": "+"} for a in lst]


def parse_repertory_lippe(cleaned_lines, slug, canon=()):
    """Lippe: 'N. CHAPTER.' sections; parent rubrics '<text>, Rem. Rem.' whose
    remedy lists wrap; sub-rubrics marked with an em-dash continue the parent."""
    sections, seen = [], set()
    cur = None
    rub = None
    parent = None
    counter = {"n": 0}

    def new_section(t):
        nonlocal cur
        cur = {"id": f"{slug}-s{len(sections)+1}", "title": t, "rubrics": []}
        sections.append(cur)

    def flush():
        nonlocal rub
        if rub is not None and rub["text"] and cur is not None:   # skip front matter
            counter["n"] += 1
            rub["id"] = f"{slug}-r{counter['n']:05d}"
            cur["rubrics"].append(rub)
        rub = None

    for line in cleaned_lines:
        if not line:
            continue
        m = re.match(r"^([IVXL]+)\.\s+([A-Z][A-Z ]{3,})\.?$", line)
        if m:
            flush()
            t = m.group(2).strip().title()
            parent = None
            if t and not any(same_section(t, x) for x in seen):
                seen.add(t)
                new_section(t)
            continue
        is_sub = line[:1] in ("—", "-", "–")
        body = line.lstrip("—–-").strip() if is_sub else line
        if not body:
            continue
        text, rems = _split_text_remedies(body)
        if rems:
            flush()
            rub = {"text": text, "parent": parent if is_sub else None,
                   "remedies": _rems(rems)}
            if not is_sub:
                parent = text
            continue
        rems2, leftover2 = parse_remedy_list(body)
        if rems2 and not leftover2 and rub is not None:
            rub["remedies"].extend(_rems(rems2))
            continue
        if rub is not None:
            rub["text"] = (rub["text"] + " " + body).strip()
        else:
            rub = {"text": body, "parent": None, "remedies": []}
    flush()
    return sections, []


def parse_repertory_jahr(cleaned_lines, slug, canon=()):
    """Jahr Part II: 'CHAP. X. NAME.' chapters, ALL-CAPS condition headings, and
    prose that carries remedy lists. Condition -> remedies (extracted) + note."""
    vocab = _jahr_remedy_vocab()
    sections, seen = [], set()
    cur = None
    rub = None
    buf = []
    counter = {"n": 0}

    def new_section(title):
        nonlocal cur
        cur = {"id": f"{slug}-s{len(sections)+1}", "title": title, "rubrics": []}
        sections.append(cur)

    def extract(text):
        out = []
        for t in re.findall(r"[A-Za-z][A-Za-z\-]{1,8}\.?", text):
            k = re.sub(r"[^a-z]", "", t.lower())
            if k in vocab and t not in out:
                out.append(t.rstrip("."))
        return out

    def flush():
        nonlocal rub, buf
        if rub is not None:
            note = collapse_spaces(" ".join(buf)).strip()
            rub["remedies"] = [{"abbrev": a, "grade": None, "polarity": "+"}
                               for a in extract(note)]
            rub["note"] = note or None
            if rub["text"].strip():
                if cur is None:
                    new_section("General")
                counter["n"] += 1
                rub["id"] = f"{slug}-r{counter['n']:05d}"
                cur["rubrics"].append(rub)
        rub = None
        buf = []

    for line in cleaned_lines:
        s = line.strip()
        if not s:
            continue
        cm = re.match(r"^CHAP\.?\s*[IVXLC]+\.?\s+(.+?)\.?$", s)
        if cm:
            flush()
            title = cm.group(1).strip().title()
            if title and not any(same_section(title, t) for t in seen):
                seen.add(title)
                new_section(title)
            continue
        if re.match(r"^SECT\.?\s*[IVXLC]+\.?", s):
            flush()
            continue
        hm = re.match(r"^([A-Z][A-Z0-9 '().,&/\-]{2,}?)\s*[—–]\s*(.*)$", s)
        if hm and hm.group(1).strip().isupper():
            flush()
            rub = {"text": hm.group(1).strip().title(), "remedies": []}
            if hm.group(2).strip():
                buf.append(hm.group(2))
            continue
        buf.append(s)
    flush()
    rubrics = [r for r in sections for r in r["rubrics"]]
    return sections, []


def parse_repertory_ruoff(cleaned_lines, slug, canon=()):
    """Ruoff-style, nosologically arranged: a condition heading (short line, no
    dash), then 'Remedy — clinical note' entries (note may wrap). One section."""
    rubrics = []
    cur = None
    entry = None
    counter = {"n": 0}
    lines = list(cleaned_lines)

    def flush_entry():
        nonlocal entry
        if cur is not None and entry is not None:
            note = collapse_spaces(" ".join(entry["note"])).strip()
            for r in entry["remedies"]:
                cur["remedies"].append({"abbrev": r, "grade": None,
                                        "polarity": "+", "note": note or None})
        entry = None

    def flush_rubric():
        nonlocal cur
        flush_entry()
        if cur is not None and cur["text"].strip():
            counter["n"] += 1
            cur["id"] = f"{slug}-r{counter['n']:05d}"
            rubrics.append(cur)
        cur = None

    for i, line in enumerate(lines):
        if not line:
            continue
        nxt = next((l for l in lines[i + 1:] if l.strip()), "")
        no_dash = " — " not in line
        is_caps_head = (line == line.upper() and any(c.isalpha() for c in line)
                        and 2 <= len(line.split()) <= 8 and not NOTE_RE.search(line))
        is_cond = (no_dash and line[:1].isupper() and len(line.split()) <= 10
                   and (line.rstrip().endswith(".") or " — " in nxt)
                   and not NOTE_RE.search(line))
        if is_caps_head or is_cond:
            flush_rubric()
            cur = {"text": normalize_heading(line) if is_caps_head else line.strip(),
                   "remedies": []}
            continue
        if " — " in line:
            left, right = line.split(" — ", 1)
            rems, leftover = parse_remedy_list(left)
            if rems and not leftover:
                flush_entry()
                if cur is None:
                    cur = {"text": "", "remedies": []}
                entry = {"remedies": rems, "note": [right.strip()]}
                continue
        if entry is not None:
            entry["note"].append(line.strip())
        elif cur is not None:
            cur["text"] = (cur["text"] + " " + line).strip()
    flush_rubric()
    rubrics = [r for r in rubrics if r["remedies"]]
    return [{"id": f"{slug}-s1", "title": "General", "rubrics": rubrics}], []


def load_aliases(path):
    alias = {}
    if not path or not os.path.exists(path):
        return alias
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            a = (row.get("abbrev") or "").strip()
            n = (row.get("name") or "").strip()
            if a:
                alias[a.lower().rstrip(".")] = n
    return alias


EMBED_REMEDY_RE = re.compile(r"\b([A-Z][a-zA-Z]+(?: [a-z][a-zA-Z]+){0,3})\.")


def recover_embedded_rubrics(sections, vocab):
    """Second-pass recovery: when OCR dropped the ':' separator, a remedy name
    sits inline in the rubric text. Split those into proper (text, remedies)."""
    for sec in sections:
        rubs = []
        for rub in sec["rubrics"]:
            text = rub["text"]
            hits, end = [], -1
            for m in EMBED_REMEDY_RE.finditer(text):
                if m.group(1).lower() in vocab and m.start() >= end:
                    hits.append(m)
                    end = m.end()
            if not hits:
                rubs.append(rub)
                continue
            pos, made = 0, []
            for m in hits:
                seg = text[pos:m.start()].strip()
                if seg:
                    made.append({"text": seg,
                                 "remedies": [{"abbrev": m.group(1),
                                               "grade": None, "polarity": "+"}]})
                pos = m.end()
            tail = text[pos:].strip()
            if tail:
                made.append({"text": tail, "remedies": list(rub["remedies"])})
            elif made and rub["remedies"]:
                made[-1]["remedies"].extend(rub["remedies"])
            for j, mm in enumerate(made):
                rubs.append({"id": f"{rub['id']}-{j+1}", "text": mm["text"],
                             "remedies": mm["remedies"]})
        sec["rubrics"] = rubs
    return sections


def _is_remedy_list_text(t):
    """True if a rubric's whole text is a bare remedy list (an OCR artefact:
    a wrapped remedy-list line that became its own rubric)."""
    rems, leftover = parse_remedy_list(t)
    return len(rems) >= 2 and not leftover


def fold_remedy_list_rubrics(sections):
    """Fold rubrics whose text is a bare remedy list into the previous rubric's
    remedies (they are wrapped continuation lines), removing the bogus rubric."""
    for sec in sections:
        out = []
        for r in sec["rubrics"]:
            if _is_remedy_list_text(r["text"]):
                toks = [x.strip().rstrip(".") for x in re.split(r"[;,]", r["text"]) if x.strip()]
                add = [{"abbrev": tk, "grade": None, "polarity": "+"} for tk in toks]
                add += r["remedies"]
                if out:
                    out[-1]["remedies"].extend(add)
                # no previous rubric -> drop
            else:
                out.append(r)
        sec["rubrics"] = out
    return sections


def fill_remedy_names(sections):
    """Post-pass: attach a canonical name to each remedy link where the token
    resolves against the master remedy list (never changes the parse)."""
    for sec in sections:
        for r in sec.get("rubrics", []):
            for x in r.get("remedies", []):
                if not x.get("name"):
                    x["name"] = normalize_remedy(x.get("abbrev", ""))


def build_remedy_index(sections, alias):
    index = {}
    for sec in sections:
        for rub in sec["rubrics"]:
            for r in rub["remedies"]:
                key = r["abbrev"]
                if key not in index:
                    canon = alias.get(key.lower().rstrip("."))
                    index[key] = {"name": canon, "resolved": bool(canon)}
    return index


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #

def validate(data, kind):
    errs, warns = [], []
    if data.get("schema_version") != SCHEMA_VERSION:
        errs.append("schema_version mismatch")
    if data.get("type") != kind:
        errs.append(f"type should be {kind}")
    book = data.get("book") or {}
    for f in ("id", "title", "source_file", "extraction_date"):
        if not book.get(f):
            errs.append(f"book.{f} missing")

    if kind == "repertory":
        seen = set()
        n_rub = n_rem = 0
        for sec in data.get("sections", []):
            for rub in sec.get("rubrics", []):
                n_rub += 1
                if rub["id"] in seen:
                    errs.append(f"duplicate rubric id {rub['id']}")
                seen.add(rub["id"])
                if not rub.get("text"):
                    warns.append(f"{rub['id']} empty text")
                for r in rub.get("remedies", []):
                    n_rem += 1
                    if not r.get("abbrev"):
                        errs.append(f"{rub['id']} remedy without abbrev")
        if n_rub == 0:
            errs.append("no rubrics parsed")
        data["book"].setdefault("counts", {})
        data["book"]["counts"] = {"sections": len(data.get("sections", [])),
                                  "rubrics": n_rub, "remedy_links": n_rem}
    elif kind == "materia_medica":
        n_rem = n_sym = 0
        for rem in data.get("remedies", []):
            n_rem += 1
            if not rem.get("name"):
                errs.append(f"remedy {rem.get('id')} missing name")
            n_sym += len(rem.get("symptoms", []))
        if n_rem == 0:
            errs.append("no remedies parsed")
        data["book"]["counts"] = {"remedies": n_rem, "symptoms": n_sym}

    return errs, warns


# --------------------------------------------------------------------------- #
# Materia medica parsing (line-state machine: REMEDY heading -> chapters -> text)
# --------------------------------------------------------------------------- #

# Kent's chapter names, used only when caps_chapters is on, so that all-caps
# RUBRIC headings ("CONDYLOMATA", "ERUPTIONS") are not read as chapters.
KENT_CHAPTERS = {
    "mind", "vertigo", "head", "eye", "vision", "ear", "hearing", "nose",
    "face", "mouth", "teeth", "throat", "external throat", "stomach",
    "abdomen", "rectum", "stool", "bladder", "kidneys", "prostate gland",
    "urethra", "urine", "male genitalia", "female genitalia", "genitalia",
    "larynx and trachea", "respiration", "cough", "expectoration", "chest",
    "heart", "back", "extremities", "sleep", "chill", "fever",
    "perspiration", "skin", "generalities",
}

# A remedy heading is an ALL-CAPS line ending in a period (e.g. "ACONITUM NAPELLUS.").
MM_REMEDY_RE = re.compile(r"^[A-Z][A-Z .\-]{3,}$")
# Front-matter / structural headings that must NOT be read as remedies.
MM_NONREMEDY = {
    "of the", "entered once for all", "vol i", "vol ii", "vol iii",
    "end of the first part", "materia medica", "manual of the",
    "general symptoms",
}
# Known body-system chapter labels (single- and multi-word). A segment is a
# chapter only if it matches this set, so that common names ("Deadly
# Nightshade"), running heads ("SEPIA. SEP") and one-word symptoms
# ("Constipation") are not mistaken for chapters.
MM_LABELS = {
    "head", "mind", "moral symptoms", "general symptoms", "intellectual faculties",
    "memory", "vertigo", "eyes", "eye", "ears", "ear", "nose", "face", "mouth",
    "teeth", "tongue", "throat", "stomach", "abdomen", "abdominal region",
    "gastric symptoms", "rectum", "anus", "stool", "urine", "bladder",
    "kidneys", "kidney", "genital organs", "genital parts", "male genital organs",
    "female genital organs", "larynx", "chest", "heart", "back", "trunk", "neck",
    "upper extremities", "lower extremities", "extremities", "skin", "sleep",
    "fever", "cough", "respiration", "pulse", "clinical remarks", "clinical",
    "generalities", "glands",
}
MM_RUNNING_HEAD_RE = re.compile(r"^([A-Z][A-Z .]+?)\.?\s+[A-Z]{2,6}$")
NOISE_LEAD = re.compile(r"^[\s*°^'\"“”‘’†‡§¶,.;:]+\s*")


def _clean_sym(s):
    return NOISE_LEAD.sub("", s).strip()


def _is_chapter_label(s):
    """True only for a known body-system chapter label (see MM_LABELS)."""
    return s.strip().rstrip(".").strip().lower() in MM_LABELS


def _finalize_mm(cur, buf, slug):
    """Split a remedy's raw text into clinical indications + chaptered symptoms."""
    text = collapse_spaces(" ".join(buf))
    segments = re.split(r"\s*[—–]\s*", text)
    if not segments:
        return
    chapter = "General"
    head = _clean_sym(segments[0])
    # a known chapter label may be glued to the end of the clinical list
    tail = re.search(r"([A-Z][A-Za-z ]{2,25})\.\s*$", head)
    if tail and tail.group(1).strip().lower() in MM_LABELS:
        chapter = tail.group(1).strip().title()
        head = head[:tail.start()].strip()
    if _is_chapter_label(head):
        chapter = head.rstrip(".").strip().title()
    else:
        for item in head.split(";"):
            it = _clean_sym(item)
            if it and len(it) > 2:
                cur["clinical_indications"].append(it)
    for seg in segments[1:]:
        s = _clean_sym(seg)
        if not s:
            continue
        low = s.lower()
        if "potency" in low and "employed" in low:
            cur["sections"]["dosages"].append(s)
            continue
        if _is_chapter_label(s):
            chapter = s.rstrip(".").strip().title()
            continue
        cur["symptoms"].append({
            "id": f"{cur['id']}-s{len(cur['symptoms']) + 1:04d}",
            "chapter": chapter,
            "text": s,
            "grade": None,
            "modalities": [],
        })


BELL_LABELS = {"stools", "aggravation", "amelioration", "before stool",
               "during stool", "after stool", "accompaniments", "remarks",
               "clinical", "dose", "potency"}
BELL_HEAD_RE = re.compile(r"^[0-9OoIl]{1,3}\.\s+(.+?)\.?$")


def _remedy_vocab():
    """A clean-ish canonical remedy vocabulary from the alias table + saved books."""
    import glob as _glob
    vocab = set()
    if os.path.exists("scripts/remedy_aliases.csv"):
        with open("scripts/remedy_aliases.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("name"):
                    vocab.add(row["name"].strip())
    for f in _glob.glob("materia_medica/*.json") + _glob.glob("repertory/*.json"):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for r in d.get("remedies", []):
            if r.get("name"):
                vocab.add(r["name"])
    return {v for v in vocab if len(v) > 3}


def enrich_canonical_names(remedies, cutoff=0.7):
    """Add a best-effort 'canonical' to OCR-mangled remedy names; the verbatim
    name is always kept. Only confident matches (>= cutoff) are asserted."""
    vocab = _remedy_vocab()
    vn = {re.sub(r"[^a-z]", "", v.lower()): v for v in vocab}
    for r in remedies:
        key = re.sub(r"[^a-z]", "", (r.get("name") or "").lower())
        best = difflib.get_close_matches(key, list(vn), n=1, cutoff=cutoff) if key else []
        r["canonical_name"] = vn[best[0]] if best else None


def parse_materia_medica_bell(cleaned_lines, slug):
    """Bell's Homoeopathic Therapeutics: 'N. REMEDY.' headings, then labelled
    groups (Stools:, Aggravation:, Before Stool: ...) whose items are ';'-separated."""
    remedies = []
    cur = None
    label = None
    buf = []

    def flush_items():
        nonlocal buf
        if cur is not None:
            txt = collapse_spaces(" ".join(buf)).strip()
            if txt:
                for it in re.split(r"[;:]", txt):
                    it = _clean_sym(it).strip()
                    if it and len(it) > 1:
                        cur["symptoms"].append({
                            "id": f"{cur['id']}-s{len(cur['symptoms']) + 1:04d}",
                            "chapter": label or "General", "text": it,
                            "grade": None, "modalities": []})
        buf = []

    for line in cleaned_lines:
        s = line.strip()
        if not s:
            continue
        m = BELL_HEAD_RE.match(s)
        if m and len(s.split()) <= 6 and m.group(1)[:1].isupper():
            flush_items()
            name = collapse_spaces(m.group(1))
            cur = {"id": f"{slug}-{len(remedies) + 1:04d}", "name": name,
                   "abbrev": name.split()[0][:4], "common_name": None,
                   "kingdom": None, "family": None, "clinical_indications": [],
                   "sections": {"relationships": [], "dosages": [], "antidotes": []},
                   "symptoms": []}
            remedies.append(cur)
            label = None
            continue
        lm = re.match(r"^([A-Z][A-Za-z ]{2,20})\s*:\s*(.*)$", s)
        if lm and lm.group(1).strip().lower() in BELL_LABELS:
            flush_items()
            label = lm.group(1).strip()
            if lm.group(2).strip():
                buf.append(lm.group(2))
            continue
        buf.append(s)
    flush_items()
    return remedies


def parse_materia_medica(cleaned_lines, slug):
    """Parse a 'chaptered' materia medica: remedy heading -> clinical list ->
    chapter labels -> dash-separated symptoms (e.g. Jahr's Manual, Part I)."""
    remedies = []
    cur = None
    buf = []
    body_started = False
    seen_preface = False

    def flush():
        nonlocal buf
        if cur is not None and buf:
            _finalize_mm(cur, buf, slug)
        buf = []

    for line in cleaned_lines:
        s = line.strip()
        if s == "":
            continue
        if "PREFACE" in s.upper():
            seen_preface = True
        if (MM_REMEDY_RE.match(s) and s.endswith(".")
                and 2 <= len(s.split()) <= 4):
            name = s.rstrip(".")
            low = name.lower()
            if "materia medica" in low:
                if seen_preface:          # the body heading, not the title page
                    body_started = True
                continue
            if low in MM_NONREMEDY or "vol" in low.replace(".", "").split():
                continue
            if not body_started:
                continue
            if cur is not None and low == cur["name"].lower():
                continue                      # running head of the same remedy
            flush()
            cur = {"id": f"{slug}-{len(remedies) + 1:04d}",
                   "name": name.title().strip(),
                   "abbrev": name.split()[0][:4].title(),
                   "common_name": None, "kingdom": None, "family": None,
                   "clinical_indications": [],
                   "sections": {"relationships": [], "dosages": [], "antidotes": []},
                   "symptoms": []}
            remedies.append(cur)
            continue
        if cur is not None:
            rh = MM_RUNNING_HEAD_RE.match(s)   # e.g. "SEPIA. SEP" running head
            if rh and rh.group(1).strip().lower().replace(".", "") == cur["name"].lower():
                continue
            buf.append(s)
    flush()
    return remedies


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


COMPACT = True   # compact JSON is the default; use --indent for pretty
SPACE_REMEDIES = False   # remedy lists separated by spaces (Lippe/Bryant/Clarke)
REJOIN = False           # re-glue OCR lines broken mid-sentence


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if COMPACT:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, f, ensure_ascii=False, indent=1)


def book_block(args):
    return {
        "id": args.slug,
        "title": args.title,
        "author": args.author,
        "year": args.year,
        "publisher": args.publisher,
        "language": "en",
        "public_domain": True,
        "source_file": args.src,
        "extraction_date": date.today().isoformat(),
        "pipeline_version": "omm_pipeline 1.0",
        "counts": {},
    }


def cmd_extract_repertory(args):
    global FUZZY_SECTIONS, COMPACT, SPACE_REMEDIES, REJOIN
    FUZZY_SECTIONS = getattr(args, "fuzzy_sections", False)
    COMPACT = not getattr(args, "indent", False)
    SPACE_REMEDIES = getattr(args, "space_remedies", False)
    REJOIN = getattr(args, "rejoin", False)
    raw = read_lines(args.src)
    canon = parse_contents(raw)
    cleaned, dropped = clean_lines(raw)
    if args.lippe:
        sections, notes = parse_repertory_lippe(cleaned, args.slug, canon)
    elif args.jahr:
        sections, notes = parse_repertory_jahr(cleaned, args.slug, canon)
    elif args.ruoff:
        sections, notes = parse_repertory_ruoff(cleaned, args.slug, canon)
    elif args.trailing:
        sections, notes = parse_repertory_trailing(cleaned, args.slug, canon,
                                                  flat=args.flat)
    else:
        sections, notes = parse_repertory(cleaned, args.slug, canon,
                                          hierarchy=args.hierarchy,
                                          caps_chapters=args.caps_chapters,
                                          caps_any=args.caps_any,
                                          skip_to_rubric=args.skip_to_rubric)
    # drop empty (and, optionally, sub-threshold) sections
    minr = getattr(args, "min_rubrics", 1) or 1
    sections = [s for s in sections if len(s["rubrics"]) >= minr]
    alias = load_aliases(args.aliases)
    vocab = set(k.lower() for k in build_remedy_index(sections, alias))
    # In trailing mode a section titled with a bare remedy name is an OCR artefact
    # (an all-caps remedy heading read as a chapter) -> fold into the previous one.
    # NOT in caps-chapters mode, where single-word titles are the real chapters.
    if args.trailing and not args.caps_chapters:
        merged = []
        for s in sections:
            t = s["title"].strip()
            if len(t.split()) == 1 and t.lower().rstrip(".") in vocab and merged:
                merged[-1]["rubrics"].extend(s["rubrics"])
            else:
                merged.append(s)
        sections = merged
    sections = recover_embedded_rubrics(sections, vocab)
    sections = fold_remedy_list_rubrics(sections)
    fill_remedy_names(sections)
    # drop rubrics with no text, then any section left empty
    for s in sections:
        s["rubrics"] = [r for r in s["rubrics"] if r.get("text", "").strip()]
    sections = [s for s in sections if s["rubrics"]]
    # renumber rubric ids sequentially after recovery
    n = 0
    for sec in sections:
        for rub in sec["rubrics"]:
            n += 1
            rub["id"] = f"{args.slug}-r{n:05d}"
    index = build_remedy_index(sections, alias)
    data = {
        "schema_version": SCHEMA_VERSION,
        "type": "repertory",
        "book": book_block(args),
        "sections": sections,
        "remedy_index": index,
    }
    errs, warns = validate(data, "repertory")

    # Phase-4 gate: does every rubric text trace verbatim back into the source?
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    nsrc = norm(" ".join(raw))
    allr = [r for sec in sections for r in sec["rubrics"]]
    def _vb(r):
        n = norm(r["text"])
        return len(n) < 6 or n in nsrc
    vb_ok = sum(_vb(r) for r in allr)
    vb_pct = 100 * vb_ok / max(1, len(allr))
    if vb_pct < 90:
        warns.append(f"verbatim rate below 90% ({vb_pct:.1f}%)")

    write_json(args.out, data)
    # QC report
    qc = [f"# QC report — {args.slug}",
          f"- source: {args.src}",
          f"- dropped lines (page no / running heads): {len(dropped)}",
          f"- sections: {len(sections)}",
          f"- rubrics: {data['book']['counts']['rubrics']}",
          f"- remedy links: {data['book']['counts']['remedy_links']}",
          f"- unique remedy tokens: {len(index)}",
          f"- resolved via alias table: {sum(1 for v in index.values() if v['resolved'])}",
          f"- verbatim text found in source: {vb_ok}/{len(allr)} ({vb_pct:.1f}%)",
          f"- validation errors: {len(errs)} {errs[:5]}",
          f"- warnings: {len(warns)} {warns[:5]}"]
    os.makedirs(os.path.dirname(os.path.abspath(args.qc)), exist_ok=True)
    with open(args.qc, "w", encoding="utf-8") as f:
        f.write("\n".join(qc) + "\n")
    print("\n".join(qc))


def cmd_extract_mm(args):
    global COMPACT, SPACE_REMEDIES, REJOIN
    COMPACT = not getattr(args, "indent", False)
    SPACE_REMEDIES = getattr(args, "space_remedies", False)
    REJOIN = getattr(args, "rejoin", False)
    raw = read_lines(args.src)
    cleaned, dropped = clean_lines(raw)
    if getattr(args, "bell", False):
        remedies = parse_materia_medica_bell(cleaned, args.slug)
        enrich_canonical_names(remedies)
    else:
        remedies = parse_materia_medica(cleaned, args.slug)
    data = {
        "schema_version": SCHEMA_VERSION,
        "type": "materia_medica",
        "book": book_block(args),
        "remedies": remedies,
    }
    errs, warns = validate(data, "materia_medica")

    # Phase-4 gate: does every symptom text trace verbatim back into the source?
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    nsrc = norm(" ".join(raw))
    alls = [s for r in remedies for s in r["symptoms"]]
    def _vb(s):
        n = norm(s["text"])
        return len(n) < 6 or n in nsrc
    vb_ok = sum(_vb(s) for s in alls)
    vb_pct = 100 * vb_ok / max(1, len(alls))
    if vb_pct < 90:
        warns.append(f"verbatim rate below 90% ({vb_pct:.1f}%)")

    write_json(args.out, data)
    qc = [f"# QC report — {args.slug}",
          f"- source: {args.src}",
          f"- remedies: {data['book']['counts']['remedies']}",
          f"- symptoms: {data['book']['counts']['symptoms']}",
          f"- remedies with 0 symptoms: {sum(1 for r in remedies if not r['symptoms'])}",
          f"- verbatim text found in source: {vb_ok}/{len(alls)} ({vb_pct:.1f}%)",
          f"- validation errors: {len(errs)} {errs[:5]}",
          f"- warnings: {len(warns)} {warns[:5]}"]
    os.makedirs(os.path.dirname(os.path.abspath(args.qc)), exist_ok=True)
    with open(args.qc, "w", encoding="utf-8") as f:
        f.write("\n".join(qc) + "\n")
    print("\n".join(qc))


def cmd_validate(args):
    with open(args.json, encoding="utf-8") as f:
        data = json.load(f)
    errs, warns = validate(data, data.get("type"))
    print(json.dumps({"errors": errs, "warnings": warns[:20],
                      "counts": data["book"].get("counts")}, indent=1))
    sys.exit(1 if errs else 0)


def cmd_classify(args):
    lines = read_line = read_lines(args.src)
    sample = "\n".join(lines[:4000])
    colon_ratio = sum(1 for l in lines[:4000] if ":" in l) / max(1, len(lines[:4000]))
    verdict = "repertory" if colon_ratio > 0.25 else "materia_medica"
    print(json.dumps({"file": args.src, "colon_ratio": round(colon_ratio, 3),
                      "guess": verdict}, indent=1))


def cmd_to_sqlite(args):
    """Convert a final JSON (repertory or materia_medica) into a normalised SQLite
    database. Integer keys keep it small; indexes make rubric/remedy lookups fast."""
    import sqlite3
    d = json.load(open(args.json, encoding="utf-8"))
    t = d.get("type")
    if os.path.exists(args.db):
        os.remove(args.db)
    con = sqlite3.connect(args.db)
    cur = con.cursor()
    cur.executescript("""
        PRAGMA journal_mode=OFF;
        CREATE TABLE book(id TEXT PRIMARY KEY, type TEXT, schema_version TEXT,
                          title TEXT, author TEXT, year INT, publisher TEXT,
                          source_file TEXT, extraction_date TEXT, counts TEXT);
        CREATE TABLE section(id INTEGER PRIMARY KEY, book_id TEXT, ordinal INT, title TEXT);
        CREATE TABLE rubric(id INTEGER PRIMARY KEY, book_id TEXT, section_id INT,
                            text TEXT, parent TEXT, note TEXT);
        CREATE TABLE remedy_link(rubric_id INT, abbrev TEXT, grade INT, polarity TEXT,
                                 note TEXT);
        CREATE TABLE remedy_index(book_id TEXT, abbrev TEXT, name TEXT, resolved INT);
        CREATE TABLE mm_remedy(id INTEGER PRIMARY KEY, book_id TEXT, name TEXT,
                               abbrev TEXT, canonical_name TEXT, common_name TEXT,
                               kingdom TEXT, family TEXT);
        CREATE TABLE mm_symptom(id INTEGER PRIMARY KEY, remedy_id INT, chapter TEXT,
                                text TEXT, grade INT);
    """)
    b = d["book"]
    cur.execute("INSERT INTO book VALUES(?,?,?,?,?,?,?,?,?,?)",
                (b.get("id"), t, d.get("schema_version"), b.get("title"),
                 b.get("author"), b.get("year"), b.get("publisher"),
                 b.get("source_file"), b.get("extraction_date"),
                 json.dumps(b.get("counts", {}))))
    bid = b.get("id")
    if t == "repertory":
        for si, sec in enumerate(d.get("sections", [])):
            cur.execute("INSERT INTO section(book_id,ordinal,title) VALUES(?,?,?)",
                        (bid, si, sec["title"]))
            sid = cur.lastrowid
            for r in sec["rubrics"]:
                cur.execute("INSERT INTO rubric(book_id,section_id,text,parent,note) "
                            "VALUES(?,?,?,?,?)",
                            (bid, sid, r.get("text"), r.get("parent"), r.get("note")))
                rid = cur.lastrowid
                for x in r.get("remedies", []):
                    cur.execute("INSERT INTO remedy_link VALUES(?,?,?,?,?)",
                                (rid, x["abbrev"], x.get("grade"), x.get("polarity"),
                                 x.get("note")))
    elif t == "materia_medica":
        for rem in d.get("remedies", []):
            cur.execute("INSERT INTO mm_remedy(book_id,name,abbrev,canonical_name,"
                        "common_name,kingdom,family) VALUES(?,?,?,?,?,?,?)",
                        (bid, rem.get("name"), rem.get("abbrev"),
                         rem.get("canonical_name"), rem.get("common_name"),
                         rem.get("kingdom"), rem.get("family")))
            mid = cur.lastrowid
            for sym in rem.get("symptoms", []):
                cur.execute("INSERT INTO mm_symptom(remedy_id,chapter,text,grade) "
                            "VALUES(?,?,?,?)",
                            (mid, sym.get("chapter"), sym.get("text"), sym.get("grade")))
    for k, v in d.get("remedy_index", {}).items():
        cur.execute("INSERT INTO remedy_index VALUES(?,?,?,?)",
                    (bid, k, v.get("name"), 1 if v.get("resolved") else 0))
    cur.execute("CREATE INDEX ix_rubric_section ON rubric(section_id)")
    cur.execute("CREATE INDEX ix_remedy_rubric ON remedy_link(rubric_id)")
    cur.execute("CREATE INDEX ix_remedy_abbrev ON remedy_link(abbrev)")
    cur.execute("CREATE INDEX ix_symptom_remedy ON mm_symptom(remedy_id)")
    con.commit()
    cur.execute("VACUUM")
    con.commit()
    con.close()
    print(f"wrote {args.db} ({round(os.path.getsize(args.db)/1e6,1)} MB) from {args.json}")


def build_parser():
    p = argparse.ArgumentParser(description="OMM extraction pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--src", required=True)
        sp.add_argument("--slug", required=True)
        sp.add_argument("--title", default="")
        sp.add_argument("--author", default="")
        sp.add_argument("--year", type=int, default=None)
        sp.add_argument("--publisher", default="")
        sp.add_argument("--out", required=True)

    r = sub.add_parser("extract-repertory")
    common(r)
    r.add_argument("--aliases", default="scripts/remedy_aliases.csv")
    r.add_argument("--qc", default="data/processed/qc_report.md")
    r.add_argument("--hierarchy", action="store_true",
                   help="prefix lower-case sub-rubrics with the last heading")
    r.add_argument("--caps-chapters", action="store_true",
                   help="treat a short ALL-CAPS line as a chapter heading")
    r.add_argument("--trailing", action="store_true",
                   help="rubric '. ' remedy-list grammar (Drake-style)")
    r.add_argument("--flat", action="store_true",
                   help="single General section, no chapter detection")
    r.add_argument("--rejoin", action="store_true",
                   help="re-glue OCR lines broken mid-sentence before parsing")
    r.add_argument("--space-remedies", action="store_true",
                   help="remedy lists are space-separated (Lippe/Bryant/Clarke)")
    r.add_argument("--indent", action="store_true",
                   help="pretty-print JSON (default is compact)")
    r.add_argument("--min-rubrics", type=int, default=1,
                   help="drop sections with fewer than N rubrics")
    r.add_argument("--skip-to-rubric", action="store_true",
                   help="ignore everything before the first real rubric")
    r.add_argument("--caps-any", action="store_true",
                   help="any short ALL-CAPS line is a chapter heading")
    r.add_argument("--lippe", action="store_true",
                   help="Lippe grammar: N. CHAPTER. + 'text, Rem. Rem.' rubrics")
    r.add_argument("--jahr", action="store_true",
                   help="Jahr Part II: CHAP headings + ALL-CAPS conditions + prose")
    r.add_argument("--ruoff", action="store_true",
                   help="condition -> 'Remedy - clinical note' grammar (Ruoff-style)")
    r.add_argument("--fuzzy-sections", action="store_true",
                   help="merge OCR-variant section titles")
    r.set_defaults(func=cmd_extract_repertory)

    m = sub.add_parser("extract-mm")
    common(m)
    m.add_argument("--qc", default="data/processed/qc_report.md")
    m.add_argument("--rejoin", action="store_true",
                   help="re-glue OCR lines broken mid-sentence")
    m.add_argument("--space-remedies", action="store_true",
                   help="remedy lists are space-separated")
    m.add_argument("--indent", action="store_true",
                   help="pretty-print JSON (default is compact)")
    m.add_argument("--bell", action="store_true",
                   help="Bell-style: numbered remedy headings + labelled groups")
    m.set_defaults(func=cmd_extract_mm)

    v = sub.add_parser("validate")
    v.add_argument("--json", required=True)
    v.set_defaults(func=cmd_validate)

    sq = sub.add_parser("to-sqlite")
    sq.add_argument("--json", required=True)
    sq.add_argument("--db", required=True)
    sq.set_defaults(func=cmd_to_sqlite)

    c = sub.add_parser("classify")
    c.add_argument("--src", required=True)
    c.set_defaults(func=cmd_classify)
    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
