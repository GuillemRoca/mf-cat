"""Tests for lint.py and gap.py.
Run: python3 -m unittest translation/ca/tools/test_lint.py   (needs mf_us_baserom.gba)"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gap  # noqa: E402
import lint  # noqa: E402


def centred(category, text):
    """`text` with the GAPs gap.py would give it."""
    return gap.recompute(category, text, catext.widths())[0]


SAVE_ROOM = 'LOCATION_16 = "%s"' % centred("location", "Sala de guardat")


class LintTest(unittest.TestCase):
    def run_lint(self, files, middot_glyph=True, base=None):
        with tempfile.TemporaryDirectory() as tmp:
            for category, info in catext.CATEGORIES.items():
                if base:
                    shutil.copy(catext.dump_path(category, base), Path(tmp) / info[0])
                else:
                    (Path(tmp) / info[0]).write_text("\n".join(files.get(category, [])) + "\n", encoding="utf-8")
            glyph = Path(tmp) / ("glyph.png" if middot_glyph else "none.png")
            if middot_glyph:
                glyph.write_bytes(b"")
            identical = Path(tmp) / "identical.txt"
            identical.write_text("\n".join(files.get("identical", [])) + "\n")
            rep, progress = lint.lint(Path(tmp), glyph, identical)
        return [(i["level"], i["id"], i["message"]) for i in rep.items], progress

    def assertOnly(self, items, level, fragment):
        self.assertEqual(len(items), 1, items)
        self.assertEqual(items[0][0], level, items)
        self.assertIn(fragment, items[0][2])

    def test_empty_translation_is_clean(self):
        items, progress = self.run_lint({})
        self.assertEqual(items, [])
        self.assertEqual({c: n for c, (_, n) in progress.items()},
                         {"message": 48, "location": 26, "navigation": 114, "pause": 111, "monologue": 19})
        self.assertEqual(sum(d for d, _ in progress.values()), 0)

    def test_good_entry(self):
        items, progress = self.run_lint({"location": [SAVE_ROOM]})
        self.assertEqual(items, [])
        self.assertEqual(progress["location"], (1, 26))

    def test_character_not_in_charmap(self):
        items, _ = self.run_lint({"location": ['LOCATION_16 = "Sala € de guardat"']})
        self.assertEqual(items[0][0], "error")
        self.assertIn("not in charmap", items[0][2])

    def test_lookalike_hint(self):
        items, _ = self.run_lint({"location": ['LOCATION_16 = "Sala d’espera"']})
        self.assertIn("use ' instead of ’", items[0][2])

    def test_unknown_and_duplicate_ids(self):
        items, _ = self.run_lint({"location": ['LOCATION_99 = "X"']})
        self.assertOnly(items, "error", "not in the English table")
        items, _ = self.run_lint({"location": [SAVE_ROOM, SAVE_ROOM]})
        self.assertOnly(items, "error", "defined twice")

    def test_stale_gap_is_a_warning(self):
        items, _ = self.run_lint({"location": ['LOCATION_16 = "{GAP(10)}Sala de guardat"']})
        self.assertOnly(items, "warning", "stale GAP(10)")

    def test_fixed_line_count(self):
        items, _ = self.run_lint({"location": ['LOCATION_16 = "%s"' % centred("location", "Sala\\nde guardat")]})
        self.assertOnly(items, "error", "2 lines, the Spanish has 1")
        items, _ = self.run_lint({"pause": ['PAUSE_001 = "Investiga la zona."']})
        self.assertOnly(items, "error", "1 lines, the Spanish has 2")

    def test_overflow(self):
        long = "Sala de guardat de la zona restringida del laboratori"
        items, _ = self.run_lint({"location": ['LOCATION_16 = "%s"' % long]})
        self.assertOnly(items, "error", "over the 224 px limit")

    def test_message_buttons_must_stay(self):
        text = centred("message", "Dades de míssils baixades.\\nPrem {B_button} per disparar.")
        items, _ = self.run_lint({"message": ['MESSAGE_04 = "%s"' % text]})
        self.assertOnly(items, "error", "event codes ['{B_button}'] differ")
        text = centred("message", "Dades de míssils baixades.\\nMantén {R_button} i prem {B_button}.")
        items, _ = self.run_lint({"message": ['MESSAGE_04 = "%s"' % text]})
        self.assertEqual(items, [])

    def test_prompt_keeps_its_indents(self):
        text = "%s\\n{GAP(87)}{INDENT(64)}Sí {INDENT(160)}No" % centred("message", "Guardar？")
        self.assertEqual(self.run_lint({"message": ['MESSAGE_33 = "%s"' % text]})[0], [])
        items, _ = self.run_lint({"message": ['MESSAGE_33 = "%s"' % centred("message", "Guardar？\\nSí No")]})
        self.assertOnly(items, "error", "event codes")

    def test_navigation_page_holds_two_lines(self):
        en = catext.vanilla_text("navigation", "english")["NAV_001"]
        events = "".join(lint.events("navigation", en))
        items, _ = self.run_lint({"navigation": ['NAV_001 = "U\\ndos\\ntres%s"' % events]})
        self.assertTrue(any("has 3 lines, the box holds 2" in m for _, _, m in items), items)

    def test_navigation_events_must_stay(self):
        en = catext.vanilla_text("navigation", "english")["NAV_000"]
        self.assertIn("{xFB00}", lint.events("navigation", en))
        items, _ = self.run_lint({"navigation": ['NAV_000 = "Hola."']})
        self.assertTrue(any(l == "error" and "event codes [] differ" in m for l, _, m in items), items)

    def test_monologue_needs_its_arrows(self):
        items, _ = self.run_lint({"monologue": ['MONOLOGUE_08 = "Una línia."']})
        self.assertOnly(items, "error", "doesn't end with {ARROW}")
        items, _ = self.run_lint({"monologue": ['MONOLOGUE_08 = "Una.{NEW_PAGE}Dues.{ARROW}"']})
        self.assertOnly(items, "error", "{NEW_PAGE} without {ARROW}")
        items, _ = self.run_lint({"monologue": ['MONOLOGUE_08 = "Una.{ARROW}{NEW_PAGE}Dues.{ARROW}"']})
        self.assertEqual(items, [])

    def test_monologue_page_size_is_the_shipped_one(self):
        three = 'MONOLOGUE_08 = "U\\ndos\\ntres{ARROW}"'       # over a cutscene: 2 lines
        self.assertOnly(self.run_lint({"monologue": [three]})[0], "error", "has 3 lines, the box holds 2")
        full = 'MONOLOGUE_00 = "%s{ARROW}"' % "\\n".join("abcdefghi")  # full screen: 9 lines
        self.assertEqual(self.run_lint({"monologue": [full]})[0], [])

    def test_colour_left_on(self):
        en = catext.vanilla_text("navigation", "english")["NAV_001"]
        events = "".join(lint.events("navigation", en))
        items, _ = self.run_lint({"navigation": ['NAV_001 = "Ves a la {COLOR(2)}sala%s"' % events]})
        self.assertTrue(any(l == "warning" and "ends in {COLOR(2)}" in m for l, _, m in items), items)

    def test_identical_to_spanish_and_identical_txt(self):
        es = catext.vanilla_text("location", "spanish")["LOCATION_16"]
        items, _ = self.run_lint({"location": ['LOCATION_16 = "%s"' % centred("location", es)]})
        self.assertTrue(any("identical to the Spanish" in m for _, _, m in items) or es != centred("location", es))
        en = catext.vanilla_text("pause", "english")["PAUSE_109"]
        items, progress = self.run_lint({"pause": ['PAUSE_109 = "%s"' % en]})
        self.assertEqual(progress["pause"][0], 0)
        self.assertOnly(items, "warning", "identical to the Spanish")
        items, progress = self.run_lint({"pause": ['PAUSE_109 = "%s"' % en], "identical": ["PAUSE_109  # debug"]})
        self.assertEqual((items, progress["pause"][0]), ([], 1))

    def test_middot_todo(self):
        entry = 'LOCATION_16 = "%s"' % centred("location", "Cel·la")
        self.assertOnly(self.run_lint({"location": [entry]}, middot_glyph=False)[0], "todo", "0357.png")
        self.assertEqual(self.run_lint({"location": [entry]})[0], [])

    def test_shipped_translations_pass(self):
        # The rules must accept what Nintendo shipped: no errors in German, French or Spanish.
        # (The English has a 225 px line and a navigation line that relies on the automatic
        # wrap; the Italian has a 3-line page and extra codes.)
        for language in ("german", "french", "spanish"):
            items, _ = self.run_lint({}, base=language)
            self.assertEqual([i for i in items if i[0] == "error"], [], language)


class GapTest(unittest.TestCase):
    def test_rule_reproduces_the_english(self):
        w = catext.widths(catalan=False)
        for category in gap.CENTRED:
            for idx, text in catext.vanilla_text(category, "english").items():
                self.assertEqual(gap.recompute(category, text, w)[1], [], idx)

    def test_full_and_empty_lines(self):
        w = catext.widths()
        self.assertEqual(gap.recompute("message", "{GAP(3)}\\n", w)[0], "{GAP(110)}\\n{GAP(110)}")
        full = catext.vanilla_text("message", "english")["MESSAGE_14"].split("\\n")[0]
        self.assertFalse(full.startswith("{GAP"))
        self.assertEqual(gap.recompute("message", "{GAP(9)}" + full, w)[0].split("\\n")[0], full)

    def test_prompt_line_is_left_alone(self):
        line = "{GAP(87)}{INDENT(64)}Sí {INDENT(160)}No"
        self.assertEqual(gap.recompute("message", line, catext.widths()), (line, []))

    def test_other_categories_have_no_gaps(self):
        self.assertEqual(gap.recompute("navigation", "Hola", catext.widths()), ("Hola", []))


if __name__ == "__main__":
    unittest.main()
