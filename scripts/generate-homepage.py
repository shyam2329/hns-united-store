#!/usr/bin/env python3
"""
HNS UNITED — homepage generator.
Takes the original single-file index.html (with inline base64 images and
inline scripts) and produces the optimized homepage:
  - base64 product images -> external /images/products/*.jpg files
  - inline site-logic script -> external js/site.js (byte-identical)
  - inline analytics script -> external js/analytics.js (extended)
  - each .card gets data-href="/product/<slug>/" for navigation
  - JSON-LD ItemList + Organization structured data added to <head>
No existing visual markup, CSS, copy, or card internals are altered.
"""
import re
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL = "/home/claude/original.html"
SITE_URL = "https://hns-united-store.vercel.app"

SLUGS = [
    'argentina-away', 'portugal-home', 'portugal-away', 'brazil-away',
    'spain-away', 'argentina-home-set', 'brazil-home-set', 'portugal-black-gold'
]

with open(ORIGINAL) as f:
    content = f.read()

# ── 1. Split into cards, replace each card's base64 images with file refs,
#       and tag the card with data-href for navigation ──
parts = content.split('<div class="card" data-cat=')
head_part = parts[0]
card_parts = parts[1:]

assert len(card_parts) == len(SLUGS), f"Expected {len(SLUGS)} cards, found {len(card_parts)}"

rebuilt_cards = []
for slug, card_body in zip(SLUGS, card_parts):
    card = '<div class="card" data-cat=' + card_body

    # Replace front/back base64 images with external file refs
    def repl_front(m):
        return f'src="../images/products/{slug}-front.jpg"' if False else f'src="images/products/{slug}-front.jpg"'
    card = re.sub(
        r'class="img-front" src="data:image/jpeg;base64,[^"]+"',
        f'class="img-front" src="images/products/{slug}-front.jpg"',
        card, count=1
    )
    card = re.sub(
        r'class="img-back" src="data:image/jpeg;base64,[^"]+"',
        f'class="img-back" src="images/products/{slug}-back.jpg"',
        card, count=1
    )
    # Add loading="lazy" / width / height isn't already present verbatim — keep existing loading attr as-is.

    # Add data-href right after data-cat="..." data-search="..."  (insert before the closing '>')
    # Find the end of the opening <div ...> tag
    tag_end = card.find('>')
    opening_tag = card[:tag_end]
    rest = card[tag_end:]
    if 'data-href' not in opening_tag:
        opening_tag = opening_tag + f' data-href="product/{slug}/"'
    card = opening_tag + rest

    rebuilt_cards.append(card)

new_content = head_part + ''.join(rebuilt_cards)

# ── 2. Replace logo base64 (3 occurrences: header, hero, footer) with external file ──
new_content = re.sub(
    r'src="data:image/webp;base64,[^"]+"',
    'src="images/logo.webp"',
    new_content
)

# ── 3. Replace inline site-logic <script>...</script> with external reference ──
# This is the block starting with "/* ── Front / Back Toggle ── */"
site_js_pattern = re.compile(
    r'<script>\s*/\* ── Front / Back Toggle ── \*/.*?</script>',
    re.DOTALL
)
m = site_js_pattern.search(new_content)
assert m, "Could not locate inline site-logic script block"
new_content = new_content[:m.start()] + '<script src="js/site.js"></script>' + new_content[m.end():]

# ── 4. Replace inline analytics <script>...</script> with external reference ──
analytics_pattern = re.compile(
    r'<script>\s*/\* ═+\s*ANALYTICS.*?</script>',
    re.DOTALL
)
m2 = analytics_pattern.search(new_content)
assert m2, "Could not locate inline analytics script block"
new_content = new_content[:m2.start()] + '<script src="js/products-data.js"></script>\n<script src="js/analytics.js"></script>' + new_content[m2.end():]

# ── 5. Add products-data.js + gallery hooks not needed on homepage (no gallery there) ──
# Already added products-data.js above (used by analytics for nothing critical, but
# kept available in case future homepage features want it).

# ── 6b. Inject cursor:pointer for clickable cards (additive CSS, scoped) ──
cursor_css = '\n.card[data-href]{cursor:pointer}\n.card[data-href] .card-img-wrap{cursor:pointer}\n'
style_close = new_content.find('</style>')
assert style_close != -1, "Could not find </style> to inject cursor CSS"
new_content = new_content[:style_close] + cursor_css + new_content[style_close:]

# ── 7. Insert JSON-LD structured data (Organization + ItemList) into <head> ──
organization_jsonld = {
    "@context": "https://schema.org/",
    "@type": "SportingGoodsStore",
    "name": "HNS United",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/images/logo.webp",
    "image": SITE_URL + "/images/logo.webp",
    "telephone": "+91-94444-73545",
    "address": {"@type": "PostalAddress", "addressLocality": "Chennai", "addressCountry": "IN"},
    "sameAs": ["https://instagram.com/hns_united"]
}

# Load product data for ItemList
import importlib.util
spec_path = os.path.join(ROOT, 'js', 'products-data.js')
with open(spec_path) as f:
    js_data = f.read()
products_match = re.search(r'window\.HNS_PRODUCTS\s*=\s*(\[.*?\]);', js_data, re.DOTALL)
def js_to_json(s):
    s = re.sub(r'(?<=[{,\s])(\w+)(?=\s*:)', r'"\1"', s)
    s = re.sub(r',(\s*[\]}])', r'\1', s)
    return s
products = json.loads(js_to_json(products_match.group(1)))

itemlist_jsonld = {
    "@context": "https://schema.org/",
    "@type": "ItemList",
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": i + 1,
            "url": f"{SITE_URL}/product/{p['slug']}/"
        } for i, p in enumerate(products)
    ]
}

jsonld_block = (
    '<script type="application/ld+json">\n' + json.dumps(organization_jsonld, indent=2) + '\n</script>\n'
    '<script type="application/ld+json">\n' + json.dumps(itemlist_jsonld, indent=2) + '\n</script>\n'
)

# Insert OG/canonical + JSON-LD right before </head>, plus canonical/OG for homepage itself
home_meta = f'''<link rel="canonical" href="{SITE_URL}/">
<meta property="og:type" content="website">
<meta property="og:title" content="HNS United – Quality • Trust • Passion">
<meta property="og:description" content="Premium football jerseys with full embroidery. Cash on Delivery & GPay accepted. Shop Argentina, Brazil, Portugal, Spain and more.">
<meta property="og:image" content="{SITE_URL}/images/products/argentina-home-set-front.jpg">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:site_name" content="HNS United">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="HNS United – Quality • Trust • Passion">
<meta name="twitter:description" content="Premium football jerseys with full embroidery. Cash on Delivery & GPay accepted.">
<meta name="twitter:image" content="{SITE_URL}/images/products/argentina-home-set-front.jpg">
'''

head_close = new_content.find('</head>')
new_content = new_content[:head_close] + home_meta + jsonld_block + new_content[head_close:]

with open(os.path.join(ROOT, 'index.html'), 'w') as f:
    f.write(new_content)

print("Homepage built:", os.path.join(ROOT, 'index.html'))
print("New size:", len(new_content), "bytes  (was", len(content), ")")

# ── 8. Regenerate sitemap.xml to stay in sync with product data ──
urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/product/{p['slug']}/" for p in products]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    priority = "1.0" if u == f"{SITE_URL}/" else "0.8"
    sitemap += f'  <url>\n    <loc>{u}</loc>\n    <priority>{priority}</priority>\n  </url>\n'
sitemap += '</urlset>\n'
with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
    f.write(sitemap)
print("sitemap.xml regenerated with", len(urls), "URLs")
