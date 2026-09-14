"""Selected work.

Four projects, four genuinely different compositions — the layout of each one is
chosen to suit what that project actually is, not to fill a grid. The hover state
reveals role, stack, year and category, which is information, not decoration.
"""

from __future__ import annotations

from ..render import esc, join, link_out, picture, section_heading, tags


def _meta_row(p: dict) -> str:
    cells = [
        ("Role", p["role"]),
        ("Year", p["year"]),
        ("Category", p["category"]),
    ]
    return (
        '<dl class="project__meta">'
        + join(
            f'<div class="project__meta-cell"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
            for k, v in cells
        )
        + f'<div class="project__meta-cell project__meta-cell--stack">'
        f"<dt>Stack</dt><dd>{esc(' · '.join(p['stack']))}</dd></div>"
        "</dl>"
    )


def _head(p: dict, base: str) -> str:
    case_link = (
        f'<a class="project__case-link" href="{base}work/{esc(p["slug"])}/">'
        f"<span>Read the case study</span>"
        f'<svg viewBox="0 0 12 12" aria-hidden="true" focusable="false">'
        f'<path d="M2 10 L10 2 M4.5 2 H10 V7.5" fill="none" stroke="currentColor" '
        f'stroke-width="1.4" stroke-linecap="square"/></svg></a>'
        if p.get("caseStudy")
        else ""
    )

    title_inner = esc(p["title"])
    if p.get("caseStudy"):
        title_inner = (
            f'<a class="project__title-link" href="{base}work/{esc(p["slug"])}/">'
            f"{title_inner}</a>"
        )

    return f"""
    <div class="project__head">
      <p class="project__index" aria-hidden="true">{esc(p['index'])}</p>
      <div class="project__headings">
        <p class="project__kicker">{esc(p['kicker'])}</p>
        <h3 class="project__title">{title_inner}</h3>
      </div>
    </div>
    <div class="project__copy">
      <p class="project__problem"><span class="project__label">Problem</span>{esc(p['problem'])}</p>
      <p class="project__built"><span class="project__label">What I built</span>{esc(p['built'])}</p>
      {_meta_row(p)}
      <div class="project__links">
        {join(link_out(l['label'], l['href'], l.get('primary', False)) for l in p.get('links', []))}
        {case_link}
      </div>
    </div>
    """


def _outcome(p: dict) -> str:
    m = p.get("outcomeMetric")
    if not m:
        return ""
    return f"""
    <div class="outcome">
      <p class="outcome__value">{esc(m['value'])}<span class="outcome__unit">{esc(m['unit'])}</span></p>
      <p class="outcome__caption">{esc(m['caption'])}</p>
      <p class="outcome__full">{esc(p['outcome'])}</p>
    </div>"""


# --------------------------------------------------------------------------
# Layouts
# --------------------------------------------------------------------------

def _layout_covers(p: dict, base: str) -> str:
    covers = join(
        f'<li class="cover" style="--i:{i}">'
        f'<a class="cover__link" href="{esc(c["href"])}" target="_blank" rel="noopener noreferrer">'
        + picture(
            c["id"],
            f"Cover of the {c['label']} issue of the University of Dayton Magazine",
            sizes="(max-width:600px) 44vw, (max-width:1000px) 30vw, 15vw",
            cls="cover__img",
        )
        + f'<span class="cover__label"><span class="cover__issue">{esc(c["label"])}</span>'
        f'<span class="cover__go" aria-hidden="true">View</span></span>'
        f"</a></li>"
        for i, c in enumerate(p["covers"])
    )
    return f"""
    <div class="project__visual project__visual--covers">
      <ul class="covers">{covers}</ul>
    </div>
    {_outcome(p)}"""


def _layout_scale(p: dict, base: str) -> str:
    m = p["outcomeMetric"]
    details = join(
        f'<div class="detail"><dt class="detail__label">{esc(d["label"])}</dt>'
        f'<dd class="detail__text">{esc(d["text"])}</dd></div>'
        for d in p.get("detail", [])
    )
    return f"""
    <div class="project__visual project__visual--scale">
      <div class="scale">
        <p class="scale__value" aria-hidden="true">{esc(m['value'])}</p>
        <p class="scale__caption">{esc(m['caption'])}</p>
      </div>
      <dl class="details">{details}</dl>
    </div>"""


def _layout_pipeline(p: dict, base: str) -> str:
    stages = join(
        f'<li class="stage" style="--i:{i}">'
        f'<span class="stage__n" aria-hidden="true">{esc(s["n"])}</span>'
        f'<h4 class="stage__title">{esc(s["title"])}</h4>'
        f'<p class="stage__text">{esc(s["text"])}</p>'
        f"</li>"
        for i, s in enumerate(p["stages"])
    )
    return f"""
    <div class="project__visual project__visual--pipeline">
      <ol class="pipeline">{stages}</ol>
    </div>
    {_outcome(p)}"""


def _layout_split(p: dict, base: str) -> str:
    points = join(
        f'<div class="point" style="--i:{i}">'
        f'<dt class="point__label">{esc(pt["label"])}</dt>'
        f'<dd class="point__text">{esc(pt["text"])}</dd></div>'
        for i, pt in enumerate(p["splitPoints"])
    )
    return f"""
    <div class="project__visual project__visual--split">
      <dl class="points">{points}</dl>
      {_outcome(p)}
    </div>"""


def _layout_shots(p: dict, base: str) -> str:
    """A large lead screenshot, then a strip of detail shots beneath it.

    For work whose evidence is the artefact itself — you show the thing rather
    than describing it.
    """
    lead = p["lead"]
    strip = join(
        f'<figure class="shot" style="--i:{i}">'
        + picture(
            s["id"],
            s["alt"],
            sizes="(max-width:700px) 92vw, 30vw",
            cls="shot__img",
        )
        + f'<figcaption class="shot__label">{esc(s["label"])}</figcaption>'
        f"</figure>"
        for i, s in enumerate(p.get("shots", []))
    )

    return f"""
    <div class="project__visual project__visual--shots">
      <figure class="shot shot--lead">
        {picture(lead["id"], lead["alt"], sizes="(max-width:700px) 92vw, 92vw", cls="shot__img")}
      </figure>
      <div class="shots">{strip}</div>
    </div>
    {_outcome(p)}"""


LAYOUTS = {
    "shots": _layout_shots,
    "covers": _layout_covers,
    "scale": _layout_scale,
    "pipeline": _layout_pipeline,
    "split": _layout_split,
}


def render(projects: dict, base: str = "") -> str:
    items = join(
        f'<article class="project project--{esc(p["layout"])}" id="project-{esc(p["slug"])}" '
        f'data-reveal>{_head(p, base)}{LAYOUTS[p["layout"]](p, base)}</article>'
        for p in projects["items"]
    )

    return f"""
<section class="section section--work" id="work" aria-labelledby="work-title">
  <div class="shell">
    {section_heading(projects['eyebrow'], projects['sectionTitle'], '01', 'work')}
    <div class="projects">{items}</div>
  </div>
</section>
"""
