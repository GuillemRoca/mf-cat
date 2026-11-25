#!/usr/bin/env python3
"""Composes the Catalan labels of the file select screen: ENERGIA, TEMPS and COBERTA.

  gfx_file_select.py            writes translation/ca/gfx/menus/file_select/obj.png
  gfx_file_select.py --check    the file is what this tool builds (CI)

The screen's sprite sheet is LZ77 data at 0x73dc20 inside data/Blob_73cfac_7478a0.bin (512
tiles), loaded by address in asm/disasm_0x0809e598.s. Its labels are light letters ('2') with
a dark outline ('3') in two condensed fonts:
  ENERGY, TIME   9 rows; each is one 32 x 16 sprite (tiles 0x118 and 0x11c)
  SECTOR n, MAIN DECK   11 rows; MAIN DECK is a 32 x 16 and a 16 x 16 sprite (tiles 0x8a, 0x8e)
The sheet also holds the area names of four other languages, among them the Spanish CUBIERTA,
which gives COBERTA its letters (the O is SECTOR's). SECTOR and its digits stay.

The outlines are drawn by hand (some corners are open, some closed, and the spacing is not
always one column), so a letter is taken with the outline pixels it has in the sheet, and
letters drawn here get the common pattern: every pixel that touches the letter, without the
four corners outside its box. The tool checks its cutting first: ENERGY and SECTOR put together
again from the letters it took must be the vanilla labels, light pixel for light pixel.

ENERGIA is one letter longer than ENERGY in a sprite that ENERGY nearly filled (31 of 32 px),
so its two E's are 3 px wide instead of 4. TEMPS has the room it needs.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gfx  # noqa: E402
import gfx_pause as gp  # noqa: E402

OUT = catext.CA / "gfx" / "menus" / "file_select" / "obj.png"
ENERGY, TIME, AREA = "ENERGIA", "TEMPS", "COBERTA"
INK, EDGE = 2, 3


def light(v):
    return v == INK


class Glyph:
    """A letter: its light pixels (rows of True/None) and its outline, as (dx, dy) offsets
    from its top-left corner."""

    def __init__(self, ink, halo):
        self.ink, self.halo, self.width = ink, halo, len(ink[0])


def touches(ink, dx, dy):
    return any(0 <= dy + j < len(ink) and 0 <= dx + i < len(ink[0]) and ink[dy + j][dx + i]
               for i in (-1, 0, 1) for j in (-1, 0, 1))


def take(rows, x0, x1, y, h):
    """The letter between columns x0 and x1 of the sheet, with the outline it has there."""
    ink = [[True if light(v) else None for v in rows[y + r][x0:x1 + 1]] for r in range(h)]
    halo = {(dx, dy) for dy in range(-1, h + 1) for dx in range(-1, x1 - x0 + 2)
            if rows[y + dy][x0 + dx] == EDGE and touches(ink, dx, dy)}
    return Glyph(ink, halo)


def drawn(*art):
    """A letter drawn here: outlined all round, except the corners outside its box."""
    ink = gp.art(*art)
    h, w = len(ink), len(ink[0])
    halo = {(dx, dy) for dy in range(-1, h + 1) for dx in range(-1, w + 1)
            if not (0 <= dy < h and 0 <= dx < w and ink[dy][dx]) and touches(ink, dx, dy)
            and (dx, dy) not in ((-1, -1), (w, -1), (-1, h), (w, h))}
    return Glyph(ink, halo)


def take_word(font, rows, word, x0, x1, y, h, cuts=()):
    """Takes the letters of a word: split where a column has no light pixel, or at `cuts`
    (the first column of a letter that touches the one before it)."""
    spans, start = [], None
    for x in range(x0, x1 + 2):
        lit = x <= x1 and any(light(rows[y + r][x]) for r in range(h))
        if lit and (start is None or x in cuts):
            if start is not None:
                spans.append((start, x - 1))
            start = x
        elif not lit and start is not None:
            spans.append((start, x - 1))
            start = None
    letters = word.replace(" ", "")
    if len(spans) != len(letters):
        sys.exit(f"error: {word}: found {len(spans)} letters between x={x0} and x={x1}")
    for ch, (a, b) in zip(letters, spans):
        font.setdefault(ch, take(rows, a, b, y, h))


def fonts(rows):
    small, big = {}, {}
    take_word(small, rows, "ENERGY", 193, 223, 72, 7, cuts=(218,))        # G and Y touch
    take_word(small, rows, "TIME", 225, 246, 72, 7)
    small["e"] = drawn("###", "#..", "#..", "##.", "#..", "#..", "###")          # a narrower E
    small["A"] = drawn(".##.", "#..#", "#..#", "####", "#..#", "#..#", "#..#")
    small["P"] = drawn("###.", "#..#", "#..#", "###.", "#...", "#...", "#...")
    small["S"] = drawn(".###", "#...", "#...", ".##.", "...#", "...#", "###.")
    take_word(big, rows, "SECTOR", 0, 31, 36, 9)
    take_word(big, rows, "MAIN DECK", 80, 126, 36, 9)
    take_word(big, rows, "CUBIERTA", 214, 255, 100, 9, cuts=(245,))        # its R and T touch
    return small, big


def label(rows, box, x, y, font, text, touching=()):
    """Clears a sprite's box and writes the text from x: letters one outline column apart,
    except the pairs in `touching`, which stand against each other."""
    x0, x1, y0, y1 = box
    gp.fill(rows, x0, x1, y0, y1, 0)
    halo = set()
    for i, ch in enumerate(text):
        if ch == " ":
            x += 2
            continue
        g = font[ch]
        gp.put(rows, x, y, g.ink, gp.const(INK))
        halo |= {(x + dx, y + dy) for dx, dy in g.halo}
        x += g.width + (0 if text[i:i + 2] in touching else 1)
    if any(not (x0 <= hx <= x1 and y0 <= hy <= y1) for hx, hy in halo):
        sys.exit(f"error: {text} doesn't fit its sprite")
    for hx, hy in halo:
        if rows[hy][hx] == 0:
            rows[hy][hx] = EDGE


BOX_ENERGY, BOX_TIME = (192, 223, 64, 79), (224, 255, 64, 79)
BOX_SECTOR, BOX_AREA = (0, 31, 32, 47), (80, 127, 32, 47)


def build():
    rows = gfx.tiles_to_rows(gfx.vanilla_tiles(gfx.assets()["menus/file_select/obj"]))
    vanilla = [r[:] for r in rows]
    small, big = fonts(rows)
    # the letters taken must give the vanilla labels back: every light pixel, and the outline
    # but for the corners the sheet draws differently on its two E's
    trial = [r[:] for r in rows]
    label(trial, BOX_ENERGY, 194, 72, small, "ENERGY", touching=("GY",))
    label(trial, BOX_SECTOR, 1, 36, big, "SECTOR")
    bad = [(x, y) for y in range(len(rows)) for x in range(256) if trial[y][x] != vanilla[y][x]]
    if len(bad) > 2 or any(INK in (trial[y][x], vanilla[y][x]) for x, y in bad):
        sys.exit(f"error: redrawing ENERGY and SECTOR changes {len(bad)} pixels, first at {bad[0]}")
    label(rows, BOX_ENERGY, 194, 72, dict(small, E=small["e"]), ENERGY)
    label(rows, BOX_TIME, 226, 72, small, TIME)
    label(rows, BOX_AREA, 81, 36, big, AREA, touching=("RT",))   # as in CUBIERTA
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    rows = build()
    if a.check:
        from PIL import Image
        if Image.open(OUT).tobytes() != bytes(v for row in rows for v in row):
            sys.exit(f"error: {OUT} is not what gfx_file_select.py builds: run it again")
        print("file select graphic is current")
    else:
        gp.save_png(rows, OUT)
        print(f"wrote {OUT}")
