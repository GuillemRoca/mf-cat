"""GBA BIOS LZ77 (type 0x10), as LZ77UncompVram and LZ77UncompWram read it.

  decompress(data, offset=0) -> (bytes, compressed size)
  compress(data) -> bytes        VRAM-safe (no match at distance 1), padded to 4 bytes
"""


def decompress(data, offset=0):
    if data[offset] != 0x10:
        raise ValueError(f"not LZ77 data at 0x{offset:x} (first byte 0x{data[offset]:02x})")
    size = data[offset + 1] | (data[offset + 2] << 8) | (data[offset + 3] << 16)
    out = bytearray()
    pos = offset + 4
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = data[pos], data[pos + 1]
                pos += 2
                length = (b1 >> 4) + 3
                dist = (((b1 & 0xF) << 8) | b2) + 1
                for _ in range(length):
                    out.append(out[-dist])
            else:
                out.append(data[pos])
                pos += 1
    return bytes(out[:size]), ((pos - offset) + 3) & ~3


def compress(data):
    data = bytes(data)
    n = len(data)
    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    # hash chains over 3-byte prefixes
    head, prev = {}, [0] * n
    pos = 0

    def insert(i):
        if i + 2 < n:
            key = data[i:i + 3]
            prev[i] = head.get(key, -1)
            head[key] = i

    while pos < n:
        flag_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            best_len, best_dist = 0, 0
            if pos + 2 < n:
                cand = head.get(data[pos:pos + 3], -1)
                tries = 0
                limit = min(18, n - pos)
                while cand >= 0 and pos - cand <= 0x1000 and tries < 256:
                    if pos - cand >= 2:  # VRAM-safe
                        length = 3
                        while length < limit and data[cand + length] == data[pos + length]:
                            length += 1
                        if length > best_len:
                            best_len, best_dist = length, pos - cand
                            if length == limit:
                                break
                    cand = prev[cand]
                    tries += 1
            if best_len >= 3:
                flags |= 0x80 >> bit
                out.append(((best_len - 3) << 4) | ((best_dist - 1) >> 8))
                out.append((best_dist - 1) & 0xFF)
                for i in range(pos, pos + best_len):
                    insert(i)
                pos += best_len
            else:
                out.append(data[pos])
                insert(pos)
                pos += 1
        out[flag_at] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)
