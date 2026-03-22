# swizzle magic! (not really)
"""
SWZLv2 Image Format (.swzl2)
============================

file spec:
- there's a magic string at the start of the file that contains the letters "SM" and a bit
that dictates whether the image stores alpha data or not.

- the width of the image is then specified after the magic string as a little endian uint32.

- each pixel is described by its hex color value (and 8-bit alpha value if the image stores alpha data).
rgb mode takes up 3 bytes per pixel, rgba mode takes 4.

- height is row-based, so every {image width} pixels, the decoder assumes the next row of pixels.
"""

import struct
from pathlib import Path
from PIL import Image

# --- Format ---

MAGIC = b"SM"
FLAG_ALPHA = 0b00000001


# --- Encoder ---

def encode(image_path: str, output_path: str, force_alpha: bool = False) -> None:
    img = Image.open(image_path)

    has_alpha = force_alpha or img.mode in ("RGBA", "LA", "PA")

    if has_alpha:
        img = img.convert("RGBA")
        flags = FLAG_ALPHA
    else:
        img = img.convert("RGB")
        flags = 0

    width, height = img.size
    pixels = img.tobytes()

    print(f"[encode_v2] {image_path} -> {output_path}")
    print(f"             Mode: {'RGBA' if has_alpha else 'RGB'} | Size: {width}×{height}")

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("B", flags))
        f.write(struct.pack("<I", width))

        f.write(pixels)

    size_kb = Path(output_path).stat().st_size / 1024
    print(f"             Written: {size_kb:.1f} KB")


# --- Decoder ---

def decode(swzl_path: str, output_path: str) -> None:
    data = Path(swzl_path).read_bytes()

    if data[:2] != MAGIC:
        raise ValueError(f"[!] Invalid magic: {data[:2]!r}")

    flags = data[2]
    has_alpha = bool(flags & FLAG_ALPHA)

    width = struct.unpack("<I", data[3:7])[0]
    pixel_data = data[7:]
    bytes_per_pixel = 4 if has_alpha else 3
    total_pixels = len(pixel_data) // bytes_per_pixel

    if total_pixels % width != 0:
        raise ValueError(
            f"[!] Corrupt file: pixel count {total_pixels} not divisible by width {width}"
        )

    height = total_pixels // width

    mode = "RGBA" if has_alpha else "RGB"

    print(f"[decode_v2] {swzl_path} -> {output_path}")
    print(f"             Mode: {mode} | Size: {width}×{height}")

    img = Image.frombytes(mode, (width, height), pixel_data)
    img.save(output_path)

    print(f"             Saved: {output_path}")


# --- Inspector ---

def inspect(swzl_path: str) -> None:
    data = Path(swzl_path).read_bytes()

    if data[:2] != MAGIC:
        print("[inspect] Not a valid SWZLv2 file")
        return

    flags = data[2]
    has_alpha = bool(flags & FLAG_ALPHA)

    width = struct.unpack("<I", data[3:7])[0]

    pixel_data = data[7:]
    bpp = 4 if has_alpha else 3

    total_pixels = len(pixel_data) // bpp
    height = total_pixels // width if width else "?"

    file_kb = Path(swzl_path).stat().st_size / 1024

    print(f"[inspect] {swzl_path}")
    print(f"  Mode:        {'RGBA' if has_alpha else 'RGB'}")
    print(f"  Width:       {width}")
    print(f"  Height:      {height}")
    print(f"  Pixels:      {total_pixels}")
    print(f"  Filesize:    {file_kb:.1f} KB")
