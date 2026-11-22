#!/usr/bin/env python3
"""Checks that a LANG_CA ROM changed nothing it shouldn't: the decomp is not shiftable.

  romcheck.py [BUILT.gba] [--selftest]

Compares BUILT (default mf_us_ca.gba) with the base ROM byte by byte. Every byte that differs
must be in one of the regions the translation is allowed to write:
  - a pointer of the English slot (message, location, navigation and monologue tables), which
    must now point into the appended data;
  - the appended data: the padding after the last byte of the vanilla ROM (0x79ecc8 on).
Both ROMs must have the same size. With --selftest (a CA_SELFTEST=1 build) every English
pointer must also lead to a copy of its vanilla string.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402


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
    stray = [i for i in range(len(base)) if base[i] != built[i] and not allowed[i]]
    if stray:
        problems.append(f"{len(stray)} bytes changed outside the allowed regions, first at 0x{stray[0]:x}")
    stats = {"pointers": pointers, "appended_start": appended, "appended_bytes": end - appended,
             "free_bytes": len(base) - end}
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
        print(f"{stats['pointers']} English pointers repointed; {stats['appended_bytes']} bytes appended at "
              f"0x{stats['appended_start']:x}; {stats['free_bytes']} bytes of padding left; "
              f"{len(problems)} problems")
    sys.exit(1 if problems else 0)
