#!/usr/bin/env python3
"""Generates translation/ca/build/include/ca/credits.inc for LANG_CA=1: sCredits with the
Catalan translators from translation/ca/credits.txt.

The input is the vanilla array (the `#else // !LANG_CA` branch around
`#include "ca/credits.inc"` in src/data/ending_data.c). The US credits have no TRANSLATION
section; the closest equivalent is the LOCALIZATION block of "NOA ENGLISH LOCALIZATION". A
"CATALAN" block goes right after its last name, laid out like the blocks around it (a blank
coloured line, two empty lines, the blue heading, a blank line, the name).

The array has a fixed size and the decomp is not shiftable, so the table is rewritten in place
with the same number of entries. The credits scroll one row at a time (WHITE_BIG lines take 2
rows, the others 1) and stop at the END line; to keep them exactly as long as vanilla, in time
with the music, the rows added are taken from the empty lines between the executive producer
and the copyright. Entries and rows are both checked to come out as in vanilla.

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
AFTER = "LOCALIZATION"                       # the block the Catalan one follows
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
    # the LOCALIZATION block: its heading, then (BLANK, name) pairs
    start = next(i for i, (t, x) in enumerate(entries) if t == "BLUE" and x.strip() == AFTER)
    end = start + 1
    while entries[end][0] == "BLANK" and entries[end + 1][0] == BIG and entries[end + 1][1].strip():
        end += 2
    separator = entries[end:end + 3]  # the blank coloured line and two empty lines between blocks
    if [t for t, _ in separator] != ["RED", BIG, BIG] or any(x.strip() for _, x in separator):
        sys.exit("error: the lines after the LOCALIZATION block are not the expected separator")
    block = list(separator) + [("BLUE", centred(heading))]
    for name in names:
        block += [("BLANK", ""), (BIG, centred(name))]
    out = entries[:end] + block + entries[end:]
    # give back the rows and the entries from the empty lines before the copyright
    need_rows, need_entries = rows(block), len(block)
    stop = next(i for i, (t, _) in enumerate(out) if t == BEFORE_COPYRIGHT)
    i = stop - 1
    while (need_rows or need_entries) and i > end + len(block):
        t, x = out[i]
        if x.strip() or t not in (BIG, "BLANK"):
            break
        r = ROWS.get(t, 1)
        # take big lines while the rows left allow it, so that entries and rows run out together
        if r <= need_rows and need_entries and (need_rows - r) >= (need_entries - 1):
            del out[i]
            need_rows -= r
            need_entries -= 1
        i -= 1
    if need_rows or need_entries or len(out) != len(entries) or rows(out) != rows(entries):
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
