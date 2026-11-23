#!/usr/bin/env bash
# The Catalan build checks, run by CI (.github/workflows/catalan.yml) and the same way locally.
#
#   translation/ca/tools/ci.sh            usual checks; fails on lint errors
#   RELEASE=1 translation/ca/tools/ci.sh  also fails on lint warnings and untranslated text
#                                         (CI sets it on v* tags, which are releases)
#
# Needs the base ROM (see translation/ca/README.md), agbcc (on PATH or in tools/agbcc) and
# arm-none-eabi binutils, python3 with Pillow, and libmgba-dev for the emulator checks.
# Outputs in translation/ca/dist/: mf-cat-<version>.bps, lint.txt, lint.json, mf-cat-ca.po (for
# Poedit). No ROM is ever copied there.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$ROOT"
CA=translation/ca
JOBS=$(nproc)
DIST=$CA/dist
mkdir -p "$DIST"

step() { echo "::group::$*" 2>/dev/null || true; echo "== $*"; }
endstep() { echo "::endgroup::" 2>/dev/null || true; }
have_mgba() { pkg-config --exists libmgba 2>/dev/null || [ -f /usr/include/mgba/core/core.h ]; }

step "Base ROM"
"$CA/tools/get_baserom.sh" us
[ -d data ] || python3 tools/extractor.py > /dev/null
endstep

step "Tool tests"
python3 -m unittest "$CA/tools/test_extract.py" "$CA/tools/test_lint.py" "$CA/tools/test_po.py"
python3 "$CA/tools/extract.py" --check
python3 "$CA/tools/gap.py" vanilla | tail -5
python3 "$CA/tools/gfx.py" roundtrip
python3 "$CA/tools/gfx.py" check
python3 "$CA/tools/font.py" check
endstep

step "Vanilla US"
make -j"$JOBS" > /dev/null
sha1sum -c mf_us.sha1
VANILLA=$(cut -d' ' -f1 mf_us.sha1 | tr '[:upper:]' '[:lower:]')
endstep

step "LANG_CA self-test (vanilla text and graphics through the Catalan plumbing)"
make LANG_CA=1 CA_SELFTEST=1 -j"$JOBS" > /dev/null
python3 "$CA/tools/romcheck.py" --selftest
if have_mgba; then
    make ca-emu-tools > /dev/null
    python3 "$CA/tools/selftest.py"
else
    echo "warning: libmgba not installed, the self-test ROM was not compared in the emulator"
fi
endstep

step "Lint"
LINT_FLAGS=()
[ "${RELEASE:-0}" = 1 ] && LINT_FLAGS+=(--release)
set +e
python3 "$CA/tools/lint.py" --json "$DIST/lint.json" "${LINT_FLAGS[@]}" | tee "$DIST/lint.txt"
LINT=${PIPESTATUS[0]}
set -e
[ "$LINT" = 0 ] || { echo "error: lint failed" >&2; exit 1; }
python3 "$CA/tools/gap.py" check
python3 "$CA/tools/review.py" --check
python3 "$CA/tools/po.py" export "$DIST/mf-cat-ca.po"
endstep

step "Catalan US"
make LANG_CA=1 -j"$JOBS" > /dev/null
python3 "$CA/tools/romcheck.py"
sha1sum mf_us_ca.gba
endstep

step "Patch"
# The tag on a release commit (v1.0.0), else the last tag plus the commit (v1.0.0-3-gabc1234).
VERSION=$(git describe --tags --match 'v*' --always --dirty 2>/dev/null || echo dev)
rm -f "$DIST"/*.bps
PATCH="$DIST/mf-cat-$VERSION.bps"
python3 "$CA/tools/bps.py" create mf_us_baserom.gba mf_us_ca.gba "$PATCH" \
    --metadata "Metroid Fusion en catala $VERSION. Base: US ROM, SHA1 $VANILLA."
python3 "$CA/tools/bps.py" apply mf_us_baserom.gba "$PATCH" "$DIST/.check.gba"
cmp "$DIST/.check.gba" mf_us_ca.gba && rm -f "$DIST/.check.gba"
if have_mgba; then
    "$CA/build/bpscheck" mf_us_baserom.gba "$PATCH" mf_us_ca.gba
else
    echo "warning: libmgba not installed, patch not checked with mGBA's loader"
fi
ls -l "$DIST"
endstep
