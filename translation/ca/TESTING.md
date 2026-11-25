# Testing the Catalan build in mGBA

Each CI run's artifact (Actions → Catalan → the run → Artifacts → `mf-cat-<commit>`) holds:

- `mf-cat-<version>.bps`: the game, what a release ships. `<version>` is the tag (`v1.0.0`), or
  the last tag plus the commit, or just the commit while there is no tag.
- `mf-cat-ca.po`: every text string for Poedit (see "Reviewing in Poedit" in `README.md`).
- `lint.txt`, `lint.json`: the linter's report.

Locally, `make LANG_CA=1` builds `mf_us_ca.gba` and `translation/ca/tools/ci.sh` builds the
patch into `translation/ca/dist/`.

## Load it in mGBA

1. Copy your US dump (SHA1 `ca33f4348c2c05dd330d37b97e2c5a69531dfe87`) to a folder as
   `fusion.gba`, and the patch next to it as `fusion.bps`. mGBA applies a `.bps` with the same
   name automatically (Flips or Rom Patcher JS work too).
2. Open `fusion.gba`. Default keys: A = X, B = Z, L = A, R = S, Start = Enter, Select =
   Backspace. Save state: Shift+F1…F9; load: F1…F9.
3. Title: press Start, then A on file A, then A on START. The intro narration is the first
   Catalan text; A turns its pages. There is no language selector: Catalan replaces English.
4. After the first briefing answer "Sí". Once Samus can move, save a state (Shift+F1).

What to expect for now: all the text is in Catalan (banners, briefings, objectives,
monologues) and so are the game over screen, the pause screen (map and status), the HUD and
the credit, the title says PREM START, and the file select and the erase-all-data screen
(hold L and R while the game starts) are in Catalan, as is the title of the intro's vaccine
panel. The results screen after the credits is still in English. `PROGRESS.md` has the list.

## Where each kind of text shows

`translations.csv` lists every string with its ID. To find one in game:

| IDs | Where |
|---|---|
| `FILE_00`, `FILE_01` | the file select (Start on the title): its labels; A on a file opens the menu |
| `FILE_24`, `FILE_02` to `04` | the same with a saved file: its menu, and the copy and erase prompts |
| `MONOLOGUE_08` to `18` | the intro, in order |
| `MONOLOGUE_00` | full screen, right after the intro's last picture |
| `NAV_000` | the first briefing, before Samus can move |
| `LOCATION_00`, `LOCATION_12` | walk left from the docking bay: "Coberta principal" in the long corridor, "Sala de navegació" two rooms later |
| `NAV_002` | step on the pad of that first Navigation Room |
| `MESSAGE_45`, `46`, `47` | pause (Start), then L: the Sleep Mode prompt |
| `PAUSE_nnn` | pause (Start): the objective line; it changes after each event |
| `MESSAGE_39`, `40` | pick up an Energy Tank or a Missile Tank |
| `MESSAGE_33`, `34` | a Save Room |
| `MESSAGE_00` to `03` | the Security Rooms |
| `MONOLOGUE_01` to `06` | the elevator rides after the main story events |
| `NAV_100`, `102`, `104` | the Restricted Laboratory briefing and the two that follow |
| `MONOLOGUE_07`, `NAV_112` | the ending |

The docking bay's exit is on the LEFT. The first Navigation Room is past the tall shaft: climb
to its top and take the hatch on the left.

## Scripted checks (no window needed)

`make ca-emu-tools` builds `translation/ca/build/gbashot`, a headless mGBA that plays a script:

```
wait N | hold KEYS N | tap KEYS | shot FILE.ppm | save FILE | load FILE
peek8|peek16|peek32 ADDR | poke8|poke16|poke32 ADDR VALUE      (hex)
```

KEYS are `A B s(elect) S(tart) R L U D r l` (r and l are the shoulder buttons).
`tools/selftest.py` is the example to copy: it plays a new game through the intro, the first
briefing, the walk to the first Navigation Room, its conversation, the pause screen and the
game over screen, on the vanilla and on the self-test ROM, and compares the screenshots.

Useful addresses (US ROM): `gMainGameMode` 0x03000BDE (1 in game, 3 briefing, 7 intro; writing
8 with 0 in `gSubGameMode1`, 0x03000BE0, opens the game over screen), `gCurrentRoom`
0x0300002D, `gSamusData.xPosition` 0x0300125A and `.yPosition` 0x0300125C (writing them moves
Samus), `gEventCounter` 0x03000B87.

To see the whole status screen without playing that far, switch every item on before pausing:
`poke8 300131a ff`, `poke8 300131b ff`, `poke8 300131c ff` (`gEquipment`'s beam, weapon and
suit/misc flags), then `tap S`, `wait 90`, `tap r`. On the map screen the DESTÍ flag is drawn
on alternate frames only, as TARGET is in English: take two screenshots one frame apart
(`shot`, `wait 1`, `shot`) and one of them has it.

With the Catalan ROM the intro and the first briefing have more pages than in English: gameplay
starts after about 190 presses of A instead of 182, so a route written for the English text
needs more presses there.
