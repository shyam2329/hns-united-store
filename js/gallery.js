/* ════════════════════════════════════════════════════
   HNS UNITED — PRODUCT GALLERY
   Hand-built carousel (no external library): mouse drag,
   touch swipe, arrow nav, thumbnails, click-to-zoom (desktop),
   pinch-to-zoom (mobile), lazy loading, slide/fade transitions.
   ════════════════════════════════════════════════════ */

function initGallery(rootEl) {
  const track = rootEl.querySelector('.gallery-track');
  const slides = Array.from(rootEl.querySelectorAll('.gallery-slide'));
  const dotsWrap = rootEl.querySelector('.gallery-dots');
  const prevBtn = rootEl.querySelector('.gallery-arrow.prev');
  const nextBtn = rootEl.querySelector('.gallery-arrow.next');
  const thumbBtns = Array.from(document.querySelectorAll('.gallery-thumb'));
  const mainEl = rootEl;

  let current = 0;
  let isDragging = false;
  let startX = 0;
  let currentTranslate = 0;
  let prevTranslate = 0;
  let widthPx = rootEl.offsetWidth;

  function update(animate) {
    widthPx = rootEl.offsetWidth;
    track.classList.toggle('dragging', !animate);
    track.style.transform = `translateX(${-current * widthPx}px)`;
    slides.forEach((s, i) => s.classList.toggle('is-active', i === current));
    if (dotsWrap) {
      Array.from(dotsWrap.children).forEach((d, i) => d.classList.toggle('active', i === current));
    }
    thumbBtns.forEach((t, i) => t.classList.toggle('active', i === current));
    if (prevBtn) prevBtn.disabled = false;
    if (nextBtn) nextBtn.disabled = false;
    currentTranslate = -current * widthPx;
    prevTranslate = currentTranslate;
  }

  function goTo(index, opts) {
    const from = current;
    current = (index + slides.length) % slides.length;
    update(true);
    if (opts && opts.silent) return;
    if (from !== current) {
      hnsTrackEvent('product_image_swipe', { from_index: from, to_index: current });
    }
  }

  function next() { goTo(current + 1); }
  function prev() { goTo(current - 1); }

  if (nextBtn) nextBtn.addEventListener('click', next);
  if (prevBtn) prevBtn.addEventListener('click', prev);

  /* Thumbnails */
  thumbBtns.forEach((thumb, i) => {
    thumb.addEventListener('click', () => {
      goTo(i);
      hnsTrackEvent('thumbnail_click', { index: i });
    });
  });

  /* ── Mouse drag (desktop) ── */
  function dragStart(x) {
    isDragging = true;
    startX = x;
    track.classList.add('dragging');
  }
  function dragMove(x) {
    if (!isDragging) return;
    const delta = x - startX;
    track.style.transform = `translateX(${prevTranslate + delta}px)`;
  }
  function dragEnd(x) {
    if (!isDragging) return;
    isDragging = false;
    track.classList.remove('dragging');
    const delta = x - startX;
    const threshold = widthPx * 0.18;
    if (delta < -threshold) next();
    else if (delta > threshold) prev();
    else update(true);
  }

  mainEl.addEventListener('mousedown', (e) => { if (mainEl.classList.contains('zoomed')) return; dragStart(e.clientX); });
  window.addEventListener('mousemove', (e) => dragMove(e.clientX));
  window.addEventListener('mouseup', (e) => dragEnd(e.clientX));

  /* ── Touch swipe (mobile) + pinch zoom ── */
  let pinchStartDist = 0;
  let isPinching = false;
  const activeImg = () => slides[current].querySelector('img');

  function dist(touches) {
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.hypot(dx, dy);
  }

  mainEl.addEventListener('touchstart', (e) => {
    if (e.touches.length === 2) {
      isPinching = true;
      pinchStartDist = dist(e.touches);
    } else if (e.touches.length === 1 && !mainEl.classList.contains('zoomed')) {
      dragStart(e.touches[0].clientX);
    }
  }, { passive: true });

  mainEl.addEventListener('touchmove', (e) => {
    if (isPinching && e.touches.length === 2) {
      const scale = dist(e.touches) / pinchStartDist;
      const img = activeImg();
      if (img) img.style.transform = `scale(${Math.max(1, Math.min(scale, 3))})`;
    } else if (e.touches.length === 1 && isDragging) {
      dragMove(e.touches[0].clientX);
    }
  }, { passive: true });

  mainEl.addEventListener('touchend', (e) => {
    if (isPinching) {
      isPinching = false;
      const img = activeImg();
      if (img) {
        const currentScale = img.style.transform;
        if (currentScale && currentScale !== 'scale(1)') {
          hnsTrackEvent('image_zoom', { method: 'pinch', index: current });
        }
        setTimeout(() => { img.style.transform = ''; }, 1500);
      }
      return;
    }
    dragEnd(e.changedTouches[0].clientX);
  });

  /* ── Click-to-zoom (desktop) ── */
  mainEl.addEventListener('click', (e) => {
    if (isDragging) return;
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      const wasZoomed = mainEl.classList.contains('zoomed');
      mainEl.classList.toggle('zoomed');
      if (!wasZoomed) {
        hnsTrackEvent('image_zoom', { method: 'click', index: current });
        const rect = mainEl.getBoundingClientRect();
        const xPct = ((e.clientX - rect.left) / rect.width) * 100;
        const yPct = ((e.clientY - rect.top) / rect.height) * 100;
        activeImg().style.transformOrigin = `${xPct}% ${yPct}%`;
        activeImg().style.transform = 'scale(2.2)';
      } else {
        activeImg().style.transform = '';
      }
    }
  });

  /* ── Keyboard support ── */
  rootEl.setAttribute('tabindex', '0');
  rootEl.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') prev();
  });

  window.addEventListener('resize', () => update(false));

  update(false);
}

document.addEventListener('DOMContentLoaded', function() {
  const galleries = document.querySelectorAll('.gallery-main');
  galleries.forEach(initGallery);
});
