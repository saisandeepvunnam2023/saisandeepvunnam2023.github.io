"""404.

GitHub Pages serves /404.html for any unmatched path at any depth, so every
asset reference here is absolute from the site root rather than relative.
"""

from __future__ import annotations

from ..layout import document, head
from ..render import esc, join


def render(*, site, projects, css, scripts, base: str = "/") -> str:
    meta = site["meta"]

    routes = [("Home", base), ("Selected work", f"{base}#work"),
              ("Experience", f"{base}#experience"), ("Contact", f"{base}#contact")]
    routes += [(p["title"], f"{base}work/{p['slug']}/")
               for p in projects["items"] if p.get("caseStudy")]

    links = join(
        f'<li><a href="{esc(href)}"><span>{esc(label)}</span>'
        f'<span class="nf__arrow" aria-hidden="true">→</span></a></li>'
        for label, href in routes
    )

    body = f"""
<main id="main" class="nf">
  <div class="shell nf__inner">
    <p class="nf__code" aria-hidden="true">404</p>
    <h1 class="nf__title">Out of frame.</h1>
    <p class="nf__body">
      This page does not exist. Here is everything that does.
    </p>
    <ul class="nf__links">{links}</ul>
    <p class="nf__sign">
      <a class="btn btn--primary" href="{esc(base)}"><span>Back to the start</span></a>
      <a class="btn" href="mailto:{esc(site['email'])}"><span>{esc(site['email'])}</span></a>
    </p>
  </div>
</main>"""

    # 404 can be served from any path, so its head must not use relative asset URLs.
    head_html = head(
        site=site,
        css=css,
        title=f"Page not found · {site['name']}",
        description="That page does not exist.",
        canonical=meta["siteUrl"] + "/404.html",
        base=base,
    ).replace("</head>", '<meta name="robots" content="noindex">\n</head>')

    return document(head_html=head_html, body=body, base=base, scripts=scripts)
