#!/usr/bin/env python3
"""
HNS UNITED — homepage generator.
Builds index.html from products-data.js + the shared header/footer partials.
Run this whenever js/products-data.js changes.
"""
import re, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://hns-united-store.vercel.app"

# Load product data
with open(os.path.join(ROOT, 'js', 'products-data.js')) as f:
    js_data = f.read()

products_match = re.search(r'window\.HNS_PRODUCTS\s*=\s*(\[.*?\]);', js_data, re.DOTALL)
def js_to_json(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)  # strip JS block comments
    s = re.sub(r'(?<=[{,\s])(\w+)(?=\s*:)', r'"\1"', s)
    s = re.sub(r',(\s*[\]}])', r'\1', s)
    return s
products = json.loads(js_to_json(products_match.group(1)))

# Load partials
with open(os.path.join(ROOT, 'js', '_header_partial.html')) as f:
    HEADER = f.read().replace('{{HOME_PATH}}', '#').replace('{{LOGO_PATH}}', 'images/logo.webp')

with open(os.path.join(ROOT, 'js', '_footer_partial.html')) as f:
    FOOTER = f.read().replace('{{LOGO_PATH}}', 'images/logo.webp').replace('{{HOME_PATH}}', '#')

with open(os.path.join(ROOT, 'js', '_modals_partial.html')) as f:
    MODALS = f.read()

# Read original site JS for inline blocks
original_path = '/home/claude/original.html'
if os.path.exists(original_path):
    with open(original_path) as f:
        orig = f.read()
    site_js_m = re.search(r'<script>\s*/\* ── Front / Back Toggle ── \*/(.*?)</script>', orig, re.DOTALL)
    SITE_JS_INLINE = site_js_m.group(1).strip() if site_js_m else ''
    # Extract existing CSS (between <style> and </style>)
    css_m = re.search(r'<style>(.*?)</style>', orig, re.DOTALL)
    SITE_CSS = css_m.group(1) if css_m else ''
else:
    SITE_JS_INLINE = ''
    SITE_CSS = open(os.path.join(ROOT, 'css', 'base.css')).read()

def discount_pct(old, new):
    return round((1 - new/old) * 100)

def card_html(product):
    slug = product['slug']
    name = product['name']
    price = product['price']
    price_old = product['priceOld']
    badges = product['badges']
    img_front = product['images'][0]
    discount = discount_pct(price_old, price)

    # discount badge
    badge_html = f'<span class="discount-badge">{discount}% OFF</span>'
    # extra badge (Bestseller etc)
    for b in badges:
        badge_html += f'<span class="badge">{b}</span>'

    # Card: NO view-toggle, NO img-back (front image only on homepage)
    card = f'''    <div class="card" data-cat="national" data-search="{product['searchTerms']}" data-href="product/{slug}/">
      <div class="card-img-wrap">{badge_html}<img class="img-front" src="images/products/{img_front}" alt="{name}" loading="lazy" width="900" height="900"></div>
      <div class="card-body">
        <p class="card-tag">{product['tag']}</p>
        <p class="card-name">{name}</p>
        <button class="size-guide-link" onclick="openSizeModal()">📏 Size Guide</button>
        <div class="card-opts">
          <select class="opt-size" aria-label="Select size"><option value="S">S</option><option value="M">M</option><option value="L">L</option><option value="XL">XL</option><option value="XXL" disabled>X̶X̶L̶ (Out of Stock)</option></select>
          <div class="qty">
            <button type="button" class="qty-btn" onclick="adjustQty(this,-1)" aria-label="Decrease quantity">&#8722;</button>
            <span class="qty-val">1</span>
            <button type="button" class="qty-btn" onclick="adjustQty(this,1)" aria-label="Increase quantity">&#43;</button>
          </div>
        </div>
        <div class="addr-wrap">
          <textarea class="addr-input" rows="2" placeholder="Your delivery address..."></textarea>
        </div>
        <div class="card-footer">
          <div class="card-price"><span class="price-old">&#8377;{price_old:,}</span>&#8377;{price:,} <span>all incl.</span></div>
          <a class="order-btn" href="#" data-jersey="{name}" onclick="return orderJersey(this)">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            Order Now
          </a>
        </div>
      </div>
    </div>'''
    return card

# Build grid HTML
cards_html = '\n'.join(card_html(p) for p in products)

# JSON-LD
org_jsonld = json.dumps({
    "@context": "https://schema.org/",
    "@type": "SportingGoodsStore",
    "name": "HNS United",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/images/logo.webp",
    "telephone": "+91-94444-73545",
    "address": {"@type": "PostalAddress", "addressLocality": "Chennai", "addressCountry": "IN"},
    "sameAs": ["https://instagram.com/hns_united"]
}, indent=2)

itemlist_jsonld = json.dumps({
    "@context": "https://schema.org/",
    "@type": "ItemList",
    "itemListElement": [{"@type":"ListItem","position":i+1,"url":f"{SITE_URL}/product/{p['slug']}/"} for i,p in enumerate(products)]
}, indent=2)

# Read the existing working index.html as the base HTML shell (it has all existing sections: hero, about, why, contact, footer)
# We just replace the card grid section
existing_index = os.path.join(ROOT, 'index.html')
if os.path.exists(existing_index):
    with open(existing_index) as f:
        base_html = f.read()
    
    # Replace the card grid content between <div class="grid" id="jersey-grid"> and </div>
    # followed by the no-results paragraph
    grid_pattern = re.compile(
        r'(<div class="grid" id="jersey-grid">)(.*?)(\s*</div>\s*<p class="no-results")',
        re.DOTALL
    )
    new_html = grid_pattern.sub(
        r'\1\n' + cards_html + r'\n  \3',
        base_html
    )
    
    # Update JSON-LD blocks
    new_html = re.sub(
        r'<script type="application/ld\+json">\s*\{[^<]*"ItemList"[^<]*\}[^<]*</script>',
        f'<script type="application/ld+json">\n{itemlist_jsonld}\n</script>',
        new_html,
        flags=re.DOTALL
    )
    
    # Update products-data.js reference (already there, just verify)
    if 'js/products-data.js' not in new_html:
        new_html = new_html.replace('<script src="js/analytics.js">', 
                                    '<script src="js/products-data.js"></script>\n<script src="js/analytics.js">')
    
    print(f"Updated existing index.html grid ({len(products)} products)")
else:
    print("ERROR: No existing index.html to update")
    exit(1)

with open(existing_index, 'w') as f:
    f.write(new_html)

print("Homepage written:", existing_index)

# Regenerate sitemap
urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/product/{p['slug']}/" for p in products]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    priority = "1.0" if u == f"{SITE_URL}/" else "0.8"
    sitemap += f'  <url>\n    <loc>{u}</loc>\n    <priority>{priority}</priority>\n  </url>\n'
sitemap += '</urlset>\n'
with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
    f.write(sitemap)
print(f"sitemap.xml written with {len(urls)} URLs")
