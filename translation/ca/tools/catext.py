"""Shared helpers for the Catalan text tools: the vanilla text tables of the US ROM, the
charmap, character widths, the pen model and the translation files.

Metroid Fusion keeps all its text in one binary blob (0x6b2fac-0x72eee0), reached through
per-language pointer tables. Everything here reads the base ROM (mf_us_baserom.gba), never the
build.
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CA = ROOT / "translation" / "ca"
BASEROM = ROOT / "mf_us_baserom.gba"
CHARMAP = CA / "charmap.txt"
WIDTHS_SRC = ROOT / "src" / "data" / "menus" / "pause_screen_misc_data.c"
ROM_BASE = 0x08000000

# gLanguage order (include/constants/game_state.h)
LANGUAGES = ["japanese", "hiragana", "english", "german", "french", "italian", "spanish"]
# The US game always plays in English (SetLanguage, asm/disasm_0x0809e598.s, stores 2 in
# gLanguage), so Catalan takes the English tables.
SLOT = "english"
# The vanilla translation the Catalan is modelled on: the linter compares control codes and
# layout with it.
REFERENCE = "spanish"
# The languages whose layout bounds the Catalan (same script, same font).
WESTERN = ["english", "german", "french", "italian", "spanish"]

TEXT_BLOB = (0x6B2FAC, 0x72EEE0)  # data/Blob_6b2fac_72eee0.bin
FILE_BLOB = (0x73CFAC, 0x7478A0)  # data/Blob_73cfac_7478a0.bin: the file select's data and text

# Pointer tables, as ROM offsets per language.
#   message, location   data/Blob_79c5c0_79cdd8.bin: per language 48 + 26 pointers
#   navigation          data/Blob_79ce10_79e6a0.bin: 225 pointers (222 in hiragana)
#   monologue           sMonologueTextPointers<Language>, src/new_file_intro.c
#   fileselect          data/Blob_79e890_79eca0.bin (src/menus/game_over.c): per language 25
#                       pointers, indexed through the table at 0x79EC68 (hiragana shares the
#                       Japanese block). Their strings are in data/Blob_73cfac_7478a0.bin.
_MSG = [0x79C5C0 + 0x128 * i for i in range(7)]
_LOC = [0x79C680 + 0x128 * i for i in range(7)]
_NAV = [0x79CE10, 0x79D194, 0x79D50C, 0x79D890, 0x79DC14, 0x79DF98, 0x79E31C]
_NAV_COUNT = [225, 222, 225, 225, 225, 225, 225]
_MONO = [0x79E6A0, 0x79E6A0, 0x79E6EC, 0x79E738, 0x79E784, 0x79E7D0, 0x79E81C]
_FILE = [0x79EA08, 0x79EA08, 0x79EA6C, 0x79EAD0, 0x79EB34, 0x79EB98, 0x79EBFC]
NAV_SPLIT = 114  # sPauseScreenTextPointers[lang] == sNavConversationTextPointers[lang] + 114

# name: (file, ID format, table of each language, first index, count of each language)
CATEGORIES = {
    "message": ("message.txt", "MESSAGE_%02d", _MSG, 0, [48] * 7),
    "location": ("location.txt", "LOCATION_%02d", _LOC, 0, [26] * 7),
    "navigation": ("navigation.txt", "NAV_%03d", _NAV, 0, [NAV_SPLIT] * 7),
    "pause": ("pause.txt", "PAUSE_%03d", _NAV, NAV_SPLIT, [n - NAV_SPLIT for n in _NAV_COUNT]),
    "monologue": ("monologue.txt", "MONOLOGUE_%02d", _MONO, 0, [19] * 7),
    "fileselect": ("fileselect.txt", "FILE_%02d", _FILE, 0, [25] * 7),
}
# Table entries that are not strings the game draws. File select entries 11 to 23 have no
# terminator: they are the wording of text that is drawn as graphics (PRESS START, the game
# over prompt, the results screen, the erase-all-data screen), kept in the ROM for reference.
SKIP = {"fileselect": set(range(11, 24))}
HEADERS = {
    "message": "Message banners (item and security-level messages, save and recharge prompts)",
    "location": "Location banners",
    "navigation": "Navigation Room conversations and other typed dialogue",
    "pause": "Pause screen text (objectives, sleep mode, the rest of the navigation table)",
    "monologue": "Samus's monologues and the intro and ending narration",
    "fileselect": "File select screen (labels, the file menus, the copy and erase prompts, corrupted save messages)",
}

LINE_LIMIT = 224  # px: a text line is 28 tiles wide

CHAR_TERMINATOR = 0xFF00
# Codes that take an argument: name -> mask of the argument.
PARAM = {"GAP": 0xFF, "COLOR": 0xFF, "SPEED": 0xFF, "INDENT": 0xFF, "DELAY": 0xFF,
         "SPEAKER": 0xFF, "PLAY": 0xFFF, "STOP": 0xFFF}


# --- ROM -----------------------------------------------------------------------------

_rom = None


def rom():
    global _rom
    if _rom is None:
        if not BASEROM.exists():
            raise SystemExit(f"error: {BASEROM.name} not found (translation/ca/tools/get_baserom.sh)")
        _rom = BASEROM.read_bytes()
    return _rom


def u32(off):
    return struct.unpack_from("<I", rom(), off)[0]


def read_string(off):
    """The u16 codes of the string at ROM offset `off`, without its terminator."""
    data, out = rom(), []
    while True:
        v = struct.unpack_from("<H", data, off)[0]
        off += 2
        if v == CHAR_TERMINATOR:
            return out
        out.append(v)


def lang_index(language):
    return LANGUAGES.index(language)


def entry_ids(category, language=SLOT):
    _, fmt, _, _, counts = CATEGORIES[category]
    return [fmt % i for i in range(counts[lang_index(language)]) if i not in SKIP.get(category, ())]


def pointer_offsets(category, language):
    """ROM offsets of the pointers of a category's table."""
    _, _, tables, first, counts = CATEGORIES[category]
    li = lang_index(language)
    return [tables[li] + 4 * (first + i) for i in range(counts[li]) if i not in SKIP.get(category, ())]


def vanilla_codes(category, language):
    """[(ID, ROM offset of the string, [u16 codes])] of a vanilla table."""
    out = []
    for idx, p in zip(entry_ids(category, language), pointer_offsets(category, language)):
        off = u32(p) - ROM_BASE
        out.append((idx, off, read_string(off)))
    return out


_vanilla = {}


def vanilla_text(category, language):
    """{ID: text} of a vanilla table, decoded."""
    key = (category, language)
    if key not in _vanilla:
        _vanilla[key] = {idx: decode(codes) for idx, _, codes in vanilla_codes(category, language)}
    return _vanilla[key]


# --- charmap -------------------------------------------------------------------------

class CharMap:
    def __init__(self, path=CHARMAP):
        self.chars, self.named = {}, {}
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.split("@")[0].strip()
            if not line:
                continue
            left, right = line.rsplit("=", 1)
            sym, ids = left.strip(), [int(v, 16) for v in right.split()]
            if len(sym) > 1 and sym.startswith("'") and sym.endswith("'"):
                sym = sym[1:-1]
                self.chars["'" if sym == "\\'" else sym] = ids
            else:
                self.named[sym] = ids
        # decoding: longest sequences first; plain characters win over names
        self.rev = {}
        for sym, ids in self.named.items():
            if sym not in PARAM:
                self.rev[tuple(ids)] = "{" + sym + "}"
        for sym, ids in self.chars.items():
            if sym not in ("{", "}", '"', "\\"):
                self.rev[tuple(ids)] = sym
        self.longest = max(len(k) for k in self.rev)
        self.param = sorted(((self.named[n][0], mask, n) for n, mask in PARAM.items()), reverse=True)


_charmap = None


def charmap():
    global _charmap
    if _charmap is None:
        _charmap = CharMap()
    return _charmap


def decode(codes):
    """u16 codes -> text in the `ID = "text"` syntax. encode(decode(x)) == x for any x."""
    cm, out, i = charmap(), [], 0
    while i < len(codes):
        for n in range(min(cm.longest, len(codes) - i), 0, -1):
            sym = cm.rev.get(tuple(codes[i:i + n]))
            if sym is not None:
                out.append(sym)
                i += n
                break
        else:
            v = codes[i]
            for base, mask, name in cm.param:
                if v & ~mask == base:
                    out.append(f"{{{name}({v & mask})}}")
                    break
            else:
                out.append(f"{{x{v:04X}}}")
            i += 1
    return "".join(out)


CODE_RE = re.compile(r"\{(\w+)(?:\((\d+)\))?\}")
RAW_RE = re.compile(r"x[0-9A-F]{4}")


def tokens(text):
    """[(kind, value, raw)]. kind: char, nl, code (a control code without argument, or a raw
    {xHHHH} of 0x8000 and over), or the lower-case name of a code with an argument (gap,
    color, speed, indent, play, stop, delay, speaker)."""
    cm = charmap()
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == "{":
            j = text.find("}", i)
            raw = text[i:j + 1] if j >= 0 else text[i:]
            m = CODE_RE.fullmatch(raw)
            if not m:
                raise KeyError(f"bad code {raw!r}")
            name, arg = m.group(1), m.group(2)
            if arg is not None:
                if name not in PARAM:
                    raise KeyError(f"{raw!r} takes no argument")
                if int(arg) > PARAM[name]:
                    raise KeyError(f"{raw!r}: the argument is over {PARAM[name]}")
                out.append((name.lower(), cm.named[name][0] + int(arg), raw))
            elif RAW_RE.fullmatch(name):
                v = int(name[1:], 16)
                if v == CHAR_TERMINATOR:
                    raise KeyError("the terminator is added by the tools: remove {xFF00}")
                out.append(("code" if v >= 0x8000 else "char", v, raw))
            else:
                vals = cm.named.get(name)
                if vals is None or name in PARAM:
                    raise KeyError(f"unknown code {raw!r}")
                if len(vals) == 1 and vals[0] >= 0x8000:
                    out.append(("code", vals[0], raw))
                else:
                    for v in vals:
                        out.append(("char", v, raw))
            i = j + 1
        elif c == "\\":
            raw = text[i:i + 2]
            vals = cm.chars.get(raw)
            if vals is None:
                raise KeyError(f"unknown escape {raw!r}")
            out.append(("nl", vals[0], raw) if raw == "\\n" else ("char", vals[0], raw))
            i += 2
        else:
            vals = cm.chars.get(c)
            if vals is None or c in '{}"':
                raise KeyError(f"character not in charmap.txt: {c!r} (U+{ord(c):04X})")
            for v in vals:
                out.append(("char", v, c))
            i += 1
    return out


def encode(text):
    """Text -> u16 codes, without the terminator."""
    return [v for _, v, _ in tokens(text)]


def to_bytes(codes, terminator=True):
    vals = list(codes) + ([CHAR_TERMINATOR] if terminator else [])
    return struct.pack(f"<{len(vals)}H", *vals)


# --- widths --------------------------------------------------------------------------

_widths = None


def vanilla_widths():
    """sCharacterWidths as upstream has it (the vanilla branch of the LANG_CA block)."""
    global _widths
    if _widths is None:
        src = WIDTHS_SRC.read_text(encoding="utf-8")
        i = src.index("const u8 sCharacterWidths[1184]")
        body = src[src.index("{", i) + 1:src.index("};", i)]
        if "#ifdef LANG_CA" in body:
            body = body.split("#else // !LANG_CA", 1)[1].split("#endif // LANG_CA", 1)[0]
        body = re.sub(r"//.*|/\*.*?\*/", "", body, flags=re.S)
        _widths = [int(x, 0) for x in re.findall(r"\b(?:0x[0-9A-Fa-f]+|\d+)\b", body)]
        if len(_widths) != 1184:
            raise ValueError(f"expected 1184 character widths, found {len(_widths)}")
    return list(_widths)


def width_overrides(path=CA / "font" / "widths.txt"):
    """{char id: width} from font/widths.txt lines like `0357 2  # middle dot`."""
    over = {}
    if path.exists():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            m = re.fullmatch(r"([0-9A-Fa-f]{3,4})\s+(\d+)", line)
            if not m:
                raise ValueError(f"{path}:{n}: expected `HEXID WIDTH`")
            over[int(m.group(1), 16)] = int(m.group(2))
    return over


def widths(catalan=True):
    w = vanilla_widths()
    if catalan:
        for cid, v in width_overrides().items():
            w[cid] = v
    return w


# --- layout --------------------------------------------------------------------------

def split_lines(text):
    """Split on \\n, {NEW_PAGE} and {ARROW}; returns the raw text of each line."""
    return re.split(r"\\n|\{NEW_PAGE\}|\{ARROW\}", text)


def split_pages(text):
    """[[line, ...], ...]: pages (split on {NEW_PAGE}) of lines (split on \\n)."""
    return [page.split("\\n") for page in text.split("{NEW_PAGE}")]


def line_layout(line_text, w):
    """Pen model of one line. Returns dict: lead_gap (int or None), glyph_width (sum of the
    glyph widths), pen_end (final pen, with GAP and INDENT), overflow (a glyph or GAP would
    cross 224 px)."""
    toks = tokens(line_text)
    first = next((t for t in toks if t[0] not in ("color", "speed", "speaker", "code")), None)
    lead = first[1] & 0xFF if first and first[0] == "gap" else None
    pen = glyphs = 0
    overflow = False
    for kind, v, _ in toks:
        if kind == "gap":
            step = v & 0xFF
        elif kind == "char":
            step = w[v] if v < len(w) else 10  # TextGetCharacterWidth
            glyphs += step
        elif kind == "indent":
            pen = v & 0xFF
            continue
        else:
            continue
        if pen + step > LINE_LIMIT:
            overflow = True
        pen += step
    return {"lead_gap": lead, "glyph_width": glyphs, "pen_end": pen, "overflow": overflow}


# --- translation files ---------------------------------------------------------------

ENTRY_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s*=\s*"(.*)"\s*$')


def read_entries(path):
    """{ID: (text, line number)} of a text file. Lines: `ID = "text"`; `#` comments."""
    entries = {}
    path = Path(path)
    if not path.exists():
        return entries
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = ENTRY_RE.match(s)
        if not m:
            raise ValueError(f"{path}:{n}: expected ID = \"text\"")
        if m.group(1) in entries:
            raise ValueError(f"{path}:{n}: {m.group(1)} is defined twice")
        if '"' in m.group(2):
            raise ValueError(f"{path}:{n}: use ” (charmap 0x42) for quotes, not \"")
        entries[m.group(1)] = (m.group(2), n)
    return entries


def read_translation(category, base=CA / "text"):
    """({ID: (text, line number)}, path) of the Catalan text of a category."""
    path = Path(base) / CATEGORIES[category][0]
    return read_entries(path), path


def dump_path(category, language, base=CA / "text"):
    return Path(base) / language / CATEGORIES[category][0]


def identical_ids(path=CA / "identical.txt"):
    """IDs whose Catalan text is meant to equal the English (counted as translated)."""
    if not path.exists():
        return set()
    return {l.split("#", 1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines()} - {""}
