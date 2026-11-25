#!/usr/bin/env python3
"""Composes the Catalan erase-all-data screen (L and R held at power-on).

  gfx_erase.py            writes translation/ca/gfx/menus/erase_sram/question.png and confirm.png
  gfx_erase.py --check    the files are what this tool builds (CI)

Each language has two sheets of 128 tiles (256 x 32 px), LZ77 data with no entry in
database.json, listed in pairs in the table at 0x79c228 (data/Blob_79c170_79c27c.bin,
src/text.c; English at 0x79c238 and 0x79c23c):
  the first asks "Do you want to / erase all saved data?", the second "Are you sure you want /
  to erase all saved data?", each with its answers, "No" over "Yes", at x = 200.
They are the game's own font on a flat background (colour 13 in the first sheet, 6 in the
second): fill 2, outline 3, a 16 px line per row of the sheet. Letters take the widths the
game gives them, a space takes 8 px, and both lines of the question start at the same x, a
multiple of 8 that centres the longer one in the 192 px the question's sprites show (x 16 in
the first English sheet, x 0 in the second). The answers' sprites show x 192-255.

So the Catalan sheets are typed with the font by that rule. The tool checks the rule first:
typing the English questions must give the vanilla sheets. Not quite pixel for pixel: those
were typed with a slightly different cut of a few letters (w, r, e, s) and have four stray
pixels, 77 pixels in all, so the check allows that many and no more. Every word falls where
the rule puts it.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import font as fontlib  # noqa: E402
import gfx  # noqa: E402
import gfx_pause as gp  # noqa: E402
import render  # noqa: E402

OUT = catext.CA / "gfx" / "menus" / "erase_sram"
SHEETS = {  # file: (asset, the two lines of the question, the two answers)
    "question": ("menus/erase_sram/question", ["Vols esborrar totes", "les dades guardades？"], ["No", "Sí"]),
    "confirm": ("menus/erase_sram/confirm", ["Segur que vols esborrar", "totes les dades？"], ["No", "Sí"]),
}
VANILLA = {"question": ["Do you want to", "erase all saved data？"],
           "confirm": ["Are you sure you want", "to erase all saved data？"]}
QUESTION_W, ANSWER_X, SPACE = 192, 200, 8
TOLERANCE = {"question": 11, "confirm": 66}   # pixels the vanilla sheets differ from the font's typing


def typed(lines, answers, paper):
    """A sheet: the question's lines, centred on a tile, and the answers at ANSWER_X."""
    font, w = fontlib.load(), catext.widths(catalan=True)
    lines = [line.replace(" ", "{GAP(%d)}" % SPACE) for line in lines]
    width = max(catext.line_layout(line, w)["pen_end"] for line in lines)
    if width > QUESTION_W:
        sys.exit(f"error: a line of the erase screen is {width} px, over {QUESTION_W}")
    x0 = (QUESTION_W - width) // 2 // 8 * 8
    canvas = {}
    for i, (line, answer) in enumerate(zip(lines, answers)):
        text = "{INDENT(%d)}%s{INDENT(%d)}%s" % (x0, line, ANSWER_X, answer) if x0 else \
            "%s{INDENT(%d)}%s" % (line, ANSWER_X, answer)
        render.draw_line(text, font, w, canvas, i * 16)
    rows = [[paper] * 256 for _ in range(32)]
    for (x, y), (val, _) in canvas.items():
        rows[y][x] = val
    return rows


def build():
    out = {}
    for name, (asset, lines, answers) in SHEETS.items():
        vanilla = gfx.tiles_to_rows(gfx.vanilla_tiles(gfx.assets()[asset]))
        paper = max(set(v for row in vanilla for v in row), key=lambda c: sum(row.count(c) for row in vanilla))
        # the rule must give the vanilla sheet back, but for a few letters cut differently
        trial = typed(VANILLA[name], ["No", "Yes"], paper)
        bad = [(x, y) for y in range(32) for x in range(256) if trial[y][x] != vanilla[y][x]]
        if len(bad) > TOLERANCE[name]:
            sys.exit(f"error: typing the English {name} changes {len(bad)} pixels of the vanilla sheet"
                     f" (expected {TOLERANCE[name]}), first at {bad[0]}")
        out[name] = typed(lines, answers, paper)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sheets = build()
    for name, rows in sheets.items():
        path = OUT / f"{name}.png"
        if a.check:
            from PIL import Image
            if Image.open(path).tobytes() != bytes(v for row in rows for v in row):
                sys.exit(f"error: {path} is not what gfx_erase.py builds: run it again")
        else:
            gp.save_png(rows, path)
    print("erase screen graphics are current" if a.check else f"wrote question.png and confirm.png in {OUT}")
