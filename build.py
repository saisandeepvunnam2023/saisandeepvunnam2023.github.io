#!/usr/bin/env python3
"""
Static site generator for saisandeepvunnam2023.github.io.

Python standard library only — no Node, no npm, no framework, nothing to install
and nothing to go stale. Content lives in content/*.json, layout lives in
site/**, and this script turns the two into flat HTML in dist/.

    python3 build.py                 # build into dist/
    python3 build.py --serve         # build, then serve dist/ on :8000

Images are handled separately by optimize_images.py, which is the only script
that needs Pillow. Run that when photographs change; run this every other time.
"""

from __future__ import annotations

import http.server
import json
import re
import shutil
import socketserver
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
STATIC = ROOT / "static"

sys.path.insert(0, str(ROOT))

from builder import render as R  # noqa: E402
from builder.pages import case_study, home, notfound  # noqa: E402


# --------------------------------------------------------------------------
# Assets
# --------------------------------------------------------------------------

CSS_ORDER = [
    "tokens.css",
    "reset.css",
    "type.css",
    "layout.css",
    "nav.css",
    "hero.css",
    "work.css",
    "skills.css",
    "experience.css",
    "frames.css",
    "about.css",
    "contact.css",
    "case-study.css",
    "misc.css",
]

JS_FILES = ["main.js", "focus-field.js", "signal-field.js"]


def minify_css(css: str) -> str:
    """Conservative minification: comments out, whitespace collapsed.

    Deliberately does not touch anything inside url(...) or quotes, because the
    LQIP data URIs in the markup and the font URLs here must survive intact.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", "\n", css)
    css = re.sub(r"\n+", "\n", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return css.strip()


def build_css() -> str:
    parts = []
    for name in CSS_ORDER:
        path = STATIC / "css" / name
        if not path.exists():
            raise SystemExit(f"missing stylesheet: {path}")
        parts.append(f"/* {name} */\n" + path.read_text(encoding="utf-8"))
    return minify_css("\n".join(parts))


def script_tags(base: str) -> str:
    return f'<script type="module" src="{base}js/main.js"></script>'


# --------------------------------------------------------------------------
# Generated files
# --------------------------------------------------------------------------

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="6" fill="#0B0C0D"/>
<circle cx="16" cy="16" r="10.5" fill="none" stroke="#F4EFE9" stroke-width="1.8"/>
<circle cx="16" cy="16" r="4.2" fill="#FF4A24"/>
</svg>
"""


def manifest(site: dict) -> str:
    return json.dumps(
        {
            "name": site["name"],
            "short_name": "SSV",
            "description": site["meta"]["description"],
            "start_url": "/",
            "display": "standalone",
            "background_color": site["meta"]["themeColor"],
            "theme_color": site["meta"]["themeColor"],
            "icons": [
                {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
                {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            ],
        },
        indent=2,
    )


def sitemap(site: dict, projects: dict) -> str:
    base = site["meta"]["siteUrl"]
    today = date.today().isoformat()
    urls = [(base + "/", "1.0")]
    urls += [
        (f"{base}/work/{p['slug']}/", "0.8")
        for p in projects["items"]
        if p.get("caseStudy")
    ]
    entries = "".join(
        f"<url><loc>{loc}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>monthly</changefreq><priority>{pri}</priority></url>"
        for loc, pri in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}</urlset>"
    )


def robots(site: dict) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {site['meta']['siteUrl']}/sitemap.xml\n"


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def copy_static() -> None:
    for folder in ("media", "fonts", "files"):
        src = STATIC / folder
        if src.exists():
            shutil.copytree(src, DIST / folder, dirs_exist_ok=True)

    root_files = STATIC / "root"
    if root_files.exists():
        for f in root_files.iterdir():
            if f.is_file():
                shutil.copy2(f, DIST / f.name)

    js_dir = DIST / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    for name in JS_FILES:
        path = STATIC / "js" / name
        if not path.exists():
            raise SystemExit(f"missing script: {path}")
        shutil.copy2(path, js_dir / name)

    # The hero source is only an input to optimize_images.py; it should never ship.
    stray = DIST / "media" / "_headshot-src.jpeg"
    if stray.exists():
        stray.unlink()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    site = R.load_content("site")
    projects = R.load_content("projects")
    skills = R.load_content("skills")
    experience = R.load_content("experience")
    story = R.load_content("story")

    derived_path = ROOT / "content" / "media.derived.json"
    if derived_path.exists():
        R.DERIVED.update(json.loads(derived_path.read_text()))
    else:
        print("!  content/media.derived.json missing — run python3 optimize_images.py")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    css = build_css()
    copy_static()

    write(
        DIST / "index.html",
        home.render(
            site=site,
            projects=projects,
            skills_data=skills,
            exp=experience,
            story=story,
            css=css,
            scripts=script_tags(""),
        ),
    )

    case_count = 0
    for p in projects["items"]:
        if not p.get("caseStudy"):
            continue
        write(
            DIST / "work" / p["slug"] / "index.html",
            case_study.render(
                site=site,
                project=p,
                projects=projects,
                css=css,
                scripts=script_tags("../../"),
            ),
        )
        case_count += 1

    write(
        DIST / "404.html",
        notfound.render(site=site, projects=projects, css=css, scripts=script_tags("/")),
    )

    write(DIST / "favicon.svg", FAVICON_SVG)
    write(DIST / "site.webmanifest", manifest(site))
    write(DIST / "sitemap.xml", sitemap(site, projects))
    write(DIST / "robots.txt", robots(site))
    (DIST / ".nojekyll").write_text("")  # stop Pages from running Jekyll over dist/

    # Warn loudly about anything still unresolved rather than shipping it quietly.
    warnings = []
    if not (DIST / "files" / "Sai-Sandeep-Vunnam-Resume.pdf").exists():
        warnings.append("résumé PDF missing → static/files/Sai-Sandeep-Vunnam-Resume.pdf")
    if not site["links"]["linkedin"].startswith("http"):
        warnings.append("LinkedIn URL not set → content/site.json")
    if not (DIST / "media" / "og-image.jpg").exists():
        warnings.append("social preview image missing → run python3 optimize_images.py")

    blob = json.dumps([site, projects, skills, experience, story])
    todo_count = len(re.findall(r'"TODO', blob)) + blob.count("TODO —")

    size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    pages = 2 + case_count

    print(f"\n  dist/  {pages} pages · {len(css) / 1024:.1f} KB CSS inlined · {size / 1024 / 1024:.1f} MB total")
    print(f"         index.html, {case_count} case studies, 404.html, sitemap, robots, manifest")
    if todo_count:
        print(f"\n  {todo_count} TODO markers still in content/ — they render visibly on the page.")
    for w in warnings:
        print(f"  !  {w}")
    print()

    if "--serve" in sys.argv:
        serve()
    return 0


def serve(port: int = 8000) -> None:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(DIST), **kw)

        def log_message(self, *a):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"  serving dist/ at http://localhost:{port}  (ctrl-c to stop)\n")
        httpd.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
