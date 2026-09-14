"""About, field notes and the playground.

The about copy is a short story with an argument in it, not a biography. Field
notes are the human layer. Playground is deliberately a plain list so that
adding an experiment later costs one object in story.json.
"""

from __future__ import annotations

from ..render import esc, is_todo, join, picture, section_heading, text_or_todo


def render_about(about: dict, notes: dict) -> str:
    paras = join(f"<p>{esc(p)}</p>" for p in about["paragraphs"])

    note_items = join(
        f'<div class="note" data-reveal style="--i:{i}">'
        f'<dt class="note__label">{esc(n["label"])}</dt>'
        f'<dd class="note__text">{text_or_todo(n["text"])}</dd></div>'
        for i, n in enumerate(notes["items"])
    )

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

    <div class="notes">
      <h3 class="notes__title">
        <span class="notes__eyebrow">{esc(notes['eyebrow'])}</span>
        {esc(notes['sectionTitle'])}
      </h3>
      <dl class="notes__list">{note_items}</dl>
    </div>
  </div>
</section>
"""


def render_playground(playground: dict) -> str:
    items = join(
        f'<li class="exp exp--{esc(x["status"])}" data-reveal style="--i:{i}">'
        f'<div class="exp__head">'
        f'<h3 class="exp__title">{esc(x["title"])}</h3>'
        f'<span class="exp__status">{esc(x["status"])}</span>'
        f"</div>"
        f'<p class="exp__text">{esc(x["text"])}</p>'
        f'<p class="exp__meta"><span>{esc(x["tech"])}</span><span>{esc(x["year"])}</span></p>'
        f"</li>"
        for i, x in enumerate(playground["items"])
    )

    return f"""
<section class="section section--playground" id="playground" aria-labelledby="playground-title">
  <div class="shell">
    <header class="section__head section__head--compact">
      <p class="eyebrow"><span class="eyebrow__index">06</span><span>{esc(playground['eyebrow'])}</span></p>
      <h2 class="section__title section__title--sm" id="playground-title">{esc(playground['sectionTitle'])}</h2>
      <p class="section__intro">{esc(playground['intro'])}</p>
    </header>
    <ul class="experiments">{items}</ul>
    <p class="playground__footnote">{esc(playground['footnote'])}</p>
  </div>
</section>
"""
