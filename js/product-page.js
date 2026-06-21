/* ════════════════════════════════════════════════════
   HNS UNITED — PRODUCT PAGE LOGIC
   Size selection, quantity, WhatsApp order message,
   and related products rendering.
   ════════════════════════════════════════════════════ */

(function() {
  const root = document.querySelector('[data-product-slug]');
  if (!root) return;
  const slug = root.dataset.productSlug;
  const product = window.HNS_PRODUCTS.find(p => p.slug === slug);
  if (!product) return;

  let selectedSize = null;
  let qty = 1;

  /* ── Size selection (remembered via sessionStorage per product) ── */
  const sizeButtons = Array.from(document.querySelectorAll('.size-opt'));
  const storageKey = 'hns_size_' + slug;

  function selectSize(btn, silent) {
    if (btn.classList.contains('disabled')) return;
    sizeButtons.forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedSize = btn.dataset.size;
    try { sessionStorage.setItem(storageKey, selectedSize); } catch (e) {}
    if (!silent) {
      hnsTrackEvent('size_selection', { product_name: product.name, size: selectedSize });
    }
  }

  sizeButtons.forEach(btn => {
    btn.addEventListener('click', () => selectSize(btn));
  });

  /* Restore remembered size, else default to first available */
  (function restoreSize() {
    let remembered = null;
    try { remembered = sessionStorage.getItem(storageKey); } catch (e) {}
    const target = sizeButtons.find(b => b.dataset.size === remembered && !b.classList.contains('disabled'))
      || sizeButtons.find(b => !b.classList.contains('disabled'));
    if (target) selectSize(target, true);
  })();

  /* ── Quantity ── */
  const qtyValEl = document.querySelector('.pi-qty-val');
  const qtyMinus = document.querySelector('.pi-qty .qty-minus');
  const qtyPlus = document.querySelector('.pi-qty .qty-plus');

  function setQty(v) {
    qty = Math.max(1, Math.min(99, v));
    if (qtyValEl) qtyValEl.textContent = qty;
  }
  if (qtyMinus) qtyMinus.addEventListener('click', () => setQty(qty - 1));
  if (qtyPlus) qtyPlus.addEventListener('click', () => setQty(qty + 1));

  /* ── WhatsApp order ── */
  const ctaBtn = document.querySelector('.pi-cta');
  if (ctaBtn) {
    ctaBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const addrEl = document.querySelector('.pi-addr textarea');
      const address = addrEl ? addrEl.value.trim() : '';
      const total = product.price * qty;
      const productUrl = window.HNS_SITE_URL + '/product/' + product.slug + '/';

      const message =
        'Hi HNS UNITED,\n\n' +
        'I would like to order:\n\n' +
        'Product: ' + product.name + '\n' +
        'Selected Size: ' + (selectedSize || '-') + '\n' +
        'Quantity: ' + qty + '\n' +
        'Price: ₹' + product.price + ' each (Total: ₹' + total + ')\n' +
        'Address: ' + (address || '(will share)') + '\n' +
        'Payment: COD / GPay\n\n' +
        'Product Link: ' + productUrl + '\n' +
        'Website: ' + window.HNS_SITE_URL + '\n\n' +
        'Please confirm my order. Thank you!';

      hnsTrackEvent('order_whatsapp_click', {
        product_name: product.name,
        selling_price: product.price,
        current_page: hnsGetCurrentPage(),
        timestamp: new Date().toISOString(),
        device_type: hnsGetDeviceType()
      });

      const encoded = encodeURIComponent(message);
      window.open('https://wa.me/' + window.HNS_WHATSAPP_NUMBER + '?text=' + encoded, '_blank');
      if (typeof showToast === 'function') {
        showToast('✅ Opening WhatsApp — your order is ready to send!');
      }
    });
  }

  /* ── Related products: same category, excluding current, max 4 ── */
  const relatedGrid = document.querySelector('.related-grid');
  if (relatedGrid) {
    const pool = window.HNS_PRODUCTS.filter(p => p.slug !== product.slug);
    const sameCategory = pool.filter(p => p.category === product.category);
    const rest = pool.filter(p => p.category !== product.category);
    const related = sameCategory.concat(rest).slice(0, 4);

    relatedGrid.innerHTML = related.map(p => {
      const discount = Math.round((1 - p.price / p.priceOld) * 100);
      return `
        <a class="related-card" href="../${p.slug}/" data-slug="${p.slug}">
          <div class="related-img">
            <img src="../../images/products/${p.images[0]}" alt="${p.name}" loading="lazy" width="600" height="800">
          </div>
          <div class="related-body">
            <p class="related-tag">${p.tag}</p>
            <p class="related-name">${p.name}</p>
            <div class="related-price"><span class="old">₹${p.priceOld.toLocaleString('en-IN')}</span>₹${p.price.toLocaleString('en-IN')} <span style="font-size:10px;color:var(--grey)">(${discount}% OFF)</span></div>
          </div>
        </a>`;
    }).join('');
  }

  /* ── Product page view event ── */
  hnsTrackEvent('product_page_view', {
    product_name: product.name,
    price: product.price,
    category: product.category
  });
})();
