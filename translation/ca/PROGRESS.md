# Progress

Working notes for the Catalan translation of Metroid Fusion (US). Read this first when
resuming: it says which step is in progress, what is verified and how, the decisions taken and
the questions still open. The plan is the nine steps of the original brief.

## Status

| # | Step | State |
|---|---|---|
| 1 | Extractor and round-trip test | done |
| 2 | Plumbing self-test (`LANG_CA=1 CA_SELFTEST=1`) | done |
| 3 | Tooling (gentext, lint, render, gap, po, glossary, review) | next (gentext done) |
| 4 | Glossary | |
| 5 | Translate all the text | |
| 6 | Font (· and any missing glyph) | |
| 7 | Graphics with baked-in text | |
| 8 | Credits | |
| 9 | Patch, CI, release | |

## Verified

- Vanilla `make` matches `mf_us.sha1`, checked before every commit (last: after the LANG_CA
  hooks went into `Makefile`, `linker.ld` and `src/new_file_intro.c`).
- `extract.py --check`: all 2223 strings of the seven languages, re-encoded from the dumps, are
  byte for byte what their pointers read in the ROM, and together they cover the whole text
  blob (0x6b2fac-0x72eee0). The only bytes no table points at are six lone terminators (an
  unreferenced empty string after the last navigation string of each language but the first).
  `test_extract.py` runs the same check on a fresh dump and on the committed one.
- Plumbing self-test (`make LANG_CA=1 CA_SELFTEST=1`), two ways:
  - `romcheck.py --selftest`: `mf_us_ca.gba` has the size of the base ROM and differs from it
    only in the 318 pointers of the English slot and in 76 581 bytes appended at 0x79ecc8;
    every English pointer leads to an identical copy of its vanilla string.
  - `selftest.py`: the same scripted input played on vanilla and on the self-test ROM in
    headless mGBA from power-on gives 271 identical screenshots (pixel for pixel). The route
    covers a new game, the whole intro (monologue text, the ship computer's typed dialogue), the
    first briefing (coloured words, Yes/No prompt), the "Main Deck" and "Navigation Room"
    location banners, the conversation in the first Navigation Room, the status screen and the
    Sleep Mode prompt of the pause screen. Eleven frames are kept as PNG in
    `translation/ca/build/selftest/` (gitignored). I looked at them: each shows what its label
    says.
  - Not covered by the route: message banners (item pickups, save prompt). They go through the
    same `sMessageTextPointers` table that `romcheck.py` verifies; a screenshot of one is still
    owed (step 5, once there is Catalan text to look at).
- `get_baserom.sh`: ROM already present, `$BASEROM_DIR`, and the "no source" error were each run.
  The `$BASEROM_US_URL` branch is the mzm-cat code unchanged and was not exercised here.

## How the game reaches its text (all checked against the ROM and the code)

- `gLanguage` (0x03000011) is written in two places only. `SetLanguage`
  (`asm/disasm_0x0809e598.s`, 0x080A13D0) stores the constant 2 (`LANGUAGE_ENGLISH`); `agbmain`
  calls it every time the title screen starts. The SRAM code in `asm/disasm_0x0807e678.s`
  (0x0808039x) restores a saved value or 0 at boot, before the title. So the US game always
  plays from slot 2, and Catalan replaces English. No other slot was considered.
- Pointer tables (ROM offsets), seven languages in `LANGUAGE_*` order:
  - message (48 entries) at 0x79c5c0 + 0x128·lang, location (26) at 0x79c680 + 0x128·lang
    (`data/Blob_79c5c0_79cdd8.bin`).
  - navigation (225 entries; hiragana has 222) at 0x79ce10, 0x79d194, 0x79d50c, 0x79d890,
    0x79dc14, 0x79df98, 0x79e31c (`data/Blob_79ce10_79e6a0.bin`).
  - monologue (19) in C, `sMonologueTextPointers<Language>` in `src/new_file_intro.c`
    (English at 0x79e6ec).
- References to those tables, found by grepping src/, include/ and asm/ and by scanning the
  whole ROM for words that point into them:
  - `sMessageTextPointers` (0x79cdf4) and `sLocationTextPointers` (0x79cdd8), also reached by
    raw address `0x879cdf4` six times in `asm/disasm_0x08079afc.s`.
  - `sNavigationTextPointers` (0x79c3ac, `src/new_file_intro.c`).
  - `sNavConversationTextPointers` (0x79c0f0) and `sPauseScreenTextPointers` (0x79c10c) in
    `src/menus/pause_screen.c`: the same navigation tables again, the second one from entry
    114 (`0x879D6D4` = `0x879D50C` + 114·4). So the navigation table is two things: entries
    0-113 are conversations, 114-224 the pause-screen text.
  - `sMonologueTextPointers` (0x79c5a4).
- Individual English strings are pointed at only from the English tables above. The ROM-wide
  scan found three other words equal to a string address; all three are coincidences (two at
  odd offsets inside code, one inside the compressed `menus/pause_screen/obj.gfx.lz`), and none
  is an English string.
- The ROM has 398 136 bytes of 0xFF padding after 0x79ecc8, so appended data fits in 8 MB.

## Control codes

Read from `NavigationConversationProcessText` (`asm/disasm_0x08079afc.s`) and `src/text.c`.
Named in `charmap.txt`:

| Code | Name | Meaning |
|---|---|---|
| 80xx | `{GAP(n)}` | advance the pen n px |
| 81xx | `{COLOR(n)}` | ink colour |
| 82xx | `{SPEED(n)}` | frames per character (0 = 8); not used by the shipped text |
| 83xx | `{INDENT(n)}` | pen to n px from the start of the line |
| 9xxx | `{PLAY(n)}` | `unk_3bd4`: play music n, or sound n if n is not a music ID |
| Axxx | `{STOP(n)}` | `unk_3c14`: stop it |
| E1xx | `{DELAY(n)}` | wait n frames |
| E2xx | `{SPEAKER(n)}` | 0: the computer's text box; 1 and 2: the lower box, each with its own typing sound |
| FC00 | `{ARROW}` | next-page arrow, wait for a button |
| FD00 | `{NEW_PAGE}` | wait for a button, clear the box |
| FE00 | `\n` | new line |
| FF00 | (terminator) | added by the tools |

Kept as raw `{xHHHH}` because only part of their effect is known (byte for byte the same in
every language, so the linter just requires them to match the Spanish):

- `{xE000}` sets bit 0x400 of the conversation flags when bit 0x200 is set; `{xE001}` waits
  until bit 0x400 clears. Probably "show the target on the map and wait for it".
- `{xE300}` / `{xE301}` set and clear bit 0x40 of the same flags.
- `{xB001}`, `{xB002}` set a byte at offset 0x264 of the conversation data; `{xB003}` starts
  music 0x2a.
- `{xFB00}` ends the text like the terminator but sets the end state to 2 instead of 1.
- Cxxx sets the end state to 6 (not used by the shipped text).

Button icons are two codes each (`{B_button}` = 030A 030B).

## Decisions

- **In-place tables.** The English pointer tables keep their addresses and sizes; only the
  pointer values in them change, to strings in an object appended after everything else. This
  is the brief's rule ("only the replaced pointer values move") applied one level lower than
  `sMessageTextPointers[slot]`: since the tables themselves don't move, every raw reference to
  them (`0x879D50C`, `0x879D6D4`, `0x879cdf4`) stays valid without being touched.
- **IDs** are table + index (`MESSAGE_07`, `NAV_042`, `PAUSE_003`, `MONOLOGUE_11`): upstream has
  no names for them. `PAUSE_nnn` is navigation-table entry 114 + nnn.
- **Vanilla dumps are committed** under `text/<language>/`, as the brief asks. They are
  generated files; `test_extract.py` fails if they drift from the ROM.
- **Charmap** lives in `translation/ca/charmap.txt` (upstream's `charmap.txt` is a TODO stub):
  the mzm one plus Fusion's control codes, with the button icons as two codes.

## Upstream files touched

- `Makefile`: one `include translation/ca/ca.mk`, right after `TARGET` gets its `.gba`.
- `linker.ld`: under `#ifdef LANG_CA`, a `.ca_data` section after `.data` that holds
  `translation/ca/build/ca_text.o(.rodata)`.
- `src/new_file_intro.c`: under `#ifdef LANG_CA`, the include of the generated
  `ca/text_tables.h`; the two blobs that are pointer tables (`sBlob_79c5c0_79cdd8`,
  `sBlob_79ce10_79e6a0`) become arrays of pointers with the same contents except the English
  entries; `sMonologueTextPointersEnglish` gets its 19 pointers from the same header.

## Environment notes

- Toolchain used here: `binutils-arm-none-eabi` (apt), agbcc built from pret/agbcc and installed
  into `tools/agbcc` (gitignored), python3 with Pillow, libpng-dev, libmgba-dev 0.10.2.
- `gbashot` (from mzm-cat) gained `peek8/16/32 ADDR` and `poke8/16/32 ADDR VALUE`, to read the
  game state while scripting a route and to place Samus. Useful addresses (from `linker.ld`):
  `gCurrentRoom` 0x0300002D, `gSamusData.xPosition` 0x0300125A, `.yPosition` 0x0300125C,
  `gEventCounter` 0x03000B87, `gMainGameMode` 0x03000BDE.
- The docking bay exit is on the LEFT. The first shaft (room 6) is tall; the hatch to the
  Navigation Room is at its top left (Samus at x=0x180, y=0x23f stands next to it).
- Base ROM: sparse checkout of `metroid-fusion/` from the private ROM repository, copied to
  `mf_us_baserom.gba` (gitignored by `*.gba`).

## Open questions

None yet.
