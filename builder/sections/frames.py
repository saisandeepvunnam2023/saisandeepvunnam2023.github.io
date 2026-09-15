"""Photography — 'Through another lens'.

Seven photographs in an editorial grid, large, with captions that explain the
decision behind each frame rather than admiring it. The span values in
story.json drive the composition, so reordering the section is a content edit.
"""

from __future__ import annotations

from ..render import esc, join, link_out, picture, section_heading

SIZES = {
    "full": "(max-width:900px) 100vw, 92vw",
    "wide": "(max-width:900px) 100vw, 62vw",
    "half": "(max-width:900px) 100vw, 46vw",
    "tall": "(max-width:900px) 100vw, 34vw",
}


def render(photography: dict) -> str:
    frames = join(
        f'<figure class="frame frame--{esc(p["span"])}" data-reveal style="--i:{i}">'
        + picture(
            p["id"],
            p["alt"],
            sizes=SIZES.get(p["span"], SIZES["half"]),
            cls="frame__img",
        )
        + f'<figcaption class="frame__caption">'
        f'<span class="frame__title">{esc(p["title"])}</span>'
        f'<span class="frame__text">{esc(p["caption"])}</span>'
        f"</figcaption></figure>"
        for i, p in enumerate(photography["photographs"])
    )

    return f"""
<section class="section section--frames" id="frames" aria-labelledby="frames-title">
  <div class="shell">
    {section_heading(photography['eyebrow'], photography['sectionTitle'], '04', 'frames')}
    <p class="section__intro section__intro--wide">{esc(photography['intro'])}</p>
  </div>
  <div class="shell shell--wide">
    <div class="frames">{frames}</div>
    <div class="frames__foot">
      <p class="frames__outro">{esc(photography['outro'])}</p>
      {link_out(photography['link']['label'], photography['link']['href'], primary=True)}
    </div>
  </div>
</section>
"""
