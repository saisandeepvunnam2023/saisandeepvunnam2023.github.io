/**
 * Focus Field — the hero interaction.
 *
 * One photograph, held at three resolutions at once. The page opens as a coarse,
 * desaturated mosaic; the pointer acts as a focal plane, and inside it the image
 * resolves to finer detail and then to full colour. Noise becomes signal, which
 * is the argument the whole site is making.
 *
 * Why Canvas 2D and not WebGL:
 *   The effect is three composited draws. A shader would do the same work, plus
 *   a context, a program, uniforms, and a fallback path for machines without
 *   WebGL. Performance was the requirement, not the technology, so this uses the
 *   cheapest thing that produces the effect.
 *
 * Cost per frame: one full-canvas blit of a pre-baked layer, plus a handful of
 * operations inside a ~520px square around the pointer. Everything expensive —
 * the downsampling, the desaturation, the mosaic — happens once per resize, not
 * once per frame.
 *
 * It stops entirely when the tab is hidden or the hero scrolls away, and it
 * never starts under prefers-reduced-motion.
 */

const BASE_DIVISOR = 30;   // coarse mosaic: canvas width / 30
const MID_DIVISOR = 9;     // mid mosaic
const FOCUS_BOX = 520;     // px square the focus work happens inside
const CORE_RATIO = 0.3;    // sharp core, as a fraction of the focus box
const MAX_DPR = 1.4;       // sharpness past this is invisible and costs fill rate
const EASE = 0.12;         // pointer follow

const INK = [11, 12, 13];

export function init(canvas, { reducedMotion = false } = {}) {
  const hero = canvas.closest('.hero');
  const hint = document.querySelector('[data-hero-hint]');

  let sources;
  try {
    sources = JSON.parse(canvas.dataset.sources);
  } catch {
    return null;
  }

  const ctx = canvas.getContext('2d', { alpha: false });
  if (!ctx) return null;

  // --- state -------------------------------------------------------------
  let image = null;
  let W = 0;
  let H = 0;
  let dpr = 1;
  let baseLayer = null;   // coarse mosaic, desaturated + darkened
  let midLayer = null;    // finer mosaic, lightly desaturated
  let focusPad = null;    // scratch canvas for the mid-resolution reveal
  let corePad = null;     // scratch canvas for the sharp core

  let px = 0;
  let py = 0;
  let tx = 0;
  let ty = 0;
  let pointerSeen = false;
  let running = false;
  let frame = 0;
  let visible = true;
  let inView = true;
  let t0 = performance.now();

  // --- layer baking ------------------------------------------------------

  function makeCanvas(w, h) {
    const c = document.createElement('canvas');
    c.width = Math.max(1, Math.round(w));
    c.height = Math.max(1, Math.round(h));
    return c;
  }

  /** Cover-fit source rectangle for drawing `img` into a W x H box. */
  function cover(img, w, h) {
    const scale = Math.max(w / img.width, h / img.height);
    const sw = w / scale;
    const sh = h / scale;
    return {
      sx: (img.width - sw) / 2,
      sy: (img.height - sh) / 2,
      sw,
      sh,
    };
  }

  /**
   * Downscale to `w/divisor`, then blow it back up with smoothing off. That is
   * what produces real pixel blocks rather than a blur — the image is genuinely
   * carrying less information, which is the point.
   */
  function bakeMosaic(divisor, { desaturate, darken }) {
    const small = makeCanvas(W / divisor, H / divisor);
    const sctx = small.getContext('2d');
    const { sx, sy, sw, sh } = cover(image, small.width, small.height);
    sctx.drawImage(image, sx, sy, sw, sh, 0, 0, small.width, small.height);

    const out = makeCanvas(W, H);
    const octx = out.getContext('2d', { alpha: false });
    octx.imageSmoothingEnabled = false;
    octx.drawImage(small, 0, 0, small.width, small.height, 0, 0, W, H);

    if (desaturate > 0) {
      octx.globalCompositeOperation = 'saturation';
      octx.globalAlpha = desaturate;
      octx.fillStyle = 'hsl(0,0%,50%)';
      octx.fillRect(0, 0, W, H);
      octx.globalCompositeOperation = 'source-over';
      octx.globalAlpha = 1;
    }

    if (darken > 0) {
      octx.fillStyle = `rgba(${INK[0]},${INK[1]},${INK[2]},${darken})`;
      octx.fillRect(0, 0, W, H);
    }

    return out;
  }

  function build() {
    if (!image) return;

    const rect = hero.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    W = Math.max(1, Math.round(rect.width * dpr));
    H = Math.max(1, Math.round(rect.height * dpr));

    canvas.width = W;
    canvas.height = H;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    baseLayer = bakeMosaic(BASE_DIVISOR, { desaturate: 0.85, darken: 0.5 });
    midLayer = bakeMosaic(MID_DIVISOR, { desaturate: 0.45, darken: 0.34 });

    const box = Math.round(FOCUS_BOX * dpr);
    focusPad = makeCanvas(box, box);
    corePad = makeCanvas(box, box);

    if (!pointerSeen) {
      px = tx = W * 0.32;
      py = ty = H * 0.55;
    }

    draw(px, py);
  }

  // --- drawing -----------------------------------------------------------

  /**
   * Feather a scratch canvas to a soft disc. destination-in keeps only what the
   * gradient covers, which is how a hard clip becomes a lens falloff.
   */
  function feather(pad, pctx, inner, outer) {
    const c = pad.width / 2;
    const g = pctx.createRadialGradient(c, c, inner, c, c, outer);
    g.addColorStop(0, 'rgba(0,0,0,1)');
    g.addColorStop(0.72, 'rgba(0,0,0,0.92)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    pctx.globalCompositeOperation = 'destination-in';
    pctx.fillStyle = g;
    pctx.fillRect(0, 0, pad.width, pad.height);
    pctx.globalCompositeOperation = 'source-over';
  }

  function draw(x, y) {
    if (!baseLayer) return;

    ctx.drawImage(baseLayer, 0, 0);

    const box = focusPad.width;
    const half = box / 2;
    const ox = Math.round(x - half);
    const oy = Math.round(y - half);

    // Mid-resolution ring.
    const fctx = focusPad.getContext('2d');
    fctx.clearRect(0, 0, box, box);
    fctx.drawImage(midLayer, ox, oy, box, box, 0, 0, box, box);
    feather(focusPad, fctx, half * 0.1, half * 0.96);
    ctx.drawImage(focusPad, ox, oy);

    // Sharp core, drawn from the full-resolution decode.
    const core = box * CORE_RATIO;
    const cctx = corePad.getContext('2d');
    cctx.clearRect(0, 0, box, box);

    const { sx, sy, sw, sh } = cover(image, W, H);
    const scaleX = sw / W;
    const scaleY = sh / H;
    cctx.imageSmoothingEnabled = true;
    cctx.imageSmoothingQuality = 'high';
    cctx.drawImage(
      image,
      sx + ox * scaleX,
      sy + oy * scaleY,
      box * scaleX,
      box * scaleY,
      0,
      0,
      box,
      box,
    );
    cctx.fillStyle = `rgba(${INK[0]},${INK[1]},${INK[2]},0.14)`;
    cctx.fillRect(0, 0, box, box);
    feather(corePad, cctx, core * 0.42, core);
    ctx.drawImage(corePad, ox, oy);

    // A single hairline at the focal boundary. The only overtly optical
    // element on the page, and it is one stroke.
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, core * 1.02, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,74,36,0.30)';
    ctx.lineWidth = Math.max(1, dpr);
    ctx.stroke();
    ctx.restore();
  }

  // --- loop --------------------------------------------------------------

  function tick(now) {
    if (!running) return;

    if (!pointerSeen) {
      // Idle drift, so the effect is legible before anyone touches anything —
      // and so it works at all on a device with no pointer.
      const t = (now - t0) / 1000;
      tx = W * (0.42 + Math.sin(t * 0.34) * 0.26);
      ty = H * (0.52 + Math.cos(t * 0.23) * 0.2);
    }

    px += (tx - px) * EASE;
    py += (ty - py) * EASE;

    draw(px, py);
    frame = requestAnimationFrame(tick);
  }

  function start() {
    if (running || reducedMotion) return;
    running = true;
    t0 = performance.now();
    frame = requestAnimationFrame(tick);
  }

  function stop() {
    running = false;
    cancelAnimationFrame(frame);
  }

  function sync() {
    if (visible && inView) start();
    else stop();
  }

  // --- input -------------------------------------------------------------

  function setTargetFromEvent(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    tx = (clientX - rect.left) * dpr;
    ty = (clientY - rect.top) * dpr;
    if (!pointerSeen) {
      pointerSeen = true;
      hint?.parentElement?.classList.add('is-done');
    }
  }

  const onPointerMove = (e) => setTargetFromEvent(e.clientX, e.clientY);

  const onTouchMove = (e) => {
    const t = e.touches[0];
    if (t) setTargetFromEvent(t.clientX, t.clientY);
  };

  // --- lifecycle ---------------------------------------------------------

  function chooseSource() {
    const want = window.innerWidth * Math.min(window.devicePixelRatio || 1, MAX_DPR);
    const i = sources.widths.findIndex((w) => w >= want);
    const idx = i === -1 ? sources.widths.length - 1 : i;
    // AVIF where supported, JPEG otherwise. The <picture> in the markup has
    // already warmed whichever one this browser picked, so this is a cache hit.
    return { avif: sources.avif[idx], jpg: sources.jpg[idx] };
  }

  function load() {
    const { avif, jpg } = chooseSource();
    const img = new Image();
    img.decoding = 'async';

    img.onload = () => {
      image = img;
      build();
      canvas.classList.add('is-live');
      hero.classList.add('has-canvas');
      if (reducedMotion) {
        // One static, resolved frame. No loop, no drift, nothing moving.
        draw(W * 0.34, H * 0.52);
      } else {
        sync();
      }
    };

    img.onerror = () => {
      if (img.src.endsWith('.avif')) img.src = jpg;
    };

    img.src = avif;
  }

  let resizeTimer;
  const onResize = () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      build();
      if (reducedMotion) draw(W * 0.34, H * 0.52);
    }, 180);
  };

  document.addEventListener('visibilitychange', () => {
    visible = !document.hidden;
    sync();
  });

  if (!reducedMotion) {
    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: true });

    const io = new IntersectionObserver(
      ([entry]) => {
        inView = entry.isIntersecting;
        sync();
      },
      { threshold: 0 },
    );
    io.observe(hero);
  }

  window.addEventListener('resize', onResize, { passive: true });

  load();

  return { start, stop };
}
