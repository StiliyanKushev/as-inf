#!/usr/bin/env python3
"""Create the neutral image used when reference mode is disabled."""

from __future__ import annotations

import binascii
import struct
import sys
import zlib
from pathlib import Path


def chunk(kind: bytes, data: bytes) -> bytes:
    payload = kind + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", binascii.crc32(payload) & 0xFFFFFFFF)


target = Path(sys.argv[1] if len(sys.argv) > 1 else "__NO_REFERENCE__.png")
target.parent.mkdir(parents=True, exist_ok=True)

width = height = 64
pixel = bytes((96, 96, 96))
rows = b"".join(b"\x00" + pixel * width for _ in range(height))
png = (
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(rows, 9))
    + chunk(b"IEND", b"")
)
target.write_bytes(png)
print(target)
