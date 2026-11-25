#!/usr/bin/env python3
"""Composes the Catalan HUD label: ENERGIA over the energy counter.

  gfx_hud.py            writes translation/ca/gfx/hud/common.png
  gfx_hud.py --check    the file is what this tool builds (CI)

The label is the top-left sprite of the HUD (src/hud.c): 32 x 16 px at tile 0x50, the first
four tiles of two rows of hud/common.gfx. Only three tiles of the top row belong to the label:
the game redraws the fourth (and the four of the next sprite) with the energy tanks whenever
the energy changes (HudDrawEnergy copies them to VRAM_OBJ + 0xA60), so the label has 24 px.
ENERGY took 23 of them, a box with a margin column at each end. ENERGIA is 23 px of letters:
the box keeps its margin on the right, where the tanks follow, and starts at the edge of the
screen on the left. The digits under the label are drawn by the game. The sheet is
uncompressed and edited in place.

The letters are the label's own; I and A, which ENERGY doesn't have, are drawn here.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gfx  # noqa: E402
import gfx_pause as gp  # noqa: E402

LABEL = "ENERGIA"
OUT = catext.CA / "gfx" / "hud" / "common.png"
X0, X1, Y0 = 128, 151, 0          # the label's three tiles
INK, PAPER = 2, 0xE


def build():
    rows = gfx.tiles_to_rows(gfx.vanilla_tiles(gfx.assets()["hud/common"]))
    glyphs = {}
    gp.harvest(glyphs, rows, "ENERGY", 130, 150, 2, 5, lambda v: v == INK)
    glyphs["I"] = gp.art("#", "#", "#", "#", "#")
    glyphs["A"] = gp.art(".#.", "#.#", "###", "#.#", "#.#")
    font = gp.Font(glyphs)
    width = font.measure(LABEL)
    if width > X1 - X0:
        sys.exit(f"error: {LABEL} is {width} px, the label has {X1 - X0} and a margin")
    x = X1 - width                                   # one column of margin on the right
    gp.fill(rows, X0, X1, Y0, Y0 + 7, 0)
    gp.fill(rows, max(X0, x - 1), X1, 1, 7, PAPER)   # the box
    font.draw(rows, x, 2, LABEL, gp.const(INK))
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    rows = build()
    if a.check:
        from PIL import Image
        if Image.open(OUT).tobytes() != bytes(v for row in rows for v in row):
            sys.exit(f"error: {OUT} is not what gfx_hud.py builds: run it again")
        print("HUD graphic is current")
    else:
        gp.save_png(rows, OUT)
        print(f"wrote {OUT}")
