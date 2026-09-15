"""Architecture diagrams for the case studies.

Hand-authored inline SVG: no library, no raster, scales to any width, inherits
colour from the page, and carries a real title/desc for screen readers. Each one
shows the actual mechanism — where the data goes and where a human intervenes —
rather than decorating the page with boxes.
"""

from __future__ import annotations

STYLE = """
<style>
.dg{--ink:var(--fg);--dim:var(--fg-dim);--line:var(--rule-strong);--acc:var(--accent)}
.dg text{font-family:var(--font-mono);fill:var(--ink)}
.dg .t{font-size:11px;letter-spacing:.06em;text-transform:uppercase;fill:var(--dim)}
.dg .h{font-size:13.5px;font-weight:600;fill:var(--ink);font-family:var(--font-sans)}
.dg .s{font-size:11px;fill:var(--dim);font-family:var(--font-sans);letter-spacing:0;text-transform:none}
.dg .box{fill:none;stroke:var(--line);stroke-width:1}
.dg .box--acc{stroke:var(--acc)}
.dg .fill{fill:var(--surface-2)}
.dg .arrow{stroke:var(--line);stroke-width:1;fill:none}
.dg .arrow--acc{stroke:var(--acc)}
.dg .head{fill:var(--line)}
.dg .head--acc{fill:var(--acc)}
.dg .dash{stroke-dasharray:3 3}
</style>
"""

ARROW_DEFS = """
<defs>
  <marker id="dg-a" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0 0 L8 4 L0 8 z" class="head"/>
  </marker>
  <marker id="dg-b" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0 0 L8 4 L0 8 z" class="head--acc"/>
  </marker>
</defs>
"""


def _wrap(title: str, desc: str, view: str, body: str, uid: str = "dg") -> str:
    return (
        f'<figure class="diagram">'
        f'<svg class="dg" viewBox="{view}" role="img" preserveAspectRatio="xMidYMid meet" '
        f'aria-labelledby="{uid}-t {uid}-d">'
        f'<title id="{uid}-t">{title}</title><desc id="{uid}-d">{desc}</desc>'
        f"{STYLE}{ARROW_DEFS}{body}</svg>"
        f'<figcaption class="diagram__caption">{title}</figcaption>'
        f"</figure>"
    )


def _box(x, y, w, h, label, sub="", accent=False, dashed=False):
    """A labelled box. `sub` may contain newlines; each becomes its own tspan,
    because SVG text does not wrap and silently renders \\n as a space."""
    cls = "box box--acc" if accent else "box"
    if dashed:
        cls += " dash"

    lines = [s for s in str(sub).split("\n") if s] if sub else []
    if lines:
        block = len(lines) * 14
        head_y = y + (h - block) / 2 + 2
        sub_el = "".join(
            f'<text class="s" x="{x + 14}" y="{head_y + 16 + n * 14}">{line}</text>'
            for n, line in enumerate(lines)
        )
    else:
        head_y = y + h / 2 - 5
        sub_el = ""

    return (
        f'<rect class="fill" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
        f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
        f'<text class="h" x="{x + 14}" y="{head_y + 5}">{label}</text>{sub_el}'
    )


def _arrow(x1, y1, x2, y2, accent=False):
    cls = "arrow--acc" if accent else "arrow"
    marker = "dg-b" if accent else "dg-a"
    return f'<path class="arrow {cls}" d="M{x1} {y1} L{x2} {y2}" marker-end="url(#{marker})"/>'


# --------------------------------------------------------------------------

def magazine() -> str:
    b = "".join([
        '<text class="t" x="0" y="16">Template layer, mine</text>',
        '<text class="t" x="300" y="16">Editor surface</text>',
        '<text class="t" x="600" y="16">Output</text>',

        _box(0, 30, 250, 60, "Issue template", "layout, regions, responsive rules"),
        _box(0, 106, 250, 60, "Structured data definition", "cover, features, departments, credits"),
        _box(0, 182, 250, 60, "Layout primitives", "shared CSS, no per-issue stylesheets"),

        _box(300, 78, 230, 90, "Issue entry", "constrained fields only,\nno free-form markup", accent=True),

        _box(600, 30, 240, 60, "Issue pages", "one document outline each"),
        _box(600, 106, 240, 60, "Responsive images", "one upload, every size"),
        _box(600, 182, 240, 60, "GA4 + WCAG AA", "measured and checked"),

        _arrow(250, 60, 296, 110),
        _arrow(250, 136, 296, 126),
        _arrow(250, 212, 296, 142),
        _arrow(530, 100, 596, 62, accent=True),
        _arrow(530, 123, 596, 136, accent=True),
        _arrow(530, 146, 596, 208, accent=True),
    ])
    return _wrap(
        "Magazine publishing architecture",
        "Template layer and structured data definitions on the left feed a constrained editor "
        "surface in the middle, which produces issue pages, responsive images and instrumented, "
        "accessible output on the right. Editors only ever touch the middle column.",
        "-4 0 848 252",
        b,
        uid="dg-mag",
    )


def pipeline() -> str:
    # SVG text does not wrap. Every sub-line below is kept under ~21 characters
    # so it cannot run outside its box at the width the box is drawn.
    stages = [
        ("Originals", "immutable,\nnever written to"),
        ("Normalise", "exposure + white\nbalance, from the\nhistogram"),
        ("Tone-map", "HDR across\nbracketed sets"),
        ("Frame", "content-aware crop,\nper ratio"),
        ("Emit", "responsive ladder,\nCMS naming"),
    ]
    W, GAP, TOP, H = 160, 12, 36, 88
    parts = ['<text class="t" x="0" y="16">Each stage independent and re-runnable</text>']
    x = 0
    for i, (label, sub) in enumerate(stages):
        accent = i in (1, 3)
        parts.append(_box(x, TOP, W, H, label, sub, accent=accent))
        if i < len(stages) - 1:
            parts.append(_arrow(x + W, TOP + H / 2, x + W + GAP, TOP + H / 2, accent=accent))
        x += W + GAP

    last = 4 * (W + GAP)
    parts.append(_box(W + GAP, 162, 3 * W + 2 * GAP, 46, "Derivative store",
                      "regenerate at will. a bad automated decision costs one re-run",
                      dashed=True))
    parts.append(_arrow(W + GAP + 76, TOP + H, W + GAP + 76, 158))
    parts.append(_arrow(last + 80, TOP + H, last + 80, 185))
    parts.append(f'<path class="arrow dash" d="M{last + 80} 185 L{4 * W + 3 * GAP} 185"/>')
    return _wrap(
        "Image pipeline stages",
        "Five sequential stages: ingest of immutable originals, exposure and white balance "
        "normalisation, HDR tone mapping, content-aware framing, then emission of the responsive "
        "ladder. Every stage writes to a derivative store that can be regenerated, so originals "
        "are never modified.",
        "-4 0 872 220",
        parts_join(parts),
        uid="dg-pipe",
    )


def triage() -> str:
    signals = [
        ("Layout", "page structure, visually"),
        ("Text density", "substance, not stubs"),
        ("Visual freshness", "image classification"),
        ("Usage", "does anyone read it"),
    ]
    parts = ['<text class="t" x="0" y="16">Four independent signals</text>']
    y = 32
    for i, (label, sub) in enumerate(signals):
        parts.append(_box(0, y, 210, 52, label, sub))
        parts.append(_arrow(210, y + 26, 286, 140))
        y += 62

    parts.append(_box(290, 96, 190, 76, "Relevance score", "no single signal\ncan condemn a page", accent=True))
    parts.append(_arrow(480, 134, 526, 134, accent=True))
    parts.append(_box(530, 96, 180, 76, "Ranked list", "recommendation only"))
    parts.append(_arrow(710, 134, 756, 134))

    parts.append('<rect class="box box--acc" x="760" y="60" width="84" height="148" rx="2"/>')
    parts.append('<text class="h" x="774" y="120">Human</text>')
    parts.append('<text class="h" x="774" y="138">gate</text>')
    parts.append('<text class="s" x="774" y="160">deletion is</text>')
    parts.append('<text class="s" x="774" y="174">irreversible</text>')

    parts.append(_box(290, 200, 420, 44, "Audit record", "written at every step, reviewable months later", dashed=True))
    parts.append(_arrow(385, 172, 385, 196))
    parts.append(_arrow(620, 172, 620, 196))
    return _wrap(
        "Archive triage decision flow",
        "Four independent signals (layout, text density, visual freshness and usage) combine "
        "into a relevance score, which produces a ranked recommendation list. A human gate stands "
        "between the recommendation and any deletion, and an audit record is written at every step.",
        "-4 0 848 252",
        parts_join(parts),
        uid="dg-triage",
    )


def parts_join(parts) -> str:
    return "".join(parts)


DIAGRAMS = {"magazine": magazine, "pipeline": pipeline, "triage": triage}


def render(name: str) -> str:
    fn = DIAGRAMS.get(name)
    return fn() if fn else ""
