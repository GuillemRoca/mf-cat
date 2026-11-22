#!/usr/bin/env python3
"""Prints the width in px of text lines, to try wordings before putting them in text/*.txt.

  measure.py "line" ["line"...]      (\\n inside an argument splits it into lines)
  measure.py < FILE                  one line per input line

A line may be 224 px at most. Uses the Catalan width overrides (font/widths.txt).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402

if __name__ == "__main__":
    w = catext.widths()
    args = sys.argv[1:] or [l.rstrip("\n") for l in sys.stdin]
    for arg in args:
        for line in arg.split("\\n"):
            try:
                px = catext.line_layout(line, w)["pen_end"]
            except KeyError as e:
                print(f"  ?  {line}   ({e})")
                continue
            print(f"{px:4}{' !' if px > catext.LINE_LIMIT else '  '} {line}")
