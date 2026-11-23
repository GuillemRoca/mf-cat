#!/usr/bin/env python3
"""Composes the Catalan game over prompt from the glyphs of the five vanilla prompts.

  gfx_game_over.py [OUT.png]     default: translation/ca/gfx/game_over/text_english.png

The prompt (game_over/text_<language>.gfx.lz, 32 x 6 tiles) is three 16-px lines of an outlined
font: the question in a shaded red, the two options in blue. Each glyph is cut out of a vanilla
line whose text is known: its fill columns (the bright colours, which never touch between
letters) plus one outline column on each side. The Catalan lines are set with the vanilla
spacing. The question is centred like the English one; the options start where the English
ones do (the helmet cursor doesn't move) and their brackets are aligned, as in every language.
Glyphs no prompt has (the hyphen) are built in DRAWN from the same colours.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import lz77  # noqa: E402

from PIL import Image  # noqa: E402

CATALAN = ["TORNAR-HO A PROVAR ?", "SÍ ( CONTINUA )", "NO ( SURT )"]
VANILLA = {
    "english": ["TRY AGAIN ?", "YES ( RETURN TO GAME )", "NO ( GO TO TITLE )"],
    "german": ["ERNEUTER VERSUCH ?", "JA ( ZUM SPIEL )", "NEIN ( ZUM TITEL )"],
    "french": ["RECOMMENCER LA PARTIE ?", "OUI ( REJOUER )", "NON ( QUITTER LE JEU )"],
    "italian": ["RIPROVARE ?", "SÌ ( RITORNA AL GIOCO )", None],   # None: a line that doesn't segment
    "spanish": [None, "SÍ ( CONTINUAR )", "NO ( SALIR )"],
}
WIDTH, LINE_H = 256, 16
RED_FILL = {1, 6}      # question: outline 3-5, shaded fill; only these never touch
BLUE_OUTLINE = 9       # options: one outline colour
QUESTION_CENTRE = 120  # the English question is centred on the screen
OPTIONS_LEFT = 55      # x of the options' outline in English
SPLIT = {"U", "V"}     # letters whose fill is two separate stems in the red font


def database():
    return {e["path"]: e for e in json.loads((catext.ROOT / "database.json").read_text())}


def sheet(language, db=None):
    """The prompt of a language as rows of palette indices (256 x 48)."""
    e = (db or database())[f"game_over/text_{language}.gfx.lz"]
    raw = lz77.decompress(catext.rom(), int(e["addr"]["us"], 16))[0]
    px = [[0] * WIDTH for _ in range(len(raw) // 32 // 32 * 8)]
    for t in range(len(raw) // 32):
        for y in range(8):
            for xb in range(4):
                b = raw[t * 32 + y * 4 + xb]
                px[(t // 32) * 8 + y][(t % 32) * 8 + xb * 2] = b & 15
                px[(t // 32) * 8 + y][(t % 32) * 8 + xb * 2 + 1] = b >> 4
    return px


def segments(px, line, is_fill):
    rows = px[line * LINE_H:(line + 1) * LINE_H]
    cols = [any(is_fill(r[x]) for r in rows) for x in range(WIDTH)]
    out, x = [], 0
    while x < WIDTH:
        if cols[x]:
            s = x
            while x < WIDTH and cols[x]:
                x += 1
            out.append((s, x))
        else:
            x += 1
    return out


def atlas(sheets):
    """({(colour, char): columns}, {colour: (letter gap, word gap)}); colour 0 = the red
    question, 1 = the blue options. Gaps are measured between fills."""
    glyphs, gaps = {}, {0: (Counter(), Counter()), 1: (Counter(), Counter())}
    for language, lines in VANILLA.items():
        px = sheets[language]
        for line, text in enumerate(lines):
            if text is None:
                continue
            colour = min(line, 1)
            is_fill = (lambda v: v in RED_FILL) if colour == 0 else (lambda v: v not in (0, BLUE_OUTLINE))
            segs = segments(px, line, is_fill)
            chars = text.replace(" ", "")
            if colour == 0:  # the two stems of U and V
                merged, i = [], 0
                for ch in chars:
                    if ch in SPLIT and i + 1 < len(segs) and segs[i][1] - segs[i][0] <= 3 \
                            and segs[i + 1][1] - segs[i + 1][0] <= 3:
                        merged.append((segs[i][0], segs[i + 1][1]))
                        i += 2
                    else:
                        merged.append(segs[i])
                        i += 1
                segs = merged + segs[i:]
            if len(segs) != len(chars):
                sys.exit(f"error: {language} line {line}: {len(segs)} glyphs for {text!r}")
            for (s, e), ch in zip(segs, chars):
                cols = [[px[y][x] for y in range(line * LINE_H, (line + 1) * LINE_H)] for x in range(s - 1, e + 1)]
                glyphs.setdefault((colour, ch), cols)
            words, i = text.split(" "), 0
            for w in words:
                for k in range(len(w) - 1):
                    gaps[colour][0][segs[i + k + 1][0] - segs[i + k][1]] += 1
                i += len(w)
                if i < len(segs):
                    gaps[colour][1][segs[i][0] - segs[i - 1][1]] += 1
    # the hyphen: the crossbar of the red H, capped with its outline colour
    h = glyphs[(0, "H")]
    mid = h[len(h) // 2]
    bar = [y for y in range(LINE_H) if mid[y] in RED_FILL]
    top, bottom = bar[0] - 1, bar[-1] + 1
    column = [mid[y] if top <= y <= bottom else 0 for y in range(LINE_H)]
    cap = [mid[top] if top <= y <= bottom else 0 for y in range(LINE_H)]
    glyphs[(0, "-")] = [cap] + [column] * 4 + [cap]
    return glyphs, {c: (g[0].most_common(1)[0][0], g[1].most_common(1)[0][0]) for c, g in gaps.items()}


def set_text(glyphs, colour, text, letter_gap, word_gap):
    """Columns of a composed text, from the first outline column to the last."""
    out, pen, space = {}, 1, False
    for ch in text:
        if ch == " ":
            space = True
            continue
        cols = glyphs.get((colour, ch))
        if cols is None:
            sys.exit(f"error: no {'red' if colour == 0 else 'blue'} glyph for {ch!r}")
        if out:
            pen += word_gap if space else letter_gap
        space = False
        for i, col in enumerate(cols):
            prev = out.get(pen - 1 + i, [0] * LINE_H)
            out[pen - 1 + i] = [c if c else p for c, p in zip(col, prev)]
        pen += len(cols) - 2
    return [out.get(x, [0] * LINE_H) for x in range(min(out), max(out) + 1)]


def compose():
    """The Catalan prompt as rows of palette indices (256 x 48)."""
    db = database()
    sheets = {language: sheet(language, db) for language in VANILLA}
    glyphs, gaps = atlas(sheets)
    px = [[0] * WIDTH for _ in range(3 * LINE_H)]

    def paste(cols, left, line):
        if left < 0 or left + len(cols) > 240:
            sys.exit(f"error: line {line} doesn't fit the screen ({left} to {left + len(cols)})")
        for dx, col in enumerate(cols):
            for dy, v in enumerate(col):
                if v:
                    px[line * LINE_H + dy][left + dx] = v

    question = set_text(glyphs, 0, CATALAN[0], *gaps[0])
    paste(question, round(QUESTION_CENTRE - len(question) / 2), 0)
    # options: word, bracket column, text, closing bracket, as "NO ( SALIR )" is laid out
    parts = [line.split(" ( ") for line in CATALAN[1:]]
    words = [set_text(glyphs, 1, p[0], *gaps[1]) for p in parts]
    es = segments(sheets["spanish"], 2, lambda v: v != 0)  # NO, (, SALIR, )
    bracket = OPTIONS_LEFT + max(len(w) for w in words) + (es[1][0] - es[0][1])
    for i, (word, p) in enumerate(zip(words, parts)):
        inner = set_text(glyphs, 1, p[1].rstrip(" )"), *gaps[1])
        paste(word, OPTIONS_LEFT, i + 1)
        paste(glyphs[(1, "(")], bracket, i + 1)
        left = bracket + (es[2][0] - es[1][0])
        paste(inner, left, i + 1)
        paste(glyphs[(1, ")")], left + len(inner) + (es[3][0] - es[2][1]), i + 1)
    return px


def palette():
    """Row 0 of game_over/background.pal as RGB triples."""
    e = database()["game_over/background.pal"]
    a = int(e["addr"]["us"], 16)
    out = []
    for i in range(16):
        v = int.from_bytes(catext.rom()[a + 2 * i:a + 2 * i + 2], "little")
        out += [(v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3]
    return out


def main(out_png):
    px = compose()
    img = Image.new("P", (WIDTH, len(px)), 0)
    img.putpalette(palette() + [0] * (768 - 48))
    for y, row in enumerate(px):
        for x, v in enumerate(row):
            img.putpixel((x, y), v)
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    print(f"wrote {out_png}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else catext.CA / "gfx" / "game_over" / "text_english.png")
