"""Build the website logo files from the H2O logo animation (GIF) and the still logo (PNG).

The GIF (600 px, 115 frames, 40 ms) fades in from white (frames 0-19), animates (20-48),
holds the full logo (49-100) and fades back to white (101-114), looping forever.
On the website it plays ONCE and stops on the full logo, so only frames 0-49 are kept.
The white square around the round seal is made transparent (anti-aliased circular mask).

Usage:  python -I tools/make_logo.py [GIF] [PNG]
Writes assets/img/h2o-logo.png (still, 600 px), h2o-logo-64.png (favicon),
h2o-logo-intro.webp (600 px, home page) and h2o-logo-intro-sm.webp (168 px, header).
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "img"
SRC = ROOT / "tools" / "logo_source"
GIF = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC / "H2O_Logo_intro_1.gif"
PNG = Path(sys.argv[2]) if len(sys.argv) > 2 else SRC / "H2O_logo_still.png"
LAST = 49          # first frame with the full logo; the animation stops here
FRAME_MS = 40


def circle_box(im):
    """Bounding box of the round seal = the non-white pixels."""
    diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, (255, 255, 255)))
    bbox = diff.convert("L").point(lambda v: 255 if v > 24 else 0).getbbox()
    x0, y0, x1, y1 = bbox
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2
    return cx, cy, r


def circle_mask(size, cx, cy, r, ss=4):
    w, h = size
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).ellipse([(cx - r) * ss, (cy - r) * ss, (cx + r) * ss, (cy + r) * ss], fill=255)
    return m.resize(size, Image.LANCZOS)


def masked(im, box, size):
    """Crop to the seal (square), make the outside transparent, resize."""
    cx, cy, r = box
    r += 1.5  # keep the anti-aliased edge of the dark ring
    crop = (round(cx - r), round(cy - r), round(cx + r), round(cy + r))
    im = im.convert("RGBA").crop(crop)
    mask = circle_mask(im.size, cx - crop[0], cy - crop[1], r - 0.5)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), mask))
    return im.resize((size, size), Image.LANCZOS)


def main():
    gif = Image.open(GIF)
    frames = []
    for i in range(LAST + 1):
        gif.seek(i)
        frames.append(gif.convert("RGB"))
    box = circle_box(frames[LAST])
    print("seal in GIF: centre (%.1f, %.1f), radius %.1f px" % box)

    for name, size in [("h2o-logo-intro.webp", 600), ("h2o-logo-intro-sm.webp", 168)]:
        fr = [masked(f, box, size) for f in frames]
        durations = [FRAME_MS] * len(fr)
        fr[0].save(IMG / name, save_all=True, append_images=fr[1:], duration=durations,
                   loop=1, quality=82, method=6, minimize_size=True)  # loop=1: play once
        print(name, (IMG / name).stat().st_size // 1024, "KB")

    still = Image.open(PNG).convert("RGB")
    sbox = circle_box(still)
    print("seal in PNG: centre (%.1f, %.1f), radius %.1f px" % sbox)
    for name, size in [("h2o-logo.png", 600), ("h2o-logo-64.png", 64)]:
        masked(still, sbox, size).save(IMG / name, optimize=True)
        print(name, (IMG / name).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
