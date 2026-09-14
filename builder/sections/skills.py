"""Skills.

Four capabilities as columns, the technologies under each as a plain scannable
list, and one readout underneath that fills in as you point at something.

The previous version was a tall two-column list with connector lines drawn on
hover. It had two problems: it read like a spreadsheet, and the idea it was
built around — the relationships — only appeared if you happened to hover.
This version puts the scannable part first and keeps the detail one glance away.

Accessibility and no-JS both matter here, so the detail for every technology
(what it is for, which project it appears in) is always in the DOM next to its
name. On a pointer device it is visually collapsed and mirrored into the large
readout; on touch and without JavaScript it simply stays visible inline, which
degrades to exactly the readable list it started as.
"""

from __future__ import annotations

from ..render import esc, join, section_heading


def _tech(node: dict, lookup: dict, base: str, i: int) -> str:
    slug = node.get("project")
    where = ""
    where_attrs = ""

    if slug and slug in lookup:
        p = lookup[slug]
        target = f'{base}work/{p["slug"]}/' if p.get("caseStudy") else f'#project-{p["slug"]}'
        where = (
            f'<a class="tech__where" href="{esc(target)}">'
            f'<span aria-hidden="true">→ </span>{esc(p["title"])}</a>'
        )
        where_attrs = f' data-where="{esc(p["title"])}" data-href="{esc(target)}"'

    return (
        f'<li class="tech" style="--i:{i}">'
        f'<span class="tech__name" data-tech data-use="{esc(node["use"])}"{where_attrs}>'
        f'{esc(node["name"])}</span>'
        f'<span class="tech__meta">'
        f'<span class="tech__use">{esc(node["use"])}</span>{where}'
        f"</span>"
        f"</li>"
    )


def render(skills: dict, projects: dict, base: str = "") -> str:
    lookup = {p["slug"]: p for p in projects["items"]}

    columns = join(
        f'<div class="cap-col" data-reveal style="--i:{n}">'
        f'<div class="cap-col__head">'
        f'<h3 class="cap-col__verb">{esc(c["verb"])}</h3>'
        f'<p class="cap-col__line">{esc(c["line"])}</p>'
        f"</div>"
        f'<ul class="cap-col__list">'
        + join(_tech(node, lookup, base, i) for i, node in enumerate(c["nodes"]))
        + "</ul></div>"
        for n, c in enumerate(skills["capabilities"])
    )

    total = sum(len(c["nodes"]) for c in skills["capabilities"])

    return f"""
<section class="section section--skills" id="skills" aria-labelledby="skills-title">
  <div class="shell">
    {section_heading(skills['eyebrow'], skills['sectionTitle'], '02', 'skills')}
    <p class="section__intro">{esc(skills['intro'])}</p>

    <div class="matrix" data-skills>
      <div class="matrix__cols">{columns}</div>

      <div class="readout" data-readout aria-hidden="true">
        <p class="readout__hint" data-readout-hint>
          <span class="readout__hint-mark"></span>
          Point at any of the {total} above.
        </p>
        <div class="readout__body" data-readout-body hidden>
          <p class="readout__name" data-readout-name></p>
          <p class="readout__use" data-readout-use></p>
          <a class="readout__where" data-readout-where hidden></a>
        </div>
      </div>
    </div>
  </div>
</section>
"""
