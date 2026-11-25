# Release checklist

Copy this list into the release issue and tick every item. A release is a `.bps` against the
vanilla US ROM (SHA1 `ca33f4348c2c05dd330d37b97e2c5a69531dfe87`); never distribute a ROM.

`PROGRESS.md` says which of these are already known to hold and which work is still open. As
of this writing the graphics (other than the game over prompt) and the credits are not done:
do not release before they are.

## Build and CI

- [ ] CI green on the release commit, run with **release mode** (Actions → Catalan → Run
      workflow → release): lint has 0 errors, 0 warnings, 0 TODOs and 318/318 translated.
- [ ] Vanilla US still matches `mf_us.sha1` (CI).
- [ ] The LANG_CA self-test passes (CI): `romcheck.py --selftest` finds only repointed pointers
      and appended data, and `selftest.py` gets identical screenshots from both ROMs.
- [ ] `romcheck.py` on the Catalan ROM: no byte changed outside the pointers, the appended data
      and the redrawn glyphs (CI).
- [ ] Release commit on `main` tagged `v1.0.0` and the tag pushed; its build (release mode) is
      green and its patch is `mf-cat-v1.0.0.bps` (see README, "Releasing").
- [ ] `gap.py check` clean; `gfx.py roundtrip` and `gfx.py check` pass; `extract.py --check`
      passes; `translations.csv` current and every row "translated" or "same as English".
- [ ] No PROPOSED term left in `glossary.md` (or each one listed as an open choice in
      `notes/translator-notes.md`).

## Graphics

- [ ] Game over: the logo "FI DE LA / PARTIDA"; the prompt "TORNAR-HO A PROVAR ?", "SÍ (
      CONTINUA )", "NO ( SURT )"; the helmet cursor lines up with both options.
- [ ] Ending results screen: clear time, item rate, the last line.
- [ ] Pause screen: SLEEP / STATUS tabs, OBJECTIVE, TARGET, the area names, the LOCK labels.
- [ ] Status screen: headings and every item name, each inside its box.
- [ ] Title screen (PRESS START and its menu) and file select (SAMUS DATA, ENERGY, TIME,
      SOUND, EXIT, START / COPY DATA / ERASE DATA, the erase and copy prompts).
- [ ] HUD: ENERGY.
- [ ] Intro: the vaccine panel.
- [ ] Anything left in English on purpose is listed in `PROGRESS.md` with the reason.

## Playthrough coverage (real hardware or mGBA)

- [ ] Title → file select: new file, copy, erase, sound setting.
- [ ] Intro: every narration page changes picture where the English does; the ship computer's
      box; the first full-screen monologue.
- [ ] First briefing: coloured terms, the map target, "Has entès l'objectiu？ Sí / No", both
      answers.
- [ ] Every Navigation Room briefing, read to the end, and the short reminder each room gives
      afterwards.
- [ ] Every location banner (decks, six sectors, special rooms).
- [ ] Every message banner: four security levels, each data download, each recovered ability,
      stabilizers (5), water level, cooling unit, gate, auxiliary power, lab detachment, orbit
      change, tanks (energy, missile, power bomb).
- [ ] Save Room (prompt, Yes/No, complete), Recharge Room (three messages), "Connectar amb
      l'Adam？" at a Navigation Room.
- [ ] Pause screen: the objective line after each event; Sleep Mode prompt and wake-up.
- [ ] The elevator monologues (MONOLOGUE_01 to 06) and the ending (MONOLOGUE_07, NAV_112).
- [ ] The Federation conversations (NAV_050, 100, 102, 104): the right speaker's box for
      every line.
- [ ] A word with l·l on screen (e.g. "cèl·lula" in the intro, "Col·lisió imminent.").
- [ ] Game over prompt (both options).
- [ ] Ending: results, credits.

## Credits

- [ ] "CATALAN / Guillem Roca Castany" shows as a group of its own before EXECUTIVE PRODUCER
      (`credits.txt`), and the credits still end in time with the music.

## Patch

- [ ] Publish only `mf-cat-<version>.bps`, never a ROM.
- [ ] Patch applied with Flips and with Rom Patcher JS to a **clean US dump** (SHA1 above): the
      result boots and matches the CI build's SHA1.
- [ ] Vanilla US saves load and play correctly with the patched ROM.
- [ ] Release notes in `.github/release-notes/v1.0.0.md`, in Catalan with an English summary:
      base ROM name and SHA1, version, how to apply, credits, licence. Pushing them to `main`
      publishes the release.
