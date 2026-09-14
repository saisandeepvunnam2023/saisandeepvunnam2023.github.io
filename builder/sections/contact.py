"""Contact and footer.

The email address is the loudest element on the page and is a real mailto link,
not a click-to-reveal. Résumé, GitHub and LinkedIn sit beside it, which is the
fourth place on the site the résumé appears.
"""

from __future__ import annotations

from ..render import esc, is_todo, join


def render(site: dict, contact: dict) -> str:
    links = site["links"]
    headline = join(
        f'<span class="contact__line" style="--i:{i}">{esc(line)}</span>'
        for i, line in enumerate(contact["headline"])
    )

    rows = [("Résumé", links["resume"]), ("GitHub", links["github"])]
    if links["linkedin"].startswith("http"):
        rows.append(("LinkedIn", links["linkedin"]))
    else:
        rows.append(("LinkedIn", None))
    if site.get("showPhone"):
        rows.append(("Phone", f"tel:{site['phone'].replace(' ', '').replace('(', '').replace(')', '').replace('-', '')}"))

    row_html = join(
        (
            f'<li class="channel"><a href="{esc(href)}"'
            f'{" target=_blank rel=noopener" if str(href).startswith("http") else ""} data-magnetic>'
            f'<span class="channel__label">{esc(label)}</span>'
            f'<span class="channel__arrow" aria-hidden="true">→</span></a></li>'
            if href
            else f'<li class="channel channel--todo"><span class="channel__inner">'
            f'<span class="channel__label">{esc(label)}</span>'
            f'<span class="todo">add URL in content/site.json</span></span></li>'
        )
        for label, href in rows
    )

    return f"""
<section class="section section--contact" id="contact" aria-labelledby="contact-title">
  <div class="shell">
    <p class="eyebrow"><span class="eyebrow__index">07</span><span>{esc(contact['eyebrow'])}</span></p>
    <h2 class="contact__headline" id="contact-title">{headline}</h2>
    <p class="contact__body">{esc(contact['body'])}</p>

    <a class="contact__email" href="mailto:{esc(site['email'])}" data-magnetic>
      <span class="contact__email-label">{esc(contact['emailLabel'])}</span>
      <span class="contact__email-address">{esc(site['email'])}</span>
      <span class="contact__email-rule" aria-hidden="true"></span>
    </a>

    <p class="contact__availability">
      <span class="hero__status-dot" aria-hidden="true"></span>
      {esc(contact['availability'])}
    </p>

    <ul class="channels">{row_html}</ul>
  </div>
</section>
"""


def render_footer(site: dict) -> str:
    footer = site["footer"]
    return f"""
<footer class="footer">
  <div class="shell footer__inner">
    <p class="footer__copy">© <span data-year>2026</span> {esc(site['name'])} · {esc(site['location'])}</p>
    <p class="footer__signoff">{esc(footer['signoff'])}</p>
    <p class="footer__colophon">{esc(footer['colophon'])}</p>
    <a class="footer__top" href="#top" data-magnetic>
      <span>Back to top</span>
      <svg viewBox="0 0 12 12" aria-hidden="true" focusable="false">
        <path d="M6 10 V2 M2.5 5.5 L6 2 L9.5 5.5" fill="none" stroke="currentColor"
              stroke-width="1.4" stroke-linecap="square"/>
      </svg>
    </a>
  </div>
</footer>
"""
