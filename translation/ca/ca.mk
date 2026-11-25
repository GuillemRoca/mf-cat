# Catalan translation build hooks, included from the top-level Makefile.
#
#   make LANG_CA=1                 mf_us_ca.gba: Catalan in the English slot
#   make LANG_CA=1 CA_SELFTEST=1   the same plumbing with the vanilla English text: the game must
#                                  look and play exactly as vanilla (translation/ca/TESTING.md)
#   make                           vanilla mf_us.gba, which still matches mf_us.sha1
#
# The decomp is not shiftable, so LANG_CA never moves or resizes anything that exists. New data
# goes in objects that linker.ld places after everything else in the ROM, and only pointers
# (in tables that keep their place and size) change:
#   $(CA_BUILD)/ca_text.o          the text of the English slot (gentext.py asm)
#   $(CA_INC)/ca/text_tables.h     the pointer tables of src/new_file_intro.c (gentext.py tables)
#   $(CA_BUILD)/ca_gfx.o           the edited graphics of gfx/ (gfx.py asm), which the C code
#                                  points at by symbol (tools/gfx_assets.json)
# The font is the one exception: it is edited in place (font.py), which keeps its size:
#   $(CA_INC)/ca/font.inc          sCharactersGfx with font/glyphs/*.png drawn over it
#   $(CA_INC)/ca/char_widths.inc   sCharacterWidths with font/widths.txt applied
# and so are the staff credits (gencredits.py), with the same number of entries and rows:
#   $(CA_INC)/ca/credits.inc       sCredits with the translators of credits.txt
# and the OAM frames of the map's security level legend (gfx_pause.py --oam), same size:
#   $(CA_INC)/ca/pause_legend_oam.inc   a wider label sprite, the legend 8 px further left
# and the uncompressed graphics marked "inplace" in gfx_assets.json (gfx.py inc):
#   $(CA_INC)/ca/hud_common.inc    the HUD sprites with gfx/hud/common.png's label
# Objects are built in-tree for both modes, so every object that depends on the mode also
# depends on $(CA_STAMP), which changes whenever the mode does.

# This file is included before the Makefile's `all` rule; keep `all` the default goal.
.DEFAULT_GOAL := all

CA_DIR := translation/ca
CA_TOOLS := $(CA_DIR)/tools
CA_BUILD := $(CA_DIR)/build
CA_INC := $(CA_BUILD)/include
CA_STAMP := $(CA_BUILD)/mode.stamp
CA_BASEROM := mf_us_baserom.gba

LANG_CA ?= 0
CA_SELFTEST ?= 0

CA_TEXT_ASM := $(CA_BUILD)/ca_text.s
CA_TEXT_OBJ := $(CA_BUILD)/ca_text.o
CA_GFX_ASM := $(CA_BUILD)/ca_gfx.s
CA_GFX_OBJ := $(CA_BUILD)/ca_gfx.o
CA_TABLES_H := $(CA_INC)/ca/text_tables.h
CA_FONT_INC := $(CA_INC)/ca/font.inc
CA_WIDTHS_INC := $(CA_INC)/ca/char_widths.inc
CA_CREDITS_INC := $(CA_INC)/ca/credits.inc
CA_LEGEND_INC := $(CA_INC)/ca/pause_legend_oam.inc
CA_HUD_INC := $(CA_INC)/ca/hud_common.inc

ifeq ($(CA_SELFTEST),1)
  CA_GENTEXT_FLAGS := --selftest
  CA_FONT_FLAGS := --vanilla
else
  CA_GENTEXT_FLAGS :=
  CA_FONT_FLAGS :=
endif

# Rewrite the stamp only when the mode changes, so its timestamp marks the last switch.
CA_MODE := LANG_CA=$(LANG_CA) CA_SELFTEST=$(CA_SELFTEST)
$(shell mkdir -p $(CA_BUILD) && (echo '$(CA_MODE)' | cmp -s - $(CA_STAMP) || echo '$(CA_MODE)' > $(CA_STAMP)))

# Objects whose output depends on the mode: the sources that mention LANG_CA, and the linker
# script.
CA_AFFECTED := $(shell grep -rlF --include='*.c' -e LANG_CA src)
$(CA_AFFECTED:.c=.s) linker.ld.pp: $(CA_STAMP)

ifeq ($(LANG_CA),1)
  ifneq ($(REGION),us)
    $(error LANG_CA=1 needs REGION=us)
  endif
  CPPFLAGS += -DLANG_CA -I$(CA_INC)
  TARGET := $(TARGET:.gba=_ca.gba)

  src/new_file_intro.s: $(CA_TABLES_H)
  src/data/text_data.s: $(CA_FONT_INC)
  src/data/menus/pause_screen_misc_data.s: $(CA_WIDTHS_INC)
  src/data/ending_data.s: $(CA_CREDITS_INC)
  src/data/menus/pause_screen_data.s: $(CA_LEGEND_INC)
  src/data/hud_data.s: $(CA_HUD_INC)
  $(TARGET:.gba=.elf): $(CA_TEXT_OBJ) $(CA_GFX_OBJ)
else ifeq ($(CA_SELFTEST),1)
  $(error CA_SELFTEST=1 needs LANG_CA=1)
endif

CA_FONT_DEPS := $(wildcard $(CA_DIR)/font/glyphs/*.png) $(wildcard $(CA_DIR)/font/widths.txt) \
                $(CA_TOOLS)/font.py $(CA_TOOLS)/catext.py $(CA_STAMP)

$(CA_FONT_INC): data/text_characters.gfx $(CA_FONT_DEPS)
	$(MSG) FONT $@
	$Q$(PYTHON) $(CA_TOOLS)/font.py build $@ $(CA_FONT_FLAGS)

$(CA_WIDTHS_INC): src/data/menus/pause_screen_misc_data.c $(CA_FONT_DEPS)
	$(MSG) WIDTHS $@
	$Q$(PYTHON) $(CA_TOOLS)/font.py widths $@ $(CA_FONT_FLAGS)

$(CA_CREDITS_INC): $(CA_DIR)/credits.txt src/data/ending_data.c $(CA_TOOLS)/gencredits.py $(CA_STAMP)
	$(MSG) CREDITS $@
	$Q$(PYTHON) $(CA_TOOLS)/gencredits.py $@ $(CA_FONT_FLAGS)

$(CA_LEGEND_INC): $(CA_TOOLS)/gfx_pause.py $(CA_BASEROM) $(CA_STAMP)
	$(MSG) LEGEND $@
	$Q$(PYTHON) $(CA_TOOLS)/gfx_pause.py --oam $@ $(CA_FONT_FLAGS)

$(CA_HUD_INC): $(wildcard $(CA_DIR)/gfx/hud/common.png) $(CA_TOOLS)/gfx.py $(CA_TOOLS)/gfx_assets.json \
               $(CA_BASEROM) $(CA_STAMP)
	$(MSG) GFX $@
	$Q$(PYTHON) $(CA_TOOLS)/gfx.py inc hud/common $@ $(CA_GENTEXT_FLAGS)

CA_TEXT_DEPS := $(wildcard $(CA_DIR)/text/*.txt) $(CA_DIR)/charmap.txt $(CA_BASEROM) \
                $(CA_TOOLS)/gentext.py $(CA_TOOLS)/catext.py $(CA_STAMP)

$(CA_TEXT_ASM): $(CA_TEXT_DEPS) $(wildcard $(CA_DIR)/font/widths.txt)
	$(MSG) GENTEXT $@
	$Q$(PYTHON) $(CA_TOOLS)/gentext.py asm $@ $(CA_GENTEXT_FLAGS)

$(CA_TABLES_H): $(CA_BASEROM) $(CA_TOOLS)/gentext.py $(CA_TOOLS)/catext.py $(CA_STAMP)
	$(MSG) GENTEXT $@
	$Q$(PYTHON) $(CA_TOOLS)/gentext.py tables $@

$(CA_GFX_ASM): $(shell find $(CA_DIR)/gfx -name '*.png' -o -name '*.tm' 2>/dev/null) $(CA_TOOLS)/gfx.py $(CA_TOOLS)/gfx_assets.json \
               $(CA_TOOLS)/lz77.py $(CA_BASEROM) $(CA_STAMP)
	$(MSG) GFX $@
	$Q$(PYTHON) $(CA_TOOLS)/gfx.py asm $@ $(CA_GENTEXT_FLAGS)

# Headless mGBA tools (need libmgba-dev): scripted screenshots, and patch checks with mGBA's
# own BPS loader.
$(CA_BUILD)/gbashot $(CA_BUILD)/bpscheck: $(CA_BUILD)/%: $(CA_TOOLS)/gbashot/%.c
	$(MSG) CC $@
	$Q$(HOSTCC) -O2 -Wall $< -o $@ -lmgba

.PHONY: ca-emu-tools ca-clean
ca-emu-tools: $(CA_BUILD)/gbashot $(CA_BUILD)/bpscheck
ca-clean:
	$(RM) -r $(CA_BUILD)
