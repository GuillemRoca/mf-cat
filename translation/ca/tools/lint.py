#!/usr/bin/env python3
"""Lints translation/ca/text/*.txt against the vanilla text of the US ROM.

  lint.py [--release] [--json OUT] [--text-dir DIR]

The Catalan replaces the English tables (catext.SLOT). It is compared with the vanilla Spanish
(catext.REFERENCE), which it is modelled on, and where the shipped translations disagree with
each other, with the English too.

Errors (exit 1):
  - malformed lines, duplicate IDs, IDs that aren't in the English tables
  - characters missing from charmap.txt, unknown {CODES}
  - a line that crosses 224 px (the game would break it in the middle of a word)
  - too many lines: message, location and pause text have exactly the lines of the Spanish;
    a navigation page has at most 2; a monologue page at most what the shipped languages use
    for that monologue (9 on the full-screen ones, 2 over the cutscenes)
  - event codes that differ, in order, from both the Spanish and the English: {SPEAKER(n)},
    {PLAY(n)}, {STOP(n)}, the raw {xHHHH} codes, and in message banners the buttons and
    {INDENT(n)}
  - a monologue that doesn't end with {ARROW}, or a {NEW_PAGE} in one without {ARROW} before it
Warnings (exit 1 with --release):
  - stale centring GAPs (fix with gap.py fix)
  - {COLOR(n)} left on at the end of a text that ends in {COLOR(0)} in Spanish, or colours
    that no shipped language uses in that text
  - an empty page or an empty last line (a stray \\n or {NEW_PAGE})
  - text identical to the Spanish original (copied by mistake?)
TODO (never fail): · used while font/glyphs/0357.png doesn't exist yet.
Untranslated IDs show in English; --release fails if any remain.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gap  # noqa: E402

FIXED_LINES = {"message", "location", "pause"}
LOOKALIKES = {"’": "'", "‘": "'", "“": "”", "–": "-", "—": "-", "…": "...", "€": "(not in the font)"}
PAGE_RE = re.compile(r"\{NEW_PAGE\}|\{xFB00\}")
EVENTS = {"speaker", "play", "stop", "code"}
LAYOUT_CODES = {"{ARROW}", "{NEW_PAGE}"}


def pages(text):
    """[[line, ...], ...]: the text split where the box is cleared ({NEW_PAGE}, {xFB00}), each
    page split on \\n."""
    return [page.split("\\n") for page in PAGE_RE.split(text)]


def events(category, text):
    """The codes that must stay as in the vanilla text, in order."""
    out = []
    for kind, _, raw in catext.tokens(text):
        if kind in EVENTS and raw not in LAYOUT_CODES:
            out.append(raw)
        elif category == "message" and (kind == "indent" or (kind == "char" and raw.startswith("{"))):
            if not out or out[-1] != raw or kind == "indent":
                out.append(raw)  # a button is two glyphs with the same name: count it once
    return out


def colours(text):
    """(set of colours switched on, colour in effect at the end)."""
    used, current = set(), 0
    for kind, v, _ in catext.tokens(text):
        if kind == "color":
            current = v & 0xFF
            if current:
                used.add(current)
    return used, current


def page_limit(category, idx, others):
    if category == "navigation":
        return 2
    if category == "monologue":
        return max(len(p) for o in others for p in pages(o[idx]))
    return None


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, path, line, idx, msg):
        self.items.append({"level": level, "file": str(path), "line": line, "id": idx, "message": msg})

    def count(self, level):
        return sum(1 for i in self.items if i["level"] == level)


def lint(text_dir=catext.CA / "text", middot_glyph=catext.CA / "font" / "glyphs" / "0357.png",
         identical_path=catext.CA / "identical.txt"):
    rep = Report()
    w = catext.widths(catalan=True)
    identical = catext.identical_ids(Path(identical_path))
    middot_fixed = Path(middot_glyph).exists()
    progress = {}
    for category in catext.CATEGORIES:
        ids = catext.entry_ids(category)
        english = catext.vanilla_text(category, catext.SLOT)
        reference = catext.vanilla_text(category, catext.REFERENCE)
        others = [catext.vanilla_text(category, l) for l in catext.WESTERN]
        try:
            entries, path = catext.read_translation(category, text_dir)
        except ValueError as e:
            rep.add("error", Path(text_dir) / catext.CATEGORIES[category][0], 0, None, str(e))
            entries, path = {}, Path(text_dir) / catext.CATEGORIES[category][0]
        rel = path.relative_to(catext.ROOT) if path.is_relative_to(catext.ROOT) else path
        for idx in sorted(set(entries) - set(ids)):
            rep.add("error", rel, entries[idx][1], idx, "not in the English table (extra string)")
        done = 0
        for idx in ids:
            if idx not in entries:
                continue
            text, n = entries[idx]
            es, en = reference[idx], english[idx]
            if text != en or idx in identical:
                done += 1
            err = lambda msg: rep.add("error", rel, n, idx, msg)  # noqa: E731
            warn = lambda msg: rep.add("warning", rel, n, idx, msg)  # noqa: E731
            try:
                catext.tokens(text)
            except KeyError as e:
                msg = str(e).strip('"')
                bad = next((c for c in text if c in LOOKALIKES), None)
                err(msg + (f"; use {LOOKALIKES[bad]} instead of {bad}" if bad and repr(bad) in msg else ""))
                continue
            if "·" in text and not middot_fixed:
                rep.add("todo", rel, n, idx, "uses · before font/glyphs/0357.png exists")

            ev = events(category, text)
            if ev != events(category, es) and ev != events(category, en):
                err(f"event codes {ev} differ from the Spanish {events(category, es)}"
                    f" and the English {events(category, en)}")

            ca_pages, es_pages = pages(text), pages(es)
            if category in FIXED_LINES:
                if len(ca_pages) != 1 or len(ca_pages[0]) != len(es_pages[0]):
                    err(f"{len(text.split(chr(92) + 'n'))} lines, the Spanish has {len(es_pages[0])} (the box is fixed)")
            else:
                limit = page_limit(category, idx, others)
                for pn, page in enumerate(ca_pages, 1):
                    if len(page) > limit:
                        err(f"page {pn} has {len(page)} lines, the box holds {limit}")
            ln = 0
            for pn, page in enumerate(ca_pages, 1):
                for line in page:
                    ln += 1
                    lay = catext.line_layout(line, w)
                    if lay["overflow"]:
                        err(f"line {ln} (page {pn}) is {lay['pen_end']} px, over the {catext.LINE_LIMIT} px limit")
                if category not in FIXED_LINES:
                    visible = [l for l in page if catext.line_layout(l, w)["glyph_width"]]
                    last = pn == len(ca_pages)
                    if not visible and not (last and page == [""]) and \
                            any(catext.line_layout(l, w)["glyph_width"] for p in es_pages for l in p):
                        if not (last and not any(k == "char" for l in page for k, _, _ in catext.tokens(l))):
                            warn(f"page {pn} is empty")
                    elif visible and len(page) > 1 and not catext.line_layout(page[-1], w)["glyph_width"]:
                        warn(f"page {pn} ends with an empty line")

            if category == "monologue":
                bare = re.sub(r"\{DELAY\(\d+\)\}", "", text)
                if not bare.endswith("{ARROW}") and re.sub(r"\{DELAY\(\d+\)\}", "", es).endswith("{ARROW}"):
                    err("doesn't end with {ARROW}, the Spanish does")
                if re.search(r"(?<!\{ARROW\})\{NEW_PAGE\}", bare):
                    err("{NEW_PAGE} without {ARROW} before it: the page would vanish without waiting")

            used, last_colour = colours(text)
            shipped = set().union(*(colours(o[idx])[0] for o in others))
            if last_colour != colours(es)[1]:
                warn(f"ends in {{COLOR({last_colour})}}, the Spanish in {{COLOR({colours(es)[1]})}}")
            if used - shipped:
                warn(f"uses colours {sorted(used - shipped)} that no shipped language uses in this text")

            for line, old, new in gap.recompute(category, text, w)[1]:
                warn(f"line {line}: stale {gap.show(old)}, should be {gap.show(new)} (gap.py fix)")
            if text == es and idx not in identical:
                warn("identical to the Spanish original")
        progress[category] = (done, len(ids))
    return rep, progress


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", action="store_true", help="also fail on warnings and untranslated text")
    ap.add_argument("--json", help="write the report as JSON")
    ap.add_argument("--text-dir", type=Path, default=catext.CA / "text")
    a = ap.parse_args()
    rep, progress = lint(a.text_dir)
    for i in rep.items:
        print(f"{i['file']}:{i['line']}: {i['level']}: {i['id']}: {i['message']}")
    print("\ntranslated:")
    total_done = total = 0
    for category, (done, n) in progress.items():
        total_done += done
        total += n
        print(f"  {category:12} {done:3}/{n:<3} {100 * done / n:5.1f}%")
    print(f"  {'total':12} {total_done:3}/{total:<3} {100 * total_done / total:5.1f}%")
    errors, warnings, todos = rep.count("error"), rep.count("warning"), rep.count("todo")
    print(f"\n{errors} errors, {warnings} warnings, {todos} TODOs")
    if a.json:
        Path(a.json).write_text(json.dumps({"items": rep.items, "progress": {
            c: {"translated": d, "total": n} for c, (d, n) in progress.items()}}, indent=2, ensure_ascii=False))
    failed = errors or (a.release and (warnings or total_done < total))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
