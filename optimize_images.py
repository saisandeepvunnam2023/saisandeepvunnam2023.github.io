#!/usr/bin/env python3
"""
Image pipeline.

Reads content/media.json, and for every source photograph emits a responsive
ladder of AVIF + WebP + JPEG derivatives into static/media/.

The originals are 8000px-wide camera files (15-35 MB each). Nothing that large
should ever reach a browser, so this is the only place they are touched: run it
once when photographs change, commit the derivatives, and the site itself never
depends on Pillow again.

    python3 optimize_images.py            # only encode what is missing
    python3 optimize_images.py --force    # re-encode everything

Requires: pip3 install pillow
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).parent
OUT = ROOT / "static" / "media"
ROOT_FILES = ROOT / "static" / "root"   # copied to the site root by build.py

# Quality is tuned per format: AVIF carries the load, WebP is the mid-tier
# fallback, JPEG exists only for browsers that support neither.
QUALITY = {"avif": 52, "webp": 74, "jpeg": 80}

# JPEG exists only for browsers that support neither AVIF nor WebP. Every such
# browser predates 2020, and none of them are driving a 2560px viewport, so the
# top of the ladder is encoded as AVIF and WebP only. This is roughly a third of
# the repository's image weight.
JPEG_MAX_WIDTH = 1440

# Width ladders, keyed by the role an image plays in the layout.
LADDERS = {
    "hero": [960, 1440, 1920, 2560],
    "gallery": [640, 960, 1440, 1920],
    "cover": [480, 720, 1080],
    "portrait": [320, 480, 640],
}


def load(src: Path, max_width: int) -> Image.Image:
    """Open a source file, using JPEG draft mode to avoid decoding 45 megapixels."""
    im = Image.open(src)
    im.draft("RGB", (max_width * 2, max_width * 2))
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


def encode(im: Image.Image, stem: str, width: int, force: bool) -> None:
    ratio = width / im.width
    size = (width, max(1, round(im.height * ratio)))
    resized = im.resize(size, Image.LANCZOS) if size != im.size else im

    for fmt, ext in (("avif", "avif"), ("webp", "webp"), ("jpeg", "jpg")):
        if fmt == "jpeg" and width > JPEG_MAX_WIDTH:
            continue
        target = OUT / f"{stem}-{width}.{ext}"
        if target.exists() and not force:
            continue
        opts = {"quality": QUALITY[fmt]}
        if fmt == "jpeg":
            opts.update(progressive=True, optimize=True, subsampling=1)
        elif fmt == "webp":
            opts.update(method=6)
        elif fmt == "avif":
            opts.update(speed=4)
        resized.save(target, fmt.upper(), **opts)
        print(f"  {target.name:<34} {target.stat().st_size // 1024:>5} KB")


def placeholder(im: Image.Image, stem: str) -> str:
    """A ~20px-wide JPEG as a data URI, used as the CSS blur-up background."""
    import base64
    import io

    small = im.copy()
    small.thumbnail((20, 20), Image.LANCZOS)
    buf = io.BytesIO()
    small.save(buf, "JPEG", quality=40)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> int:
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((ROOT / "content" / "media.json").read_text())
    derived: dict[str, dict] = {}
    missing: list[str] = []

    for item in manifest["images"]:
        src = Path(item["src"]).expanduser()
        stem, role = item["id"], item["role"]
        widths = LADDERS[role]

        if not src.exists():
            missing.append(f'{stem}: {item["src"]}')
            continue

        print(f"{stem}  ({role})")
        im = load(src, max(widths))

        # Never upscale: clamp the ladder to the source's real resolution.
        usable = [w for w in widths if w <= im.width] or [im.width]
        for w in usable:
            encode(im, stem, w, force)

        derived[stem] = {
            "widths": usable,
            "jpegWidths": [w for w in usable if w <= JPEG_MAX_WIDTH] or usable[:1],
            "aspect": round(im.width / im.height, 4),
            "lqip": placeholder(im, stem),
        }

    (ROOT / "content" / "media.derived.json").write_text(
        json.dumps(derived, indent=2) + "\n"
    )

    print("\nicons + social card")
    build_icons()
    hero = next((i["src"] for i in manifest["images"] if i["id"] == "hero-rain"), "")
    build_og_card(hero)

    if missing:
        print("\nSOURCE FILES NOT FOUND — these images will render as TODO blocks:")
        for m in missing:
            print("  -", m)

    print(f"\n{len(derived)} images processed -> static/media/")
    return 0



# ==========================================================================
# Icons and the social preview card.
#
# Generated here rather than in build.py so that build.py stays dependency-free.
# Re-run this script if the hero photograph or the name ever changes.
# ==========================================================================

BG = (11, 12, 13)
FG = (244, 239, 233)
DIM = (154, 150, 145)
ACCENT = (255, 74, 36)

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONTS = {
    "display": f"{FONT_DIR}/Arial Black.ttf",
    "bold": f"{FONT_DIR}/Arial Bold.ttf",
    "regular": f"{FONT_DIR}/Arial.ttf",
}


def _font(kind: str, size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype(FONTS[kind], size)
    except OSError:
        return ImageFont.load_default(size)


def build_icons() -> None:
    """Apple touch icon and favicon.ico — the same mark as favicon.svg."""
    from PIL import Image, ImageDraw

    def mark(size: int, radius_ratio: float = 0.22) -> Image.Image:
        s = size * 4  # supersample, then downscale: cheap antialiasing
        im = Image.new("RGB", (s, s), BG)
        d = ImageDraw.Draw(im)
        pad = s * 0.17
        d.ellipse([pad, pad, s - pad, s - pad], outline=FG, width=max(2, int(s * 0.055)))
        c = s / 2
        r = s * 0.13
        d.ellipse([c - r, c - r, c + r, c + r], fill=ACCENT)
        return im.resize((size, size), Image.LANCZOS)

    ROOT_FILES.mkdir(parents=True, exist_ok=True)
    mark(180).save(ROOT_FILES / "apple-touch-icon.png", "PNG")
    ico = mark(64)
    ico.save(ROOT_FILES / "favicon.ico", "ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print("  apple-touch-icon.png, favicon.ico")


def build_og_card(hero_src: str) -> None:
    """1200x630 social preview, generated from content/site.json.

    Everything on it is read from the same file the site reads, so the card
    cannot drift out of step with the positioning the way a hardcoded one does.
    """
    from PIL import Image, ImageDraw, ImageEnhance

    site = json.loads((ROOT / "content" / "site.json").read_text())
    meta = site["meta"]

    W, H = 1200, 630
    card = Image.new("RGB", (W, H), BG)

    src = Path(hero_src).expanduser()
    if src.exists():
        photo = load(src, 1600)
        scale = max(W / photo.width, H / photo.height)
        photo = photo.resize(
            (max(W, round(photo.width * scale)), max(H, round(photo.height * scale))),
            Image.LANCZOS,
        )
        left = (photo.width - W) // 2
        top = (photo.height - H) // 2
        photo = photo.crop((left, top, left + W, top + H))
        photo = ImageEnhance.Color(photo).enhance(0.45)
        photo = ImageEnhance.Brightness(photo).enhance(0.5)
        card.paste(photo, (0, 0))

        scrim = Image.new("L", (W, 1))
        for x in range(W):
            scrim.putpixel((x, 0), int(238 * max(0.0, 1 - (x / W) * 1.4)))
        card = Image.composite(Image.new("RGB", (W, H), BG), card, scrim.resize((W, H)))

    d = ImageDraw.Draw(card)
    x = 76

    d.rectangle([x, 92, x + 46, 95], fill=ACCENT)
    d.text((x + 62, 82), site["role"].upper(), font=_font("bold", 20), fill=ACCENT)

    parts = site["name"].rsplit(" ", 1)
    d.text((x, 150), parts[0].upper(), font=_font("display", 78), fill=FG)
    d.text((x, 236), parts[-1].upper(), font=_font("display", 78), fill=FG)

    d.rectangle([x, 364, x + 210, 365], fill=(90, 88, 85))

    for i, line in enumerate(_wrap_text(site["discipline"], 40)[:2]):
        d.text((x, 396 + i * 40), line, font=_font("bold", 29), fill=FG)

    d.text((x, 506), meta.get("ogProof", ""), font=_font("regular", 23), fill=DIM)

    d.ellipse([x, 556, x + 11, 567], fill=ACCENT)
    d.text((x + 24, 549), f"{site['location']} · {site['status']}",
           font=_font("regular", 22), fill=DIM)

    card.save(OUT / "og-image.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    print(f"  og-image.jpg                   {(OUT / 'og-image.jpg').stat().st_size // 1024:>5} KB")


def _wrap_text(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
