/**
 * Entry point.
 *
 * Small, and deliberately so. Everything here is progressive enhancement over
 * markup that already works: the page is complete, readable and navigable before
 * a byte of this runs.
 *
 * The skills readout is dynamically imported, and only when that section is near
 * the viewport on a device that can hover — nobody downloads it to read the hero.
 */

const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE_POINTER = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

/* -------------------------------------------------------------------------
   Navigation: condensed state, scroll progress, current section
   ---------------------------------------------------------------------- */

function initNav() {
  const nav = $('#nav');
  const progress = $('[data-scroll-progress]');
  if (!nav) return;

  let ticking = false;

  const update = () => {
    const y = window.scrollY;
    nav.classList.toggle('is-scrolled', y > 24);

    if (progress) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = max > 0 ? Math.min(1, y / max) : 0;
      progress.style.transform = `scaleX(${ratio.toFixed(4)})`;
    }
    ticking = false;
  };

  window.addEventListener(
    'scroll',
    () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    },
    { passive: true },
  );

  update();
}

function initCurrentSection() {
  const links = $$('[data-nav-link]').filter((a) => a.hash);
  const sections = links
    .map((a) => ({ link: a, el: document.getElementById(a.hash.slice(1)) }))
    .filter((x) => x.el);

  if (!sections.length || !('IntersectionObserver' in window)) return;

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const match = sections.find((s) => s.el === entry.target);
        if (!match) return;
        if (entry.isIntersecting) {
          links.forEach((l) => l.classList.remove('is-current'));
          match.link.classList.add('is-current');
        }
      });
    },
    { rootMargin: '-45% 0px -50% 0px' },
  );

  sections.forEach((s) => io.observe(s.el));
}

function initMobilePanel() {
  const toggle = $('.nav__toggle');
  const panel = $('#nav-panel');
  if (!toggle || !panel) return;

  const setOpen = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    panel.hidden = false;
    // Let `hidden` clear before the transition starts, so the panel animates
    // rather than snapping.
    requestAnimationFrame(() => panel.classList.toggle('is-open', open));
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) panel.querySelector('a')?.focus({ preventScroll: true });
    if (!open) setTimeout(() => { if (!panel.classList.contains('is-open')) panel.hidden = true; }, 320);
  };

  toggle.addEventListener('click', () => {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  panel.addEventListener('click', (e) => {
    if (e.target.closest('a')) setOpen(false);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });
}

/* -------------------------------------------------------------------------
   Reveals — one rise per block, then the observer lets go of it
   ---------------------------------------------------------------------- */

function initReveals() {
  const items = $$('[data-reveal]');
  if (!items.length) return;

  if (REDUCED || !('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('is-revealed'));
    return;
  }

  const io = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target); // done: stop paying for it
      });
    },
    { rootMargin: '0px 0px -12% 0px', threshold: 0.08 },
  );

  items.forEach((el) => io.observe(el));
}

/* -------------------------------------------------------------------------
   Magnetic buttons + cursor dot
   Pointer-device only, and skipped entirely under reduced motion.
   ---------------------------------------------------------------------- */

function initMagnetic() {
  if (!FINE_POINTER || REDUCED) return;

  const STRENGTH = 0.28;
  const MAX = 5;

  $$('[data-magnetic]').forEach((el) => {
    let raf = 0;

    const move = (e) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) * STRENGTH;
        const dy = (e.clientY - (r.top + r.height / 2)) * STRENGTH;
        const cx = Math.max(-MAX, Math.min(MAX, dx));
        const cy = Math.max(-MAX, Math.min(MAX, dy));
        el.style.transform = `translate3d(${cx.toFixed(2)}px, ${cy.toFixed(2)}px, 0)`;
      });
    };

    const reset = () => {
      cancelAnimationFrame(raf);
      el.style.transform = '';
    };

    el.addEventListener('pointermove', move);
    el.addEventListener('pointerleave', reset);
    el.addEventListener('blur', reset);
  });
}

function initCursor() {
  if (!FINE_POINTER || REDUCED) return;

  const dot = document.createElement('div');
  dot.className = 'cursor-dot';
  dot.setAttribute('aria-hidden', 'true');
  document.body.appendChild(dot);

  let x = 0;
  let y = 0;
  let raf = 0;

  window.addEventListener(
    'pointermove',
    (e) => {
      x = e.clientX;
      y = e.clientY;
      dot.classList.add('is-active');
      const interactive = e.target.closest('a, button, summary, [data-magnetic]');
      dot.classList.toggle('is-over-link', Boolean(interactive));

      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        dot.style.translate = `${x}px ${y}px`;
      });
    },
    { passive: true },
  );

  document.addEventListener('pointerleave', () => dot.classList.remove('is-active'));
}

/* -------------------------------------------------------------------------
   Lazy module loading
   ---------------------------------------------------------------------- */

function initSkills() {
  const root = $('[data-skills]');
  if (!root || !('IntersectionObserver' in window)) return;

  // The readout only exists on pointer devices; on touch the detail is already
  // rendered inline, so there is nothing for this module to do.
  if (!FINE_POINTER) return;

  const io = new IntersectionObserver(
    (entries, observer) => {
      if (!entries[0].isIntersecting) return;
      observer.disconnect();
      import('./skills.js').then((m) => m.init(root)).catch(() => {});
    },
    { rootMargin: '300px' },
  );

  io.observe(root);
}

/* -------------------------------------------------------------------------
   Odds
   ---------------------------------------------------------------------- */

function initYear() {
  $$('[data-year]').forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
}

/* ---------------------------------------------------------------------- */

function boot() {
  initNav();
  initCurrentSection();
  initMobilePanel();
  initReveals();
  initMagnetic();
  initCursor();
  initYear();
  initSkills();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot, { once: true });
} else {
  boot();
}
