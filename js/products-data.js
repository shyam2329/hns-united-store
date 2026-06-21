/* ════════════════════════════════════════════════════
   PRODUCT DATA — single source of truth
   To add a new product: add one object here, drop two
   images in /images/products/<slug>-front.jpg / -back.jpg,
   then run generate-products.py to build its page.
   ════════════════════════════════════════════════════ */

window.HNS_PRODUCTS = [
  {
    slug: "argentina-away",
    name: "Argentina Away Jersey (Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 999,
    price: 450,
    badges: [],
    images: ["argentina-away-front.jpg", "argentina-away-back.jpg"],
    searchTerms: "argentina away jersey argentina national team albiceleste messi afa embroidery",
    description: [
      "Premium embroidered badge and crest",
      "Breathable quick-dry match fabric",
      "Authentic away colourway",
      "Regular athletic fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "portugal-home",
    name: "Portugal Home Jersey (Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 999,
    price: 450,
    badges: ["Best Seller"],
    images: ["portugal-home-front.jpg", "portugal-home-back.jpg"],
    searchTerms: "portugal home jersey portugal national team seleção fpf embroidery",
    description: [
      "Premium embroidered badge and crest",
      "Breathable quick-dry match fabric",
      "Authentic home colourway",
      "Regular athletic fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "portugal-away",
    name: "Portugal Away Jersey (Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 999,
    price: 450,
    badges: [],
    images: ["portugal-away-front.jpg", "portugal-away-back.jpg"],
    searchTerms: "portugal away jersey portugal national team seleção fpf embroidery",
    description: [
      "Premium embroidered badge and crest",
      "Breathable quick-dry match fabric",
      "Authentic away colourway",
      "Regular athletic fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "brazil-away",
    name: "Brazil Away Jersey (Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 999,
    price: 450,
    badges: [],
    images: ["brazil-away-front.jpg", "brazil-away-back.jpg"],
    searchTerms: "brazil away jersey brazil national team brasil seleção cbf embroidery",
    description: [
      "Premium embroidered badge and crest",
      "Breathable quick-dry match fabric",
      "Authentic away colourway",
      "Regular athletic fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "spain-away",
    name: "Spain Away Jersey (Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 999,
    price: 450,
    badges: ["Bestseller"],
    images: ["spain-away-front.jpg", "spain-away-back.jpg"],
    searchTerms: "spain away jersey spain national team españa la roja rfef embroidery",
    description: [
      "Premium embroidered badge and crest",
      "Breathable quick-dry match fabric",
      "Authentic away colourway",
      "Regular athletic fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "argentina-home-set",
    name: "Argentina 2026 World Cup Home Set (Master Edition – Full Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 1500,
    price: 749,
    badges: ["New Arrival"],
    images: ["argentina-home-set-front.jpg", "argentina-home-set-back.jpg"],
    searchTerms: "argentina 2026 world cup home set master edition full embroidery argentina national team albiceleste afa jersey shorts",
    description: [
      "Full embroidery badges and logos",
      "Premium player version quality",
      "Includes Jersey + Shorts",
      "Breathable quick-dry fabric",
      "Regular fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "brazil-home-set",
    name: "Brazil 2026 World Cup Home Set (Master Edition – Full Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 1500,
    price: 749,
    badges: ["New Arrival"],
    images: ["brazil-home-set-front.jpg", "brazil-home-set-back.jpg"],
    searchTerms: "brazil 2026 world cup home set master edition full embroidery brazil national team brasil seleção cbf jersey shorts",
    description: [
      "Full embroidery badges and logos",
      "Premium player version quality",
      "Includes Jersey + Shorts",
      "Breathable quick-dry fabric",
      "Regular fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  },
  {
    slug: "portugal-black-gold",
    name: "Portugal Special Edition Black-and-Gold (Embroidery)",
    tag: "National Team",
    category: "national",
    priceOld: 999,
    price: 550,
    badges: ["Bestseller"],
    images: ["portugal-black-gold-front.jpg", "portugal-black-gold-back.jpg"],
    searchTerms: "portugal special edition black and gold embroidery portugal national team seleção fpf jersey",
    description: [
      "Premium embroidered badge and crest",
      "Limited black-and-gold colourway",
      "Breathable quick-dry match fabric",
      "Regular athletic fit",
      "Cash on Delivery available",
      "GPay accepted"
    ]
  }
];

/* Sizes available storewide; XXL is out of stock on every product
   (matches existing site behaviour). Override per-product by adding
   a `sizes` array to that product object if it ever differs. */
window.HNS_DEFAULT_SIZES = [
  { label: "S", available: true },
  { label: "M", available: true },
  { label: "L", available: true },
  { label: "XL", available: true },
  { label: "XXL", available: false }
];

window.HNS_SITE_URL = "https://hns-united-store.vercel.app";
window.HNS_WHATSAPP_NUMBER = "919444473545";
