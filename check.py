#!/usr/bin/env python3
"""
Post-build checks.

Not a linter — a list of the specific ways this site could silently break:
dead asset references, a broken heading outline, an image without alt text, an
internal link pointing at an id that does not exist, unbalanced tags. Run it
after every build.

    python3 check.py
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DIST = Path(__file__).parent / "dist"


def site_base() -> str:
    """The path prefix the site is served under, read from content/site.json.

    Root-absolute URLs in the output (the 404 page, the manifest) are correct
    for the deployed site but are not filesystem paths inside dist/, so they
    have to have this prefix stripped before they can be resolved on disk.
    """
    import json
    from urllib.parse import urlparse

    data = json.loads((Path(__file__).parent / "content" / "site.json").read_text())
    path = urlparse(data["meta"]["siteUrl"]).path.strip("/")
    return f"/{path}/" if path else "/"


BASE = site_base()


def local(url: str, relative_to: Path) -> Path:
    """Map a URL in the output to the file it should resolve to inside dist/."""
    if url.startswith("/"):
        if BASE != "/" and url.startswith(BASE):
            url = url[len(BASE):]
        return DIST / url.lstrip("/")
    return relative_to / url

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr", "path", "circle", "rect",
        "line", "polygon", "polyline", "ellipse", "use", "stop"}


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.unbalanced = []
        self.headings = []
        self.ids = set()
        self.imgs = []
        self.links = []
        self.assets = []
        self.landmarks = []
        self.buttons = 0
        self._h = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if "id" in a:
            self.ids.add(a["id"])
        if re.fullmatch(r"h[1-6]", tag):
            self._h = int(tag[1])
            self.headings.append([self._h, ""])
        if tag == "img":
            self.imgs.append(a)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag in ("script", "link", "source", "img", "canvas"):
            for k in ("src", "href", "srcset"):
                if k in a:
                    self.assets.append((tag, k, a[k]))
        if tag in ("main", "nav", "header", "footer") or a.get("role") in ("main", "navigation"):
            self.landmarks.append(tag)
        if tag == "button":
            self.buttons += 1

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                self.unbalanced.append(tag)
        self._h = None

    def handle_data(self, data):
        if self._h and self.headings:
            self.headings[-1][1] += data.strip()


def check(path: Path, problems: list, notes: list) -> None:
    rel = path.relative_to(DIST)
    html = path.read_text(encoding="utf-8")
    doc = Doc()
    doc.feed(html)

    def bad(msg):
        problems.append(f"{rel}: {msg}")

    # --- structure ---------------------------------------------------------
    if doc.stack:
        bad(f"unclosed tags: {doc.stack[:6]}")
    if doc.unbalanced:
        bad(f"mismatched close tags: {set(doc.unbalanced)}")

    h1s = [h for h in doc.headings if h[0] == 1]
    if len(h1s) != 1:
        bad(f"expected exactly one h1, found {len(h1s)}")

    levels = [h[0] for h in doc.headings]
    for i in range(1, len(levels)):
        if levels[i] - levels[i - 1] > 1:
            bad(f"heading jumps h{levels[i - 1]} -> h{levels[i]} at {doc.headings[i][1][:40]!r}")

    if "main" not in doc.landmarks:
        bad("no <main> landmark")

    # --- images ------------------------------------------------------------
    for img in doc.imgs:
        if "alt" not in img:
            bad(f"img with no alt attribute: {img.get('src', '?')}")
        if not img.get("width") or not img.get("height"):
            bad(f"img without width/height (layout shift): {img.get('src', '?')}")

    # --- metadata ----------------------------------------------------------
    for needle, label in [
        ('rel="canonical"', "canonical"),
        ('property="og:image"', "og:image"),
        ('name="twitter:card"', "twitter card"),
        ('name="description"', "meta description"),
        ('rel="icon"', "favicon"),
        ("<title>", "title"),
    ]:
        if needle not in html:
            bad(f"missing {label}")

    # --- assets exist ------------------------------------------------------
    base = path.parent
    for tag, attr, value in doc.assets:
        for url in re.split(r",", value):
            url = url.strip().split(" ")[0]
            if not url or url.startswith(("http", "data:", "mailto:", "#", "tel:")):
                continue
            target = local(url, base)
            if not target.exists():
                bad(f"{tag} {attr} -> missing file: {url}")

    # --- internal links ----------------------------------------------------
    for href in doc.links:
        if href.startswith(("http", "mailto:", "tel:")):
            continue

        # Same-page anchor: the id must exist in this document.
        if href.startswith("#"):
            if len(href) > 1 and href[1:] not in doc.ids:
                bad(f"anchor points at missing id: {href}")
            continue

        # Cross-page link, possibly with a fragment ("../../#work"). Only the
        # path part addresses a file; the fragment is resolved by the browser.
        path_part = href.split("#", 1)[0]
        if not path_part:
            continue

        target = local(path_part, base)
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            bad(f"link -> missing page: {href}")

    # --- canvas sources ------------------------------------------------------
    # The hero canvas fetches images from a JSON attribute, so they are invisible
    # to the asset walk above. The JPEG ladder is shorter than the AVIF one, and
    # that mismatch is exactly the kind of thing that only breaks on old browsers.
    for m in re.finditer(r"data-sources='([^']+)'", html):
        import json as _json

        try:
            src = _json.loads(m.group(1))
        except ValueError:
            bad("data-sources is not valid JSON")
            continue
        for url in src.get("avif", []) + src.get("jpg", []):
            if not (DIST / url).exists():
                bad(f"canvas source -> missing file: {url}")

    # --- content warnings ---------------------------------------------------
    if 'class="todo' in html:
        bad("a TODO marker reached the rendered page — it should have been omitted")

    size = len(html.encode()) / 1024
    notes.append(f"{rel}: {size:.0f} KB html · {len(doc.imgs)} img · {len(doc.links)} links")


def main() -> int:
    if not DIST.exists():
        print("no dist/ — run python3 build.py first")
        return 1

    problems: list[str] = []
    notes: list[str] = []

    pages = sorted(DIST.rglob("*.html"))
    for p in pages:
        check(p, problems, notes)

    # Weight of everything the first visit actually pulls down.
    critical = [DIST / "index.html", DIST / "js" / "main.js",
                DIST / "fonts" / "archivo-var-latin.woff2"]
    hero = sorted(DIST.glob("media/hero-rain-1920.avif"))
    critical += hero
    weight = sum(f.stat().st_size for f in critical if f.exists()) / 1024

    print(f"\n  {len(pages)} pages checked\n")
    for n in notes:
        print(f"    {n}")
    print(f"\n    first-load critical path: ~{weight:.0f} KB (html + js + font + hero avif)")

    if problems:
        print(f"\n  {len(problems)} PROBLEM(S):\n")
        for p in problems:
            print(f"    ✗ {p}")
        print()
        return 1

    print("\n  no structural problems found\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
