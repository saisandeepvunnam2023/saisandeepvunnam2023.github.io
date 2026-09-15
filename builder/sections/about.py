"""About.

A short story with an argument in it, not a biography.
"""

from __future__ import annotations

from ..render import esc, is_todo, join, picture, section_heading, text_or_todo


def render_about(about: dict) -> str:
    paras = join(f"<p>{esc(p)}</p>" for p in about["paragraphs"])

    return f"""
<section class="section section--about" id="about" aria-labelledby="about-title">
  <div class="shell">
    {section_heading(about['eyebrow'], about['sectionTitle'], '05', 'about')}
    <div class="about">
      <div class="about__portrait" data-reveal>
        {picture(
          "portrait",
          about["portraitAlt"],
          sizes="(max-width:900px) 60vw, 26vw",
          cls="about__img",
        )}
        <span class="about__portrait-mark" aria-hidden="true"></span>
      </div>
      <div class="about__copy">{paras}</div>
    </div>
  </div>
</section>
"""

