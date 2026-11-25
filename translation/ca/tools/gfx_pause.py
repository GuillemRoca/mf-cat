#!/usr/bin/env python3
"""Composes the Catalan pause screen: map screen labels and the status screen.

  gfx_pause.py               writes the three files below
  gfx_pause.py --check       they are what this tool builds (CI)
  gfx_pause.py --fonts       prints the letters it took from the vanilla sheets

Writes, under translation/ca/gfx/menus/pause_screen/:
  bg.png            the background sheet: the status screen's title, counters, group headers
                    and item names, and the L/R tabs
  obj.png           the sprite sheet: the L/R tabs, the area name, OBJECTIVE, TARGET, START,
                    LOCK/OPEN and SYSTEM
  status_screen.tm  the status screen tilemap: where the item names and the longer headers are
and, with --oam OUT (the build does this), the eight OAM frames of the security levels'
legend as C, for src/data/menus/pause_screen_data.c (see LEGEND below).

Every letter is taken from the vanilla sheets (the same small fonts), so nothing here stores
graphics: only the few letters English doesn't have are drawn below, in the same style.

Status screen. An item name is a run of tiles in the background sheet that the status tilemap
points at; the game copies whole rows of that tilemap (rows 21-31) into view as items are
collected. The Catalan names are packed into the tiles of the English ones (POOL) and the
tilemap rows are rewritten to match. Names on the left take 5 tiles, on the right 7 plus the
panel's border tile (a name may run 4 px into it, as SPEED BOOSTER does). Three headers are longer than the English ones (BOMBA, VESTIT, ALTRES) and
take tiles from the same pool in place of the plain filler tile that followed them.

LEGEND. "L1 [door] LOCK" is three sprites, the last one 16 px wide: room for four small
letters. TANCAT and OBERT need 25 and 21 px, so that sprite becomes 32 px wide, reads from
tiles the sheet marks as unused (0x377 and 0x3b6 on), and the whole legend starts 8 px (one map
cell) further left to end where it did. That is an edit of the frames' OAM data in place, in
src/data/menus/pause_screen_data.c under LANG_CA: same size, nothing moves.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gfx  # noqa: E402
import lz77  # noqa: E402

OUT = catext.CA / "gfx" / "menus" / "pause_screen"
SOURCES = {"bg": "menus/pause_screen/bg.gfx.lz", "obj": "menus/pause_screen/obj.gfx.lz",
           "status": "menus/pause_screen/status_screen.tm.lz"}

# ---------------------------------------------------------------------------- the Catalan

COUNTERS = {"energy": "ENERGIA", "missile": "MÍSSIL", "pbomb": "BOMBA E."}
TITLE = "ESTAT"
HEADERS = {"beam": "RAIG", "missile": "MÍSSIL", "bomb": "BOMBA", "suit": "VESTIT", "misc": "ALTRES"}
ITEMS = {  # English name on the status screen: Catalan
    "CHARGE": "CÀRREGA", "WIDE": "AMPLE", "PLASMA": "PLASMA", "WAVE": "ONES", "ICE": "GEL",
    "SUPER": "SÚPER", "DIFFUSION": "DIFUSIÓ", "POWER": "ENERGIA",
    "VARIA": "CLIMÀTIC", "GRAVITY": "GRAVITATORI",
    "MORPH BALL": "MORFOSFERA", "HI-JUMP": "SUPERSALT", "SPEED BOOSTER": "ACCELERACIÓ",
    "SPACE JUMP": "SALT ESPACIAL", "SCREW ATTACK": "ATAC ESPIRAL",
}
TAB_L, TAB_R = "REPÒS", "ESTAT"
AREA = "COBERTA"            # MAIN DECK: "Coberta principal" doesn't fit the 46 px of the label
OBJECTIVE = "OBJECTIU"
TARGET = "DESTÍ"            # the flag on the map and the label on the station diagram
START = "INICI"             # where Samus is, on the station diagram
LOCK, OPEN = "TANCAT", "OBERT"
SYSTEM = "SISTEMA"

BASE = {"À": "A", "Í": "I", "Ò": "O", "Ó": "O", "Ú": "U"}
GRAVE = "ÀÒ"

# ---------------------------------------------------------------------------- pixel helpers


def load_sheet(key):
    return gfx.tiles_to_rows(gfx.vanilla_tiles({"source": SOURCES[key]}))


def segments(sheet, x0, x1, y0, h, ink):
    """The glyphs between x0 and x1 (inclusive), split at the columns without ink. A glyph is
    h rows of pixel values, None where there is no ink."""
    out, cur = [], []
    for x in range(x0, x1 + 2):
        col = [sheet[y0 + r][x] if x <= x1 and ink(sheet[y0 + r][x]) else None for r in range(h)]
        if any(v is not None for v in col):
            cur.append(col)
        elif cur:
            out.append([[c[r] for c in cur] for r in range(h)])
            cur = []
    return out


def harvest(font, sheet, word, x0, x1, y0, h, ink):
    glyphs = segments(sheet, x0, x1, y0, h, ink)
    letters = word.replace(" ", "")
    if len(glyphs) != len(letters):
        sys.exit(f"error: {word}: found {len(glyphs)} glyphs at ({x0},{y0})")
    for ch, g in zip(letters, glyphs):
        font.setdefault(ch, g)


def art(*rows):
    """A hand-drawn glyph: '.' is empty, '#' is ink, a hex digit is ink of that colour."""
    return [[None if c == "." else True if c == "#" else int(c, 16) for c in r] for r in rows]


def width(g):
    return len(g[0])


def put(sheet, x, y, glyph, colour):
    """Draws a glyph; colour(value, row, column) gives the palette index of an ink pixel."""
    for r, row in enumerate(glyph):
        for c, v in enumerate(row):
            if v is not None:
                sheet[y + r][x + c] = colour(v, r, c)


def fill(sheet, x0, x1, y0, y1, value):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            sheet[y][x] = value


class Font:
    """Letters of one of the small fonts. An accent is a list of (dx, dy) pixels from the
    top-left of its letter: `acute` and `grave` for the wide letters, `narrow` for an I."""

    def __init__(self, glyphs, gap=1, space=2, acute=((2, -1),), grave=((1, -1),), narrow=((1, -1),)):
        self.glyphs, self.gap, self.space = glyphs, gap, space
        self.acute, self.grave, self.narrow = acute, grave, narrow

    def glyph(self, ch):
        g = self.glyphs.get(BASE.get(ch, ch))
        if g is None:
            sys.exit(f"error: no glyph for {ch!r}")
        return g

    def measure(self, text):
        w = 0
        for i, ch in enumerate(text):
            if ch == " ":
                w += self.space - self.gap
            else:
                w += width(self.glyph(ch)) + (self.gap if i + 1 < len(text) else 0)
        return w

    def draw(self, sheet, x, y, text, colour, accent=None):
        """Draws text with its top-left at (x, y); returns the x just after the last letter."""
        for i, ch in enumerate(text):
            if ch == " ":
                x += self.space - self.gap
                continue
            g = self.glyph(ch)
            put(sheet, x, y, g, colour)
            if ch in BASE:
                dots = self.narrow if width(g) <= 2 else self.grave if ch in GRAVE else self.acute
                for dx, dy in dots:
                    sheet[y + dy][x + dx] = (accent or colour)(True, dy, dx)
            x += width(g) + self.gap
        return x - self.gap


def outline(sheet, x0, x1, y0, y1, ink, edge=0xE):
    """Gives the ink in a sprite's box its outline: every empty pixel that touches ink, and
    every empty pixel the ink encloses, as the vanilla labels have it."""
    def is_ink(x, y):
        return x0 <= x <= x1 and y0 <= y <= y1 and ink(sheet[y][x])
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if sheet[y][x] == 0 and any(is_ink(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                sheet[y][x] = -1
    # flood the empty pixels from the box's border: what is left empty is enclosed
    seen, todo = set(), [(x, y) for x in range(x0, x1 + 1) for y in (y0, y1)]
    todo += [(x, y) for y in range(y0, y1 + 1) for x in (x0, x1)]
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (x0 <= x <= x1 and y0 <= y <= y1) or sheet[y][x] != 0:
            continue
        seen.add((x, y))
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if sheet[y][x] == -1 or (sheet[y][x] == 0 and (x, y) not in seen):
                sheet[y][x] = edge


def const(value):
    return lambda v, r, c: value


def own(default):
    """The colours the glyph was drawn or found with; `default` for plain ink."""
    return lambda v, r, c: default if v is True else v


def show(name, font):
    print(f"-- {name}")
    for ch in sorted(font):
        print(ch)
        for row in font[ch]:
            print("   " + "".join("." if v is None else "#" if v is True else "%x" % v for v in row))


# ---------------------------------------------------------------------------- the fonts


def bold_fonts(bg):
    """The 6 px bold capitals of the counters ('8' on 'a') and of the group headers."""
    top, head = {}, {}
    harvest(top, bg, "ENERGY", 18, 58, 2, 5, lambda v: v == 8)
    harvest(top, bg, "MISSILE", 103, 144, 2, 5, lambda v: v == 8)
    harvest(top, bg, "P-BOMB", 166, 205, 2, 5, lambda v: v == 8)
    letters = lambda v: v in (0xD, 0xE)  # noqa: E731
    harvest(head, bg, "BEAM", 80, 108, 58, 5, letters)
    harvest(head, bg, "MISSIL", 80, 114, 66, 5, letters)
    harvest(head, bg, "BOMB", 88, 116, 74, 5, letters)
    harvest(head, bg, "SUIT", 88, 110, 82, 5, letters)
    harvest(head, bg, "MISC", 88, 112, 90, 5, letters)
    both = dict(top)
    both.update(head)
    both["V"] = art("##..##", "##..##", "##..##", ".####.", "..##..")
    both["."] = art("..", "..", "..", "##", "##")
    return both


def item_font(bg):
    """The 4 px capitals of the item names ('8' on 'd')."""
    f = {}
    for word, x0, x1, y0 in (
            ("NORMAL", 80, 111, 99), ("SUPER", 112, 151, 99), ("CHARGE", 80, 111, 107),
            ("ICE", 112, 127, 107), ("WIDE", 80, 111, 115), ("DIFFUSION", 112, 151, 115),
            ("PLASMA", 80, 111, 123), ("POWER", 112, 143, 123), ("WAVE", 80, 103, 131),
            ("VARIA", 112, 143, 131), ("GRAVITY", 112, 143, 139), ("MORPH BALL", 80, 139, 147),
            ("HI-JUMP", 80, 111, 155), ("SPEED BOOSTER", 152, 211, 59),
            ("SPACE JUMP", 152, 199, 67), ("SCREW ATTACK", 152, 207, 75)):
        harvest(f, bg, word, x0, x1, y0, 5, lambda v: v == 8)
    return f


def obj_fonts(obj):
    five, med, lock, opened, system = {}, {}, {}, {}, {}
    harvest(five, obj, "SECTOR", 131, 165, 225, 5, lambda v: v == 8)
    harvest(five, obj, "MAINDECK", 170, 213, 225, 5, lambda v: v == 8)
    harvest(five, obj, "OBJECTIVE", 129, 177, 242, 5, lambda v: v == 2)
    five["U"] = art("#...#", "#...#", "#...#", "#...#", "#####")
    harvest(med, obj, "TARGET", 187, 212, 183, 5, lambda v: v == 7)
    harvest(med, obj, "START", 193, 214, 242, 5, lambda v: v == 0xC)
    med["D"] = art("###.", "#..#", "#..#", "#..#", "###.")
    med["N"] = art("#..#", "##.#", "#.##", "#..#", "#..#")
    med["C"] = art(".###", "#...", "#...", "#...", ".###")
    med["I"] = art("#", "#", "#", "#", "#")
    harvest(lock, obj, "LOCK", 97, 110, 114, 5, lambda v: v == 5)
    lock["T"] = art("###", ".#.", ".#.", ".#.", ".#.")
    lock["A"] = art(".#.", "#.#", "###", "#.#", "#.#")
    lock["N"] = art("#.#", "###", "###", "###", "#.#")
    # OPEN: '1' letters whose closed counters are filled with 'd'
    harvest(opened, obj, "OPEN", 97, 110, 122, 5, lambda v: v in (1, 0xD))
    opened["B"] = art("11.", "1d1", "11.", "1d1", "11.")
    opened["R"] = art("11.", "1d1", "11.", "1.1", "1.1")
    opened["T"] = art("111", ".1.", ".1.", ".1.", ".1.")
    opened["E"] = art("111", "1..", "11.", "1..", "111")
    harvest(system, obj, "SYSTEM", 129, 159, 114, 5, lambda v: v in (8, 9))
    system["I"] = art("#", "#", "#", "#", "#")
    system["A"] = art("####", "#..#", "####", "#..#", "#..#")
    system["T"] = art("###", ".#.", ".#.", ".#.", ".#.")
    return five, med, lock, opened, system


def tab_fonts(bg, obj):
    """The 3 px letters of the L/R tabs, with their softened corners: '3' and '4' on '5' in
    the background sheet, '2' and '3' on '4' in the sprite sheet."""
    b, o = {}, {}
    harvest(b, bg, "SLEEP", 14, 33, 180, 5, lambda v: v != 5)
    harvest(b, bg, "STATUS", 76, 99, 180, 5, lambda v: v != 5)
    harvest(o, obj, "SLEEP", 228, 247, 218, 5, lambda v: v != 4)
    harvest(o, obj, "STATUS", 222, 245, 226, 5, lambda v: v != 4)
    b["R"] = art("3334", "3..3", "3334", "3.3.", "3..3")
    b["O"] = art("434", "3.3", "3.3", "3.3", "434")
    o["R"] = art("2223", "2..2", "2223", "2.2.", "2..2")
    o["O"] = art("323", "2.2", "2.2", "2.2", "323")
    return b, o


# ---------------------------------------------------------------------------- background sheet

# The tiles of the English item names (and of NORMAL, which the game never shows) plus the
# blank ones around them: the Catalan names and the longer headers are packed into these.
POOL = ([*range(0x1AA, 0x1AE), *range(0x1CA, 0x1CD), *range(0x1EA, 0x1EE), *range(0x20A, 0x20D),
         *range(0x22A, 0x22C), *range(0x18E, 0x191), *range(0x1AE, 0x1B0), *range(0x1CE, 0x1D3),
         *range(0x1EE, 0x1F2), *range(0x20E, 0x212), *range(0x22E, 0x232), *range(0x24A, 0x251),
         *range(0x26A, 0x26E), *range(0x0F3, 0x0FB), *range(0x113, 0x119), *range(0x133, 0x13A),
         *range(0x18A, 0x18E), 0x191, 0x1B0, 0x1B1, 0x1B2, 0x1F2, 0x212, 0x232, 0x252,
         *range(0x26F, 0x273)])
FILLER_NAME, FILLER_HEADER, BORDER = 0x1CD, 0x12F, 0x25F

# (tilemap row, column of the first name tile, name tiles, English name)
NAME_ROWS = [(22, 3, 5, "CHARGE"), (23, 3, 5, "WIDE"), (24, 3, 5, "PLASMA"), (25, 3, 5, "WAVE"),
             (26, 3, 5, "ICE"), (22, 11, 5, "SUPER"), (23, 11, 5, "ICE"), (24, 11, 5, "DIFFUSION"),
             (29, 3, 7, "POWER"), (22, 21, 7, "VARIA"), (23, 21, 7, "GRAVITY"),
             (26, 21, 7, "MORPH BALL"), (27, 21, 7, "HI-JUMP"), (28, 21, 7, "SPEED BOOSTER"),
             (29, 21, 7, "SPACE JUMP"), (30, 21, 7, "SCREW ATTACK")]

# header: (first tile of its letters, vanilla letter tiles, x of that tile in the panel,
#          [(tilemap row, column) of the first filler tile after the letters])
HEADER_TILES = {"beam": (0x0EA, 4, 80, []), "missile": (0x10A, 6, 80, []),
                "bomb": (0x12B, 4, 88, [(28, 6)]), "suit": (0x14B, 3, 88, [(8, 23), (21, 23)]),
                "misc": (0x16B, 4, 88, [(25, 24)])}


def get_tile(sheet, t):
    return [sheet[(t // 32) * 8 + r][(t % 32) * 8:(t % 32) * 8 + 8] for r in range(8)]


def set_tile(sheet, t, px):
    for r in range(8):
        sheet[(t // 32) * 8 + r][(t % 32) * 8:(t % 32) * 8 + 8] = px[r]


def strip_of(sheet, tiles):
    """The tiles side by side, as one 8-row canvas."""
    return [[v for t in tiles for v in get_tile(sheet, t)[r]] for r in range(8)]


def write_strip(sheet, tiles, canvas):
    for i, t in enumerate(tiles):
        set_tile(sheet, t, [canvas[r][i * 8:i * 8 + 8] for r in range(8)])


def build_bg(bg, tm):
    vanilla = [row[:] for row in bg]
    bold = Font(bold_fonts(bg), space=3, narrow=((1, -1), (2, -1)))
    pool = list(POOL)
    used = {v & 0x3FF for v in tm}
    for t in pool:
        if t not in used and any(v for row in get_tile(bg, t) for v in row):
            if not 0x18A <= t <= 0x18D:
                sys.exit(f"error: pool tile {t:#x} is neither used by the status screen nor blank")

    # the counters at the top: '8' letters on 'a'. A text that fills its cell starts one
    # pixel nearer the icon, to stay off the cell's edge
    for text, x0, x1 in ((COUNTERS["energy"], 18, 85), (COUNTERS["missile"], 103, 149),
                         (COUNTERS["pbomb"], 166, 213)):
        fill(bg, x0, x1, 1, 6, 0xA)
        end = bold.draw(bg, x0 - (bold.measure(text) > x1 - x0), 2, text, const(8))
        if end > x1:
            sys.exit(f"error: {text} doesn't fit its counter")

    # the title: each letter in the tones of its place (dark at the ends, bright in the
    # middle), H = highlight, M = main, S = shade
    tones = {"d": {"M": 0xD, "S": 0xF}, "c": {"H": 1, "M": 0xC, "S": 0xD}, "a": {"H": 1, "M": 0xA, "S": 0xC}}
    title = [("d", ["MMMMS", "MS...", "MMMS.", "MS...", "MMMMS"]),                     # E
             ("c", ["HMMMMMS", "HMS....", "HMMMMMS", "....HMS", "HMMMMMS"]),          # S
             ("a", ["HMMMMMS", "..HMS..", "..HMS..", "..HMS..", "..HMS.."]),          # T
             ("c", [".HMMMS.", "HMS.HMS", "HMMMMMS", "HMS.HMS", "HMS.HMS"]),          # A
             ("d", [".MMMMMS", "...MS..", "...MS..", "...MS..", "...MS.."])]          # T
    if TITLE != "ESTAT":
        sys.exit("error: the title's letters are drawn for ESTAT")
    fill(bg, 99, 139, 43, 47, 7)
    fill(bg, 112, 132, 48, 48, 7)
    x = 119 - sum(len(rows[0]) for _, rows in title) // 2
    for tone, rows in title:
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch != ".":
                    bg[43 + r][x + c] = tones[tone][ch]
        if tone != "d":  # the shine under the stems of the middle letters
            for c, ch in enumerate(rows[4]):
                if ch in "MS" or (ch == "H" and tone == "a"):
                    bg[48][x + c] = 1
        x += len(rows[0])

    # the group headers: bold letters over the bar, bright up to x = 98 and darker after
    new_tiles = {}
    for key, (first, count, x0, fillers) in HEADER_TILES.items():
        text = HEADERS[key]
        y0 = (first // 32) * 8
        extra = max(0, -(-bold.measure(text) // 8) - count)
        if extra and not fillers or extra > 2:
            sys.exit(f"error: {text} doesn't fit its header")
        tiles = list(range(first, first + count)) + [pool.pop() for _ in range(extra)]
        for t in tiles[count:]:
            set_tile(bg, t, get_tile(vanilla, FILLER_HEADER))
        canvas = strip_of(bg, tiles)
        for r in range(2, 7):
            for c in range(len(canvas[0])):
                # the bar is plain up to x = 111, then it fades as under BEAM (without its dots)
                canvas[r][c] = 8 if x0 + c < 112 or key != "missile" else vanilla[56 + 2 + r % 2][x0 + c]
        x = 0
        for ch in text:
            g = bold.glyph(ch)
            tone = 0xE if x0 + x <= 98 else 0xD
            bold.draw(canvas, x, 2, ch, const(tone))
            x += width(g) + bold.gap
        write_strip(bg, tiles, canvas)
        new_tiles[key] = tiles[count:]
        for row, col in fillers:
            for i, t in enumerate(tiles[count:]):
                if tm[row * 32 + col + i] & 0x3FF != FILLER_HEADER:
                    sys.exit(f"error: {key}: no filler tile at row {row}, column {col + i}")
                tm[row * 32 + col + i] = tm[row * 32 + col + i] & 0xFC00 | t

    # the item names: '8' letters on 'd', under the line that separates the rows
    small = Font(item_font(bg), space=3, acute=((2, -1), (3, -2)), grave=((1, -1), (0, -2)))
    blank = get_tile(vanilla, FILLER_NAME)
    placed = {}
    pool.reverse()  # names take the pool from its start, the headers took from its end
    edge = get_tile(vanilla, BORDER)
    for row, col, room, english in NAME_ROWS:
        text = ITEMS[english]
        if text not in placed:
            # a name on the right may run 4 px into the tile of the panel's border
            n = -(-small.measure(text) // 8)
            if n > room and not (room == 7 and small.measure(text) <= 60):
                sys.exit(f"error: {text} is {small.measure(text)} px, {english} has {room * 8}")
            tiles = [pool.pop() for _ in range(n)]
            canvas = [[v for i in range(n) for v in (edge if i == 7 else blank)[r]] for r in range(8)]
            small.draw(canvas, 0, 3, text, const(8))
            write_strip(bg, tiles, canvas)
            placed[text] = tiles
        tiles = placed[text]
        attr = tm[row * 32 + col] & 0xFC00
        for i in range(room):
            tm[row * 32 + col + i] = attr | (tiles[i] if i < len(tiles) else FILLER_NAME)
        if room == 7:
            tm[row * 32 + col + 7] = tm[row * 32 + col + 7] & 0xFC00 | (tiles[7] if len(tiles) > 7 else BORDER)
    for t in pool:  # what is left of the English names
        set_tile(bg, t, blank)

    # the L and R tabs: soft 3 px letters, '3' (and '4' corners) on '5'
    tabs = Font(tab_fonts(vanilla, load_sheet("obj"))[0], grave=((0, -1),))
    fill(bg, 13, 36, 179, 184, 5)
    tabs.draw(bg, 14, 180, TAB_L, own(3), const(3))
    fill(bg, 75, 100, 179, 184, 5)
    tabs.draw(bg, 76 + (23 - tabs.measure(TAB_R)) // 2, 180, TAB_R, own(3), const(3))
    return new_tiles


# ---------------------------------------------------------------------------- sprite sheet

LEGEND_FRAMES = 0x566502      # sPauseScreenOam_L1Lock_Frame0; the 8 frames follow each other
LEGEND_SHIFT = 8              # px the legend moves left
LEGEND_LABEL_X = -9           # x of the label sprite (it was 0)
LEGEND_TILES = {0x1CC: 0x377, 0x1EC: 0x3B6}   # LOCK, OPEN: the 4 unused tiles they move to


def label(obj, x0, x1, y0, font, text, colour, x=None, top=2, accent_room=False):
    """Redraws a sprite label: clears the box (whole tiles, x0..x1, tile row at y0), writes
    the text with its first letter at x and gives it its outline."""
    fill(obj, x0, x1, y0, y0 + 7, 0)
    end = font.draw(obj, x0 + 1 if x is None else x, y0 + top, text, colour)
    if end - 1 > x1:
        sys.exit(f"error: {text} doesn't fit its label")
    outline(obj, x0, x1, y0, y0 + 7, lambda v: v not in (0, -1, 0xE))


def build_obj(obj):
    five, med, lock, opened, system = (Font(f) for f in obj_fonts(obj))
    med.narrow = ((1, -1),)
    tabs = Font(tab_fonts(load_sheet("bg"), obj)[1], grave=((0, -1),))

    # the security levels' legend: LOCK and OPEN move to wider, unused tiles
    for t in (*range(0x377, 0x37B), *range(0x3B6, 0x3BA)):
        px = get_tile(obj, t)
        if [v for row in px for v in row].count(1) != 10 or any(v not in (0, 1) for row in px for v in row):
            sys.exit(f"error: tile {t:#x} isn't one of the sheet's unused (crossed) tiles")
    label(obj, 184, 215, 216, lock, LOCK, own(5))
    label(obj, 176, 207, 232, opened, OPEN, own(1))

    # SYSTEM, on the computer's text box: lighter top and bottom rows
    label(obj, 128, 159, 112, system, SYSTEM, lambda v, r, c: 9 if r in (0, 4) else 8)

    # the TARGET flag on the map (two colour sets): the box stays, the word changes
    for x0, paper, ink in ((184, 6, 7), (216, 0xD, 2)):
        fill(obj, x0 + 2, x0 + 29, 182, 187, paper)
        med.draw(obj, x0 + 2 + (28 - med.measure(TARGET)) // 2, 183, TARGET, const(ink))

    # the tabs' highlights: 'L REPÒS' and 'ESTAT R'
    fill(obj, 225, 254, 217, 222, 4)
    tabs.draw(obj, 228, 218, TAB_L, own(2), const(2))
    fill(obj, 221, 246, 225, 230, 4)
    tabs.draw(obj, 222 + (23 - tabs.measure(TAB_R)) // 2, 226, TAB_R, own(2), const(2))

    # the area name beside SECTOR n
    fill(obj, 169, 214, 225, 229, 0xA)
    five.draw(obj, 169 + (46 - five.measure(AREA)) // 2, 225, AREA, const(8))

    # OBJECTIVE, beside the A button
    label(obj, 128, 191, 240, five, OBJECTIVE, const(2))

    # START and TARGET on the station diagram, each in two colours
    for x0, ink in ((192, 0xC), (216, 0xD)):
        label(obj, x0, x0 + 23, 240, med, START, const(ink))
    for x0, ink in ((96, 8), (128, 0xA)):
        label(obj, x0, x0 + 31, 248, med, TARGET, const(ink), x=x0 + 2)


def legend_frames():
    """The 8 legend frames as lists of (attr0, attr1, attr2), vanilla and Catalan."""
    rom = catext.rom()
    vanilla, catalan = [], []
    for f in range(8):
        off = LEGEND_FRAMES + f * 20
        count, *parts = struct.unpack_from("<10H", rom, off)
        entries = [tuple(parts[i * 3:i * 3 + 3]) for i in range(3)]
        tile = entries[2][2] & 0x3FF
        if count != 3 or tile not in LEGEND_TILES or entries[2][1] & 0xC1FF != 0 or entries[2][0] >> 14 != 1:
            sys.exit(f"error: the legend frame at {off:#x} isn't what it should be")
        vanilla.append(entries)
        new = [(a0, a1 & 0xFE00 | (a1 - LEGEND_SHIFT) & 0x1FF, a2) for a0, a1, a2 in entries[:2]]
        a0, a1, a2 = entries[2]
        new.append((a0, a1 & 0x3E00 | 1 << 14 | LEGEND_LABEL_X & 0x1FF, a2 & 0xFC00 | LEGEND_TILES[tile]))
        catalan.append(new)
    return vanilla, catalan


def legend_bytes(selftest=False):
    """What the legend frames are in a LANG_CA ROM (for romcheck.py)."""
    frames = legend_frames()[0 if selftest else 1]
    return b"".join(struct.pack("<10H", 3, *[v for e in f for v in e]) for f in frames)


def write_oam_inc(path, vanilla=False):
    names = [f"L{n}{state}" for state in ("Lock", "Open") for n in range(1, 5)]
    dims = {(1, 0): "OAM_DIMS_16x8", (0, 0): "OAM_DIMS_8x8", (1, 1): "OAM_DIMS_32x8"}
    lines = ["// Generated by translation/ca/tools/gfx_pause.py. Do not edit.",
             "// The security levels' legend with a 32 px label (TANCAT, OBERT), 8 px further left.", ""]
    for name, frame in zip(names, legend_frames()[0 if vanilla else 1]):
        lines += [f"static const u16 sPauseScreenOam_{name}_Frame0[OAM_DATA_SIZE(3)] = {{", "    3,"]
        for a0, a1, a2 in frame:
            x, y = a1 & 0x1FF, a0 & 0xFF
            x, y = x - 0x200 if x >= 0x100 else x, y - 0x100 if y >= 0x80 else y
            lines.append(f"    OAM_ENTRY({x}, {y}, {dims[(a0 >> 14, a1 >> 14)]}, OAM_NO_FLIP, "
                         f"{a2 & 0x3FF:#x}, {a2 >> 12}, {a2 >> 10 & 3}),")
        lines += ["};", ""]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines))


# ---------------------------------------------------------------------------- output


def save_png(rows, path):
    from PIL import Image
    img = Image.new("P", (gfx.COLS * 8, len(rows)))
    img.putpalette(gfx.GREY + [0] * (768 - 48))
    img.putdata([v for row in rows for v in row])
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def build():
    bg, obj = load_sheet("bg"), load_sheet("obj")
    raw = gfx.vanilla_tiles({"source": SOURCES["status"]})
    tm = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    build_bg(bg, tm)
    build_obj(obj)
    return bg, obj, struct.pack(f"<{len(tm)}H", *tm)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", action="store_true", help="print the letters taken from the vanilla sheets")
    ap.add_argument("--oam", metavar="OUT", help="write the legend's OAM frames (C) instead of the graphics")
    ap.add_argument("--vanilla", action="store_true", help="with --oam: the vanilla frames (self-test build)")
    ap.add_argument("--check", action="store_true", help="the files in gfx/ are what this tool builds")
    a = ap.parse_args()
    if a.oam:
        write_oam_inc(a.oam, a.vanilla)
    elif a.fonts:
        bg, obj = load_sheet("bg"), load_sheet("obj")
        show("bold", bold_fonts(bg))
        show("item", item_font(bg))
        for name, f in zip(("five", "med", "lock", "open", "system"), obj_fonts(obj)):
            show(name, f)
        for name, f in zip(("tab bg", "tab obj"), tab_fonts(bg, obj)):
            show(name, f)
    elif a.check:
        from PIL import Image
        bg, obj, tm = build()
        for name, rows in (("bg.png", bg), ("obj.png", obj)):
            if Image.open(OUT / name).tobytes() != bytes(v for row in rows for v in row):
                sys.exit(f"error: {OUT / name} is not what gfx_pause.py builds: run it again")
        if (OUT / "status_screen.tm").read_bytes() != tm:
            sys.exit("error: status_screen.tm is not what gfx_pause.py builds: run it again")
        print("pause screen graphics are current")
    else:
        bg, obj, tm = build()
        save_png(bg, OUT / "bg.png")
        save_png(obj, OUT / "obj.png")
        (OUT / "status_screen.tm").write_bytes(tm)
        print(f"wrote bg.png, obj.png and status_screen.tm in {OUT}")
