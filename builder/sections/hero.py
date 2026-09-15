"""The hero.

The photograph is shown plainly behind the type, graded only enough that the
headline stays legible over it.

Everything a recruiter needs — name, role, location, availability, work, GitHub,
LinkedIn — is real HTML in this section, so it survives with JavaScript off.
"""

from __future__ import annotations

from ..render import esc, is_todo, join, picture


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

    resume_btn = ""
    if site.get("showResume"):
        resume_btn = (
            f'<a class="btn btn--lg" href="{esc(links["resume"])}" data-magnetic>'
            f"<span>Résumé</span></a>"
        )

    return f"""
<header class="hero" id="top">
  <div class="hero__stage" aria-hidden="true">
    <div class="hero__photo">
      {picture(
        "hero-rain",
        "",
        sizes="100vw",
        cls="hero__photo-img",
        priority=True,
        blur_up=True,
      )}
    </div>
    <div class="hero__scrim"></div>
    <div class="hero__grain"></div>
  </div>

  <div class="hero__inner shell">
    <div class="hero__top">
      {status}
      <div class="hero__top-right">
        <p class="hero__caption">
          <span class="hero__caption-rule" aria-hidden="true"></span>
          Photograph mine. UD campus, in the rain.
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
        {resume_btn}
        <a class="btn btn--ghost btn--lg" href="mailto:{esc(site['email'])}" data-magnetic>
          <span>{esc(site['email'])}</span>
        </a>
      </div>
    </div>
  </div>

</header>
"""
