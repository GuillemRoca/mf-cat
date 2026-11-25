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
- the English pointer tables (five of them, in three blobs and one C array) keep their place
  and size, and only their pointer values change;
- the font (one glyph and its width), the staff credits, the HUD sprites (one label) and eight
  small OAM frames of the map screen are edited in place, keeping their size.

`tools/romcheck.py` proves it on every build: a Catalan ROM may differ from the base ROM only in
those pointers, in those in-place edits and in the appended area. Plain `make` still matches `mf_us.sha1`.

## Layout

```
text/<category>.txt      the Catalan text: message, location, navigation, pause, monologue, fileselect
text/<language>/*.txt    the vanilla text of the seven languages, dumped from the ROM (generated)
charmap.txt              the characters and control codes of the text
font/glyphs/XXXX.png     edited glyphs (char ID in hex), drawn over the extracted font
font/widths.txt          sCharacterWidths overrides for those glyphs
gfx/<asset>.png          edited graphics (.tm: a tilemap); <asset> is its key in tools/gfx_assets.json
credits.txt              the Catalan translators, added to the staff credits
identical.txt            IDs whose Catalan is meant to equal the English
glossary.md              terminology (APPROVED / PROPOSED), STYLE.md, notes/translator-notes.md
RELEASE_CHECKLIST.md     what a release needs; TESTING.md: playing and scripting the build
ca.mk                    the LANG_CA build, included from the top-level Makefile
translations.csv         every string in English, Spanish and Catalan, for playtesting (generated)
tools/                   extractor, generators, linter, GAP tool, emulator tools
reference/               your private references; gitignored
build/, dist/            generated files and CI outputs; gitignored
```

Upstream files touched: `Makefile` (one `include`), `linker.ld` (a section after `.data`, under
`#ifdef LANG_CA`), `src/new_file_intro.c` (the English pointer tables of the game text),
`src/menus/game_over.c` (the file select's pointer table; the game over prompt, the logo's
sheet and its tilemap),
`src/menus/pause_screen.c` (the pause screen's two sheets and the status tilemap),
`src/menus/title_screen.c` (the title's sprite sheet),
`asm/disasm_0x0809e598.s` (one literal: the file select's sprite sheet, under `.ifdef LANG_CA`),
`src/data/menus/pause_screen_data.c` (the OAM frames of the map's security level legend),
`src/data/hud_data.c` (the HUD sprites),
`src/data/ending_data.c` (the staff credits), `src/data/text_data.c` (the font) and
`src/data/menus/pause_screen_misc_data.c` (the character widths), each under `#ifdef LANG_CA`.

## Building

```sh
python3 tools/extractor.py                   # once, from your base ROM (below)
make -j"$(nproc)"                            # vanilla: still matches mf_us.sha1
make -j"$(nproc)" LANG_CA=1                  # mf_us_ca.gba, Catalan in the English slot
make -j"$(nproc)" LANG_CA=1 CA_SELFTEST=1    # plumbing self-test: the vanilla English, appended
python3 translation/ca/tools/romcheck.py     # the Catalan ROM changed nothing it shouldn't
translation/ca/tools/ci.sh                   # everything CI runs, plus the .bps in dist/
```

Switching between these is safe: objects that depend on the mode are rebuilt automatically.
Tools need python3 with Pillow, and libmgba-dev for the emulator tools.

## Translating text

Each `text/<category>.txt` line is `ID = "text"`. IDs are the table and the index in it
(`MESSAGE_33`, `NAV_042`, `PAUSE_003`, `MONOLOGUE_11`, `FILE_01`), the same in every language; the vanilla
text of each language is in `text/<language>/`. IDs left out show in English, so the game
always builds.

| Category | What | Layout |
|---|---|---|
| `message` | banners: items, security levels, save and recharge prompts | 2 lines, centred with `{GAP(n)}` |
| `location` | location banners | 1 line, centred with `{GAP(n)}` |
| `navigation` | Navigation Room conversations and other typed dialogue | pages (`{NEW_PAGE}`) of 1 or 2 lines |
| `pause` | objectives on the pause screen | 2 lines |
| `monologue` | Samus's monologues, intro and ending narration | pages of up to 9 lines (full screen) or 2 (over a cutscene), each ending `{ARROW}{NEW_PAGE}` |
| `fileselect` | the file select screen: labels, menus, copy and erase prompts, corrupted save messages | the lines of the English entry; narrow boxes (the linter gives each line's limit) |

No line may pass 224 px (less on the file select). `charmap.txt` lists the control codes; `PROGRESS.md` explains them.
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

## Graphics

```sh
python3 translation/ca/tools/gfx_game_over.py            # composes gfx/game_over/text_english.png
python3 translation/ca/tools/gfx_game_over_logo.py       # composes the logo: background.png, text_tilemap.tm
python3 translation/ca/tools/gfx_pause.py                # composes the pause and status screens: bg.png, obj.png, status_screen.tm
python3 translation/ca/tools/gfx_hud.py                  # composes the HUD label: gfx/hud/common.png
python3 translation/ca/tools/gfx_title.py                # composes the title prompt: gfx/menus/title_screen/objects.png
python3 translation/ca/tools/gfx_file_select.py          # composes the file select labels: gfx/menus/file_select/obj.png
python3 translation/ca/tools/gfx.py export game_over/text_english out.png   # a vanilla sheet
python3 translation/ca/tools/gfx.py check                # the PNGs are valid
python3 translation/ca/tools/gfx.py roundtrip            # the codec reproduces the vanilla assets
```

`tools/gfx_assets.json` lists each translated graphic: its vanilla source, the symbol the C
code points at under `LANG_CA`, how many tiles it may hold and which ROM pointers are
repointed. The graphic is compressed and appended after the text; the vanilla one stays where
it is. An uncompressed graphic is marked `"inplace"` instead: it keeps its place and size, and
the source file that holds it includes the edited bytes under `LANG_CA`. A PNG is indexed, 256 px wide (32 tiles per row); its palette is only for viewing.

The composers build each graphic from letters they take out of the vanilla sheets, so a word
is changed by editing the constant at the top of the tool and running it again; each tool
stops with an error if the new word doesn't fit. The words of the pause and status screens
are in `gfx_pause.py`, and `translations.csv` lists them with the English.

## Testing in the emulator

`make ca-emu-tools` builds `build/gbashot` (headless mGBA: scripted input, screenshots, save
states, RAM peeks and pokes) and `build/bpscheck` (checks a patch with mGBA's own loader).

```sh
make -j"$(nproc)" && make -j"$(nproc)" LANG_CA=1 CA_SELFTEST=1
python3 translation/ca/tools/selftest.py     # same input on both ROMs, screenshots must be equal
```

See `TESTING.md` for playing the build in mGBA and for where each kind of text shows.

## Releasing

A release is a `v*` tag (`v1.0.0`) on `main` plus its notes in `.github/release-notes/<tag>.md`,
in Catalan with an English summary. Go through `RELEASE_CHECKLIST.md` first.

1. Tag the release commit and push the tag: `git tag v1.0.0 && git push origin v1.0.0`. The
   Catalan workflow builds it in release mode and names the patch `mf-cat-v1.0.0.bps`.
2. Push the notes file to `main`. `.github/workflows/release.yml` waits for the tag's build,
   then publishes the release "Metroid Fusion en català 1.0.0" with that patch and nothing
   else.

Editing a released notes file and pushing it updates that release's notes. Builds that aren't
on a tag are named after the last tag and the commit (`mf-cat-v1.0.0-3-gabc1234.bps`), or after
the commit alone while there is no tag.

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

### Base ROM in CI

`.github/workflows/catalan.yml` needs the ROM on every run. GitHub secrets are capped at 48 KB,
so the 8 MB ROM can't be a secret itself. Either:

- **A private ROM repository with a read-only deploy key** (what this repository uses): the
  variable `BASEROM_REPO` names the repository, `BASEROM_REPO_PATH` the folder in it that holds
  `mf_us_baserom.gba`, and the secret `BASEROM_REPO_KEY` is the private half of a deploy key
  that the ROM repository accepts read-only. CI checks out only that folder.
- **A private link**: the secret `BASEROM_US_URL`, a direct download link for the `.gba` or a
  `.zip` of it. Anyone with the link can download the ROM, so share it with nobody else.

Either way, the workflow never prints the source, uploads the ROM or caches it. Pull requests
from forks get no secrets, so their runs stop at "Get base ROM".
