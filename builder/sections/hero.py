"""The hero, and the one signature interaction.

The photograph behind the type is rendered by a canvas at four resolutions at
once: coarse mosaic at the edges, resolving to full detail under the pointer.
Noise becomes signal, which is the whole argument of the site.

Everything a recruiter needs — name, role, location, availability, work, résumé,
GitHub, LinkedIn — is real HTML in this section. If the canvas never runs, a
static <picture> sits behind the type and nothing is lost.
"""

from __future__ import annotations

import json

from ..render import canvas_sources, esc, is_todo, join, picture


def render(site: dict) -> str:
    links = site["links"]
    name_lines = join(
        f'<span class="hero__name-line" style="--i:{i}">{esc(part)}</span>'
        for i, part in enumerate(site["nameLines"])
    )
    headline = join(
        f'<span class="hero__statement-line" style="--i:{i}">{esc(line)}</span>'
        for i, line in enumerate(site["headline"])
    )

    # Source ladder handed to the canvas; it picks by viewport width and DPR.
    sources = json.dumps(canvas_sources("hero-rain"), separators=(",", ":"))

    status = ""
    if site.get("statusActive"):
        status = (
            f'<p class="hero__status">'
            f'<span class="hero__status-dot" aria-hidden="true"></span>'
            f'<span>{esc(site["location"])}</span>'
            f'<span class="hero__status-sep" aria-hidden="true">/</span>'
            f'<span class="hero__status-open">{esc(site["status"])}</span>'
            f"</p>"
        )

    social = []
    if links["github"].startswith("http"):
        social.append(("GitHub", links["github"]))
    if links["linkedin"].startswith("http"):
        social.append(("LinkedIn", links["linkedin"]))
    else:
        social.append(("LinkedIn — TODO", "#contact"))

    social_html = join(
        f'<li><a class="hero__social" href="{esc(href)}"'
        f'{" target=_blank rel=noopener" if href.startswith("http") else ""}>'
        f"{esc(label)}</a></li>"
        for label, href in social
    )

    resume_flag = (
        '<span class="todo todo--inline">résumé PDF not added yet</span>'
        if is_todo(site.get("resumeNote", ""))
        else ""
    )

    return f"""
<header class="hero" id="top">
  <div class="hero__stage" aria-hidden="true">
    <div class="hero__fallback">
      {picture(
        "hero-rain",
        "",
        sizes="100vw",
        cls="hero__fallback-img",
        priority=True,
        blur_up=True,
      )}
    </div>
    <canvas class="hero__canvas" data-focus-field data-sources='{sources}'></canvas>
    <div class="hero__scrim"></div>
    <div class="hero__grain"></div>
  </div>

  <div class="hero__inner shell">
    <div class="hero__top">
      {status}
      <div class="hero__top-right">
        <p class="hero__hint">
          <span class="hero__hint-pointer" aria-hidden="true"></span>
          <span data-hero-hint>Move to focus</span>
        </p>
        <p class="hero__caption">
          <span class="hero__caption-rule" aria-hidden="true"></span>
          Photograph mine — UD campus, in the rain.
        </p>
      </div>
    </div>

    <h1 class="hero__name">
      <span class="sr-only">{esc(site['name'])}</span>
      <span aria-hidden="true">{name_lines}</span>
    </h1>

    <div class="hero__body">
      <p class="hero__role">
        <span class="hero__role-main">{esc(site['role'])}</span>
        <span class="hero__role-sub">{esc(site['discipline'])}</span>
      </p>

      <p class="hero__statement">{headline}</p>

      <p class="hero__positioning">{esc(site['positioning'])}</p>
    </div>

    <div class="hero__foot">
      <div class="hero__actions">
        <a class="btn btn--primary btn--lg" href="#work" data-magnetic>
          <span>View selected work</span>
          <svg class="btn__arrow" viewBox="0 0 12 12" aria-hidden="true" focusable="false">
            <path d="M6 1.5 V10 M2.5 6.5 L6 10.2 L9.5 6.5" fill="none"
                  stroke="currentColor" stroke-width="1.5" stroke-linecap="square"/>
          </svg>
        </a>
        <a class="btn btn--lg" href="{esc(links['resume'])}" data-magnetic>
          <span>Résumé</span>{resume_flag}
        </a>
        <a class="btn btn--ghost btn--lg" href="mailto:{esc(site['email'])}" data-magnetic>
          <span>{esc(site['email'])}</span>
        </a>
      </div>
      <ul class="hero__socials">{social_html}</ul>
    </div>
  </div>

</header>
"""
