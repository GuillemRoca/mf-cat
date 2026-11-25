#!/usr/bin/env python3
"""Checks that a LANG_CA ROM changed nothing it shouldn't: the decomp is not shiftable.

  romcheck.py [BUILT.gba] [--selftest]

Compares BUILT (default mf_us_ca.gba) with the base ROM byte by byte. Every byte that differs
must be in one of the regions the translation is allowed to write:
  - a pointer of the English slot (message, location, navigation, monologue and file select
    tables), which
    must now point into the appended data;
  - the appended data: the padding after the last byte of the vanilla ROM (0x79ecc8 on);
  - a pointer listed in gfx_assets.json (an edited graphic), which must also point into the
    appended data;
  - the tiles that differ in an uncompressed graphic edited in place ("inplace" in
    gfx_assets.json: the HUD sprites);
  - the staff credits, rewritten in place with the same size (sCredits, 0x74b0b0);
  - the eight OAM frames of the map's security level legend, edited in place (0x566502,
    160 bytes: see gfx_pause.py);
  - the font, edited in place: the tiles of the glyphs in font/glyphs/*.png (sCharactersGfx,
    0x682fac) and the bytes of sCharacterWidths (0x576234) listed in font/widths.txt.
Both ROMs must have the same size. With --selftest (a CA_SELFTEST=1 build) every English
pointer must also lead to a copy of its vanilla string, and the font must be untouched.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import font  # noqa: E402
import gencredits  # noqa: E402
import gfx  # noqa: E402
import gfx_pause  # noqa: E402
import lz77  # noqa: E402

FONT_OFFSET = 0x682FAC    # sCharactersGfx
WIDTHS_OFFSET = 0x576234  # sCharacterWidths
CREDITS_OFFSET = 0x74B0B0  # sCredits


def vanilla_end(rom):
    """Offset after the last byte of the vanilla ROM that is not 0xFF padding, 4-aligned."""
    i = len(rom)
    while rom[i - 1] == 0xFF:
        i -= 1
    return (i + 3) & ~3


def check(built_path, selftest=False):
    base = catext.rom()
    built = Path(built_path).read_bytes()
    problems = []
    if len(built) != len(base):
        return [f"{built_path} is {len(built)} bytes, the base ROM is {len(base)}"], {}
    appended = vanilla_end(base)
    end = len(built)
    while end > appended and built[end - 1] == 0xFF:
        end -= 1

    allowed = bytearray(len(base))  # 1 = may differ
    allowed[appended:] = b"\x01" * (len(base) - appended)
    pointers = 0
    for category in catext.CATEGORIES:
        offsets = catext.pointer_offsets(category, catext.SLOT)
        for (idx, _, codes), off in zip(catext.vanilla_codes(category, catext.SLOT), offsets):
            allowed[off:off + 4] = b"\x01\x01\x01\x01"
            pointers += 1
            target = struct.unpack_from("<I", built, off)[0] - catext.ROM_BASE
            if not appended <= target < end:
                problems.append(f"{idx}: its pointer at 0x{off:x} leads to 0x{target:x}, outside the appended data")
            elif selftest:
                data = catext.to_bytes(codes)
                if built[target:target + len(data)] != data:
                    problems.append(f"{idx}: the appended string differs from the vanilla English")
    for name, info in gfx.assets().items():
        if info.get("inplace"):  # same place and size; only the edited tiles may differ
            off, want = gfx.address(info), gfx.asset_tiles(name, info, selftest)
            if built[off:off + len(want)] != want:
                problems.append(f"{name}: the graphic in the ROM is not the expected one")
            for t in range(len(want) // 32):
                if want[t * 32:t * 32 + 32] != base[off + t * 32:off + t * 32 + 32]:
                    allowed[off + t * 32:off + t * 32 + 32] = b"\x01" * 32
            continue
        for off in (int(p, 16) for p in info["pointers"]):
            allowed[off:off + 4] = b"\x01\x01\x01\x01"
            pointers += 1
            target = struct.unpack_from("<I", built, off)[0] - catext.ROM_BASE
            if not appended <= target < end:
                problems.append(f"{name}: its pointer at 0x{off:x} leads to 0x{target:x}, outside the appended data")
            elif lz77.decompress(built, target)[0] != gfx.asset_tiles(name, info, selftest):
                problems.append(f"{name}: the appended graphic is not the expected one")
    credits = gencredits.pack(gencredits.table(vanilla_only=selftest))
    if built[CREDITS_OFFSET:CREDITS_OFFSET + len(credits)] != credits:
        problems.append("sCredits in the ROM is not the table gencredits.py builds")
    if selftest and credits != base[CREDITS_OFFSET:CREDITS_OFFSET + len(credits)]:
        problems.append("gencredits.py --vanilla doesn't reproduce the vanilla credits")
    if not selftest:
        allowed[CREDITS_OFFSET:CREDITS_OFFSET + len(credits)] = b"\x01" * len(credits)
    legend = gfx_pause.legend_bytes(selftest)
    if built[gfx_pause.LEGEND_FRAMES:gfx_pause.LEGEND_FRAMES + len(legend)] != legend:
        problems.append("the map legend's OAM frames are not the ones gfx_pause.py builds")
    if not selftest:
        allowed[gfx_pause.LEGEND_FRAMES:gfx_pause.LEGEND_FRAMES + len(legend)] = b"\x01" * len(legend)
    glyphs = 0
    if not selftest:
        w = catext.widths(catalan=True)
        for png in sorted(font.GLYPHS.glob("*.png")):
            cid = int(png.stem, 16)
            for off in font.glyph_tiles(cid, cid >= len(w) or w[cid] > 8):
                allowed[FONT_OFFSET + off:FONT_OFFSET + off + 32] = b"\x01" * 32
            glyphs += 1
        for cid in catext.width_overrides():
            allowed[WIDTHS_OFFSET + cid] = 1
            if built[WIDTHS_OFFSET + cid] != w[cid]:
                problems.append(f"the width of glyph {cid:04X} is {built[WIDTHS_OFFSET + cid]}, expected {w[cid]}")
        if built[FONT_OFFSET:FONT_OFFSET + font.FONT_SIZE] != font.load():
            problems.append("the font in the ROM is not the vanilla font with font/glyphs/*.png on top")
    stray = [i for i in range(len(base)) if base[i] != built[i] and not allowed[i]]
    if stray:
        problems.append(f"{len(stray)} bytes changed outside the allowed regions, first at 0x{stray[0]:x}")
    stats = {"pointers": pointers, "appended_start": appended, "appended_bytes": end - appended,
             "free_bytes": len(base) - end, "glyphs": glyphs}
    return problems, stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("built", nargs="?", default=str(catext.ROOT / "mf_us_ca.gba"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    problems, stats = check(a.built, a.selftest)
    for p in problems[:40]:
        print("error:", p)
    if stats:
        print(f"{stats['pointers']} pointers repointed; {stats['appended_bytes']} bytes appended at "
              f"0x{stats['appended_start']:x}; {stats['free_bytes']} bytes of padding left; "
              f"{stats['glyphs']} font glyphs redrawn in place; "
              f"{len(problems)} problems")
    sys.exit(1 if problems else 0)
