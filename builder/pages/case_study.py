"""A dedicated case-study page per project: /work/<slug>/index.html

Seven numbered movements — Context, Challenge, Approach, Architecture,
Engineering, Result, Reflection. The point is to show how the problem was
reasoned about, so 'Challenge' and 'Reflection' carry as much weight as 'Result'.
"""

from __future__ import annotations

import json

from ..layout import document, head
from ..render import esc, is_todo, join, link_out, section_heading, tags
from ..sections import nav
from . import diagrams

BASE = "../../"


def _written(s: dict) -> bool:
    """A section with nothing but TODOs in it is not a section yet."""
    body = [p for p in s.get("body", []) if not is_todo(p)]
    return bool(body or s.get("diagram") or s.get("callout"))


def _section(s: dict, n: int) -> str:
    paras = join(f"<p>{esc(p)}</p>" for p in s.get("body", []) if not is_todo(p))
    callout = (
        f'<aside class="cs__callout"><p>{esc(s["callout"])}</p></aside>'
        if s.get("callout")
        else ""
    )
    diagram = diagrams.render(s["diagram"]) if s.get("diagram") else ""

    return f"""
  <section class="cs__section" id="cs-{n:02d}" data-reveal>
    <div class="cs__section-head">
      <p class="cs__n" aria-hidden="true">{n:02d}</p>
      <h2 class="cs__section-title">{esc(s['title'])}</h2>
    </div>
    <div class="cs__section-body">{paras}{callout}{diagram}</div>
  </section>"""


def _breadcrumbs(site: dict, p: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Work", "item": f"{site['meta']['siteUrl']}/#work"},
            {"@type": "ListItem", "position": 2, "name": p["title"],
             "item": f"{site['meta']['siteUrl']}/work/{p['slug']}/"},
        ],
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(data, separators=(",", ":"))
        + "</script>"
    )


def render(*, site, project, projects, css, scripts) -> str:
    p = project
    meta = site["meta"]
    m = p.get("outcomeMetric")

    others = [o for o in projects["items"] if o["slug"] != p["slug"] and o.get("caseStudy")]
    next_up = others[0] if others else None
    next_html = ""
    if next_up:
        next_html = f"""
  <a class="cs__next" href="{BASE}work/{esc(next_up['slug'])}/" data-magnetic>
    <span class="cs__next-label">Next case study</span>
    <span class="cs__next-title">{esc(next_up['title'])}</span>
    <span class="cs__next-arrow" aria-hidden="true">→</span>
  </a>"""

    outcome = ""
    if m:
        outcome = f"""
      <div class="cs__metric">
        <p class="cs__metric-value">{esc(m['value'])}<span>{esc(m['unit'])}</span></p>
        <p class="cs__metric-caption">{esc(m['caption'])}</p>
      </div>"""

    body = f"""
{nav.render(site, base=BASE)}
<main id="main" class="cs">
  <header class="cs__hero shell">
    <a class="cs__back" href="{BASE}#work">
      <span aria-hidden="true">←</span><span>All work</span>
    </a>
    <p class="cs__index" aria-hidden="true">{esc(p['index'])}</p>
    <p class="cs__kicker">{esc(p['kicker'])}</p>
    <h1 class="cs__title">{esc(p['title'])}</h1>
    <p class="cs__problem">{esc(p['problem'])}</p>

    <div class="cs__facts">
      <dl class="cs__facts-list">
        <div><dt>Role</dt><dd>{esc(p['role'])}</dd></div>
        <div><dt>Year</dt><dd>{esc(p['year'])}</dd></div>
        <div><dt>Category</dt><dd>{esc(p['category'])}</dd></div>
        <div class="cs__facts-stack"><dt>Stack</dt><dd>{esc(' · '.join(p['stack']))}</dd></div>
      </dl>
      {outcome}
    </div>

    <div class="cs__links">
      {join(link_out(l['label'], l['href'], l.get('primary', False)) for l in p.get('links', []))}
    </div>
  </header>

  <div class="shell cs__sections">
    {join(
        _section(s, i)
        for i, s in enumerate(
            [x for x in p.get('caseStudySections', []) if _written(x)], start=1
        )
    )}
  </div>

  <div class="shell">{next_html}</div>
</main>
{_footer(site)}"""

    description = f"{p['title']} — {p['problem']} Case study by {site['name']}."

    return document(
        head_html=head(
            site=site,
            css=css,
            title=f"{p['title']} — {site['name']}",
            description=description[:300],
            canonical=f"{meta['siteUrl']}/work/{p['slug']}/",
            base=BASE,
            schema=_breadcrumbs(site, p),
        ),
        body=body,
        base=BASE,
        scripts=scripts,
    )


def _footer(site: dict) -> str:
    from ..sections.contact import render_footer

    return render_footer(site).replace('href="#top"', 'href="#main"')
