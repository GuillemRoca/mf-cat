#!/usr/bin/env python3
"""Offline preview of text lines as the game draws them (TextDrawCharacter, src/text.c).

  render.py OUT.png "line" ["line"...] [--vanilla] [--scale N]

Uses the extracted font (data/text_characters.gfx) and sCharacterWidths, with the Catalan glyph
and width overrides unless --vanilla. A glyph is two stacked 8x8 tiles (16 px wide when its
width is over 8, the second tile masked to the width) ORed into the line at the pen position,
so a glyph drawn wider than its width overlaps the next one exactly as in the game. Font
pixels: 2 = fill, 3 = outline; {COLOR(n)} adds 2n to both. Lines are 224 px wide; pixels past
the limit are shown in red. The preview colours are approximations of the game's palettes.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import font as fontlib  # noqa: E402

from PIL import Image  # noqa: E402

BACKGROUND = (16, 32, 56)
OUTLINE = (8, 8, 24)
FILLS = {0: (255, 255, 255), 1: (120, 220, 255), 2: (255, 80, 220), 3: (255, 230, 60),
         4: (255, 90, 90), 5: (120, 255, 120), 6: (255, 160, 60)}


def draw_line(text, font, w, canvas, y0):
    pen, color = 0, 0
    for kind, v, _ in catext.tokens(text):
        if kind == "gap":
            pen += v & 0xFF
        elif kind == "indent":
            pen = v & 0xFF
        elif kind == "color":
            color = v & 0xFF
        elif kind == "char":
            width = w[v] if v < len(w) else 10
            cols = width if width > 8 else 8
            g = fontlib.glyph_pixels(font, v)
            for y in range(16):
                for c in range(cols):
                    val = g[y][c]
                    if val:
                        old = canvas.get((pen + c, y0 + y), (0, color))[0]
                        canvas[(pen + c, y0 + y)] = (old | val, color)
            pen += width
    return pen


def render(lines, out, vanilla=False, scale=3):
    font = fontlib.load(vanilla)
    w = catext.widths(catalan=not vanilla)
    canvas = {}
    ends = [draw_line(line, font, w, canvas, i * 16) for i, line in enumerate(lines)]
    img = Image.new("RGB", (240, 16 * len(lines)), BACKGROUND)
    for (x, y), (val, col) in canvas.items():
        if 0 <= x < 240:
            rgb = OUTLINE if val & 1 else FILLS.get(col, FILLS[0])
            img.putpixel((x, y), rgb if x < catext.LINE_LIMIT else (255, 0, 0))
    for y in range(img.height):
        img.putpixel((catext.LINE_LIMIT, y), (255, 0, 0))
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    img.save(out)
    return ends


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("lines", nargs="+")
    ap.add_argument("--vanilla", action="store_true")
    ap.add_argument("--scale", type=int, default=3)
    a = ap.parse_args()
    for line, end in zip(a.lines, render(a.lines, a.out, a.vanilla, a.scale)):
        print(f"{end:3} px  {line}")
