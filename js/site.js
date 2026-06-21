/* ── Front / Back Toggle ── */
function switchView(btn, view) {
  var card = btn.closest('.card');
  var wrap = card.querySelector('.card-img-wrap');
  var front = wrap.querySelector('.img-front');
  var back  = wrap.querySelector('.img-back');
  card.querySelectorAll('.view-btn').forEach(function(b){ b.classList.remove('active'); });
  btn.classList.add('active');
  if (view === 'back') {
    front.classList.add('hidden');
    back.classList.add('visible');
  } else {
    front.classList.remove('hidden');
    back.classList.remove('visible');
  }
}

/* ── Hamburger / Mobile Nav ── */
const hamburger = document.getElementById('hamburger-btn');
const mobileNav = document.getElementById('mobile-nav');
const mobileClose = document.getElementById('mobile-nav-close');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  mobileNav.classList.toggle('open');
  document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
});

mobileClose.addEventListener('click', () => {
  hamburger.classList.remove('open');
  mobileNav.classList.remove('open');
  document.body.style.overflow = '';
});

document.querySelectorAll('.mobile-link').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('open');
    mobileNav.classList.remove('open');
    document.body.style.overflow = '';
  });
});

/* ── Size Modal ── */
function openSizeModal() {
  document.getElementById('size-modal').classList.add('open');
}
function closeSizeModal() {
  document.getElementById('size-modal').classList.remove('open');
}
document.getElementById('size-modal').addEventListener('click', function(e) {
  if(e.target === this) closeSizeModal();
});

/* ── Policy Modal ── */
function openPolicyModal() {
  document.getElementById('policy-modal').classList.add('open');
}
function closePolicyModal() {
  document.getElementById('policy-modal').classList.remove('open');
}
document.getElementById('policy-modal').addEventListener('click', function(e) {
  if(e.target === this) closePolicyModal();
});

/* ── Toast ── */
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

/* ── Filter / Search ── */
function filterCards(cat, btn) {
  document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('jersey-search').value = '';
  applyFilters(cat, '');
}

function applyFilters(cat, query) {
  let visible = 0;
  document.querySelectorAll('.card').forEach(c => {
    const matchesCat = cat === 'all' || c.dataset.cat === cat;
    const matchesSearch = !query || c.dataset.search.includes(query);
    const show = matchesCat && matchesSearch;
    c.classList.toggle('hidden', !show);
    if(show) visible++;
  });
  document.getElementById('no-results').classList.toggle('show', visible === 0);
}

function getActiveCat() {
  const active = document.querySelector('.fbtn.active');
  return active ? active.dataset.cat : 'all';
}

document.getElementById('jersey-search').addEventListener('input', function() {
  const query = this.value.trim().toLowerCase();
  applyFilters(getActiveCat(), query);
});

/* ── Qty ── */
function adjustQty(btn, delta) {
  const wrap = btn.parentElement;
  const span = wrap.querySelector('.qty-val');
  let val = parseInt(span.textContent, 10) + delta;
  if(val < 1) val = 1;
  if(val > 99) val = 99;
  span.textContent = val;
}

/* ── Order (single WhatsApp, inline address, price×qty in message) ── */
function orderJersey(link) {
  const card = link.closest('.card');
  const jerseyName = link.dataset.jersey;
  const size = card.querySelector('.opt-size').value;
  const qty = parseInt(card.querySelector('.qty-val').textContent, 10);
  const addrEl = card.querySelector('.addr-input');
  const address = addrEl ? addrEl.value.trim() : '';
  const total = 450 * qty;

  const message =
    'Hi HNS UNITED 👋\n' +
    'Jersey: ' + jerseyName + '\n' +
    'Size: ' + size + '\n' +
    'Quantity: ' + qty + '\n' +
    'Total: ₹' + total + '\n' +
    'Address: ' + (address || '(will share)') + '\n' +
    'Name: \n' +
    'Payment: COD / GPay\n\n' +
    'Please confirm my order. Thank you!';

  const encoded = encodeURIComponent(message);
  window.open('https://wa.me/919444473545?text=' + encoded, '_blank');
  showToast('✅ Opening WhatsApp — your order is ready to send!');
  return false;
}
