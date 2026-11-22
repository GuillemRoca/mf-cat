#!/usr/bin/env python3
"""Plumbing self-test in the emulator: the LANG_CA=1 CA_SELFTEST=1 ROM must draw every frame
exactly as the vanilla ROM does.

  selftest.py [VANILLA.gba] [SELFTEST.gba] [--out DIR] [--keep-all]

Plays the same scripted input on both ROMs with build/gbashot (headless mGBA) from power-on:
a new game, the whole intro (monologue text and the first typed dialogue), the first briefing
(navigation text with coloured words and the Yes/No prompt), the walk to the first Navigation
Room (the "Main Deck" and "Navigation Room" location banners), the conversation there, and the
pause screen (status screen, Sleep Mode prompt). It takes a screenshot every few seconds and
compares them pixel by pixel. A handful of them are written as PNG to DIR (default
translation/ca/build/selftest) for a human to look at.

The route uses two RAM pokes to put Samus next to the hatch at the top of the first shaft
instead of climbing it; both ROMs get the same pokes.

Needs `make ca-emu-tools`, mf_us.gba (vanilla build) and mf_us_ca.gba built with CA_SELFTEST=1.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CA = ROOT / "translation" / "ca"
GBASHOT = CA / "build" / "gbashot"

SAMUS_X, SAMUS_Y = 0x0300125A, 0x0300125C  # gSamusData.xPosition, .yPosition

# Shots kept as PNG: (label, what it shows)
KEEP = {
    "intro_005": "intro: monologue text over the cutscene",
    "intro_105": "intro: typed dialogue box (navigation table)",
    "intro_112": "intro: full-screen monologue",
    "brief_012": "first briefing: coloured words",
    "brief_036": "first briefing: Yes/No prompt",
    "walk_016": "location banner: Main Deck",
    "walk_037": "location banner: Navigation Room",
    "nav_008": "Navigation Room conversation",
    "nav_012": "Navigation Room conversation: second line",
    "pause_002": "pause: status screen",
    "pause_006": "pause: Sleep Mode prompt (pause-screen text)",
}


def route(shot):
    """The input script. `shot(group)` returns the line that takes the next screenshot."""
    s = ["wait 600", "tap S", "wait 120", "tap A", "wait 120", "tap A", "wait 60"]
    # intro: 136 taps of A (monologues, the ship's computer, the docking cutscene)
    for i in range(136):
        s += [shot("intro"), "tap A", "wait 112"]
    # first briefing, until Samus can move
    for i in range(46):
        s += [shot("brief"), "tap A", "wait 112"]
    s += ["wait 600"]
    # docking bay -> corridor -> shaft
    for i in range(6):
        s += ["hold LB 4", "hold L 56", shot("walk")]
    s += ["hold L 200", shot("walk")]
    # to the hatch at the top of the shaft, then left through the corridor into the Navigation Room
    s += [f"poke16 {SAMUS_X:x} 180", f"poke16 {SAMUS_Y:x} 23f", "wait 40", shot("walk")]
    for i in range(24):
        s += ["hold LB 4", "hold L 16", shot("walk"), "hold L 20", shot("walk")]
    # onto the pad; the conversation starts by itself
    s += ["hold R 26", "hold RA 10", "hold R 14"]
    for i in range(6):
        s += ["wait 30", shot("nav")]
    for i in range(18):
        s += ["tap A", "wait 100", shot("nav")]
    # pause screen: map, status (R), back, Sleep Mode prompt (L)
    s += ["tap S", "wait 90", shot("pause"), "tap r", "wait 90", shot("pause"), "wait 60", shot("pause"),
          "tap B", "wait 60", shot("pause"), "tap l", "wait 60", shot("pause"), "wait 60", shot("pause"),
          "wait 60", shot("pause"), "tap B", "wait 60", shot("pause"), "tap S", "wait 90", shot("pause")]
    return s


def run(rom, workdir):
    """Plays the route on `rom`; returns {label: path of the .ppm}."""
    shots, counts = {}, {}

    def shot(group):
        n = counts.get(group, 0)
        counts[group] = n + 1
        label = f"{group}_{n:03d}"
        shots[label] = workdir / f"{label}.ppm"
        return f"shot {shots[label]}"

    script = workdir / "route.txt"
    script.write_text("\n".join(route(shot)) + "\n")
    subprocess.run([str(GBASHOT), str(rom), str(script)], check=True)
    return shots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vanilla", nargs="?", default=str(ROOT / "mf_us.gba"))
    ap.add_argument("selftest", nargs="?", default=str(ROOT / "mf_us_ca.gba"))
    ap.add_argument("--out", type=Path, default=CA / "build" / "selftest")
    ap.add_argument("--keep-all", action="store_true", help="write every screenshot as PNG")
    a = ap.parse_args()
    if not GBASHOT.exists():
        sys.exit("error: build/gbashot is missing (make ca-emu-tools)")
    from PIL import Image

    a.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        dirs = [Path(tmp) / "vanilla", Path(tmp) / "selftest"]
        for d in dirs:
            d.mkdir()
        van, new = run(a.vanilla, dirs[0]), run(a.selftest, dirs[1])
        different, blank = [], 0
        for label in van:
            x, y = van[label].read_bytes(), new[label].read_bytes()
            if x != y:
                different.append(label)
            if len(set(x[-240 * 160 * 3:])) <= 1:
                blank += 1
            if a.keep_all or label in KEEP or label in different:
                Image.open(van[label]).save(a.out / f"{label}_vanilla.png")
                Image.open(new[label]).save(a.out / f"{label}_selftest.png")
        for label in KEEP:
            if label not in van:
                sys.exit(f"error: no screenshot called {label}")
    print(f"{len(van)} screenshots compared ({blank} of them one flat colour), {len(different)} differ")
    for label in different:
        print(f"  differs: {label} (see {a.out}/{label}_*.png)")
    print(f"kept as PNG in {a.out}:")
    for label, what in KEEP.items():
        print(f"  {label}: {what}")
    sys.exit(1 if different else 0)


if __name__ == "__main__":
    main()
