"""Tests for extract.py and the text codec of catext.py.
Run: python3 -m unittest translation/ca/tools/test_extract.py   (needs mf_us_baserom.gba)"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import extract  # noqa: E402


class CodecTest(unittest.TestCase):
    def test_every_code_round_trips(self):
        # any u16 sequence, known or not, decodes to text that encodes back to itself
        for v in range(0x10000):
            if v == catext.CHAR_TERMINATOR:
                continue
            self.assertEqual(catext.encode(catext.decode([v])), [v], hex(v))

    def test_buttons_are_two_codes(self):
        self.assertEqual(catext.encode("{B_button}"), [0x030A, 0x030B])
        self.assertEqual(catext.decode([0x030E, 0x030F]), "{R_button}")
        self.assertEqual(catext.decode([0x030A]), "{x030A}")  # a lone half stays raw

    def test_named_and_raw_codes(self):
        text = "{SPEAKER(1)}{COLOR(2)}Hola{PLAY(88)}{xE000}{DELAY(20)}\\n{STOP(11)}{ARROW}{NEW_PAGE}{xFB00}"
        codes = catext.encode(text)
        self.assertEqual(codes[:2], [0xE201, 0x8102])
        self.assertEqual(codes[-1], 0xFB00)
        self.assertIn(0x9058, codes)
        self.assertIn(0xA00B, codes)
        self.assertEqual(catext.decode(codes), text)

    def test_catalan_letters(self):
        self.assertEqual(catext.encode("àçèéíïòóúü·"),
                         [0x3C0, 0x3C7, 0x3C8, 0x3C9, 0x3CD, 0x3CF, 0x3D2, 0x3D3, 0x3DA, 0x41D, 0x357])

    def test_bad_text(self):
        for bad in ["€", "{NOPE}", "{GAP}", "{ARROW(1)}", "{GAP(256)}", "{xFF00}", "{unclosed", '"']:
            with self.assertRaises(KeyError, msg=bad):
                catext.encode(bad)


class ExtractTest(unittest.TestCase):
    def test_tables(self):
        counts = {c: len(catext.entry_ids(c)) for c in catext.CATEGORIES}
        self.assertEqual(counts, {"message": 48, "location": 26, "navigation": 114, "pause": 111,
                                  "monologue": 19})
        self.assertEqual(len(catext.entry_ids("pause", "hiragana")), 108)
        # the game's own view of the split: sPauseScreenTextPointers = navigation table + 114
        self.assertEqual(catext.pointer_offsets("pause", "english")[0], 0x79D6D4)
        self.assertEqual(catext.pointer_offsets("navigation", "english")[0], 0x79D50C)

    def test_fresh_dump_reproduces_the_rom(self):
        with tempfile.TemporaryDirectory() as tmp:
            extract.cmd_extract(Path(tmp))
            problems, total = extract.check(Path(tmp))
        self.assertEqual(problems, [])
        self.assertEqual(total, 2223)

    def test_committed_dumps_reproduce_the_rom(self):
        problems, total = extract.check(catext.CA / "text")
        self.assertEqual(problems, [])
        self.assertEqual(total, 2223)

    def test_committed_dumps_are_current(self):
        for language in catext.LANGUAGES:
            for category in catext.CATEGORIES:
                path = catext.dump_path(category, language)
                self.assertEqual(path.read_text(encoding="utf-8"), extract.dump(category, language), path)


if __name__ == "__main__":
    unittest.main()
