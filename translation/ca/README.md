# Metroid Fusion en català

A Catalan fan translation built from this decompilation. The US game always plays in English,
so Catalan replaces the English slot (`LANGUAGE_ENGLISH`); the other six languages in the ROM
are untouched. Releases are `.bps` patches against the vanilla US ROM (SHA1
`ca33f4348c2c05dd330d37b97e2c5a69531dfe87`, also in `mf_us.sha1`). Everything about the
translation lives under `translation/ca/`. The ROM is never committed or distributed.

`PROGRESS.md` says what is done, what is verified and what is still open.

## How it fits in a decomp that is not shiftable

About a thousand ROM addresses are hard-coded in this decomp and all the game text is one binary
blob, so nothing that exists may move or change size. `LANG_CA=1` therefore only appends:

- the Catalan text goes in a new object that `linker.ld` places after everything else (the US
  ROM has 398 KB of padding there, so it stays 8 MB);
- the English pointer tables keep their place and size, and only their pointer values change;
- the font is edited in place (one glyph and its width), which keeps its size.

`tools/romcheck.py` proves it on every build: a Catalan ROM may differ from the base ROM only in
those pointers and in the appended area. Plain `make` still matches `mf_us.sha1`.

## Layout

```
text/<category>.txt      the Catalan text: message, location, navigation, pause, monologue
text/<language>/*.txt    the vanilla text of the seven languages, dumped from the ROM (generated)
charmap.txt              the characters and control codes of the text
font/glyphs/XXXX.png     edited glyphs (char ID in hex), drawn over the extracted font
font/widths.txt          sCharacterWidths overrides for those glyphs
identical.txt            IDs whose Catalan is meant to equal the English
glossary.md              terminology (APPROVED / PROPOSED), STYLE.md, notes/translator-notes.md
ca.mk                    the LANG_CA build, included from the top-level Makefile
translations.csv         every string in English, Spanish and Catalan, for playtesting (generated)
tools/                   extractor, generators, linter, GAP tool, emulator tools
reference/               your private references; gitignored
build/, dist/            generated files and CI outputs; gitignored
```

Upstream files touched: `Makefile` (one `include`), `linker.ld` (a section after `.data`, under
`#ifdef LANG_CA`), `src/new_file_intro.c` (the three English pointer tables), `src/data/text_data.c`
(the font) and `src/data/menus/pause_screen_misc_data.c` (the character widths), each under
`#ifdef LANG_CA`.

## Building

```sh
python3 tools/extractor.py                   # once, from your base ROM (below)
make -j"$(nproc)"                            # vanilla: still matches mf_us.sha1
make -j"$(nproc)" LANG_CA=1                  # mf_us_ca.gba, Catalan in the English slot
make -j"$(nproc)" LANG_CA=1 CA_SELFTEST=1    # plumbing self-test: the vanilla English, appended
python3 translation/ca/tools/romcheck.py     # the Catalan ROM changed nothing it shouldn't
```

Switching between these is safe: objects that depend on the mode are rebuilt automatically.
Tools need python3 with Pillow, and libmgba-dev for the emulator tools.

## Translating text

Each `text/<category>.txt` line is `ID = "text"`. IDs are the table and the index in it
(`MESSAGE_33`, `NAV_042`, `PAUSE_003`, `MONOLOGUE_11`), the same in every language; the vanilla
text of each language is in `text/<language>/`. IDs left out show in English, so the game
always builds.

| Category | What | Layout |
|---|---|---|
| `message` | banners: items, security levels, save and recharge prompts | 2 lines, centred with `{GAP(n)}` |
| `location` | location banners | 1 line, centred with `{GAP(n)}` |
| `navigation` | Navigation Room conversations and other typed dialogue | pages (`{NEW_PAGE}`) of 1 or 2 lines |
| `pause` | objectives on the pause screen | 2 lines |
| `monologue` | Samus's monologues, intro and ending narration | pages of up to 9 lines (full screen) or 2 (over a cutscene), each ending `{ARROW}{NEW_PAGE}` |

No line may pass 224 px. `charmap.txt` lists the control codes; `PROGRESS.md` explains them.
Keep `{SPEAKER(n)}`, `{PLAY(n)}`, `{STOP(n)}` and the raw `{xHHHH}` codes exactly as the
original has them: they drive sound, the map and who is speaking.

```sh
python3 translation/ca/tools/gap.py fix      # recompute the centring GAPs
python3 translation/ca/tools/lint.py         # check everything (--release: also completeness)
python3 translation/ca/tools/render.py out.png "{GAP(64)}Sala de guardat"   # quick preview
python3 translation/ca/tools/review.py       # refresh translations.csv (CI checks it is current)
python3 translation/ca/tools/extract.py --check   # the vanilla dumps still match the ROM
```

`translations.csv` lists every string side by side (English, Spanish, Catalan, where it shows,
status) for checking during a playthrough. Write your remarks in its `notes` column:
regenerating keeps them.

The linter compares each entry with the Spanish original and, where the shipped translations
disagree with each other, with the English too. `gap.py vanilla` shows the centring rule
reproduces every English, German and French GAP.

### Reviewing in Poedit

```sh
python3 translation/ca/tools/po.py export                 # translation/ca/build/mf-cat-ca.po
python3 translation/ca/tools/po.py import FILE.po --dry-run   # show what would change
python3 translation/ca/tools/po.py import FILE.po         # write it back
```

In Poedit each entry is a text ID (the context): English source, Catalan translation, and in the
sidebar the Spanish, where it shows and its line limits. Line breaks are real line breaks. Keep
the game's codes; the `{GAP(n)}` at the start of a banner line is recomputed on import. Use ”
for quotation marks (the game has no straight quote; the import refuses it). Poedit's Comment
field is the `notes` column of `translations.csv`: notes go both ways. Entries left empty keep
their text; "Needs work" entries are imported and listed.

## Testing in the emulator

`make ca-emu-tools` builds `build/gbashot` (headless mGBA: scripted input, screenshots, save
states, RAM peeks and pokes) and `build/bpscheck` (checks a patch with mGBA's own loader).

```sh
make -j"$(nproc)" && make -j"$(nproc)" LANG_CA=1 CA_SELFTEST=1
python3 translation/ca/tools/selftest.py     # same input on both ROMs, screenshots must be equal
```

## Base ROM

Every build starts from your own US dump. `tools/get_baserom.sh` puts it at `mf_us_baserom.gba`
in the repo root, and only after its SHA1 matches `mf_us.sha1`. It takes the ROM from, in order:

1. `mf_us_baserom.gba` already in the repo root (local builds; `*.gba` is gitignored),
2. `$BASEROM_DIR/mf_us_baserom.gba` (CI: a checkout of a private ROM repository),
3. `$BASEROM_US_URL`, a `.gba` or a `.zip` holding exactly one `.gba` (CI: a private link).

```sh
cp /path/to/your/dump.gba mf_us_baserom.gba
translation/ca/tools/get_baserom.sh            # verifies the SHA1
python3 tools/extractor.py && make -j"$(nproc)" && sha1sum -c mf_us.sha1
```
