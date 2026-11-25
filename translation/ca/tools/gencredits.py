#!/usr/bin/env python3
"""Generates translation/ca/build/include/ca/credits.inc for LANG_CA=1: sCredits with the
Catalan translators from translation/ca/credits.txt.

The input is the vanilla array (the `#else // !LANG_CA` branch around
`#include "ca/credits.inc"` in src/data/ending_data.c). The US credits have no TRANSLATION
section, so the "CATALAN" block is a group of its own, right before EXECUTIVE PRODUCER: it
takes the place of the middle one of the three spacers that separate the staff groups there.

The array has a fixed size and the decomp is not shiftable, so the table is rewritten in place
with the same number of entries. The credits scroll one row at a time (WHITE_BIG lines take 2
rows, the others 1) and stop at the END line; to keep them exactly as long as vanilla, in time
with the music, any row or entry added is taken from the empty lines between the executive
producer and the copyright (two blank lines become one empty big line: same rows, one entry
less). Entries and rows are both checked to come out as in vanilla.

usage: gencredits.py OUTPUT [--vanilla]   (--vanilla: reproduce vanilla, plumbing self-test)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src" / "data" / "ending_data.c"
CREDITS = ROOT / "translation" / "ca" / "credits.txt"

ENTRY_RE = re.compile(r'\[(\d+)\] = \{\s*\.type = CREDIT_LINE_TYPE_(\w+),\s*\.text = "((?:[^"\\]|\\.)*)"\s*\}')
HEADER_RE = re.compile(r"const struct CreditsEntry sCredits\[(\d+)\] = \{")
BIG = "WHITE_BIG"
ROWS = {BIG: 2, "END": 9}                    # CreditsDisplayLine, src/ending.c; the rest take 1
BLUE_OK = re.compile(r"[A-Z .,&]+")          # the blue font: capitals, . , &
NAME_OK = re.compile(r"[A-Za-z .,-]+")       # WHITE_BIG: letters, space, . , - (no accents)
LINE_CHARS = 30                              # a credits line is 30 characters wide
TEXT_SIZE = 35                               # struct CreditsEntry: u8 text[35]
BEFORE = "EXECUTIVE PRODUCER"                # the group the Catalan block comes before
BEFORE_COPYRIGHT = "ALL_RIGHTS"


def rows(entries):
    return sum(ROWS.get(t, 1) for t, _ in entries)


def vanilla():
    src = SRC.read_text(encoding="utf-8")
    m = re.search(r'#ifdef LANG_CA\n#include "ca/credits.inc"[^\n]*\n#else // !LANG_CA\n(.*?)\n#endif // LANG_CA', src, re.S)
    if not m:
        sys.exit(f"error: no LANG_CA block around sCredits in {SRC}")
    size = int(HEADER_RE.search(src).group(1))
    entries = [(t, x) for _, t, x in ENTRY_RE.findall(m.group(1))]
    if len(entries) != size:
        sys.exit(f"error: parsed {len(entries)} credits entries, the array has {size}")
    return entries


def read_credits(path=CREDITS):
    heading, names = None, []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        key, _, value = (p.strip() for p in line.partition("="))
        if key == "heading" and BLUE_OK.fullmatch(value):
            heading = value
        elif key == "name" and NAME_OK.fullmatch(value) and len(value) <= LINE_CHARS:
            names.append(value)
        else:
            sys.exit(f"error: {path}:{n}: expected `heading = A-Z text` or `name = Name` (letters without"
                     f" accents, {LINE_CHARS} characters at most)")
    if not heading or not names:
        sys.exit(f"error: {path} needs a heading and at least one name")
    return heading, names


def centred(text):
    return " " * ((LINE_CHARS - len(text)) // 2) + text


def catalan(entries):
    heading, names = read_credits()
    # The staff groups are separated by three spacers (a blank blue line and two empty lines).
    # The Catalan block takes the place of the middle spacer before EXECUTIVE PRODUCER, so it
    # has one spacer above it and one below.
    ep = next(i for i, (t, x) in enumerate(entries) if t == "BLUE" and x.strip() == BEFORE)
    spacers = entries[ep - 9:ep]
    if [t for t, _ in spacers] != ["BLUE", BIG, BIG] * 3 or any(x.strip() for _, x in spacers):
        sys.exit(f"error: the lines before {BEFORE} are not the three expected spacers")
    block = [("BLANK", ""), ("BLUE", centred(heading))]
    for name in names:
        block += [("BLANK", ""), (BIG, centred(name))]
    out = entries[:ep - 6] + block + entries[ep - 3:]
    # Give back the difference in rows and entries from the empty lines before the copyright.
    need_rows = rows(out) - rows(entries)
    need_entries = len(out) - len(entries)
    stop = next(i for i, (t, _) in enumerate(out) if t == BEFORE_COPYRIGHT)
    first = ep - 6 + len(block) + 3 + 3  # after EXECUTIVE PRODUCER, its blank line and its name

    def empties(kind):
        return [i for i in range(stop - 1, first, -1) if out[i] == (kind, "") or (out[i][0] == kind and not out[i][1].strip())]

    while need_rows > 0:
        big, blank = empties(BIG), empties("BLANK")
        if need_rows >= 2 and big:
            del out[big[0]]
            need_rows -= 2
        elif blank:
            del out[blank[0]]
            need_rows -= 1
        else:
            break
        need_entries -= 1
        stop -= 1
    while need_entries > 0:  # two blank lines become one empty big line: same rows, one entry less
        blank = empties("BLANK")
        if len(blank) < 2:
            break
        out[blank[0]] = (BIG, "")
        del out[blank[1]]
        need_entries -= 1
        stop -= 1
    while need_entries < 0:  # and the other way round
        big = empties(BIG)
        if not big:
            break
        out[big[0]:big[0] + 1] = [("BLANK", ""), ("BLANK", "")]
        need_entries += 1
        stop += 1
    if len(out) != len(entries) or rows(out) != rows(entries):
        sys.exit(f"error: can't keep the credits' size: {len(out)} entries and {rows(out)} rows, vanilla has"
                 f" {len(entries)} and {rows(entries)}")
    return out


def table(vanilla_only=False):
    """[(type, text)] of the credits as built."""
    entries = vanilla()
    return entries if vanilla_only else catalan(entries)


def pack(entries):
    """The table as the bytes of struct CreditsEntry[] (u8 type, u8 text[35])."""
    types = {"BLUE": 0, "RED": 1, "WHITE_BIG": 2, "BLANK": 5, "END": 6, "ALL_RIGHTS": 10,
             "THE_COPYRIGHT": 11, "SCENARIO": 12, "RESERVED": 13}
    out = bytearray()
    for t, x in entries:
        text = x.encode("ascii")
        if len(text) > TEXT_SIZE - 1:
            sys.exit(f"error: credits line too long: {x!r}")
        out += bytes([types[t]]) + text + bytes(TEXT_SIZE - len(text))
    return bytes(out)


def render(entries):
    lines = ["// Generated by translation/ca/tools/gencredits.py from credits.txt. Do not edit."]
    for n, (t, x) in enumerate(entries):
        lines.append(f'\t[{n}] = {{\n\t\t.type = CREDIT_LINE_TYPE_{t},\n\t\t.text = "{x}"\n\t}},')
    lines[-1] = lines[-1].rstrip(",")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("output")
    ap.add_argument("--vanilla", action="store_true")
    a = ap.parse_args()
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(table(a.vanilla)), encoding="utf-8")
