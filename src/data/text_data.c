#include "macros.h"

#ifdef LANG_CA
const u8 sCharactersGfx[192 * 1024] =
#include "ca/font.inc" // generated: translation/ca/tools/font.py
;
#else // !LANG_CA
const u8 sCharactersGfx[192 * 1024] = INCBIN_U8("data/text_characters.gfx");
#endif // LANG_CA

static const u8 sBlob_6b2fac_72eee0[] = INCBIN_U8("data/Blob_6b2fac_72eee0.bin");

