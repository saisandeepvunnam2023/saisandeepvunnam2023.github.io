/**
 * Skills readout.
 *
 * Mirrors the detail of whatever technology you are pointing at into the large
 * readout beneath the columns, and dims the rest so the eye lands.
 *
 * It is a mirror, nothing more. Every technology's name, description and
 * project link are already in the DOM beside it — this module only changes
 * where a sighted pointer user sees them. Turn JavaScript off, or open the page
 * on a phone, and that same markup renders inline as a plain readable list.
 * That is why the readout is aria-hidden: a screen reader gets the real thing.
 *
 * One listener on the container rather than 26 on the names.
 */

export function init(root) {
  const readout = root.querySelector('[data-readout]');
  if (!readout) return null;

  const hint = readout.querySelector('[data-readout-hint]');
  const body = readout.querySelector('[data-readout-body]');
  const nameEl = readout.querySelector('[data-readout-name]');
  const useEl = readout.querySelector('[data-readout-use]');
  const whereEl = readout.querySelector('[data-readout-where]');

  let current = null;

  function show(el) {
    if (el === current) return;

    current?.classList.remove('is-active');
    el.classList.add('is-active');
    current = el;

    root.classList.add('is-active');
    hint.hidden = true;
    body.hidden = false;

    nameEl.textContent = el.textContent.trim();
    useEl.textContent = el.dataset.use || '';

    const where = el.dataset.where;
    if (where) {
      whereEl.textContent = where;
      whereEl.href = el.dataset.href;
      whereEl.hidden = false;
    } else {
      whereEl.hidden = true;
    }
  }

  // Delegated: the names are plain spans, so there is nothing to tab through
  // and nothing extra in the accessibility tree.
  root.addEventListener('pointerover', (e) => {
    const el = e.target.closest('[data-tech]');
    if (el) show(el);
  });

  // The last thing pointed at stays in the readout. Clearing it on every exit
  // makes the panel flicker as the pointer crosses gaps between names.
  root.addEventListener('pointerleave', () => {
    current?.classList.remove('is-active');
    current = null;
    root.classList.remove('is-active');
  });

  return { show };
}
