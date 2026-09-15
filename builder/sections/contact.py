"""Contact and footer.

The email address is the largest interactive element on the site, and the phone
number sits beside it at the same weight. Both are plain mailto/tel links: no
reveal, no form, no copy-to-clipboard puzzle. On a phone the number dials.
"""

from __future__ import annotations

from ..render import esc, join


def _tel(phone: str) -> str:
    """A tel: href keeps only the digits and a leading +."""
    digits = "".join(c for c in phone if c.isdigit())
    return "tel:+" + digits if phone.strip().startswith("+") else "tel:" + digits


def _big_link(href: str, label: str, value: str) -> str:
    return f"""
    <a class="contact__line-link" href="{esc(href)}" data-magnetic>
      <span class="contact__link-label">{esc(label)}</span>
      <span class="contact__link-value">{esc(value)}</span>
      <span class="contact__link-rule" aria-hidden="true"></span>
    </a>"""


def render(site: dict, contact: dict) -> str:
    headline = join(
        f'<span class="contact__line" style="--i:{i}">{esc(line)}</span>'
        for i, line in enumerate(contact["headline"])
    )

    links = [_big_link(f"mailto:{site['email']}", contact["emailLabel"], site["email"])]
    if site.get("showPhone") and site.get("phone"):
        links.append(_big_link(_tel(site["phone"]), "Or call", site["phone"]))

    return f"""
<section class="section section--contact" id="contact" aria-labelledby="contact-title">
  <div class="shell">
    <p class="eyebrow"><span class="eyebrow__index">07</span><span>{esc(contact['eyebrow'])}</span></p>
    <h2 class="contact__headline" id="contact-title">{headline}</h2>
    <p class="contact__body">{esc(contact['body'])}</p>

    <div class="contact__links">{join(links)}</div>

    <p class="contact__availability">
      <span class="hero__status-dot" aria-hidden="true"></span>
      {esc(contact['availability'])}
    </p>
  </div>
</section>
"""


def render_footer(site: dict) -> str:
    return f"""
<footer class="footer">
  <div class="shell footer__inner">
    <p class="footer__copy">© <span data-year>2026</span> {esc(site['name'])} · {esc(site['location'])}</p>
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
