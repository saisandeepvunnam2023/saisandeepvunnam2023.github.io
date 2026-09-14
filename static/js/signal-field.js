/**
 * Signal Field — the skills visualisation.
 *
 * Four capabilities on the left, every technology on the right. Point at a
 * capability and the technologies that serve it light up, with a hairline drawn
 * to each one. The lines come from the same data as the list, so they can only
 * ever say something true.
 *
 * The layout underneath is a plain, complete, readable list. This module adds
 * emphasis and connectors to it and nothing else — it never hides a node, never
 * removes one from the DOM, and never becomes the only route to the information.
 * With JavaScript off you lose the lines and keep the content.
 */

export function init(field, { reducedMotion = false } = {}) {
  const svg = field.querySelector('[data-wires]');
  const caps = [...field.querySelectorAll('[data-cap]:not(.node):not(.node-group)')];
  const nodes = [...field.querySelectorAll('.node')];
  const groups = [...field.querySelectorAll('.node-group')];
  const resetBtn = field.querySelector('[data-cap-reset]');

  if (!svg || !caps.length) return null;

  let active = null;
  let pinned = null;
  let raf = 0;

  // --- geometry ----------------------------------------------------------

  function rel(el) {
    const a = el.getBoundingClientRect();
    const b = field.getBoundingClientRect();
    return { x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height };
  }

  function drawWires(id) {
    const cap = caps.find((c) => c.dataset.cap === id);
    if (!cap) return;

    const lit = nodes.filter((n) => n.dataset.cap === id);
    const f = field.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${f.width} ${f.height}`);

    const from = rel(cap);
    const x1 = from.x + from.w;
    const y1 = from.y + from.h / 2;

    const paths = lit.map((node, i) => {
      const dot = node.querySelector('.node__dot') || node;
      const to = rel(dot);
      const x2 = to.x;
      const y2 = to.y + to.h / 2;
      const mid = x1 + (x2 - x1) * 0.55;
      const d = `M${x1.toFixed(1)} ${y1.toFixed(1)} C${mid.toFixed(1)} ${y1.toFixed(1)} ${mid.toFixed(1)} ${y2.toFixed(1)} ${x2.toFixed(1)} ${y2.toFixed(1)}`;
      return { d, i };
    });

    svg.innerHTML = paths
      .map(({ d, i }) => `<path d="${d}" style="--i:${i}"/>`)
      .join('');

    // Set each path's own length as the dash length so the draw-on animation
    // runs at a consistent speed regardless of how far the line travels.
    requestAnimationFrame(() => {
      svg.querySelectorAll('path').forEach((p) => {
        const len = reducedMotion ? 0 : p.getTotalLength();
        p.style.setProperty('--len', len.toFixed(1));
        p.classList.add('is-drawn');
      });
    });
  }

  function clearWires() {
    svg.innerHTML = '';
  }

  // --- state -------------------------------------------------------------

  function apply(id) {
    active = id;

    if (!id) {
      field.classList.remove('is-filtering');
      nodes.forEach((n) => n.classList.remove('is-lit'));
      groups.forEach((g) => g.classList.remove('is-lit'));
      caps.forEach((c) => c.setAttribute('aria-pressed', 'false'));
      clearWires();
      if (resetBtn) resetBtn.hidden = true;
      return;
    }

    field.classList.add('is-filtering');
    nodes.forEach((n) => n.classList.toggle('is-lit', n.dataset.cap === id));
    groups.forEach((g) => g.classList.toggle('is-lit', g.dataset.cap === id));
    caps.forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.cap === id)));
    drawWires(id);
    if (resetBtn) resetBtn.hidden = !pinned;
  }

  function redraw() {
    if (!active) return;
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => drawWires(active));
  }

  // --- events ------------------------------------------------------------

  caps.forEach((cap) => {
    const id = cap.dataset.cap;

    // Hover and keyboard focus preview; click pins, so touch and keyboard users
    // get the same behaviour without needing a hover they do not have.
    cap.addEventListener('pointerenter', () => {
      if (!pinned) apply(id);
    });
    cap.addEventListener('focus', () => {
      if (!pinned) apply(id);
    });
    cap.addEventListener('click', () => {
      pinned = pinned === id ? null : id;
      apply(pinned);
    });
  });

  field.addEventListener('pointerleave', () => {
    if (!pinned) apply(null);
  });

  field.addEventListener('focusout', (e) => {
    if (!pinned && !field.contains(e.relatedTarget)) apply(null);
  });

  resetBtn?.addEventListener('click', () => {
    pinned = null;
    apply(null);
  });

  // The capability column is sticky, so its position changes as the page
  // scrolls. Recompute only while a capability is active.
  window.addEventListener('scroll', redraw, { passive: true });
  window.addEventListener('resize', redraw, { passive: true });

  return { apply, destroy: () => apply(null) };
}
