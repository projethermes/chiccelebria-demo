#!/usr/bin/env python3
"""Chic Celebria — build statique data-driven.

Lit products.json + collections.json et génère :
  - i18n-data.js (traductions produit/collection, 5 langues)
  - products/<id>/index.html   (une page par produit)
  - collections/<slug>/index.html
  - collections/index.html     (page "Celebrations")

Usage :  python3 build.py     (génère dans le dossier courant = racine du site)
"""

import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "es", "fr", "it", "de"]
SITE = "https://projethermes.github.io/chiccelebria-demo"

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;'
         '0,9..144,500;0,9..144,600;1,9..144,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">')


def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)


products = load("products.json")
collections = load("collections.json")


def active_products():
    return [p for p in products if p.get("actif", True)]


def active_collections():
    return [c for c in collections if c.get("actif", True)]


def occasions():
    return sorted([c for c in active_collections() if c.get("type") == "occasion"],
                  key=lambda c: c.get("ordre", 99))


def products_of(slug):
    return [p for p in active_products() if slug in p.get("collections", [])]


# --------------------------------------------------------------------------
# i18n-data.js — traductions produit + collection
# --------------------------------------------------------------------------
HERO = {
    "en": "Shop the {label} edit on Etsy.",
    "es": "Descubre la selección {label} en Etsy.",
    "fr": "Découvrez la sélection {label} sur Etsy.",
    "it": "Scopri la selezione {label} su Etsy.",
    "de": "Entdecke die {label}-Auswahl auf Etsy.",
}


def gen_i18n_data():
    d = {l: {} for l in LANGS}
    for p in active_products():
        for l in LANGS:
            d[l][f"p.{p['id']}.title"] = p["nom"][l]
            d[l][f"p.{p['id']}.desc"] = p["description"][l]
            d[l][f"p.{p['id']}.metaTitle"] = p["nom"][l] + " | Chic Celebria"
    for c in collections:
        for l in LANGS:
            d[l][f"coll.{c['slug']}.label"] = c["label"][l]
            d[l][f"coll.{c['slug']}.metaTitle"] = c["label"][l] + " | Chic Celebria"
            d[l][f"coll.{c['slug']}.hero"] = HERO[l].format(label=c["label"][l])
            d[l][f"coll.{c['slug']}.desc"] = HERO[l].format(label=c["label"][l])
    return "window.CHIC_I18N_DATA = " + json.dumps(d, ensure_ascii=False) + ";"


# --------------------------------------------------------------------------
# Header / footer (menu généré depuis collections.json)
# --------------------------------------------------------------------------
def nav_links(prefix):
    out = [f'<a href="{prefix}index.html#new-in" data-i18n="common.newIn">New In</a>',
           f'<a href="{prefix}collections/" data-i18n="common.celebrations">Celebrations</a>']
    for c in occasions():
        out.append(f'<a href="{prefix}collections/{c["slug"]}/" data-i18n="coll.{c["slug"]}.label">{c["label"]["en"]}</a>')
    out.append(f'<a href="{prefix}about.html" data-i18n="common.about">About</a>')
    return "\n      ".join(out)


def header(prefix):
    return f'''<header class="site-header" data-site-header>
  <div class="wrap header-inner">
    <a href="{prefix}index.html" class="wordmark">
      <img src="{prefix}assets/logo.png" alt="" class="logo-mark" width="30" height="30">
      Chic Celebria
    </a>
    <nav class="main-nav" id="main-nav" aria-label="Main navigation" data-i18n-aria="common.navLabel">
      {nav_links(prefix)}
    </nav>
    <div class="header-actions">
      <div class="lang-switch">
        <select id="lang-select" data-i18n-aria="common.language" aria-label="Language">
          <option value="en">EN</option>
          <option value="es">ES</option>
          <option value="fr">FR</option>
          <option value="it">IT</option>
          <option value="de">DE</option>
        </select>
      </div>
      <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="main-nav">
        <span class="sr-only" data-i18n="common.openMenu">Open menu</span>
        <span class="nav-toggle-bar" aria-hidden="true"></span>
      </button>
    </div>
  </div>
</header>'''


def footer(prefix):
    shop = [f'<a href="{prefix}index.html#new-in" data-i18n="common.newIn">New In</a>']
    for c in occasions():
        shop.append(f'<a href="{prefix}collections/{c["slug"]}/" data-i18n="coll.{c["slug"]}.label">{c["label"]["en"]}</a>')
    shop_links = "\n      ".join(shop)
    return f'''<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <a href="{prefix}index.html" class="wordmark">
        <img src="{prefix}assets/logo.png" alt="" class="logo-mark" width="30" height="30">
        Chic Celebria
      </a>
      <p data-i18n="common.footerTagline">Distinctive decor and personalised gifts for Halloween, Christmas and every celebration in between.</p>
      <a class="btn btn-outline btn-sm" href="#" data-etsy-cta data-i18n="common.shopOnEtsy">Shop on Etsy</a>
    </div>
    <nav class="footer-links" aria-label="Shop">
      <h4 data-i18n="common.shop">Shop</h4>
      {shop_links}
    </nav>
    <nav class="footer-links" aria-label="Company">
      <h4 data-i18n="common.company">Company</h4>
      <a href="{prefix}collections/" data-i18n="common.celebrations">Celebrations</a>
      <a href="{prefix}about.html" data-i18n="common.about">About</a>
      <a href="#" data-etsy-cta data-i18n="common.shopOnEtsy">Shop on Etsy</a>
    </nav>
  </div>
  <div class="wrap footer-bottom">
    <p>&copy; <span id="year">2026</span> <span data-i18n="common.footerCopyright">Chic Celebria. Prices shown in EUR.</span></p>
  </div>
</footer>'''


def scripts(prefix):
    return f'''<script src="{prefix}i18n-data.js"></script>
<script src="{prefix}i18n.js"></script>
<script src="{prefix}script.js"></script>'''


def head(prefix, title_key, title_en, desc_key, desc_en, canonical, og_type, og_image=None):
    og = f'<meta property="og:image" content="{SITE}/{og_image}">' if og_image else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title data-i18n-content="{title_key}">{title_en}</title>
<meta name="description" data-i18n-content="{desc_key}" content="{desc_en}">
<link rel="canonical" href="{SITE}/{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" data-i18n-content="{title_key}" content="{title_en}">
<meta property="og:description" data-i18n-content="{desc_key}" content="{desc_en}">
<meta property="og:url" content="{SITE}/{canonical}">
{og}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}assets/logo.png" type="image/png">
<link rel="apple-touch-icon" href="{prefix}assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS}
<link rel="stylesheet" href="{prefix}style.css">
<script src="{prefix}assets/site-config.js"></script>
'''


# --------------------------------------------------------------------------
# Pages produit
# --------------------------------------------------------------------------
def product_page(p):
    prefix = "../../"
    img = p["images"][0] if p["images"] else ""
    first_coll = p["collections"][0] if p["collections"] else "gifts"
    coll_label_en = next((c["label"]["en"] for c in collections if c["slug"] == first_coll), "Shop")
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Product",
        "name": p["nom"]["en"],
        "image": f"{SITE}/{img}" if img else "",
        "description": p["description"]["en"],
        "brand": {"@type": "Brand", "name": "Chic Celebria"},
        "offers": {
            "@type": "Offer", "url": "https://www.etsy.com/shop/ChicCelebria",
            "priceCurrency": "EUR", "price": str(p["prix"]),
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
        },
    }, ensure_ascii=False)
    return f'''{head(prefix, f"p.{p['id']}.metaTitle", p["nom"]["en"] + " | Chic Celebria",
                   f"p.{p['id']}.desc", p["description"]["en"],
                   f"products/{p['id']}/", "product", img)}
<script type="application/ld+json">
{ld}
</script>
</head>
<body data-page="product">

<a class="skip-link" href="#main" data-i18n="common.skip">Skip to content</a>

{header(prefix)}

<main id="main">
  <section class="section-tight">
    <div class="wrap">
      <div class="product-layout">
        <div class="product-gallery">
          <div class="gallery-main">
            <img src="{prefix}{img}" alt="{p['nom']['en']}" width="1000" height="1000" data-i18n-alt="p.{p['id']}.title">
          </div>
        </div>
        <div class="product-info">
          <p class="breadcrumb"><a href="{prefix}index.html" data-i18n="common.home">Home</a> / <a href="{prefix}collections/{first_coll}/" data-i18n="coll.{first_coll}.label">{coll_label_en}</a> / <span data-i18n="p.{p['id']}.title">{p['nom']['en']}</span></p>
          <h1 data-i18n="p.{p['id']}.title">{p['nom']['en']}</h1>
          <p class="product-price">€{p['prix']:.2f}</p>
          <p class="product-desc" data-i18n="p.{p['id']}.desc">{p['description']['en']}</p>
          <div class="product-cta">
            <a class="btn btn-primary btn-lg" href="#" data-etsy-cta data-i18n="common.shopOnEtsy">Shop on Etsy</a>
            <p class="product-cta-note" data-i18n="product.ctaNote">Sold and fulfilled through our Etsy shop.</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</main>

{footer(prefix)}

{scripts(prefix)}
</body>
</html>'''


# --------------------------------------------------------------------------
# Pages collection
# --------------------------------------------------------------------------
def product_card(p, prefix):
    ptype = "personalised" if "personalised" in p.get("collections", []) else "decor"
    img = p["images"][0] if p["images"] else ""
    return f'''        <article class="p-card" data-name="{p['nom']['en']}" data-price="{p['prix']}" data-type="{ptype}" data-i18n-name="p.{p['id']}.title">
          <a class="p-card-media" href="{prefix}products/{p['id']}/">
            <img class="img-main" src="{prefix}{img}" alt="{p['nom']['en']}" width="1000" height="1000" loading="lazy" data-i18n-alt="p.{p['id']}.title">
          </a>
          <div class="p-card-body">
            <a class="p-card-title" href="{prefix}products/{p['id']}/" data-i18n="p.{p['id']}.title">{p['nom']['en']}</a>
            <p class="p-card-price">€{p['prix']:.2f}</p>
          </div>
        </article>'''


def collection_page(c):
    slug = c["slug"]
    prefix = "../../"
    items = products_of(slug)
    cards = "\n".join(product_card(p, prefix) for p in items)
    accent = " accent-halloween" if slug == "halloween" else ""
    return f'''{head(prefix, f"coll.{slug}.metaTitle", c["label"]["en"] + " | Chic Celebria",
                   f"coll.{slug}.desc", c["label"]["en"] + " — shop on Etsy.",
                   f"collections/{slug}/", "website")}
</head>
<body data-page="collection-{slug}">

<a class="skip-link" href="#main" data-i18n="common.skip">Skip to content</a>

{header(prefix)}

<main id="main">
  <section class="collection-hero{accent}">
    <div class="wrap">
      <p class="breadcrumb"><a href="{prefix}index.html" data-i18n="common.home">Home</a> / <a href="{prefix}collections/" data-i18n="common.celebrations">Celebrations</a> / <span data-i18n="coll.{slug}.label">{c["label"]["en"]}</span></p>
      <span class="eyebrow" data-i18n="common.seasonalEdit">Seasonal Edit</span>
      <h1 data-i18n="coll.{slug}.label">{c["label"]["en"]}</h1>
      <p data-i18n="coll.{slug}.hero">Shop the {c["label"]["en"]} edit on Etsy.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="toolbar">
        <div class="toolbar-filters">
          <div class="toolbar-field">
            <label for="filter-type" data-i18n="toolbar.type">Type</label>
            <select id="filter-type">
              <option value="all" data-i18n="toolbar.all">All</option>
              <option value="decor" data-i18n="toolbar.decor">Decor</option>
              <option value="personalised" data-i18n="toolbar.personalised">Personalised</option>
            </select>
          </div>
          <div class="toolbar-field">
            <label for="filter-price" data-i18n="toolbar.price">Price</label>
            <select id="filter-price">
              <option value="all" data-i18n="toolbar.all">All</option>
              <option value="under-15" data-i18n="toolbar.under15">Under €15</option>
              <option value="15-25" data-i18n="toolbar.15to25">€15–€25</option>
              <option value="over-25" data-i18n="toolbar.over25">Over €25</option>
            </select>
          </div>
          <div class="toolbar-field">
            <label for="sort-by" data-i18n="toolbar.sort">Sort by</label>
            <select id="sort-by">
              <option value="name-asc" data-i18n="toolbar.nameAsc">Name (A–Z)</option>
              <option value="name-desc" data-i18n="toolbar.nameDesc">Name (Z–A)</option>
              <option value="price-asc" data-i18n="toolbar.priceAsc">Price (Low to High)</option>
              <option value="price-desc" data-i18n="toolbar.priceDesc">Price (High to Low)</option>
            </select>
          </div>
        </div>
        <p class="toolbar-count"><span data-result-count>{len(items)} pieces</span></p>
      </div>

      <div class="product-grid" data-collection-grid>
{cards}
      </div>

      <p class="collection-empty" data-collection-empty hidden data-i18n="collection.empty">No pieces match these filters yet — try widening your search.</p>
    </div>
  </section>
</main>

{footer(prefix)}

{scripts(prefix)}
</body>
</html>'''


# --------------------------------------------------------------------------
# Page Celebrations (index des collections)
# --------------------------------------------------------------------------
def celebrations_page():
    prefix = "../"
    cards = ""
    for c in active_collections():
        cards += f'''        <a class="coll-card" href="{c['slug']}/" data-i18n="coll.{c['slug']}.label">{c['label']['en']}</a>\n'''
    return f'''{head(prefix, "common.celebrations", "Celebrations | Chic Celebria",
                   "common.celebrations", "All our seasonal edits — shop on Etsy.",
                   "collections/", "website")}
</head>
<body data-page="collections">

<a class="skip-link" href="#main" data-i18n="common.skip">Skip to content</a>

{header(prefix)}

<main id="main">
  <section class="collection-hero">
    <div class="wrap">
      <p class="breadcrumb"><a href="{prefix}index.html" data-i18n="common.home">Home</a> / <span data-i18n="common.celebrations">Celebrations</span></p>
      <span class="eyebrow" data-i18n="common.seasonalEdit">Seasonal Edit</span>
      <h1 data-i18n="common.celebrations">Celebrations</h1>
      <p data-i18n="common.footerTagline">Distinctive decor and personalised gifts for every celebration.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="product-grid">
{cards}
      </div>
    </div>
  </section>
</main>

{footer(prefix)}

{scripts(prefix)}
</body>
</html>'''


# --------------------------------------------------------------------------
# Écriture des fichiers
# --------------------------------------------------------------------------
def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def static_page(name):
    """Régénère une page racine (index/about/404) : menu + footer générés, contenu <main> préservé."""
    path = os.path.join(BASE, name + ".html")
    src = open(path, encoding="utf-8").read()
    src = re.sub(r'<header class="site-header".*?</header>', lambda m: header(""), src, flags=re.DOTALL)
    src = re.sub(r'<footer class="site-footer".*?</footer>', lambda m: footer(""), src, flags=re.DOTALL)
    src = src.replace('<script src="i18n.js"></script>',
                      '<script src="i18n-data.js"></script>\n<script src="i18n.js"></script>')
    return src


def main():
    write("i18n-data.js", gen_i18n_data())
    for p in active_products():
        write(f"products/{p['id']}/index.html", product_page(p))
    for c in active_collections():
        write(f"collections/{c['slug']}/index.html", collection_page(c))
    write("collections/index.html", celebrations_page())
    for name in ["index", "about", "404"]:
        write(f"{name}.html", static_page(name))
    print(f"OK — {len(active_products())} produits, {len(active_collections())} collections, + index/about/404 générés.")


if __name__ == "__main__":
    main()
