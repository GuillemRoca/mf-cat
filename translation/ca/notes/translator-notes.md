# Translator notes

Decisions taken while translating, for the reviewer. `glossary.md` has the terms; this file has
the reasons that don't fit a table, and the list of PROPOSED terms in use.

## Voices

The game has two narrators and the Catalan keeps them apart (see `STYLE.md`):

- **The computer** (Adam): briefings in the Navigation Rooms, objectives on the pause screen,
  message banners. Formal and military. It speaks to Samus as "tu" and gives orders in the
  imperative ("Ves a la sala de dades."). The Spanish does the same.
- **Samus**: the intro and ending narration and the elevator monologues. First person,
  reflective, in the past.

Two more voices appear briefly in the navigation text: a Federation officer (`{SPEAKER(2)}`,
NAV_050 and the hidden NAV_094/095) and Samus answering the computer (`{SPEAKER(1)}`, NAV_100,
102, 104). Samus is curt and angry there; the officer is smug.

## Text the game never shows

Some entries are placeholders or debug strings ("Empty", "Demo use", "Not used", "None",
"Line 1 / Line 2", "Not displayed", the "Enemy location abnormal" message). They are translated
anyway, plainly, so that nothing in the Catalan ROM is left in English; none needs review.

## PROPOSED terms in use

All 73 PROPOSED rows of `glossary.md` are in use except Command Room's alternatives; the text
follows option 1 of each. The ones that appear most, and where: Lady → "senyoreta"
(MONOLOGUE_01, 02; NAV_104, 105, 112); target and objective → "objectiu" (every "Objectiu
eliminat." and "Ves a l'objectiu.", MESSAGE_43, 44); download → "baixar" (banners 04 to 07, the
objectives, most briefings); HQ → "quarter general"; CO → "comandant"; Quarantine Bay → "sala
de quarantena"; bio-signs → "senyals de vida"; Nightmare → "Malson"; Etecoons and Dachoras →
"etecoons i dachores"; Jumpball → "morfosalt"; Shinespark → "salt llampec" (NAV_094 only).
Changing one means searching `text/*.txt` for it and re-running `lint.py`: a longer word can
push a line over 224 px.
