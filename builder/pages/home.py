"""The home page: every section, in the order a recruiter should meet them."""

from __future__ import annotations

from ..layout import document, head, person_schema
from ..render import esc, join, preload_srcset
from ..sections import about, contact, experience, frames, hero, nav, skills, work


def render(*, site, projects, skills_data, exp, story, css, scripts) -> str:
    meta = site["meta"]

    body = join([
        nav.render(site),
        hero.render(site),
        '<main id="main">',
        work.render(projects),
        skills.render(skills_data, projects),
        experience.render(exp),
        frames.render(story["photography"]),
        about.render_about(story["about"], story["notes"]),
        about.render_playground(story["playground"]),
        contact.render(site, story["contact"]),
        "</main>",
        contact.render_footer(site),
    ])

    return document(
        head_html=head(
            site=site,
            css=css,
            title=meta["title"],
            description=meta["description"],
            canonical=meta["siteUrl"] + "/",
            base="",
            schema=person_schema(site, projects),
            preload_image=preload_srcset("hero-rain"),
        ),
        body=body,
        base="",
        scripts=scripts,
    )
