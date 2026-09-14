"""Experience, education and recognition.

An editorial column rather than a timeline widget. Each role leads with the one
line worth scanning; the detail sits underneath for anyone who wants it. Roles
still awaiting your confirmation carry a visible verify flag.
"""

from __future__ import annotations

from ..render import esc, is_todo, join, section_heading, tags, text_or_todo


def _role(r: dict, i: int) -> str:
    bullets = join(f"<li>{esc(b)}</li>" for b in r["contributions"])
    flag = (
        '<span class="todo todo--flag" title="Dates or title differ between your '
        'résumé variants — confirm before publishing">verify</span>'
        if r.get("verify")
        else ""
    )

    return f"""
    <article class="role" data-reveal style="--i:{i}">
      <div class="role__rail" aria-hidden="true"><span class="role__node"></span></div>
      <div class="role__period">
        <p class="role__dates">{esc(r['period'])}</p>
        <p class="role__place">{text_or_todo(r['location'])}</p>
      </div>
      <div class="role__body">
        <h3 class="role__title">{esc(r['role'])}</h3>
        <p class="role__company">{esc(r['company'])}{flag}</p>
        <p class="role__highlight">{esc(r['highlight'])}</p>
        <details class="role__more">
          <summary><span class="role__more-open">What I did</span><span class="role__more-close">Less</span></summary>
          <ul class="role__list">{bullets}</ul>
          {tags(r['stack'], 'tags tags--role')}
        </details>
      </div>
    </article>"""


def render(exp: dict) -> str:
    roles = join(_role(r, i) for i, r in enumerate(exp["roles"]))

    education = join(
        f'<li class="edu"><p class="edu__institution">{esc(e["institution"])}</p>'
        f'<p class="edu__credential">{text_or_todo(e["credential"])}</p>'
        f'<p class="edu__meta">{text_or_todo(e["period"])} · {esc(e["location"])}</p></li>'
        for e in exp["education"]
    )

    recognition = join(f"<li>{esc(r)}</li>" for r in exp["recognition"])

    return f"""
<section class="section section--experience" id="experience" aria-labelledby="experience-title">
  <div class="shell">
    {section_heading(exp['eyebrow'], exp['sectionTitle'], '03', 'experience')}
    <div class="roles">{roles}</div>

    <div class="credentials">
      <div class="credentials__col">
        <h3 class="credentials__title">Education</h3>
        <ul class="edus">{education}</ul>
      </div>
      <div class="credentials__col">
        <h3 class="credentials__title">Recognition</h3>
        <ul class="recognition">{recognition}</ul>
      </div>
    </div>
  </div>
</section>
"""
