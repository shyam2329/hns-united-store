#!/usr/bin/env python3
"""
HNS UNITED — static site generator.
Builds:
  /index.html                          (homepage, cards link to /product/<slug>/)
  /product/<slug>/index.html           (one real page per product, unique SEO)
Run this whenever js/products-data.js changes — no other coding required
to add a new product (per the "Future Scalability" requirement).
"""
import json
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Load product data (parse the JS array literal as JSON-ish) ──
with open(os.path.join(ROOT, 'js', 'products-data.js')) as f:
    js_data = f.read()

products_match = re.search(r'window\.HNS_PRODUCTS\s*=\s*(\[.*?\]);', js_data, re.DOTALL)
products_js = products_match.group(1)
# Convert JS object literal to valid JSON: quote unquoted keys, strip trailing commas
def js_to_json(s):
    s = re.sub(r'(?<=[{,\s])(\w+)(?=\s*:)', r'"\1"', s)
    s = re.sub(r',(\s*[\]}])', r'\1', s)
    return s

products = json.loads(js_to_json(products_js))

SITE_URL = "https://hns-united-store.vercel.app"
WHATSAPP = "919444473545"

with open(os.path.join(ROOT, 'js', '_header_partial.html')) as f:
    HEADER_PARTIAL = f.read()
with open(os.path.join(ROOT, 'js', '_modals_partial.html')) as f:
    MODALS_PARTIAL = f.read()
with open(os.path.join(ROOT, 'js', '_footer_partial.html')) as f:
    FOOTER_PARTIAL = f.read()


def render_header(home_path, logo_path):
    return HEADER_PARTIAL.replace('{{HOME_PATH}}', home_path).replace('{{LOGO_PATH}}', logo_path)


def render_footer(logo_path, home_path):
    return FOOTER_PARTIAL.replace('{{LOGO_PATH}}', logo_path).replace('{{HOME_PATH}}', home_path)


def discount_pct(old, new):
    return round((1 - new / old) * 100)


def badge_html(badges):
    out = []
    for b in badges:
        out.append(f'<span class="pi-badge gold">{b}</span>')
    out.append('<span class="pi-badge outline">Embroidery</span>')
    return '\n          '.join(out)


def size_html(product):
    sizes = product.get('sizes', None) or DEFAULT_SIZES
    out = []
    for s in sizes:
        cls = 'size-opt' + ('' if s['available'] else ' disabled')
        disabled_attr = ' aria-disabled="true"' if not s['available'] else ''
        out.append(f'<button type="button" class="{cls}" data-size="{s["label"]}"{disabled_attr}>{s["label"]}</button>')
    return '\n          '.join(out)


DEFAULT_SIZES = [
    {"label": "S", "available": True},
    {"label": "M", "available": True},
    {"label": "L", "available": True},
    {"label": "XL", "available": True},
    {"label": "XXL", "available": False},
]


def features_html():
    feats = [
        ("Premium Embroidery", "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"),
        ("Breathable Fabric", "M3 12h18M3 6h18M3 18h18"),
        ("Match Quality", "M5 13l4 4L19 7"),
        ("Comfortable Fit", "M12 2a5 5 0 015 5v2a5 5 0 01-10 0V7a5 5 0 015-5z"),
        ("Cash on Delivery", "M3 10h18M7 15h2m4 0h4M5 6h14a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2z"),
        ("GPay Accepted", "M5 13l4 4L19 7"),
        ("Fast Shipping", "M3 8l4-5h6l4 5M3 8h18M3 8v9a2 2 0 002 2h14a2 2 0 002-2V8"),
    ]
    out = []
    for label, path in feats:
        out.append(
            f'<div class="pi-feature"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{path}"/></svg>{label}</div>'
        )
    return '\n          '.join(out)


def jsonld_product(product, canonical):
    discount = discount_pct(product['priceOld'], product['price'])
    data = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product['name'],
        "image": [f"{SITE_URL}/images/products/{img}" for img in product['images']],
        "description": f"{product['name']} — {', '.join(product['description'][:3])}. Premium quality football jersey from HNS UNITED.",
        "sku": product['slug'],
        "brand": {"@type": "Brand", "name": "HNS UNITED"},
        "offers": {
            "@type": "Offer",
            "url": canonical,
            "priceCurrency": "INR",
            "price": str(product['price']),
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition"
        }
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def breadcrumb_jsonld(product, canonical):
    data = {
        "@context": "https://schema.org/",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Collection", "item": SITE_URL + "/#shop"},
            {"@type": "ListItem", "position": 3, "name": product['name'], "item": canonical},
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


PRODUCT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2THLNQHP78"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-2THLNQHP78');
</script>

<script type="text/javascript">
(function(c,l,a,r,i,t,y){{
    c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
}})(window, document, "clarity", "script", "xam6nb5lqj");
</script>

<title>{title}</title>
<meta name="description" content="{meta_description}">
<link rel="canonical" href="{canonical}">

<!-- Open Graph -->
<meta property="og:type" content="product">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{meta_description}">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="HNS United">
<meta property="product:price:amount" content="{price}">
<meta property="product:price:currency" content="INR">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{meta_description}">
<meta name="twitter:image" content="{og_image}">

<!-- Structured data -->
<script type="application/ld+json">
{jsonld}
</script>
<script type="application/ld+json">
{breadcrumb_jsonld}
</script>

<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="../../images/products/{hero_image}">
<link rel="stylesheet" href="../../css/base.css">
<link rel="stylesheet" href="../../css/product.css">
</head>
<body>

{header}

{modals}

<main class="product-main" data-product-slug="{slug}">
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="../../index.html">Home</a><span class="sep">/</span>
    <a href="../../index.html#shop">Collection</a><span class="sep">/</span>
    <span class="current">{name}</span>
  </nav>

  <div class="product-grid">
    <div class="gallery">
      <div class="gallery-main" aria-roledescription="carousel" aria-label="{name} image gallery">
        <button class="gallery-arrow prev" aria-label="Previous image">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <div class="gallery-track">
          {slides}
        </div>
        <button class="gallery-arrow next" aria-label="Next image">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M9 18l6-6-6-6"/></svg>
        </button>
        <div class="gallery-badges">
          <span class="discount-badge" style="position:static">{discount}% OFF</span>
        </div>
        <div class="gallery-dots">{dots}</div>
        <span class="zoom-hint">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          Click to zoom
        </span>
      </div>
      <div class="gallery-thumbs" role="tablist" aria-label="Select image">
        {thumbs}
      </div>
    </div>

    <div class="product-info">
      <p class="pi-tag">{tag}</p>
      <h1 class="pi-name">{name}</h1>
      <div class="pi-badges">
          {badges}
      </div>

      <div class="pi-price-row">
        <span class="pi-price-old">&#8377;{price_old}</span>
        <span class="pi-price-new">&#8377;{price}</span>
        <span class="pi-discount">{discount}% OFF</span>
      </div>
      <p class="pi-incl">all inclusive &middot; taxes included</p>

      <div class="pi-features">
          {features}
      </div>

      <div class="pi-size-row">
        <p class="pi-label"><span>Select Size</span> <a href="#" class="size-guide-link" onclick="openSizeModal();return false;">Size Guide</a></p>
        <div class="size-grid">
          {sizes}
        </div>
      </div>

      <div class="pi-qty-row">
        <p class="pi-label" style="margin-bottom:0">Quantity</p>
        <div class="pi-qty">
          <button type="button" class="qty-minus" aria-label="Decrease quantity">&#8722;</button>
          <span class="pi-qty-val">1</span>
          <button type="button" class="qty-plus" aria-label="Increase quantity">&#43;</button>
        </div>
      </div>

      <div class="pi-addr">
        <p class="pi-label">Delivery Address</p>
        <textarea rows="2" placeholder="Your delivery address..."></textarea>
      </div>

      <a href="#" class="pi-cta">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Order on WhatsApp
      </a>
      <div class="pi-trust">
        <span>&#10003; Cash on Delivery</span>
        <span>&#10003; GPay Accepted</span>
        <span>&#10003; Fast Shipping</span>
      </div>

      <div class="delivery-card">
        <h3>Delivery &amp; Guarantee</h3>
        <div class="delivery-list">
          <div class="delivery-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            <div><strong>Ships within 24 Hours</strong><small>Orders confirmed before 6 PM ship same day</small></div>
          </div>
          <div class="delivery-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 8l4-5h6l4 5M3 8h18M3 8v9a2 2 0 002 2h14a2 2 0 002-2V8"/></svg>
            <div><strong>Estimated Delivery: 3–6 Days</strong><small>Across India via trusted courier partners</small></div>
          </div>
          <div class="delivery-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10h18M7 15h2m4 0h4M5 6h14a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2z"/></svg>
            <div><strong>Cash on Delivery Available</strong><small>Pay when your jersey arrives</small></div>
          </div>
          <div class="delivery-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
            <div><strong>Secure Packaging</strong><small>Folded &amp; sealed to prevent damage in transit</small></div>
          </div>
          <div class="delivery-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"/></svg>
            <div><strong>Premium Quality Guarantee</strong><small>Match-grade embroidery &amp; fabric, every order</small></div>
          </div>
        </div>
      </div>

      <div class="pi-desc">
        <h3>Product Details</h3>
        <ul>
          {description}
        </ul>
      </div>
    </div>
  </div>
</main>

<section class="related-section">
  <div class="related-hd">
    <p class="section-lbl">You May Also Like</p>
    <h2>Complete The Collection</h2>
  </div>
  <div class="related-grid"></div>
</section>

{footer}

<script src="../../js/products-data.js"></script>
<script>
function closeSizeModal(){{document.getElementById('size-modal').classList.remove('open');}}
function openSizeModal(){{document.getElementById('size-modal').classList.add('open');}}
document.getElementById('size-modal').addEventListener('click', function(e){{ if(e.target===this) closeSizeModal(); }});
function closePolicyModal(){{document.getElementById('policy-modal').classList.remove('open');}}
function openPolicyModal(){{document.getElementById('policy-modal').classList.add('open');}}
document.getElementById('policy-modal').addEventListener('click', function(e){{ if(e.target===this) closePolicyModal(); }});

const hamburger = document.getElementById('hamburger-btn');
const mobileNav = document.getElementById('mobile-nav');
const mobileClose = document.getElementById('mobile-nav-close');
hamburger.addEventListener('click', () => {{
  hamburger.classList.toggle('open');
  mobileNav.classList.toggle('open');
  document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
}});
mobileClose.addEventListener('click', () => {{
  hamburger.classList.remove('open');
  mobileNav.classList.remove('open');
  document.body.style.overflow = '';
}});
document.querySelectorAll('.mobile-link').forEach(link => {{
  link.addEventListener('click', () => {{
    hamburger.classList.remove('open');
    mobileNav.classList.remove('open');
    document.body.style.overflow = '';
  }});
}});
function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}}
/* Header search box on product pages: redirects to homepage with query */
const jSearch = document.getElementById('jersey-search');
if (jSearch) {{
  jSearch.addEventListener('keydown', function(e) {{
    if (e.key === 'Enter') {{
      window.location.href = '../../index.html?search=' + encodeURIComponent(this.value.trim());
    }}
  }});
}}
</script>
<script src="../../js/analytics.js"></script>
<script src="../../js/gallery.js"></script>
<script src="../../js/product-page.js"></script>
</body>
</html>
"""


def build_product_page(product, all_products):
    slug = product['slug']
    canonical = f"{SITE_URL}/product/{slug}/"
    discount = discount_pct(product['priceOld'], product['price'])
    hero_image = product['images'][0]
    og_image = f"{SITE_URL}/images/products/{hero_image}"

    title = f"{product['name']} | ₹{product['price']} | HNS United"
    og_title = f"{product['name']} – HNS United"
    meta_description = (
        f"Buy {product['name']} at ₹{product['price']} (was ₹{product['priceOld']}, {discount}% OFF). "
        f"{', '.join(product['description'][:2])}. Cash on Delivery & GPay accepted. Ships across India."
    )
    if len(meta_description) > 160:
        meta_description = meta_description[:157].rsplit(' ', 1)[0] + '...'

    slides = '\n          '.join(
        f'<div class="gallery-slide{" is-active" if i == 0 else ""}"><img src="../../images/products/{img}" '
        f'alt="{product["name"]}{" – Back" if i == 1 else ""}" loading="{"eager" if i == 0 else "lazy"}" '
        f'width="900" height="1200"></div>'
        for i, img in enumerate(product['images'])
    )
    dots = ''.join(f'<span class="{"active" if i == 0 else ""}"></span>' for i in range(len(product['images'])))
    thumbs = '\n          '.join(
        f'<button type="button" class="gallery-thumb{" active" if i == 0 else ""}" role="tab" '
        f'aria-label="View image {i+1}"><img src="../../images/products/{img}" alt="" loading="lazy" width="200" height="266"></button>'
        for i, img in enumerate(product['images'])
    )

    description_html = '\n          '.join(f'<li>{d}</li>' for d in product['description'])

    html = PRODUCT_TEMPLATE.format(
        title=title,
        meta_description=meta_description,
        canonical=canonical,
        og_title=og_title,
        og_image=og_image,
        price=product['price'],
        jsonld=jsonld_product(product, canonical),
        breadcrumb_jsonld=breadcrumb_jsonld(product, canonical),
        hero_image=hero_image,
        header=render_header('../../index.html', '../../images/logo.webp'),
        modals=MODALS_PARTIAL,
        slug=slug,
        name=product['name'],
        slides=slides,
        discount=discount,
        dots=dots,
        thumbs=thumbs,
        tag=product['tag'],
        badges=badge_html(product['badges']),
        price_old=f"{product['priceOld']:,}",
        features=features_html(),
        sizes=size_html(product),
        description=description_html,
        footer=render_footer('../../images/logo.webp', '../../index.html'),
    )

    out_dir = os.path.join(ROOT, 'product', slug)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'index.html'), 'w') as f:
        f.write(html)
    return canonical


if __name__ == '__main__':
    for p in products:
        url = build_product_page(p, products)
        print("Built:", url)
