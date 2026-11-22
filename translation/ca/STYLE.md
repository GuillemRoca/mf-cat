# Style

- Standard Catalan following IEC norms. Terse, clear and atmospheric, matching Metroid's tone;
  no jokes needed.
- English is the source. The Spanish text of the US ROM is a reference for meaning and length
  only; don't copy its terms when the glossary differs. Other translations are references for
  meaning, never copied verbatim.
- Sentence case for item, room and UI names ("Raig de càrrega", "Sala de navegació"). Proper
  names and the Galactic Federation keep their capitals.
- Menu commands and options use the imperative (Softcatalà style): "Continua", "Surt".
- "la Samus" and "l'Adam" in prose, with the personal article; no article when someone is
  addressed ("Samus, ves a la sala de dades").
- Two voices, kept apart:
  - The computer (Adam's briefings, objectives, messages) is formal and military: short
    sentences, orders in the imperative, "tu" for Samus, no colloquialisms, no exclamations
    unless the English has one. It reports facts first and gives the order last.
  - Samus (monologues, intro and ending narration) is reflective and literary: first person,
    full sentences, narrated in the past with the periphrastic past ("vaig descobrir"), and a
    slightly elevated vocabulary.
- Keep untranslated: Samus Aran, Adam Malkovich, SA-X, SR388, B.S.L, Biologic, Serris, B.O.X.
  and the sector codes (SRX, TRO, PYR, AQA, ARC, NOC).
- Punctuation: only closing ? and ! (never ¿ ¡). The question mark is the wide one the English
  text uses (？); ! is the plain one. Quotations go in « ». An ellipsis is three full stops.
- Write real l·l (the font gets a fixed middle dot).
- When a line overflows, reword instead of abbreviating. A line is at most 224 px; break lines
  by hand at a natural pause, never in the middle of a name or a coloured term if it can be
  avoided.
- Keep the game's codes. {SPEAKER(n)}, {PLAY(n)}, {STOP(n)}, {DELAY(n)} and the raw {xHHHH}
  codes stay at the same point of the sentence as in the original (a sound plays when the text
  reaches them). {COLOR(n)} wraps the same term the English highlights and is closed with
  {COLOR(0)} before the line or page ends. Banner GAPs are recomputed by `tools/gap.py fix`.
- Use only characters in charmap.txt.
