"""Persistent compact navigation.

Renders as a normal <nav> with real links, so it works with JavaScript off and
reads correctly to a screen reader. JS only adds the condensed scrolled state,
the scroll-progress line and the mobile panel.
"""

from __future__ import annotations

from ..render import esc, join


def render(site: dict, base: str = "", active: str | None = None) -> str:
    links = site["links"]
    resume = f"{base}{links['resume']}"

    items = join(
        f'<li><a class="nav__link" href="{base if item["href"].startswith("#") and base else ""}'
        f'{esc(item["href"])}" data-nav-link>'
        f'<span class="nav__index">{esc(item["index"])}</span>'
        f'<span class="nav__label">{esc(item["label"])}</span></a></li>'
        for item in site["nav"]
    )

    home = f"{base}index.html" if base else "#top"

    resume_btn = ""
    if site.get("showResume"):
        resume_btn = f'''<a class="btn btn--primary btn--sm" href="{esc(resume)}" data-magnetic>
        <span>Résumé</span>
        <svg class="btn__arrow" viewBox="0 0 12 12" aria-hidden="true" focusable="false">
          <path d="M6 1.5 V9 M2.8 6 L6 9.3 L9.2 6 M2 10.5 H10" fill="none"
                stroke="currentColor" stroke-width="1.4" stroke-linecap="square"/>
        </svg>
      </a>'''

    panel_resume = (
        f'<a class="btn btn--primary" href="{esc(resume)}"><span>Résumé</span></a>'
        if site.get("showResume")
        else ""
    )

    return f"""
<nav class="nav" id="nav" aria-label="Primary">
  <div class="nav__bar">
    <a class="nav__brand" href="{esc(home)}" aria-label="{esc(site['name'])} — home">
      <span class="nav__mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" focusable="false">
          <circle cx="12" cy="12" r="9.2" stroke="currentColor" stroke-width="1.4"/>
          <circle cx="12" cy="12" r="3.4" fill="currentColor"/>
        </svg>
      </span>
      <span class="nav__name">
        <span class="nav__name-full">{esc(site['name'])}</span>
        <span class="nav__name-short" aria-hidden="true">SSV</span>
      </span>
    </a>

    <ul class="nav__list">{items}</ul>

    <div class="nav__actions">
      {resume_btn}
      <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="nav-panel">
        <span class="nav__toggle-lines" aria-hidden="true"><i></i><i></i></span>
        <span class="sr-only">Menu</span>
      </button>
    </div>
  </div>
  <div class="nav__progress" aria-hidden="true"><i data-scroll-progress></i></div>
</nav>

<div class="nav-panel" id="nav-panel" hidden>
  <ul class="nav-panel__list">
    {join(
        f'<li><a href="{base if item["href"].startswith("#") and base else ""}{esc(item["href"])}">'
        f'<span class="nav-panel__index">{esc(item["index"])}</span>'
        f'<span>{esc(item["label"])}</span></a></li>'
        for item in site["nav"]
    )}
  </ul>
  <div class="nav-panel__foot">
    {panel_resume}
    <a class="btn btn--primary" href="mailto:{esc(site['email'])}"><span>Email</span></a>
  </div>
</div>
"""
