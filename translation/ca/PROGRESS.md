# Progress

Working notes for the Catalan translation of Metroid Fusion (US). Read this first when
resuming: it says which step is in progress, what is verified and how, the decisions taken and
the questions still open. The plan is the nine steps of the original brief.

## Status

| # | Step | State |
|---|---|---|
| 1 | Extractor and round-trip test | done |
| 2 | Plumbing self-test (`LANG_CA=1 CA_SELFTEST=1`) | done |
| 3 | Tooling (gentext, lint, render, gap, po, glossary, review) | done |
| 4 | Glossary | done; every term APPROVED (2026-11-25) |
| 5 | Translate all the text | done: 330 of 330 entries (the 318 of the four tables, and the 12 of the file select table found during step 7), first draft, all awaiting your review |
| 6 | Font (· and any missing glyph) | done |
| 7 | Graphics with baked-in text | in progress: everything found is done (game over, pause and status screens, HUD, title, file select, erase-all-data screen, the intro's vaccine panel) except the results screen; three asset folders still to look through (inventory below) |
| 8 | Credits | done |
| 9 | Patch, CI, release | done ahead of steps 7 and 8 (see Decisions); no release notes yet |

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
- Tooling (step 3): `python3 -m unittest translation/ca/tools/test_*.py` runs 35 tests
  (extractor and codec, lint and gap, .po round trip).
  - `gap.py vanilla`: the centring rule `GAP = round_half_even((220 - w) / 2)` reproduces all
    118 banner GAPs of the English, German and French text, 117 of the Italian and 104 of the
    Spanish (those two were centred by hand a pixel or two off).
  - The linter's rules were checked against what shipped: linting the vanilla German, French
    and Spanish as if they were the Catalan gives no errors. The English gives 2 (a 225 px line
    in `MONOLOGUE_02`, and `NAV_105`, which relies on the game's automatic wrap) and the
    Italian 6 (a 3-line page, swapped buttons, extra `{xE000}`): real quirks of those
    translations, which the Catalan must not copy.
  - `render.py` output was looked at once (accents draw; the vanilla `·` sits high and takes
    8 px, which step 6 fixes). Its colours are approximations, not the game's palettes.
- Glossary (step 4): `glossary.py import <mzm-cat glossary.md> --dry-run` reports no conflict
  with mzm-cat: the 35 APPROVED rows carry mzm-cat's Catalan unchanged. The 73 Fusion-only
  rows are PROPOSED.
- Text (step 5): `lint.py --release` passes with 318 of 318 entries, 0 errors, 0 warnings,
  0 TODOs. `make LANG_CA=1` builds; `romcheck.py` finds 76 855 appended bytes and no stray
  change. Seen in the emulator on the Catalan ROM (contact sheets of 300 frames, not kept): the
  whole intro narration, the ship computer's box and the first full-screen monologue. The
  pictures change at the right pages and the 9-line pages fit.
  - Also seen in game on the Catalan ROM, after the font step (PNG in
    `translation/ca/build/shots/ca_*.png`, gitignored): the first briefing with its coloured
    terms, the "Has entès l'objectiu？ Sí / No" prompt and the line after it, the banners
    "Coberta principal" and "Sala de navegació", the conversation in the first Navigation Room
    (two pages) and the Sleep Mode prompt of the pause screen. All fit their boxes.
  - NOT yet seen in game: item and security message banners, the objective line of the pause
    screen, any briefing after the first Navigation Room, the monologues after the intro, the
    ending. For those the only guarantee is the linter's pen model (which did predict the
    frames above correctly). The Catalan route was a scratch script: gameplay starts after
    about 190 A presses instead of the 182 of `selftest.py`'s English route; the walk and the
    pokes are the same.
- Font (step 6): `font/glyphs/0357.png` redraws `·` in Fusion's indices (2 fill, 3 outline) in
  the first three columns at mid x-height, and `font/widths.txt` gives it width 2.
  `romcheck.py` confirms the font in the Catalan ROM is the vanilla font plus that glyph, and
  that one width byte changed. Looked at in `render.py` ("cèl·lula", "L·L" read as one
  word); no in-game frame with a `·` has been captured yet. No other glyph was needed: every Catalan letter, « » and the
  accented capitals are in the vanilla font.
  - After the font hooks went in: self-test ROM still gives 271 identical screenshots and
    passes `romcheck.py --selftest`; vanilla still matches `mf_us.sha1`.
- Graphics plumbing (step 7): `gfx.py asm` appends each asset of `gfx_assets.json` as LZ77
  data after the text and the C code points at it by symbol. `lz77.py` was checked against
  the ROM: 394 compressed assets of `database.json` decompress and survive a
  compress/decompress round trip (one entry is not LZ77 data at its address), and the
  compressor's output fits the original slot for 347 of them.
  - Game over prompt: `gfx_game_over.py` composes "TORNAR-HO A PROVAR ? / SÍ ( CONTINUA ) /
    NO ( SURT )" (mzm-cat's approved wording) from glyphs cut out of the five vanilla prompts;
    the hyphen is built from the crossbar of the red H. Seen in game on the Catalan ROM
    (`build/shots/ca_game_over.png`): the three lines fit and the helmet cursor sits beside
    "SÍ".
  - With the hooks in: `romcheck.py` on the Catalan ROM (319 pointers repointed, 78 772 bytes
    appended, no stray change) and `--selftest` on the self-test ROM pass; `selftest.py` now
    also visits the game over screen and gives 275 identical screenshots; vanilla matches
    `mf_us.sha1`.
- Pause and status screens (step 7): `gfx_pause.py` composes both sheets and the status tilemap
  from letters it takes out of the vanilla sheets (only the letters English lacks are drawn in
  the tool). Seen in game on the Catalan ROM with every item switched on by RAM pokes
  (`build/shots/ca_pause_map.png`, `ca_pause_status.png`, `ca_pause_objective.png`,
  `ca_briefing_diagram_and_legend.png`, and `pause_overview.png` with the four together):
  - map screen: tabs REPÒS / ESTAT (background and sprite versions), COBERTA, OBJECTIU, the
    DESTÍ flag, the legend "L1 [door] TANCAT" ending where LOCK ended;
  - status screen: title ESTAT, counters ENERGIA / MÍSSIL / BOMBA E., headers RAIG, MÍSSIL,
    BOMBA, VESTIT, ALTRES, and the fifteen item names with their accents, each inside its box;
  - briefing: DESTÍ on the station diagram, and the legend on the briefing's map.
  - Not seen in game: OBERT (no security level is unlocked this early), INICI (the station
    diagram's START label) and SISTEMA (the label on the computer's text box, which is off
    screen in the scenes reached so far, in vanilla too). They are in the sheet
    (`gfx/menus/pause_screen/obj.png`) and use the same code paths as LOCK, TARGET and the box.
  - The target flag is drawn on alternate frames only (its animation is 33 one-frame steps
    that switch between "flag" and "dot"), so a screenshot shows it or not depending on the
    frame: take two consecutive ones. That is vanilla behaviour, not a bug.
  - References checked: each of the three assets has exactly one pointer in the ROM
    (0x76b30, 0x76b10, 0x76cb4), all in `src/menus/pause_screen.c`. The tiles the legend
    moves to (0x377-0x37a, 0x3b6-0x3b9) are among those the sheet marks with a cross; no OAM
    frame uses them and a build with the vanilla sheet showed them still crossed at run time.
  - With the hooks in: `romcheck.py` (324 pointers, 127 288 bytes appended, the legend's 160
    bytes of OAM as generated), `--selftest` on the self-test ROM, 275 identical screenshots,
    vanilla matches `mf_us.sha1`.
- HUD (step 7): `gfx_hud.py` writes "ENERGIA" over the energy counter, with the label's own
  letters plus an I and an A. Seen in game (`build/shots/ca_hud_energia.png`). The sheet
  (`hud/common.gfx`, uncompressed) is edited in place through a generated include, like the
  font; nothing refers to it by raw address (grep of `asm/` and `src/`). `romcheck.py` allows
  only the three tiles that differ and checks the sheet in the ROM is the PNG.
  - What the code showed: the label has 24 px, not the 32 of its sprite. The sprite's fourth
    tile is the first energy tank tile, which `HudDrawEnergy` rewrites (a first attempt that
    ran into it showed "ENERGIF" in game).
  - A save state made before the change keeps showing ENERGY even after pausing: the game
    restores the sprites it had. A new room or a new game loads the edited sheet.
  - After the hook: self-test ROM passes, 275 identical screenshots, vanilla matches
    `mf_us.sha1`.
- Title screen (step 7): `gfx_title.py` builds "PREM START" from the sheet's own letter cells
  (P, R, E of PRESS, the M of START GAME, START whole), in both shadings, centred where PRESS
  START was. Seen in game (`build/shots/ca_title_prem_start.png`). The sheet is appended and
  its two pointers (0x86ae0, 0x871c4: the two loads in `src/menus/title_screen.c`) repointed.
  - The rest of that sheet (START GAME / Language in five languages) is the menu of the other
    regions' ROMs. In the US game the prompt leads straight to the file select, in vanilla
    and here, so it is left as it is.
  - After the hook: self-test ROM passes, 275 identical screenshots, vanilla matches
    `mf_us.sha1`.
- File select text (step 5, found in step 7): the twelve strings are extracted for the seven
  languages (`text/<language>/fileselect.txt`; `extract.py --check` now re-encodes 2307
  strings), translated (`text/fileselect.txt`) and appended like the rest; the English block's
  twelve pointers are repointed in place. Seen in game (`build/shots/ca_file_select.png`,
  `ca_file_select_menu.png`): "DADES DE SAMUS", "SO", "SURT" and the menu "JUGA / COPIA /
  ESBORRA".
  - Not seen in game: the copy and erase prompts (`FILE_02` to `04`, which need a saved
    file), the corrupted-save messages (`FILE_05` to `10`) and `FILE_24` ("Continua / Nova
    partida", shown for a file that has a save).
  - The boxes of that screen are narrower than a text line and their widths are not known
    from the code. `lint.py` holds each Catalan line to the widest line any shipped Western
    language has in the same box (130 px for the title, 78 for the menu, 138 for the
    prompts), and to the English number of lines.
  - The self-test route already photographs this screen and its menu (its first frames,
    now kept as `intro_001` and `intro_002`): still 275 identical screenshots, `romcheck.py
    --selftest` passes with 338 pointers, vanilla matches `mf_us.sha1`.
- File select graphics (step 7): `gfx_file_select.py` writes ENERGIA, TEMPS and COBERTA into
  the screen's sprite sheet with the sheet's own letters (COBERTA's come from the Spanish
  CUBIERTA that the sheet also holds). ENERGIA and TEMPS seen in game
  (`build/shots/ca_file_select.png`).
  - Not seen in game: COBERTA, which shows for a file saved on the Main Deck.
  - The sheet is LZ77 at 0x73dc20 inside `data/Blob_73cfac_7478a0.bin`, with one reference
    in the ROM: the literal `_0809E9B8` in `asm/disasm_0x0809e598.s`. That file is assembled
    without the C preprocessor, so the literal sits in an `.ifdef LANG_CA` and `ca.mk` passes
    `--defsym LANG_CA=1`, the way the Makefile passes the region to assembly.
  - Sizes come from the OAM data in the same blob: ENERGY and TIME are one 32 x 16 sprite
    each (tiles 0x118, 0x11c), MAIN DECK a 32 x 16 and a 16 x 16 (tiles 0x8a, 0x8e).
  - After the hook: self-test ROM passes, 275 identical screenshots (they include this
    screen), vanilla matches `mf_us.sha1`.
- Erase-all-data screen (step 7): hold L and R at power-on (`src/init_game.c`). Each language
  has two 128-tile sheets, its two questions with their answers, listed in pairs in a table
  at 0x79c228 that `EraseSramMenuInit` (`asm/disasm_0x0807e678.s`) indexes with the language.
  The table is inside `data/Blob_79c170_79c27c.bin` (`src/text.c`). `gfx_erase.py` types the
  Catalan sheets with the game font, the way the shipped ones are laid out; the two English
  pointers (0x79c238, 0x79c23c: the only references to those sheets in the ROM) are repointed
  through a generated header, as for the text tables. Seen in game
  (`build/shots/ca_erase_question.png`, `ca_erase_confirm.png`): "Vols esborrar totes / les
  dades guardades?" and "Segur que vols esborrar / totes les dades?", each with No and Sí and
  the cursor beside them.
  - Not done: answering Sí twice, which erases the save memory. "Operation complete." is in
    the file select table's reference strings (entry 19) but no graphic with it was found
    among what this screen loads (its shared sheet at 0x582bbc is the box and the cursor), so
    whether the US game shows anything after erasing is not known.
  - After the hook: self-test ROM passes, 275 identical screenshots, vanilla matches
    `mf_us.sha1`.
- Intro vaccine panel (step 7): the title Vaccine "Metroid" is in
  `new_file_intro/metroid_vaccine_obj.gfx.lz` (one pointer, 0x8c7f4, the load in
  `src/new_file_intro.c`). `gfx_intro.py` makes it Vacuna "Metroid" from the title's own
  letters; the u is built from the rows of the n. Seen in game
  (`build/shots/ca_intro_vaccine_panel.png`, the 76th press of A in the intro). Two leftovers
  of the i showed up in game and were fixed: its top row and its dot sit above the letters'
  rows.
  - The rest of that sheet and of `samus_nervous_system_obj` is diagrams, digits and small
    print that is not readable text.
  - After the hook: self-test ROM passes, 275 identical screenshots (the intro frames include
    this panel), vanilla matches `mf_us.sha1`.
- Patch and CI (step 9): `translation/ca/tools/ci.sh` ran here from start to finish with exit
  code 0: 36 tool tests, `extract.py --check`, vanilla SHA1, the self-test ROM (`romcheck.py
  --selftest` and 275 identical screenshots), lint 318/318 with no errors or warnings, the
  Catalan ROM's `romcheck.py`, and a 74 861-byte `.bps` that `bps.py apply` and mGBA's own
  loader (`bpscheck`) both turn into exactly `mf_us_ca.gba`.
  - On GitHub: run 1 of the Catalan workflow (commit 2d5ccae) finished green in under two
    minutes. Its log shows every part ran: agbcc built and cached, the ROM folder checked out
    with the deploy key, the emulator comparison, lint 318/318, and a Catalan ROM with the same
    SHA1 (3f05d044…) and the same 74 861-byte patch as the local build. The artifact
    `mf-cat-<commit>` holds the patch, the lint report and the `.po`.
  - `release.yml` is mzm-cat's with the names changed. It has never run here.
- Credits (step 8): the US credits have no TRANSLATION section. `gencredits.py` puts
  "CATALAN / Guillem Roca Castany" in a group of its own right before EXECUTIVE PRODUCER (your
  decision of 2026-11-25), in place of the middle one of the three spacers there. `sCredits` is
  rewritten in place: still 310 entries and 471 scroll rows (two blank lines before the
  copyright become one empty big line to give back the extra entry). Not checked: that the
  credits still end in time with the music (the row count says they should; nobody listened).
  - `romcheck.py` verifies the table in the ROM is the generated one, and that `--vanilla`
    reproduces the vanilla table. After the hook: self-test ROM passes, 275 identical
    screenshots, vanilla matches `mf_us.sha1`.
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
  - file select (found during step 7; the brief's list of tables didn't have it): 25
    pointers per language block at 0x79ea08 (Japanese), 0x79ea6c (English), 0x79ead0,
    0x79eb34, 0x79eb98, 0x79ebfc, inside `data/Blob_79e890_79eca0.bin`
    (`src/menus/game_over.c`). A seven-entry table at 0x79ec68 gives each language its block
    (hiragana uses the Japanese one); `asm/disasm_0x0809e598.s` reads it nine times with
    `gLanguage`. The strings are not in the text blob but in `data/Blob_73cfac_7478a0.bin`
    (0x740f08 on). Entries 0-10 and 24 are strings the game draws (`FILE_00` to `FILE_10`,
    `FILE_24`): the screen's labels, the file menu, the copy and erase prompts, six messages
    for a corrupted save, and "Continue / Start Over". The code reads entries 0-4 and 24 by
    constant offset; 5-10 (the corrupted-save messages) by a computed one, not traced.
    Entries 11-23 have no terminator and nothing was found that draws them: they are the
    wording of text that is graphics (PRESS START, SELECT LANGUAGE, the game over prompt, the
    results screen, and the erase-all-data screen). They are left as they are.
  - A second seven-entry table at 0x79ec84 points every language at the same two strings
    ("--:--" and a list of three-letter area codes): not language text, left alone.
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

## Text layout (what the linter enforces)

- No line may pass 224 px. The navigation box wraps a glyph that crosses 224 px onto its second
  line, in the middle of a word, so lines are always broken by hand.
- `message`: 2 lines; `location`: 1; `pause`: 2 (all exactly as the Spanish). Banners are
  centred with a leading `{GAP(n)}`; a line that fills the banner has none; an empty line is
  `{GAP(110)}`; the Yes/No line of a prompt is `{GAP(87)}{INDENT(64)}Yes {INDENT(160)}No` and
  is never recomputed.
- `navigation`: pages of 1 or 2 lines. `{NEW_PAGE}` ends a page; so does `{xFB00}`, after which
  the text continues in a fresh box (it is what follows the Yes/No confirmation).
- `monologue`: `MONOLOGUE_00` to `07` are full-screen pages of up to 9 lines; `08` to `18`
  are 2-line pages over a cutscene. Pages end `{ARROW}{NEW_PAGE}`, the text ends `{ARROW}`.
- Event codes (`{SPEAKER}`, `{PLAY}`, `{STOP}`, raw codes; buttons and `{INDENT}` in banners)
  must match the Spanish or the English in order. Colours, line breaks, page breaks and delays
  differ between the shipped languages, so they are only sanity-checked.

## Translation notes for the reviewer

- Fusion's font is wide (most letters 8 px), so a line holds about 28 characters. Catalan runs
  longer than English, so many banners are shorter than a literal translation (e.g. "Nivell 1
  desblocat." for "Security Level 1 unlocked.", "Míssils baixats." for "Missile data
  downloaded.", "Capacitat augmentada." without naming the tank again). The briefings add pages
  instead, as the Spanish does.
- `IntroProcessText` (asm, 0x080984AC) tells the cutscene to change picture at a double
  `{ARROW}{ARROW}`. There is exactly one in MONOLOGUE_12, 15 and 16, in every language; the
  linter requires the same count. The number of ordinary pages is free.
- Entries the game never shows (NAV_038/039 "Empty", 051 "Demo use", 092, 103 "Not used", 113
  "None", PAUSE_030, 109/110, MESSAGE_42) are translated plainly.
- NAV_018 in English writes the sector code in full-width letters and has a redundant
  `{COLOR(0)}`; the Catalan uses plain "SRX" like every other entry.
- The drafting was done per page with a scratch markup; `text/navigation.txt` is the source.

## Decisions

- **In-place tables.** The English pointer tables keep their addresses and sizes; only the
  pointer values in them change, to strings in an object appended after everything else. This
  is the brief's rule ("only the replaced pointer values move") applied one level lower than
  `sMessageTextPointers[slot]`: since the tables themselves don't move, every raw reference to
  them (`0x879D50C`, `0x879D6D4`, `0x879cdf4`) stays valid without being touched.
- **Step 9 before steps 7 and 8.** The brief orders graphics, credits, then patch and CI. The
  patch and CI were done once the text, the font and the first graphic were in, because they
  don't depend on the rest and they make every later push check the vanilla SHA1 and the
  self-test. `RELEASE_CHECKLIST.md` says not to release before the graphics and credits are
  done.
- **Graphics wording where the space decided** (all in `gfx_pause.py`, one line each to change):
  - TARGET is "DESTÍ" and START is "INICI". "OBJECTIU" doesn't fit the flag (28 px) at the
    flag's letter size, and the A button already says OBJECTIU for the mission text.
  - MAIN DECK is "COBERTA": "COBERTA PRINCIPAL" needs twice the label's 46 px. The sectors
    keep "SECTOR n".
  - P-BOMB is "BOMBA E." (Bomba d'energia); it fills its counter cell to within a pixel.
  - LOCK / OPEN are "TANCAT" / "OBERT". The label sprite was 16 px (four small letters), so
    under `LANG_CA` it is a 32 px sprite on spare tiles and the whole legend starts 8 px (one
    map cell) further left; it ends where it did. The cost: it covers one more column of map.
  - Status headers and item names are mzm-cat's (RAIG, MÍSSIL, BOMBA, VESTIT, ALTRES; CÀRREGA,
    AMPLE, ONES, GEL, SÚPER, DIFUSIÓ, ENERGIA, CLIMÀTIC, GRAVITATORI, MORFOSFERA, SUPERSALT,
    ACCELERACIÓ, SALT ESPACIAL, ATAC ESPIRAL).
  - HUD: ENERGIA is 23 px of letters in a 24 px label, so the box keeps one margin column,
    on the right where the tanks follow, and its E starts at the left edge of the screen
    (ENERGY had a margin on both sides). The alternative with both margins is "ENERG.".
  - File select: ENERGIA fits its 32 px sprite with its two E's one pixel narrower than
    ENERGY's; MAIN DECK is "COBERTA", as on the map and as the Spanish sheet does (CUBIERTA).
  - Left alone: SAMUS (a name), SECTOR, and PREVIEW (the label of the map's preview point,
    `PAUSE_OAM_ID_MAP_PREVIEW_POINT`; not seen in play so far).
- **agbcc in CI** is pret/agbcc at da598c1 (the commit built and matched here), not the
  jiangzhengwenjz fork mzm-cat pins: Fusion's README asks for pret's.
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
- `src/data/text_data.c`: under `#ifdef LANG_CA`, `sCharactersGfx` comes from the generated
  `ca/font.inc` (same size).
- `src/data/menus/pause_screen_misc_data.c`: under `#ifdef LANG_CA`, the initializer of
  `sCharacterWidths` comes from the generated `ca/char_widths.inc`.
- `src/data/ending_data.c`: under `#ifdef LANG_CA`, the initializer of `sCredits` comes from
  the generated `ca/credits.inc` (same number of entries).
- `src/menus/game_over.c`: under `#ifdef LANG_CA`, the blob that is the file select's pointer
  tables (`sBlob_79e890_79eca0`) becomes an array of pointers from the generated
  `ca/text_tables.h`, the same words except the English strings' pointers. Also there:
  `sGameOverTextGfxPointers[LANGUAGE_ENGLISH]`
  is `sCaGfx_GameOverText` (the appended graphic), and the background sheet and the text
  tilemap are loaded from `sCaGfx_GameOverBg` and `sCaGfx_GameOverTextTilemap`.
- `src/menus/pause_screen.c`: under `#ifdef LANG_CA`, the sprite sheet, the background sheet
  and the status tilemap are loaded from `sCaGfx_PauseScreenObj`, `sCaGfx_PauseScreenBg` and
  `sCaGfx_StatusScreenTilemap`.
- `asm/disasm_0x0809e598.s`: under `.ifdef LANG_CA`, the literal `_0809E9B8` (the file
  select's sprite sheet) is `sCaGfx_FileSelectObj` instead of `0x0873DC20`. The only assembly
  file touched.
- `src/text.c`: under `#ifdef LANG_CA`, the blob that holds the erase-all-data screen's
  table of sheets (`sBlob_79c170_79c27c`) becomes an array of pointers from the generated
  `ca/gfx_tables.h`, the same words except the two English entries.
- `src/menus/title_screen.c`: under `#ifdef LANG_CA`, the sprite sheet is loaded (twice) from
  `sCaGfx_TitleScreenObjects`.
- `src/data/hud_data.c`: under `#ifdef LANG_CA`, `sCommonSpritesGfx` comes from the generated
  `ca/hud_common.inc` (same size).
- `src/data/menus/pause_screen_data.c`: under `#ifdef LANG_CA`, the eight OAM frames of the
  security level legend (`sPauseScreenOam_L1Lock_Frame0` to `L4Open_Frame0`) come from the
  generated `ca/pause_legend_oam.inc` (same size, edited in place).
- `src/new_file_intro.c`: under `#ifdef LANG_CA`, the include of the generated
  `ca/text_tables.h`; the vaccine panel's sprite sheet is loaded from
  `sCaGfx_IntroMetroidVaccineObj`; the two blobs that are pointer tables (`sBlob_79c5c0_79cdd8`,
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

## Step 7 inventory

From `database.json`, rendered as tile sheets and looked at. Two kinds:

Per-language graphics (the US ROM has one per Western language and a pointer table, so the
Catalan version is appended and the English pointer repointed):

| Asset | Text | State |
|---|---|---|
| `game_over/text_english.gfx.lz` (192 tiles) | TRY AGAIN ? / YES ( RETURN TO GAME ) / NO ( GO TO TITLE ) | done |
| `ending/results_english_text.gfx.lz` (448 tiles) | digits, CLEAR TIME, YOUR RATE FOR COLLECTING ITEMS IS, an alphabet, "See you next mission" | to do. `src/ending.c` loads it in the `default:` branch of a `switch (gLanguage)` (about line 1013), so the Catalan sheet can be appended and that one call repointed. The hard part is placement: the words are sprites set up by `EndingImageLoadTextOam` and `EndingImageDisplayLinePermanently` (asm, `asm/disasm_0x0809e598.s`), with per-language data and per-language timing (the second `switch (gLanguage)`, about line 1100). Seen in game still in English (`build/shots/results_screen_still_english.png`) |

Shared graphics (one copy for every language, English text; to translate them the graphic is
edited, put back in place if it still fits when compressed, else appended and every reference
repointed):

| Asset | Text seen | State |
|---|---|---|
| `menus/pause_screen/obj.gfx.lz`, `bg.gfx.lz` (1024 tiles each), `status_screen.tm.lz` | SLEEP, STATUS, OBJECTIVE, TARGET, START, MAIN DECK, L1-L4 LOCK / OPEN, SYSTEM; status screen (title, ENERGY / MISSILE / P-BOMB, group headers, item names) | done: composed by `gfx_pause.py`, appended, their one pointer each repointed; see Verified and Decisions |
| `menus/title_screen/objects.gfx.lz` | PRESS START; START GAME / Language (other regions' menu, not shown by the US game) | done: "PREM START", composed by `gfx_title.py`; the menu rows are left alone |
| file select sprites: LZ77 at 0x73dc20 inside `Blob_73cfac_7478a0.bin` (512 tiles), loaded by raw address in `asm/disasm_0x0809e598.s` | ENERGY, TIME, SECTOR 1-6, MAIN DECK (and the area names of four other languages), the language names | done: ENERGIA, TEMPS, COBERTA, composed by `gfx_file_select.py`. SAMUS DATA, SOUND, EXIT and the menus turned out to be text (the file select table, done). The background (LZ77 at 0x742fb4, 768 tiles) has English lore text as decoration (B.S.L SPACE LABORATORY, SECTOR:SRX): left alone |
| `hud/common.gfx` (uncompressed) | ENERGY | done: "ENERGIA", edited in place by `gfx_hud.py`; see Verified and Decisions |
| `new_file_intro/metroid_vaccine_obj.gfx.lz` | the title of the vaccine panel, Vaccine "Metroid" | done: Vacuna "Metroid", composed by `gfx_intro.py` |
| `game_over/background.gfx.lz` and `game_over/text.tm.lz` | the GAME OVER logo | done: "FI DE LA / PARTIDA" on two lines (it doesn't fit one at the logo's size), composed by `gfx_game_over_logo.py` from the letters of GAME OVER; the sheet and the tilemap are appended and their one pointer each repointed. Seen in game (`build/shots/ca_game_over.png`) |
| `ending/credits_character.gfx`, `copyright_text_*.gfx` | credits font, copyright lines | step 8 |

The erase-all-data screen (`GAME_MODE_ERASE_SRAM_MENU`) is done: two sheets per language,
LZ77 with no entry in `database.json`, English at 0x588478 and 0x589804.

Looked through as contact sheets (every graphic of 16 tiles or more): `new_file_intro/*`,
`title_intro/*`, `monologue/*` and `ending_cutscene/*`, 70 sheets in six pages. Pages 1, 2, 3
and 6 were read: besides the vaccine panel, the only words are names (SR388, B.S.L, P-1 to
P-3 on the intro's star chart; B.S.L on hulls), which stay. Two sheets,
`approaching_bsl_obj` and `monologue_obj`, also hold copies of the map screen's labels
(SYSTEM, TARGET, MESSAGE, LOCK); the star chart scene of the intro shows none of them
(looked at in game), and whether any other scene does is not known. Pages 4 and 5 (the
`sr388_*`, `bsl_object_*`, `samus_sitting_bg_*` and `samus_helmet_closeup_bg_*` strips) were
only listed by name. Not looked at: the demo and link screens.

### The results screen (not done): what the code does

Read on 2026-11-25; nothing is built yet.

- `src/ending.c` loads the text sheet in the `default:` branch of its first
  `switch (gLanguage)` (`sResultsScreenEnglishTextGfx`), so a Catalan sheet can be appended
  and that one call switched under `LANG_CA`.
- The three result lines are typed letter by letter. `EndingImageLoadTextOam(line)`
  (`asm/disasm_0x0809e598.s`, 0x080A1664) branches on the language; the English branch
  (`_080A1A28`) copies, for line 0, 1 or 2, a table of 12-byte entries into `ENDING_DATA`:
  one entry per letter = {1, delay (1, 5, 9... four frames apart), 0, 0, x of the line's
  centre (120), y of the line (40, 92, 108), pointer to an OAM frame}. Each frame is one
  16 x 16 sprite (8 x 16 for I) at an x offset from the centre, its tile the letter in the
  sheet's alphabet (A = 0x100, C = 0x104, E = 0x108, I = 0x110, L = 0x114, M = 0x116,
  O = 0x11a, R = 0x11e, S = 0x140, T = 0x142, U = 0x146, Y = 0x14a...).
  - line 0: table 0x74dc90, 9 letters, CLEAR TIME; line 1: 0x74dcfc, 11 letters, YOUR RATE
    FOR; line 2: 0x74dd80, 17 letters, COLLECTING ITEMS IS.
  - The letter counts are in the code: the loop bound (`cmp r3, #8`, `#0xa`, `#0x10`) and a
    byte stored at `gNonGameplayRam + 0x9b` (0xf, 0x11, 0x17 = count + 6). The RAM arrays
    hold 30 letters a line.
- So a Catalan results screen needs: its own letter tables and frames (new data, appended);
  the three table pointers and the six immediates in that branch under `.ifdef LANG_CA`
  (same instruction sizes, so nothing moves); the same look at
  `EndingImageDisplayLinePermanently` (0x080A1B60), which has not been read; and a sheet with
  any letters the English alphabet lacks.
- Not read yet: lines 3 to 5 (`EndingImageDisplayLinePermanently(3..5)`, probably "See you
  next mission" and the totals), and how the percentage and time digits are placed.
- The second `switch (gLanguage)` in `EndingImage` only matters for timing: English and
  Italian show a third line, the others two.
- Wording to use, from mzm-cat's approved results screen: TEMPS TOTAL DE JOC, OBJECTES
  ACONSEGUITS, "Fins a la propera missió!". Three lines are available here (9, 11 and 17
  letters in English); how to split them is open.
- To see the screen: `gMainGameMode` = 11 starts the credits; the results follow at about
  9600 frames.

Useful for screenshots: `gMainGameMode` (0x03000BDE) set to 8 with `gSubGameMode1`
(0x03000BE0) set to 0 during gameplay opens the game over screen. 11 starts the credits, which
run on into the ending pictures and the results screen (about 6400 frames to the Catalan
credit, 9600 to the results). 9 (the ending cutscene) is untried.

## Where to resume

1. (Done: the glossary is approved.)
2. Step 7, what is left: the results screen ("The results screen (not done)" above has what
   the code does and what a Catalan one needs). Then
   look at the assets not inventoried yet. `gfx_pause.py` is the model: take the letters from
   the vanilla sheet, redraw, append, repoint the one pointer, screenshot.
3. Write a Catalan route tool from `selftest.py` (see `TESTING.md`) and screenshot the text
   that has not been seen in game.
4. Release notes in `.github/release-notes/`, once the checklist can be ticked.

## Open questions

Decided on 2026-11-25: every proposed term approved as option 1, except Habitation Deck,
which is "Coberta de l'hàbitat"; the Catalan credit in a group of its own before EXECUTIVE
PRODUCER; the GAME OVER logo becomes "Fi de la partida"; and every other graphic with text is
translated, as in mzm-cat.

For you to confirm, on the pause and status screens (the space decided; see Decisions):

1. TARGET as "DESTÍ" and START as "INICI" (not "OBJECTIU", which is the A button's word).
2. MAIN DECK as "COBERTA" alone.
3. P-BOMB as "BOMBA E.".
4. "TANCAT" / "OBERT" with the legend one map cell further left, rather than four-letter
   abbreviations in the original place.
5. HUD: "ENERGIA" starting at the edge of the screen, rather than "ENERG." with a margin.
