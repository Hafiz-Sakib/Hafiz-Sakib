"""
prep_photo.py — one-time photo prep for the ASCII portrait pipeline.

Run once per photo:
    python scripts/prep_photo.py source-photo.jpg

Steps:
  1. Remove background (rembg) so only the subject remains.
  2. Boost local contrast with CLAHE so flat lighting gets real
     highlights/shadows (otherwise the ASCII output is a dark blob).
  3. Composite onto pure white so background maps to the blank end
     of the ASCII density ramp (white -> space character).

Output: source-prepped.png (grayscale, ready for make_ascii_svg.py)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(input_path: str, output_path: str = "source-prepped.png") -> None:
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"No such file: {input_path}")

    # 1. Remove background -> RGBA with transparent bg
    raw = Image.open(src).convert("RGBA")
    cutout = remove(raw)

    # 2. Composite onto pure white (so bg -> white -> space glyph)
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("L")

    # 3. CLAHE contrast boost (contrast-limited adaptive histogram eq)
    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output_path)
    print(f"wrote {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
