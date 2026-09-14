"""Rendering primitives. No template engine, no dependencies — just functions
that return HTML strings, composed the way components compose.

Everything that touches user content goes through `esc`. Everything that touches
an image goes through `picture`, which is the only place srcset logic lives.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"

# Populated once by build.py so the picture helper can resolve widths/aspect.
DERIVED: dict = {}


def load_content(name: str) -> dict:
    data = json.loads((CONTENT / f"{name}.json").read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def esc(value) -> str:
    """Escape for text nodes and double-quoted attributes."""
    return html.escape(str(value if value is not None else ""), quote=True)


def join(parts) -> str:
    return "".join(p for p in parts if p)


def classes(*names) -> str:
    return " ".join(n for n in names if n)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def is_todo(value) -> bool:
    return isinstance(value, str) and value.strip().upper().startswith("TODO")


def text_or_todo(value) -> str:
    """Escape a value, or render nothing at all if it is still a TODO.

    Unresolved content is omitted from the page rather than marked on it. A
    visitor should never see the seams of how the site was made; build.py
    reports every TODO in the terminal instead, which is where the person who
    has to fix it is actually looking.
    """
    return "" if is_todo(value) else esc(value)


def unresolved(*values) -> bool:
    """True if any of these is still a TODO — callers use it to skip a block."""
    return any(is_todo(v) for v in values)


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------

def picture(
    image_id: str,
    alt: str,
    *,
    sizes: str,
    base: str = "",
    cls: str = "",
    loading: str = "lazy",
    priority: bool = False,
    blur_up: bool = True,
) -> str:
    """A <picture> with AVIF -> WebP -> JPEG, correct intrinsic ratio, and a
    base64 LQIP behind it so there is colour on screen before the file lands.

    Width and height attributes are always emitted: layout shift is a bug.
    """
    meta = DERIVED.get(image_id)
    if not meta:
        # A build-time fault, not content: the page should still be valid.
        return (
            f'<div class="media media--missing {esc(cls)}" role="img" '
            f'aria-label="{esc(alt)}"></div>'
        )

    widths = meta["widths"]
    jpeg_widths = meta.get("jpegWidths", widths)
    aspect = meta["aspect"]
    largest = widths[-1]
    height = round(largest / aspect)

    # `src` is a fallback, not a selection: anything reading it instead of the
    # srcset (a crawler, a link unfurler, a very old browser) should get a
    # sensible middle size rather than the largest file we have.
    fallback = jpeg_widths[-1]

    def srcset(ext: str) -> str:
        ladder = jpeg_widths if ext == "jpg" else widths
        return ", ".join(f"{base}media/{image_id}-{w}.{ext} {w}w" for w in ladder)

    # Single quotes inside the data URI: the whole style lands in a
    # double-quoted attribute, and a double quote here silently truncates it.
    style = f"--aspect:{aspect};"
    if blur_up:
        style += f"background-image:url('{meta['lqip']}');"

    load_attrs = (
        ' loading="eager" fetchpriority="high" decoding="async"'
        if priority
        else ' loading="lazy" decoding="async"'
    )

    return (
        f'<picture class="media {esc(cls)}" style="{style}">'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{esc(sizes)}">'
        f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{esc(sizes)}">'
        f'<img src="{base}media/{image_id}-{fallback}.jpg" srcset="{srcset("jpg")}" '
        f'sizes="{esc(sizes)}" alt="{esc(alt)}" width="{largest}" height="{height}"'
        f"{load_attrs}>"
        f"</picture>"
    )


def preload_srcset(image_id: str, base: str = "") -> tuple[str, str]:
    """srcset + sizes for a <link rel=preload>.

    The preload must offer the browser the same candidate list the <picture>
    does. Preloading one fixed width instead makes a retina viewport download
    the hero twice — once for the preload it ignores, once for the one it picks.
    """
    meta = DERIVED.get(image_id)
    if not meta:
        return "", ""
    widths = meta["widths"]
    srcset = ", ".join(f"{base}media/{image_id}-{w}.avif {w}w" for w in widths)
    return srcset, "100vw"


def image_src(image_id: str, width: int, base: str = "") -> str:
    """A single concrete URL — for preloads, OG tags and the canvas source."""
    meta = DERIVED.get(image_id)
    if not meta:
        return ""
    widths = meta["widths"]
    chosen = min(widths, key=lambda w: abs(w - width))
    return f"{base}media/{image_id}-{chosen}"


# --------------------------------------------------------------------------
# Small shared pieces
# --------------------------------------------------------------------------

def eyebrow(text: str, index: str | None = None) -> str:
    idx = f'<span class="eyebrow__index">{esc(index)}</span>' if index else ""
    return f'<p class="eyebrow">{idx}<span>{esc(text)}</span></p>'


def section_heading(eyebrow_text: str, title: str, index: str | None = None, id_: str = "") -> str:
    hid = f' id="{esc(id_)}-title"' if id_ else ""
    return (
        f'<header class="section__head">'
        f"{eyebrow(eyebrow_text, index)}"
        f'<h2 class="section__title"{hid}>{esc(title)}</h2>'
        f"</header>"
    )


def tags(items, cls: str = "tags") -> str:
    if not items:
        return ""
    cells = join(f"<li>{esc(t)}</li>" for t in items)
    return f'<ul class="{esc(cls)}">{cells}</ul>'


def link_out(label: str, href: str, primary: bool = False, base: str = "") -> str:
    external = href.startswith("http")
    rel = ' target="_blank" rel="noopener noreferrer"' if external else ""
    arrow = (
        '<svg class="btn__arrow" viewBox="0 0 12 12" aria-hidden="true" focusable="false">'
        '<path d="M2 10 L10 2 M4.5 2 H10 V7.5" fill="none" stroke="currentColor" '
        'stroke-width="1.4" stroke-linecap="square"/></svg>'
    )
    cls = "btn btn--primary" if primary else "btn"
    return (
        f'<a class="{cls}" href="{esc(href)}"{rel} data-magnetic>'
        f"<span>{esc(label)}</span>{arrow}</a>"
    )
