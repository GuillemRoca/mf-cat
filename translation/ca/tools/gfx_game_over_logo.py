#!/usr/bin/env python3
"""Composes the Catalan game over logo, "FI DE LA / PARTIDA", from the letters of GAME OVER.

  gfx_game_over_logo.py [--preview OUT.png]

Writes translation/ca/gfx/game_over/background.png (the background tile sheet with the new
logo tiles) and translation/ca/gfx/game_over/text_tilemap.tm (the tilemap of the text layer).

The vanilla logo is 22 x 3 tiles of chrome letters (tiles 0x340 on of
game_over/background.gfx.lz, placed by game_over/text.tm.lz at rows 4-6 with palette rows 14
and 15). Its bands of colour run along the rows, so letters can be rebuilt from pieces of the
existing ones as long as every piece stays on its own rows:
  E, A, R  cut out as they are            F, L  E without a bar: its stem and the other bars
  I        a free-standing stem            T     E's top bar over a stem
  D        the O with E's square corners   P     the R without its leg
The Catalan title doesn't fit one line at this size, so it takes two lines of 30 x 3 tiles, at
rows 1-3 and 4-6 of the text layer; the sheet has the spare tiles (0x340-0x3FD). Colours are
handled as RGB and mapped back to whichever of the two palette rows suits each tile best.
"""
import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import lz77  # noqa: E402

from PIL import Image  # noqa: E402

LINES = ["FI DE LA", "PARTIDA"]
OUT = catext.CA / "gfx" / "game_over"
LOGO_ROW, LOGO_COL, LOGO_W = 4, 4, 22       # the vanilla logo in the text tilemap
FIRST_TILE, LINE_TILES = 0x340, 30          # new logo: 2 lines x 3 rows x 30 tiles, stride 32
NEW_ROWS = [1, 4]                           # tilemap row of each line
H = 24
SPACE, KERN = 7, -1                         # px between words; letters overlap one outline column


def database():
    return {e["path"]: e for e in json.loads((catext.ROOT / "database.json").read_text())}


def load(db, path):
    e = db[path]
    a = int(e["addr"]["us"], 16)
    if path.endswith(".lz"):
        return lz77.decompress(catext.rom(), a)[0]
    return catext.rom()[a:a + int(e["count"], 16) * e.get("size", 1)]


def palette(db):
    raw = load(db, "game_over/background.pal")
    out = []
    for i in range(len(raw) // 2):
        v = struct.unpack_from("<H", raw, 2 * i)[0]
        out.append(((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3))
    return out


def tile_pixels(gfx, t):
    return [[(gfx[t * 32 + y * 4 + x // 2] >> (4 * (x % 2))) & 15 for x in range(8)] for y in range(8)]


def vanilla_logo(db):
    """The logo as rows of RGB (None = transparent), 176 x 24."""
    gfx, pal = load(db, "game_over/background.gfx.lz"), palette(db)
    tm = load(db, "game_over/text.tm.lz")
    vals = struct.unpack(f"<{len(tm) // 2}H", tm)
    img = [[None] * (LOGO_W * 8) for _ in range(H)]
    for r in range(3):
        for c in range(LOGO_W):
            v = vals[(LOGO_ROW + r) * 32 + LOGO_COL + c]
            px = tile_pixels(gfx, v & 0x3FF)
            for y in range(8):
                for x in range(8):
                    if px[y][x]:
                        img[r * 8 + y][c * 8 + x] = pal[(v >> 12) * 16 + px[y][x]]
    return img


class Glyph:
    """A letter being assembled: {(x, y): rgb}."""

    def __init__(self):
        self.px = {}

    def take(self, src, x0, x1, rows, dx=0, clip=None):
        """Copies src columns x0..x1-1 of `rows` to x - x0 + dx, same rows."""
        for y in rows:
            for x in range(x0, x1):
                c = src[y][x]
                if c is not None and (clip is None or clip(x, y)):
                    self.px[(x - x0 + dx, y)] = c
        return self

    def clear(self, xs, rows):
        for y in rows:
            for x in xs:
                self.px.pop((x, y), None)
        return self

    def put(self, x, y, rgb):
        self.px[(x, y)] = rgb
        return self

    @property
    def width(self):
        return max(x for x, _ in self.px) + 1


ALL = range(0, H)
E_X = 70       # E: x 70-88
O_X = 96       # O: x 96-116
R_X = 154      # R: x 154-173
M_EDGE = 67    # the right edge of M's right stem: x 67-69
# first column of the A on each row (the G is to its left), and its last column
A_LEFT = {1: 32, 2: 32, 3: 31, 4: 31, 5: 31, 6: 30, 7: 30, 8: 30, 9: 29, 10: 29, 11: 29, 12: 28, 13: 28,
          14: 27, 15: 27, 16: 26, 17: 26, 18: 26, 19: 25, 20: 25, 21: 24, 22: 25, 23: 26}


def letters(src):
    g = {}
    g["E"] = Glyph().take(src, E_X, E_X + 19, ALL)
    g["R"] = Glyph().take(src, R_X, R_X + 20, ALL)
    g["A"] = Glyph().take(src, 24, 47, ALL, clip=lambda x, y: y in A_LEFT and x >= A_LEFT[y] and (x <= 45 or y >= 16))
    # I: the left of E's stem, the right edge of M's stem; from row 17 down, R's stem, which
    # stands free there
    stem = Glyph().take(src, E_X, E_X + 5, range(0, 17)).take(src, M_EDGE, M_EDGE + 3, range(0, 17), dx=5)
    stem.take(src, R_X, R_X + 9, range(17, H))
    g["I"] = stem
    # L: the stem down to the bottom bar, then E
    g["L"] = Glyph().take(src, E_X, E_X + 5, range(0, 15)).take(src, M_EDGE, M_EDGE + 3, range(0, 15), dx=5)
    g["L"].take(src, E_X, E_X + 19, range(15, H))
    # F: E down to the middle bar, then the stem
    g["F"] = Glyph().take(src, E_X, E_X + 19, range(0, 16)).take(src, R_X, R_X + 9, range(16, H))
    # T: E's top bar (its stem's top is the bar's left end), and the stem in the middle below
    t = Glyph().take(src, E_X, E_X + 19, range(0, 8))
    for x in range(0, 8):                       # the bar's lower edge where E's stem was
        for y in (7, 8):
            t.px[(x, y)] = src[y][E_X + 10]
    t.px.pop((0, 8), None)
    t.take(src, E_X + 9, E_X + 19, range(8, 9), dx=9)
    for y in range(8, 17):
        for x in range(5):
            t.px[(5 + x, y)] = src[y][E_X + x]
        for x in range(3):
            t.px[(10 + x, y)] = src[y][M_EDGE + x]
    t.take(src, R_X, R_X + 9, range(17, H), dx=5)
    g["T"] = t
    # D: the O, with E's square corners on the left
    d = Glyph().take(src, O_X, O_X + 21, ALL)
    d.clear(range(0, 8), list(range(0, 8)) + list(range(16, H)))
    d.take(src, E_X, E_X + 8, list(range(0, 8)) + list(range(16, H)))
    g["D"] = d
    # P: the R down to its bowl, the bowl's lower edge closed, then the stem
    p = Glyph().take(src, R_X, R_X + 20, range(0, 15)).take(src, R_X, R_X + 12, range(15, 16))
    edge, under = src[15][R_X + 9], src[16][R_X + 8]
    for x in range(12, 17):
        p.put(x, 15, edge)
    p.put(17, 15, src[15][R_X + 7]).put(18, 15, src[16][R_X + 7])
    p.take(src, R_X, R_X + 8, range(16, 17))
    for x in range(8, 17):
        p.put(x, 16, under)
    p.take(src, R_X, R_X + 9, range(17, H))
    g["P"] = p
    return g


def set_line(glyphs, text):
    """{(x, y): rgb} of a line, starting at x = 0, and its width."""
    out, pen, prev = {}, 0, " "
    for ch in text:
        if ch == " ":
            pen += SPACE
            prev = ch
            continue
        if prev != " ":
            pen += 1 if "I" in (prev, ch) else KERN   # the narrow I needs air on both sides
        g = glyphs[ch]
        for (x, y), c in g.px.items():
            out.setdefault((pen + x, y), c)   # the letter on the left stays on top, as in vanilla
        pen += g.width
        prev = ch
    return out, pen


def nearest(rgb, colours):
    return min(range(1, 16), key=lambda i: sum((a - b) ** 2 for a, b in zip(rgb, colours[i])))


def compose():
    db = database()
    pal = palette(db)
    glyphs = letters(vanilla_logo(db))
    gfx = bytearray(load(db, "game_over/background.gfx.lz"))
    tm = load(db, "game_over/text.tm.lz")
    vals = list(struct.unpack(f"<{len(tm) // 2}H", tm))
    for r in range(3):                                   # the vanilla logo goes
        for c in range(LOGO_W):
            vals[(LOGO_ROW + r) * 32 + LOGO_COL + c] = 0
    for t in range(FIRST_TILE, FIRST_TILE + 6 * 32 - 2):
        gfx[t * 32:(t + 1) * 32] = bytes(32)
    preview = Image.new("RGB", (LINE_TILES * 8, 2 * H), (24, 8, 40))
    for n, text in enumerate(LINES):
        line, width = set_line(glyphs, text)
        if width > LINE_TILES * 8:
            sys.exit(f"error: {text!r} is {width} px wide, the line holds {LINE_TILES * 8}")
        left = (LINE_TILES * 8 - width) // 2
        for (x, y), c in line.items():
            preview.putpixel((left + x, n * H + y), c)
        for r in range(3):
            for col in range(LINE_TILES):
                block = {(x, y): line.get((col * 8 + x - left, r * 8 + y)) for y in range(8) for x in range(8)}
                if not any(block.values()):
                    continue
                # the palette row (14 or 15) that reproduces this tile best
                best = None
                for row in (14, 15):
                    colours = pal[row * 16:row * 16 + 16]
                    idx = {k: (nearest(c, colours) if c else 0) for k, c in block.items()}
                    err = sum(sum((a - b) ** 2 for a, b in zip(c, colours[idx[k]])) for k, c in block.items() if c)
                    if best is None or err < best[0]:
                        best = (err, row, idx)
                _, row, idx = best
                tile = FIRST_TILE + (n * 3 + r) * 32 + col
                for y in range(8):
                    for xb in range(4):
                        gfx[tile * 32 + y * 4 + xb] = idx[(xb * 2, y)] | (idx[(xb * 2 + 1, y)] << 4)
                vals[(NEW_ROWS[n] + r) * 32 + col] = (row << 12) | tile
    return bytes(gfx), struct.pack(f"<{len(vals)}H", *vals), preview


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    gfx, tilemap, preview = compose()
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.new("P", (256, len(gfx) // 32 // 32 * 8))
    img.putpalette([c for i in range(16) for c in ((0, 0, 48) if i == 0 else (40 + 14 * i,) * 3)] + [0] * 720)
    for t in range(len(gfx) // 32):
        for y in range(8):
            for xb in range(4):
                b = gfx[t * 32 + y * 4 + xb]
                img.putpixel(((t % 32) * 8 + xb * 2, (t // 32) * 8 + y), b & 15)
                img.putpixel(((t % 32) * 8 + xb * 2 + 1, (t // 32) * 8 + y), b >> 4)
    img.save(OUT / "background.png")
    (OUT / "text_tilemap.tm").write_bytes(tilemap)
    if a.preview:
        preview.resize((preview.width * 4, preview.height * 4), Image.NEAREST).save(a.preview)
    print(f"wrote {OUT / 'background.png'} and {OUT / 'text_tilemap.tm'}")


if __name__ == "__main__":
    main()
