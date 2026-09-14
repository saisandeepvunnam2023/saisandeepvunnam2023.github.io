"""The document shell: head, metadata, structured data, and the script tags.

All CSS is inlined. At ~30 KB compressed that is cheaper than a round trip, and
it means the page has no render-blocking request at all.
"""

from __future__ import annotations

import json

from .render import esc, image_src, join


def person_schema(site: dict, projects: dict) -> str:
    """Person schema for Sai, plus the work as CreativeWork entries."""
    meta = site["meta"]
    links = site["links"]

    same_as = [u for k, u in links.items() if k in ("github", "linkedin") and u.startswith("http")]

    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site["name"],
        "url": meta["siteUrl"],
        "email": f"mailto:{site['email']}",
        "jobTitle": site["role"],
        "description": meta["description"],
        "knowsAbout": [
            "Web development",
            "Content management systems",
            "Python",
            "Computer vision",
            "Web accessibility",
            "Photography",
        ],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Dayton",
            "addressRegion": "OH",
            "addressCountry": "US",
        },
        "alumniOf": {
            "@type": "CollegeOrUniversity",
            "name": "University of Dayton",
        },
    }
    if same_as:
        data["sameAs"] = same_as

    works = [
        {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": p["title"],
            "abstract": p["problem"],
            "author": {"@type": "Person", "name": site["name"]},
            "dateCreated": p["year"],
            "keywords": ", ".join(p["stack"]),
            **(
                {"url": f"{meta['siteUrl']}/work/{p['slug']}/"}
                if p.get("caseStudy")
                else {}
            ),
        }
        for p in projects["items"]
    ]

    blocks = [data] + works
    return join(
        f'<script type="application/ld+json">{json.dumps(b, separators=(",", ":"))}</script>'
        for b in blocks
    )


def head(
    *,
    site: dict,
    css: str,
    title: str,
    description: str,
    canonical: str,
    base: str,
    schema: str = "",
    preload_image: tuple[str, str] | None = None,
) -> str:
    meta = site["meta"]
    og = f"{meta['siteUrl']}/{meta['ogImage']}"

    preload = ""
    if preload_image and preload_image[0]:
        srcset, sizes = preload_image
        preload = (
            f'<link rel="preload" as="image" imagesrcset="{esc(srcset)}" '
            f'imagesizes="{esc(sizes)}" type="image/avif" fetchpriority="high">'
        )

    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="author" content="{esc(site['name'])}">
<meta name="theme-color" content="{esc(meta['themeColor'])}">
<meta name="color-scheme" content="dark">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(og)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(site['name'])} — {esc(site['role'])}">
<meta property="og:locale" content="{esc(meta['locale'])}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(og)}">

<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{base}favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="{base}apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">

<link rel="preload" href="{base}fonts/archivo-var-latin.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<style>{css}</style>
<script>document.documentElement.classList.replace('no-js','js')</script>
{schema}
</head>"""


def document(*, head_html: str, body: str, base: str, scripts: str) -> str:
    return f"""{head_html}
<body>
<a class="skip-link" href="#main">Skip to content</a>
{body}
{scripts}
</body>
</html>"""
