/* ════════════════════════════════════════════════════
   HNS UNITED — ANALYTICS & TRACKING (GA4 + Microsoft Clarity)
   Shared by homepage and every product page.
   Same hnsTrackEvent/hnsGetDeviceType helpers as the live site —
   only extended with new events, nothing renamed or removed.
   ════════════════════════════════════════════════════ */

/* ── Helper: detect device type ── */
function hnsGetDeviceType() {
  const ua = navigator.userAgent;
  if (/tablet|ipad/i.test(ua)) return 'Tablet';
  if (/mobile|android|iphone/i.test(ua)) return 'Mobile';
  return 'Desktop';
}

/* ── Helper: get current page label ── */
function hnsGetCurrentPage() {
  const path = window.location.pathname.split('/').filter(Boolean).pop();
  if (!path || path === 'index.html') return 'Home Page';
  return path;
}

/* ── Helper: safely push event to GA4 + Clarity ── */
function hnsTrackEvent(eventName, params) {
  try {
    if (typeof gtag === 'function') {
      gtag('event', eventName, params || {});
    }
    if (window.clarity) {
      window.clarity('event', eventName);
    }
  } catch (e) { /* fail silently, never block site functionality */ }
}

/* ── Helper: extract product info from a .card element (homepage grid) ── */
function hnsGetProductInfo(cardEl) {
  if (!cardEl) return { name: '', price: '', category: '' };
  const nameEl = cardEl.querySelector('.card-name');
  const priceEl = cardEl.querySelector('.card-price');
  const tagEl = cardEl.querySelector('.card-tag');
  const name = nameEl ? nameEl.textContent.trim() : '';
  let price = '';
  if (priceEl) {
    const clone = priceEl.cloneNode(true);
    const oldEl = clone.querySelector('.price-old');
    if (oldEl) oldEl.remove();
    price = clone.textContent.trim().split(' ')[0];
  }
  const category = tagEl ? tagEl.textContent.trim() : (cardEl.dataset.cat || '');
  return { name: name, price: price, category: category };
}

/* ── 1. PRODUCT CARD CLICK + PRODUCT VIEW (homepage grid) ──
   Viewport-visibility tracking, same pattern as before ── */
(function hnsSetupProductViewTracking() {
  if (!('IntersectionObserver' in window)) return;
  const seen = new WeakSet();
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting && !seen.has(entry.target)) {
        seen.add(entry.target);
        const info = hnsGetProductInfo(entry.target);
        hnsTrackEvent('product_view', {
          product_name: info.name,
          price: info.price,
          category: info.category
        });
      }
    });
  }, { threshold: 0.4 });

  function attach() {
    document.querySelectorAll('.card').forEach(function(card) {
      observer.observe(card);
    });
  }
  if (document.readyState === 'complete' || document.readyState === 'interactive') attach();
  else document.addEventListener('DOMContentLoaded', attach);
})();

/* ── 2. BUTTON CLICK TRACKING (delegated, document-wide) ── */
document.addEventListener('click', function(e) {
  const orderBtn = e.target.closest('.order-btn, .pi-cta');
  if (orderBtn) {
    hnsTrackEvent('button_click', { button_name: 'Order Now' });
  }
  const viewBtn = e.target.closest('.view-btn');
  if (viewBtn) {
    hnsTrackEvent('button_click', { button_name: 'View Product (Front/Back Toggle)' });
  }
  const filterBtn = e.target.closest('.fbtn');
  if (filterBtn) {
    hnsTrackEvent('button_click', { button_name: 'Category Filter', category: filterBtn.dataset.cat || '' });
  }
  const sizeGuideBtn = e.target.closest('.size-guide-link');
  if (sizeGuideBtn) {
    hnsTrackEvent('button_click', { button_name: 'Size Guide' });
  }
  /* Product card click → navigates to product page */
  const productCard = e.target.closest('.card[data-href]');
  if (productCard && !e.target.closest('a,button,select,input,textarea,.view-toggle')) {
    const name = productCard.querySelector('.card-name');
    hnsTrackEvent('product_card_click', {
      product_name: name ? name.textContent.trim() : '',
      destination: productCard.dataset.href
    });
    window.location.href = productCard.dataset.href;
    return;
  }
  /* Related product click (product pages) */
  const relatedCard = e.target.closest('.related-card');
  if (relatedCard) {
    const name = relatedCard.querySelector('.related-name');
    hnsTrackEvent('related_product_click', {
      product_name: name ? name.textContent.trim() : '',
      destination: relatedCard.getAttribute('href')
    });
  }
  /* Breadcrumb back navigation */
  const crumb = e.target.closest('.breadcrumb a');
  if (crumb) {
    hnsTrackEvent('back_navigation', { from: hnsGetCurrentPage(), to: crumb.getAttribute('href') });
  }
  /* External link clicks (WhatsApp, Instagram, tel:) */
  const link = e.target.closest('a[href]');
  if (link) {
    const href = link.getAttribute('href');
    const isExternal = /^https?:\/\//.test(href) && !href.includes(window.location.hostname);
    const isTel = href.startsWith('tel:');
    const isWa = href.includes('wa.me');
    if (isExternal || isTel) {
      hnsTrackEvent('external_link_click', { url: href, type: isWa ? 'whatsapp' : (isTel ? 'phone' : 'external') });
    }
  }
});

/* ── Search tracking ── */
(function hnsSetupSearchTracking() {
  const searchInput = document.getElementById('jersey-search');
  if (!searchInput) return;
  let debounceTimer;
  searchInput.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const query = this.value.trim();
    debounceTimer = setTimeout(function() {
      if (query.length > 0) {
        hnsTrackEvent('button_click', { button_name: 'Search', search_term: query });
      }
    }, 600);
  });
})();

/* ── 3. WHATSAPP ORDER CLICK TRACKING (wraps orderJersey, never edits it) ── */
(function hnsWrapOrderJersey() {
  function wrap() {
    if (typeof window.orderJersey !== 'function' || window.orderJersey.__hnsWrapped) return;
    const originalOrderJersey = window.orderJersey;
    const wrapped = function(link) {
      try {
        const card = link.closest('.card') || document;
        const info = hnsGetProductInfo(card);
        const priceEl = card.querySelector ? card.querySelector('.pi-price-new, .card-price') : null;
        hnsTrackEvent('order_whatsapp_click', {
          product_name: info.name || (link.dataset.jersey || ''),
          selling_price: info.price || (priceEl ? priceEl.textContent.trim() : ''),
          current_page: hnsGetCurrentPage(),
          timestamp: new Date().toISOString(),
          device_type: hnsGetDeviceType()
        });
      } catch (e) { /* never block the order flow */ }
      return originalOrderJersey.apply(this, arguments);
    };
    wrapped.__hnsWrapped = true;
    window.orderJersey = wrapped;
  }
  wrap();
  document.addEventListener('DOMContentLoaded', wrap);
})();

/* ── 4. SCROLL DEPTH TRACKING (25 / 50 / 75 / 100%) ── */
(function hnsSetupScrollDepth() {
  const milestones = [25, 50, 75, 100];
  const fired = {};
  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? Math.round((scrollTop / docHeight) * 100) : 0;
      milestones.forEach(function(m) {
        if (pct >= m && !fired[m]) {
          fired[m] = true;
          hnsTrackEvent('scroll_depth', { depth_percent: m, page: hnsGetCurrentPage() });
        }
      });
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
})();

/* ── 5. TIME ON PAGE / SESSION DURATION ── */
(function hnsSetupTimeOnPage() {
  const startTime = Date.now();
  let sent = false;
  function sendDuration() {
    if (sent) return;
    sent = true;
    const seconds = Math.round((Date.now() - startTime) / 1000);
    hnsTrackEvent('time_on_page', { seconds: seconds, page: hnsGetCurrentPage() });
    hnsTrackEvent('session_duration', { seconds: seconds });
  }
  window.addEventListener('pagehide', sendDuration);
  document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'hidden') sendDuration();
  });
})();

/* ── 6. RETURNING VISITOR DETECTION ── */
(function hnsSetupReturningVisitor() {
  try {
    const key = 'hns_visited';
    const hasVisited = localStorage.getItem(key);
    hnsTrackEvent(hasVisited ? 'returning_visitor' : 'new_visitor', { page: hnsGetCurrentPage() });
    localStorage.setItem(key, '1');
  } catch (e) { /* localStorage unavailable (private mode etc.) — skip silently */ }
})();

/* ── 7. PAGE VIEW / LANDING PAGE / EXIT PAGE ── */
(function hnsSetupPageViewMeta() {
  hnsTrackEvent('page_view_extended', {
    page: hnsGetCurrentPage(),
    device_type: hnsGetDeviceType(),
    referrer: document.referrer || '(direct)'
  });
  try {
    if (!sessionStorage.getItem('hns_landing_set')) {
      sessionStorage.setItem('hns_landing_page', hnsGetCurrentPage());
      sessionStorage.setItem('hns_landing_set', '1');
    }
  } catch (e) {}
  window.addEventListener('pagehide', function() {
    hnsTrackEvent('exit_page', { page: hnsGetCurrentPage() });
  });
})();

/* GA4's automatic page_view, device/browser/country/city, traffic source,
   bounce rate and engagement are all captured natively by gtag.js with no
   extra code required — these fire via the existing gtag('config', ...) call. */
