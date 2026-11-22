#!/usr/bin/env python3
"""Recomputes the centring {GAP(n)} at the start of each banner line, as the vanilla text is
laid out.

  gap.py check      list Catalan lines whose GAP is stale (exit 1 if any)
  gap.py fix        rewrite the stale GAPs in translation/ca/text/*.txt
  gap.py vanilla    recompute every vanilla line of the five Western languages and report each
                    difference: the rule must reproduce every English GAP (exit 1 otherwise)

Rule (reverse-engineered from the shipped text; src/text.c only advances the pen by GAP):
  message, location   GAP = round_half_even((220 - w) / 2) on every line, where w is the sum of
                      the line's glyph widths. A line that fills the banner (GAP of 0 or less)
                      has no GAP at all; an empty line is {GAP(110)}.
  navigation, pause, monologue   no GAPs: the text is left-aligned, or centred by the game.
Lines with an {INDENT(n)} are positions (the Yes/No columns of a prompt) and are never touched.
The rule gives every English GAP and all but a few of the other languages' (the Spanish and
one Italian line were centred by hand a pixel or two off).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402

CENTRED = ("message", "location")
LEAD_GAP = re.compile(r"^\{GAP\((\d+)\)\}")


def rule(category):
    if category in CENTRED:
        return lambda w: round((220 - w) / 2)  # Python rounds half to even
    return None


def recompute(category, text, w):
    """Returns (new text, [(line number, old gap or None, new gap or None)])."""
    f = rule(category)
    if f is None:
        return text, []
    lines, changes = text.split("\\n"), []
    for n, line in enumerate(lines):
        if "{INDENT(" in line:
            continue
        m = LEAD_GAP.match(line)
        rest = line[m.end():] if m else line
        if "{GAP(" in rest:
            continue  # gaps inside the line are layout the translator chose
        old = int(m.group(1)) if m else None
        new = f(catext.line_layout(rest, w)["glyph_width"])
        new = new if new > 0 else None
        if new != old:
            changes.append((n + 1, old, new))
            lines[n] = (f"{{GAP({new})}}" if new else "") + rest
    return "\\n".join(lines), changes


def show(gap):
    return "no GAP" if gap is None else f"GAP({gap})"


def cmd_vanilla():
    w = catext.widths(catalan=False)
    failed = 0
    for language in catext.WESTERN:
        total = diffs = 0
        for category in CENTRED:
            for idx, text in catext.vanilla_text(category, language).items():
                total += sum(1 for l in text.split("\\n") if "{INDENT(" not in l)
                for line, old, new in recompute(category, text, w)[1]:
                    diffs += 1
                    print(f"{language} {idx} line {line}: shipped {show(old)}, the rule gives {show(new)}")
        print(f"{language}: {total - diffs}/{total} recomputed GAPs match the shipped ones")
        if language == catext.SLOT:
            failed = diffs
    return failed


def cmd_check(fix):
    w = catext.widths(catalan=True)
    stale = 0
    for category in CENTRED:
        entries, path = catext.read_translation(category)
        if not entries:
            continue
        text_lines = path.read_text(encoding="utf-8").split("\n")
        for idx, (text, lineno) in entries.items():
            new, changes = recompute(category, text, w)
            for line, old, g in changes:
                stale += 1
                print(f"{path.relative_to(catext.ROOT)}:{lineno}: {idx} line {line}: {show(old)} -> {show(g)}")
            if changes and fix:
                text_lines[lineno - 1] = text_lines[lineno - 1].replace(f'"{text}"', f'"{new}"', 1)
        if fix:
            path.write_text("\n".join(text_lines), encoding="utf-8")
    if fix and stale:
        print(f"fixed {stale} GAPs")
    return stale


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "fix", "vanilla"])
    a = ap.parse_args()
    if a.cmd == "vanilla":
        sys.exit(1 if cmd_vanilla() else 0)
    stale = cmd_check(a.cmd == "fix")
    sys.exit(1 if stale and a.cmd == "check" else 0)
