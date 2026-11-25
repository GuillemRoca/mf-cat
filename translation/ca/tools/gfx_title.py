#!/usr/bin/env python3
"""Composes the Catalan title screen prompt: PREM START.

  gfx_title.py            writes translation/ca/gfx/menus/title_screen/objects.png
  gfx_title.py --check    the file is what this tool builds (CI)

PRESS START is three 32 x 16 sprites, tiles 192-203 and the row under them (x 0-95, y 48-63 of
menus/title_screen/objects.gfx.lz); the sheet has a second copy in the unlit shading right
below (y 64-79). Its letters are cells that stand side by side, each with its own outline:
P, R and E are taken from PRESS, the M from START GAME (same font, same two shadings, at
y 16-31 and 32-47), and START stays. The new prompt is centred where the old one was.

The START GAME / Language rows of the sheet are the menu of the other regions' ROMs; the US
game goes from this prompt straight to the file select, so they are left alone.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gfx  # noqa: E402
import gfx_pause as gp  # noqa: E402

OUT = catext.CA / "gfx" / "menus" / "title_screen" / "objects.png"
WORDS = ["PREM", "START"]
H = 12
# letter: (x0, x1) of its cell, outline columns included, and the word it is in
CELLS = {"P": (11, 17, "press"), "R": (18, 24, "press"), "E": (25, 32, "press"), "M": (66, 74, "game")}
START = (51, 85)                    # the word START, whole
OLD = (11, 85)                      # PRESS START
GAP = 4                             # px between the words, as in PRESS START
COPIES = [{"press": 52, "game": 20}, {"press": 68, "game": 36}]   # y of each shading


def block(rows, x0, x1, y):
    return [rows[y + r][x0:x1 + 1] for r in range(H)]


def build():
    rows = gfx.tiles_to_rows(gfx.vanilla_tiles(gfx.assets()["menus/title_screen/objects"]))
    vanilla = [r[:] for r in rows]
    if WORDS[1] != "START":
        sys.exit("error: the second word is taken whole from the sheet: it must be START")
    for copy in COPIES:
        parts = [block(vanilla, *CELLS[ch][:2], copy[CELLS[ch][2]]) for ch in WORDS[0]]
        for ch, part in zip(WORDS[0], parts):   # a cell is closed by outline on both sides
            if any(row[0] == 0 and row[-1] == 0 for row in part[2:4]):
                sys.exit(f"error: the cell of {ch} is not where it should be")
        parts.append([[0] * GAP for _ in range(H)])
        parts.append(block(vanilla, *START, copy["press"]))
        line = [[v for part in parts for v in part[r]] for r in range(H)]
        width = len(line[0])
        if width > OLD[1] - OLD[0] + 1:
            sys.exit("error: the prompt is wider than PRESS START")
        y = copy["press"]
        gp.fill(rows, 0, 95, y, y + H - 1, 0)
        x = OLD[0] + (OLD[1] - OLD[0] + 1 - width) // 2
        for r in range(H):
            rows[y + r][x:x + width] = line[r]
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    rows = build()
    if a.check:
        from PIL import Image
        if Image.open(OUT).tobytes() != bytes(v for row in rows for v in row):
            sys.exit(f"error: {OUT} is not what gfx_title.py builds: run it again")
        print("title screen graphic is current")
    else:
        gp.save_png(rows, OUT)
        print(f"wrote {OUT}")
