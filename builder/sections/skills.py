"""The Signal Field.

Four capabilities on the left, every technology on the right, and a line drawn
between them for the one you are pointed at — plus the project each technology
actually appears in.

Important: this is a highlighting layer, not a tab layer. Every technology is in
the DOM at all times, so the section is fully readable with JavaScript off, in a
screen reader, and to a crawler. The lines are the enhancement; the information
is the HTML.
"""

from __future__ import annotations

from ..render import esc, join, section_heading


def _project_lookup(projects: dict) -> dict:
    return {p["slug"]: p for p in projects["items"]}


def render(skills: dict, projects: dict, base: str = "") -> str:
    lookup = _project_lookup(projects)

    keys = join(
        f'<button class="cap" type="button" data-cap="{esc(c["id"])}" aria-pressed="false">'
        f'<span class="cap__verb">{esc(c["verb"])}</span>'
        f'<span class="cap__line">{esc(c["line"])}</span>'
        f'<span class="cap__count">{len(c["nodes"])}</span>'
        f"</button>"
        for c in skills["capabilities"]
    )

    groups = []
    for c in skills["capabilities"]:
        nodes = []
        for i, n in enumerate(c["nodes"]):
            slug = n.get("project")
            if slug and slug in lookup:
                p = lookup[slug]
                target = (
                    f'{base}work/{p["slug"]}/' if p.get("caseStudy") else f'#project-{p["slug"]}'
                )
                where = (
                    f'<a class="node__where" href="{esc(target)}">'
                    f'<span class="node__where-arrow" aria-hidden="true">→</span>'
                    f'{esc(p["title"])}</a>'
                )
            else:
                where = ""  # no project to point at: render nothing, not a dash

            nodes.append(
                f'<li class="node" data-cap="{esc(c["id"])}" style="--i:{i}">'
                f'<span class="node__dot" aria-hidden="true"></span>'
                f'<span class="node__name">{esc(n["name"])}</span>'
                f'<span class="node__use">{esc(n["use"])}</span>'
                f"{where}</li>"
            )

        groups.append(
            f'<div class="node-group" data-cap="{esc(c["id"])}">'
            f'<h3 class="node-group__title"><span aria-hidden="true">{esc(c["verb"])}</span>'
            f'<span class="sr-only">{esc(c["verb"])} — {esc(c["line"])}</span></h3>'
            f'<ul class="nodes">{join(nodes)}</ul>'
            f"</div>"
        )

    return f"""
<section class="section section--skills" id="skills" aria-labelledby="skills-title">
  <div class="shell">
    {section_heading(skills['eyebrow'], skills['sectionTitle'], '02', 'skills')}
    <p class="section__intro">{esc(skills['intro'])}</p>

    <div class="field" data-signal-field>
      <svg class="field__wires" aria-hidden="true" focusable="false" data-wires></svg>

      <div class="field__keys" role="group" aria-label="Filter technologies by capability">
        {keys}
        <button class="cap cap--reset" type="button" data-cap-reset hidden>
          <span class="cap__verb">Show all</span>
        </button>
      </div>

      <div class="field__nodes">{join(groups)}</div>
    </div>
  </div>
</section>
"""
