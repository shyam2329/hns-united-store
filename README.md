# HNS UNITED — Premium Product Page Upgrade

## What this is

A hand-built, framework-free static multi-page site. No npm/build step required —
deploy these files to Vercel (or any static host) as-is.

> **Why no React/Vite/Embla:** the build sandbox used to generate this has no
> internet access, so npm packages couldn't be installed. Everything here is
> vanilla HTML/CSS/JS that delivers the same outcomes (real routes, real
> per-page SEO, a working swipe/zoom gallery) without needing a bundler.
> If you later want to migrate to React, `js/products-data.js` is already
> the single source of truth you'd port into a CMS/props.

## Structure

```
index.html                     ← homepage (unchanged design, cards now link out)
product/<slug>/index.html      ← one real page per product, unique SEO per page
css/base.css                   ← original site styles, untouched
css/product.css                ← new product-page styles, same design tokens
js/products-data.js            ← single source of truth for all product data
js/site.js                     ← original homepage logic, byte-identical to before
js/analytics.js                ← GA4 + Clarity event tracking (shared, extended)
js/gallery.js                  ← hand-built carousel: drag, swipe, zoom, thumbs
js/product-page.js             ← size/qty/WhatsApp logic for product pages
js/_header_partial.html        ← shared header/nav template (used by generator)
js/_footer_partial.html        ← shared footer template (used by generator)
js/_modals_partial.html        ← shared size-guide/policy modal template
images/products/<slug>-front.jpg / -back.jpg
images/logo.webp
scripts/generate-homepage.py   ← rebuilds index.html from original.html
scripts/generate-products.py   ← rebuilds all product/<slug>/index.html pages
```

## Adding a new product (no page-coding required)

1. Drop two images in `images/products/`: `<slug>-front.jpg` and `<slug>-back.jpg`
   (any size — 900×900 recommended for consistency with the rest of the catalog).
2. Add one object to the array in `js/products-data.js` — copy an existing
   entry as a template and change the fields.
3. Run:
   ```
   python3 scripts/generate-products.py
   python3 scripts/generate-homepage.py
   ```
4. Deploy. That's it — no new components, no new routes to wire up, no CSS to touch.

The homepage grid, the gallery, the SEO tags, the JSON-LD structured data, the
related-products logic, and the WhatsApp message are all generated automatically
from that one data file.

## Deploying to Vercel

This is 100% static output — no build command needed.
- **Build Command:** (leave empty)
- **Output Directory:** `.` (project root)

Since there's no server-side routing, Vercel's static file server resolves
`/product/argentina-away/` to `/product/argentina-away/index.html`
automatically (this is standard behavior for directory-style static hosting).

## Analytics

- **GA4** (`G-2THLNQHP78`) and **Microsoft Clarity** (`xam6nb5lqj`) are loaded
  identically on every page — homepage and all 8 product pages — verified to
  appear exactly once each, no duplication.
- Events tracked: page_view (native GA4), product_card_click, product_page_view,
  product_image_swipe, thumbnail_click, image_zoom, size_selection,
  order_whatsapp_click, scroll_depth (25/50/75/100%), time_on_page,
  related_product_click, back_navigation, external_link_click,
  session_duration, returning_visitor/new_visitor, exit_page.
  Device type, browser, country, city, traffic source, landing/exit page,
  and bounce rate are captured natively by GA4's `gtag.js` — no custom code
  needed for those.
- Clarity captures session recordings, heatmaps, click/scroll heatmaps, rage
  clicks, dead clicks, and JS errors automatically once the script tag loads
  — that's all native Clarity behavior, nothing custom required.

## What was preserved exactly

- `js/site.js` is byte-for-byte identical to the original inline script —
  the homepage's front/back toggle, qty stepper, search, filters, and
  WhatsApp order button behave exactly as they did before.
- Homepage CSS (`css/base.css`) is the original stylesheet, untouched.
- The only homepage markup change: each `.card` gained a `data-href`
  attribute and the page gained one small CSS rule (`cursor:pointer`) so
  clicking a card (outside its buttons/inputs) opens the product page.
