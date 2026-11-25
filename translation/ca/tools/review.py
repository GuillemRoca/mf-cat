#!/usr/bin/env python3
"""Writes translation/ca/translations.csv: every game string in English, Spanish and Catalan,
side by side, to compare during a playthrough. Catalan takes the English slot; the Spanish is
there as the reference the Catalan is modelled on (catext.REFERENCE).

  review.py            regenerate the CSV
  review.py --check    fail if the CSV is out of date (CI)

One row per text ID (the five categories, in pointer-table order), then the strings drawn in
graphics and the Catalan credit, as later steps add them (EXTRA_ROWS). Control codes are
dropped and button glyphs shown as [A], [L], ...; line breaks stay line breaks inside the cell
and a blank line is a new page. Columns: section, id, where (on screen), english, spanish,
catalan, status (translated / same as English / untranslated), notes. The notes column is
yours: regenerating keeps it, matched by section and id.
"""
import argparse
import csv
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402

OUT = catext.CA / "translations.csv"
FIELDS = ["section", "id", "where", "english", "spanish", "catalan", "status", "notes"]
WHERE = {
    "message": "Message banner",
    "location": "Location banner",
    "navigation": "Navigation Room conversation / typed dialogue",
    "pause": "Pause screen, objective",
    "monologue": "Monologue or narration",
    "fileselect": "File select screen",
}
BUTTONS = {"A_button": "[A]", "B_button": "[B]", "L_button": "[L]", "R_button": "[R]",
           "Select_button": "[SELECT]", "Up_button": "[UP]", "Down_button": "[DOWN]",
           "Left_button": "[LEFT]", "Right_button": "[RIGHT]"}


def graphic_rows():
    """Strings drawn in graphics (the vanilla English and Spanish as on screen; the pause and
    status screens are English in every language of the US ROM), and the credits."""
    import gencredits
    import gfx_game_over
    rows = [{"section": "graphics", "id": "game_over_prompt", "where": "Game over screen",
             "english": "\n".join(gfx_game_over.VANILLA["english"]),
             "spanish": "¿INTENTAR DE NUEVO ?\nSÍ ( CONTINUAR )\nNO ( SALIR )",
             "catalan": "\n".join(gfx_game_over.CATALAN),
             "status": "translated" if (catext.CA / "gfx/game_over/text_english.png").exists() else "untranslated"}]
    import gfx_game_over_logo
    rows.append({"section": "graphics", "id": "game_over_logo", "where": "Game over screen, the logo",
                 "english": "GAME OVER", "spanish": "GAME OVER", "catalan": "\n".join(gfx_game_over_logo.LINES),
                 "status": "translated" if (catext.CA / "gfx/game_over/background.png").exists() else "untranslated"})
    import gfx_pause as gp
    done = "translated" if (catext.CA / "gfx/menus/pause_screen/obj.png").exists() else "untranslated"
    items = list(gp.ITEMS.items())
    for rid, where, english, catalan in (
            ("pause_tabs", "Pause screen, the L and R tabs", "SLEEP\nSTATUS", f"{gp.TAB_L}\n{gp.TAB_R}"),
            ("pause_area", "Map screen, the area name (SECTOR n stays)", "MAIN DECK", gp.AREA),
            ("pause_objective", "Map screen, beside the A button", "OBJECTIVE", gp.OBJECTIVE),
            ("pause_target", "Map screen, the flag on the objective; station diagram, its label", "TARGET", gp.TARGET),
            ("pause_start", "Station diagram, where Samus is", "START", gp.START),
            ("pause_legend", "Map screen, the security levels L1-L4", "LOCK\nOPEN", f"{gp.LOCK}\n{gp.OPEN}"),
            ("pause_system", "The computer's text box", "SYSTEM", gp.SYSTEM),
            ("status_title", "Status screen, the title", "STATUS", gp.TITLE),
            ("status_counters", "Status screen, the three counters", "ENERGY\nMISSILE\nP-BOMB",
             "\n".join(gp.COUNTERS.values())),
            ("status_headers", "Status screen, the group headers", "BEAM\nMISSILE\nBOMB\nSUIT\nMISC.",
             "\n".join(gp.HEADERS.values())),
            ("status_items", "Status screen, the item names", "\n".join(e for e, _ in items),
             "\n".join(c for _, c in items))):
        rows.append({"section": "graphics", "id": rid, "where": where, "english": english,
                     "spanish": english, "catalan": catalan, "status": done})
    import gfx_hud
    rows.append({"section": "graphics", "id": "hud_energy", "where": "HUD, over the energy counter",
                 "english": "ENERGY", "spanish": "ENERGY", "catalan": gfx_hud.LABEL,
                 "status": "translated" if gfx_hud.OUT.exists() else "untranslated"})
    import gfx_title
    rows.append({"section": "graphics", "id": "title_prompt", "where": "Title screen",
                 "english": "PRESS START", "spanish": "PRESS START", "catalan": " ".join(gfx_title.WORDS),
                 "status": "translated" if gfx_title.OUT.exists() else "untranslated"})
    import gfx_file_select as fsel
    for rid, where, english, catalan in (
            ("file_select_columns", "File select, over the files", "ENERGY\nTIME", f"{fsel.ENERGY}\n{fsel.TIME}"),
            ("file_select_area", "File select, the area of a saved file (SECTOR n stays)", "MAIN DECK", fsel.AREA)):
        rows.append({"section": "graphics", "id": rid, "where": where, "english": english, "spanish": english,
                     "catalan": catalan, "status": "translated" if fsel.OUT.exists() else "untranslated"})
    import gfx_erase
    for name, where in (("question", "Erase-all-data screen (L+R at power-on)"),
                        ("confirm", "Erase-all-data screen, after answering yes")):
        _, lines, answers = gfx_erase.SHEETS[name]
        rows.append({"section": "graphics", "id": f"erase_{name}", "where": where,
                     "english": "\n".join(gfx_erase.VANILLA[name] + ["No", "Yes"]).replace("？", "?"),
                     "spanish": {"question": "¿Quieres borrar todos\nlos datos guardados?\nNo\nSí",
                                 "confirm": "¿Seguro que quieres\nborrar todos los datos?\nNo\nSí"}[name],
                     "catalan": "\n".join(lines + answers).replace("？", "?"),
                     "status": "translated" if (gfx_erase.OUT / f"{name}.png").exists() else "untranslated"})
    heading, names = gencredits.read_credits()
    rows.append({"section": "credits", "id": "translation", "where": "Staff credits, a group of its own before EXECUTIVE PRODUCER",
                 "english": "", "spanish": "", "catalan": "\n".join([heading] + names), "status": "translated"})
    return rows


# Functions returning extra rows (graphics, credits).
EXTRA_ROWS = [graphic_rows]


def plain(text):
    """Game text without layout codes, as a reader sees it."""
    text = re.sub(r"\{NEW_PAGE\}|\{xFB00\}", r"\\n\\n", text)
    out = []
    for line in text.split("\\n"):
        line = re.sub(r"^(\{(GAP|INDENT|COLOR)\(\d+\)\})+", "", line)        # leading layout
        line = re.sub(r"\{(GAP|INDENT)\(\d+\)\}", "  ", line)                # gaps inside a line
        line = re.sub(r"\{(\w+)\}\{\1\}", r"{\1}", line)
        line = re.sub(r"\{(\w+)\}", lambda m: BUTTONS.get(m.group(1), ""), line)
        line = re.sub(r"\{\w+\(\d+\)\}", "", line)
        out.append(line.replace("？", "?").replace("！", "!").rstrip())
    text = "\n".join(out).strip("\n")
    return re.sub(r"\n{3,}", "\n\n", text)


def text_rows():
    same = catext.identical_ids()
    rows = []
    for category in catext.CATEGORIES:
        catalan, _ = catext.read_translation(category)
        english = catext.vanilla_text(category, catext.SLOT)
        spanish = catext.vanilla_text(category, catext.REFERENCE)
        for idx in catext.entry_ids(category):
            en = plain(english[idx])
            ca = plain(catalan[idx][0]) if idx in catalan else ""
            if idx in catalan:
                status = "same as English" if ca == en and idx in same else "translated"
            else:
                status = "same as English" if idx in same else "untranslated"
            rows.append({"section": category, "id": idx, "where": WHERE[category], "english": en,
                         "spanish": plain(spanish[idx]), "catalan": ca, "status": status})
    return rows


def render(old_notes):
    buf = io.StringIO()
    w = csv.DictWriter(buf, FIELDS, lineterminator="\n")
    w.writeheader()
    for r in text_rows() + [r for f in EXTRA_ROWS for r in f()]:
        r["notes"] = old_notes.get((r["section"], r["id"]), "")
        w.writerow(r)
    return buf.getvalue()


def read_notes(path=OUT):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {(r["section"], r["id"]): r.get("notes", "") for r in csv.DictReader(f) if r.get("notes")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    new = render(read_notes())
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if a.check:
        if new != old:
            sys.exit(f"error: {OUT.relative_to(catext.ROOT)} is out of date: run translation/ca/tools/review.py")
        print(f"{OUT.relative_to(catext.ROOT)} is up to date")
        return
    OUT.write_text(new, encoding="utf-8")
    print(f"wrote {OUT.relative_to(catext.ROOT)}")


if __name__ == "__main__":
    main()
