#!/usr/bin/env python3
"""Composes the Catalan title of the intro's vaccine panel: Vacuna "Metroid".

  gfx_intro.py            writes translation/ca/gfx/new_file_intro/metroid_vaccine_obj.png
  gfx_intro.py --check    the file is what this tool builds (CI)

The panel's title, Vaccine "Metroid", is a small anti-aliased bitmap on a shaded bar at the
top of new_file_intro/metroid_vaccine_obj.gfx.lz (rows 5-13, from x = 72). Its letters are
about nine pixels wide and nearly touch. "Vacuna" is put together from them:
  V, a, c   stay where they are
  u         the n's own rows: its stems, with its arch underneath as the bowl
  n, a      copies of the title's own
It is three pixels shorter than "Vaccine": the freed columns take the bar's plain shading,
and "Metroid" stays where it is. The rest of the sheet is diagrams and unreadable small print.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gfx  # noqa: E402
import gfx_pause as gp  # noqa: E402

OUT = catext.CA / "gfx" / "new_file_intro" / "metroid_vaccine_obj.png"
WORD = "Vacuna"
Y0, Y1 = 5, 13                       # the row over the letters (the i's dot reaches it), the
                                     # letters' seven rows and the soft row under them
N, A = (114, 121), (83, 90)          # the lit columns of the title's n and a
DIM = 113                            # a column between two letters (left of the n)
PLAIN = 132                          # the bar's shading where there is no text (four columns)
DOT, DOT_ROWS = (110, 112), (3, 4)   # the dot of the i; it takes the shading of the columns left of it
KEEP_TO = 100                        # "Vac" and the column after it stay
WORD_END = 130                       # last column of "Vaccine"


def block(rows, x0, x1):
    return [rows[y][x0:x1 + 1] for y in range(Y0, Y1 + 1)]


def paste(rows, x, cell):
    for r, row in enumerate(cell):
        rows[Y0 + r][x:x + len(row)] = row
    return x + len(cell[0])


def build():
    rows = gfx.tiles_to_rows(gfx.vanilla_tiles(gfx.assets()["new_file_intro/metroid_vaccine_obj"]))
    vanilla = [r[:] for r in rows]
    if WORD != "Vacuna":
        sys.exit("error: the title is put together for Vacuna")
    n, a, dim = block(vanilla, *N), block(vanilla, *A), block(vanilla, DIM, DIM)
    # the u is made of the n's rows: its two stems at full height, then the arch as a bowl
    # (its underside, then its top toned down to what the bottom row of a letter has here)
    over, top, under, stems, soft = n[0], n[1], n[2], n[3:7], n[8]
    u = [over, stems[0]] + stems + [under, [max(8, v - 3) for v in top], soft]
    x = KEEP_TO + 1
    x = paste(rows, x, u)
    x = paste(rows, x, dim)           # two dim columns between upright stems, as between i and n
    x = paste(rows, x, dim)
    x = paste(rows, x, n)
    x = paste(rows, x, dim)
    x = paste(rows, x, a)
    if x > WORD_END + 1:
        sys.exit("error: the word is longer than the one it replaces")
    paste(rows, x, block(vanilla, PLAIN, PLAIN + WORD_END - x))
    for y in DOT_ROWS:                # the dot of the i, above the letters' rows
        for dx, dot_x in enumerate(range(DOT[0], DOT[1] + 1)):
            rows[y][dot_x] = vanilla[y][DOT[0] - (DOT[1] - DOT[0] + 1) + dx]
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    rows = build()
    if a.check:
        from PIL import Image
        if Image.open(OUT).tobytes() != bytes(v for row in rows for v in row):
            sys.exit(f"error: {OUT} is not what gfx_intro.py builds: run it again")
        print("intro panel graphic is current")
    else:
        gp.save_png(rows, OUT)
        print(f"wrote {OUT}")
