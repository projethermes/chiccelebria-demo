#!/usr/bin/env python3
"""Chic Celebria — build statique data-driven, multilingue (Best-of).

Lit products.json + collections.json + i18n-strings.json et génère un site
statique avec de vraies URLs par langue :

  /en/  /es/  /fr/  /it/  /de/     (index, about, collections/, products/)
  /sitemap.xml, /robots.txt         (générés depuis les mêmes données)
  /index.html, /about.html, /404.html   (redirection vers /en/, 404 racine)

Usage :  python3 build.py     (génère dans le dossier courant = racine du site)
"""

import html
import json
import os
import re
import struct
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "es", "fr", "it", "de"]
DEFAULT_LANG = "en"
SITE = "https://projethermes.github.io/chiccelebria-demo"
OG_LOCALE = {"en": "en_US", "es": "es_ES", "fr": "fr_FR", "it": "it_IT", "de": "de_DE"}

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;'
         '0,9..144,500;0,9..144,600;1,9..144,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">')

esc = html.escape


def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)


products = load("products.json")
collections = load("collections.json")
STRINGS = load("i18n-strings.json")


def active_products():
    return [p for p in products if p.get("actif", True)]


def active_collections():
    return [c for c in collections if c.get("actif", True)]


def occasions():
    return sorted([c for c in active_collections() if c.get("type") == "occasion"],
                  key=lambda c: c.get("ordre", 99))


def products_of(slug):
    return [p for p in active_products() if slug in p.get("collections", [])]


def s(lang, key):
    return STRINGS[lang][key]


# --------------------------------------------------------------------------
# Slugs traduits — dérivés des vraies traductions nom[lang] / label[lang],
# jamais d'une table séparée inventée.
# --------------------------------------------------------------------------
def slugify(text):
    text = text.replace("ß", "ss").replace("œ", "oe").replace("æ", "ae").replace("ø", "o")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_slug_map(items, key_of, name_of):
    result = {}
    used = {lang: set() for lang in LANGS}
    for item in items:
        key = key_of(item)
        result[key] = {}
        for lang in LANGS:
            base = slugify(name_of(item, lang)) or slugify(key)
            slug, n = base, 2
            while slug in used[lang]:
                slug = f"{base}-{n}"
                n += 1
            used[lang].add(slug)
            result[key][lang] = slug
    return result


PRODUCT_SLUGS = build_slug_map(active_products(), lambda p: p["id"], lambda p, lang: p["nom"][lang])
COLL_SLUGS = build_slug_map(active_collections(), lambda c: c["slug"], lambda c, lang: c["label"][lang])


# --------------------------------------------------------------------------
# Chemins (relatifs à la racine du site, sans "/" initial) — même forme
# utilisée pour les liens internes (avec un prefix relatif) et pour les URLs
# absolues (canonical / hreflang / sitemap).
# --------------------------------------------------------------------------
def p_home(lang):
    return f"{lang}/index.html"


def p_about(lang):
    return f"{lang}/about.html"


def p_collections_index(lang):
    return f"{lang}/collections/"


def p_collection(slug, lang):
    return f"{lang}/collections/{COLL_SLUGS[slug][lang]}/"


def p_product(pid, lang):
    return f"{lang}/products/{PRODUCT_SLUGS[pid][lang]}/"


def alt_home():
    return {lang: p_home(lang) for lang in LANGS}


def alt_about():
    return {lang: p_about(lang) for lang in LANGS}


def alt_collections_index():
    return {lang: p_collections_index(lang) for lang in LANGS}


def alt_collection(slug):
    return {lang: p_collection(slug, lang) for lang in LANGS}


def alt_product(pid):
    return {lang: p_product(pid, lang) for lang in LANGS}


def absolute(rootrel):
    return f"{SITE}/{rootrel}"


# --------------------------------------------------------------------------
# Dimensions réelles des images (JPEG / PNG / WebP), sans dépendance externe
# (PIL/cwebp/ImageMagick indisponibles sur cet environnement) — évite tout
# décalage de mise en page (CLS) dû à des width/height approximatifs.
# --------------------------------------------------------------------------
_IMAGE_DIM_CACHE = {}


def image_dimensions(rootrel):
    if rootrel in _IMAGE_DIM_CACHE:
        return _IMAGE_DIM_CACHE[rootrel]
    path = os.path.join(BASE, rootrel)
    dims = None
    try:
        with open(path, "rb") as f:
            head = f.read(32)
            if head[:2] == b"\xff\xd8":  # JPEG
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        break
                    if marker[1] in (0xC0, 0xC1, 0xC2, 0xC3):
                        f.read(3)
                        h, w = struct.unpack(">HH", f.read(4))
                        dims = (w, h)
                        break
                    length = struct.unpack(">H", f.read(2))[0]
                    f.read(length - 2)
            elif head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                dims = (w, h)
            elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                chunk = head[12:16]
                if chunk == b"VP8 ":
                    w, h = struct.unpack("<HH", head[26:30])
                    dims = (w & 0x3FFF, h & 0x3FFF)
                elif chunk == b"VP8L":
                    b0, b1, b2, b3 = head[21:25]
                    w = 1 + (((b1 & 0x3F) << 8) | b0)
                    h = 1 + (((b3 & 0xF) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
                    dims = (w, h)
                elif chunk == b"VP8X":
                    w = 1 + (head[24] | (head[25] << 8) | (head[26] << 16))
                    h = 1 + (head[27] | (head[28] << 8) | (head[29] << 16))
                    dims = (w, h)
    except (OSError, struct.error):
        dims = None
    dims = dims or (1000, 1000)
    _IMAGE_DIM_CACHE[rootrel] = dims
    return dims


# --------------------------------------------------------------------------
# Head / header / footer
# --------------------------------------------------------------------------
def head(lang, prefix, current_rootrel, alt_paths, title, desc, og_type, og_image=None, extra_ld=""):
    canonical = absolute(current_rootrel)
    if alt_paths:
        hreflang_tags = "\n".join(
            f'<link rel="alternate" hreflang="{l}" href="{absolute(alt_paths[l])}">' for l in LANGS
        )
        xdefault = f'<link rel="alternate" hreflang="x-default" href="{absolute(alt_paths[DEFAULT_LANG])}">'
    else:
        hreflang_tags = xdefault = ""
    og = f'<meta property="og:image" content="{absolute(og_image)}">' if og_image else ""
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
{hreflang_tags}
{xdefault}
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
{og}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}assets/logo.png" type="image/png">
<link rel="apple-touch-icon" href="{prefix}assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS}
<link rel="stylesheet" href="{prefix}style.css">
<script src="{prefix}assets/site-config.js"></script>
{extra_ld}</head>'''


def lang_switch(lang, prefix, alt_paths):
    opts = "\n          ".join(
        f'<option value="{l}" data-url="{prefix}{alt_paths[l]}"{" selected" if l == lang else ""}>{l.upper()}</option>'
        for l in LANGS
    )
    return f'''<div class="lang-switch">
        <select id="lang-select" aria-label="{esc(s(lang, "common.language"))}">
          {opts}
        </select>
      </div>'''


def nav_links(lang, prefix):
    out = [f'<a href="{prefix}{p_home(lang)}#new-in">{s(lang, "common.newIn")}</a>',
           f'<a href="{prefix}{p_collections_index(lang)}">{s(lang, "common.celebrations")}</a>']
    for c in occasions():
        out.append(f'<a href="{prefix}{p_collection(c["slug"], lang)}">{esc(c["label"][lang])}</a>')
    out.append(f'<a href="{prefix}{p_about(lang)}">{s(lang, "common.about")}</a>')
    return "\n      ".join(out)


def header(lang, prefix, alt_paths):
    return f'''<header class="site-header" data-site-header>
  <div class="wrap header-inner">
    <a href="{prefix}{p_home(lang)}" class="wordmark">
      <img src="{prefix}assets/logo.png" alt="" class="logo-mark" width="30" height="30">
      Chic Celebria
    </a>
    <nav class="main-nav" id="main-nav" aria-label="{esc(s(lang, "common.navLabel"))}">
      {nav_links(lang, prefix)}
    </nav>
    <div class="header-actions">
      {lang_switch(lang, prefix, alt_paths)}
      <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="main-nav">
        <span class="sr-only">{s(lang, "common.openMenu")}</span>
        <span class="nav-toggle-bar" aria-hidden="true"></span>
      </button>
    </div>
  </div>
</header>'''


def footer(lang, prefix):
    shop = [f'<a href="{prefix}{p_home(lang)}#new-in">{s(lang, "common.newIn")}</a>']
    for c in occasions():
        shop.append(f'<a href="{prefix}{p_collection(c["slug"], lang)}">{esc(c["label"][lang])}</a>')
    shop_links = "\n      ".join(shop)
    return f'''<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <a href="{prefix}{p_home(lang)}" class="wordmark">
        <img src="{prefix}assets/logo.png" alt="" class="logo-mark" width="30" height="30">
        Chic Celebria
      </a>
      <p>{esc(s(lang, "common.footerTagline"))}</p>
      <a class="btn btn-outline btn-sm" href="#" data-etsy-cta>{s(lang, "common.shopOnEtsy")}</a>
    </div>
    <nav class="footer-links" aria-label="{esc(s(lang, "common.shop"))}">
      <h4>{s(lang, "common.shop")}</h4>
      {shop_links}
    </nav>
    <nav class="footer-links" aria-label="{esc(s(lang, "common.company"))}">
      <h4>{s(lang, "common.company")}</h4>
      <a href="{prefix}{p_collections_index(lang)}">{s(lang, "common.celebrations")}</a>
      <a href="{prefix}{p_about(lang)}">{s(lang, "common.about")}</a>
      <a href="#" data-etsy-cta>{s(lang, "common.shopOnEtsy")}</a>
    </nav>
  </div>
  <div class="wrap footer-bottom">
    <p>&copy; <span id="year">2026</span> {esc(s(lang, "common.footerCopyright"))}</p>
  </div>
</footer>'''


def scripts(prefix):
    return f'<script src="{prefix}script.js"></script>'


def page_shell(lang, prefix, page_id, body_main, alt_paths, head_html):
    return f'''{head_html}
<body data-page="{page_id}">

<a class="skip-link" href="#main">{s(lang, "common.skip")}</a>

{header(lang, prefix, alt_paths)}

<main id="main">
{body_main}
</main>

{footer(lang, prefix)}

{scripts(prefix)}
</body>
</html>'''


# --------------------------------------------------------------------------
# Prix
# --------------------------------------------------------------------------
def price_html(p):
    old = f'<span class="price-old">€{p["prix"]:.2f}</span> ' if p.get("promo") else ""
    return f'{old}€{p.get("promo", p["prix"]):.2f}'


# --------------------------------------------------------------------------
# Pages produit (LOT 2 — Best-of)
# --------------------------------------------------------------------------
OPTIONAL_TEXT_FIELDS = [
    ("dimensions", "accordion.dimensions"),
    ("materiaux", "accordion.materials"),
    ("entretien", "accordion.care"),
    ("livraison", "accordion.delivery"),
]


def accordion_html(lang, p):
    sections = []
    for field, label_key in OPTIONAL_TEXT_FIELDS:
        val = p.get(field)
        if val and val.get(lang):
            sections.append((s(lang, label_key), val[lang]))
    if not sections:
        return ""
    items = []
    for i, (label, text) in enumerate(sections):
        panel_id = f"panel-{field_slug(label)}-{i}"
        items.append(f'''      <div class="accordion-item">
        <button type="button" class="accordion-trigger" aria-expanded="false" aria-controls="{panel_id}">{esc(label)}</button>
        <div class="accordion-panel" id="{panel_id}" hidden>
          <p>{esc(text)}</p>
        </div>
      </div>''')
    return f'''
    <div class="accordion">
{chr(10).join(items)}
    </div>'''


def field_slug(label):
    return slugify(label) or "section"


def options_html(lang, p):
    """Sélecteurs de variantes — uniquement si le produit déclare "options"."""
    options = p.get("options")
    if not options:
        return ""
    groups = []
    for i, opt in enumerate(options):
        name = opt.get("name", {}).get(lang, "")
        values = opt.get("values", [])
        opts_html = "\n            ".join(
            f'<option value="{esc(v.get(lang, ""))}">{esc(v.get(lang, ""))}</option>' for v in values
        )
        groups.append(f'''      <div class="option-group">
        <label for="option-{i}">{esc(name)}</label>
        <select id="option-{i}" name="option-{i}">
            {opts_html}
        </select>
      </div>''')
    return f'''
    <div class="product-options">
{chr(10).join(groups)}
    </div>'''


def personalisation_html(lang, p):
    """Zone de personnalisation — uniquement si le produit déclare "personalisation"."""
    perso = p.get("personalisation")
    if not perso or not perso.get(lang):
        return ""
    return f'''
    <div class="product-personalisation">
      <label for="perso-text">{s(lang, "label.personalisation")}</label>
      <input type="text" id="perso-text" name="perso-text" placeholder="{esc(perso[lang])}">
    </div>'''


def related_products(p):
    if not p.get("collections"):
        return []
    slug = p["collections"][0]
    return [q for q in products_of(slug) if q["id"] != p["id"]][:4]


def related_html(lang, prefix, p):
    related = related_products(p)
    if not related:
        return ""
    cards = "\n".join(product_card(q, lang, prefix) for q in related)
    return f'''
  <section class="section section-alt" aria-labelledby="related-heading">
    <div class="wrap">
      <h2 class="section-title" id="related-heading">{s(lang, "product.youMayAlsoLike")}</h2>
      <div class="product-grid">
{cards}
      </div>
    </div>
  </section>'''


def product_page(p, lang):
    prefix = "../../../"
    images = p["images"]
    main_img = images[0] if images else ""
    main_w, main_h = image_dimensions(main_img) if main_img else (1000, 1000)
    first_coll = p["collections"][0] if p["collections"] else None
    coll_label = next((c["label"][lang] for c in collections if c["slug"] == first_coll), None)
    current_rootrel = p_product(p["id"], lang)
    alt_paths = alt_product(p["id"])

    availability = "https://schema.org/InStock" if p.get("stock", True) else "https://schema.org/OutOfStock"
    product_ld = json.dumps({
        "@context": "https://schema.org", "@type": "Product",
        "name": p["nom"][lang],
        "image": absolute(main_img) if main_img else "",
        "description": p["description"][lang],
        "inLanguage": lang,
        "brand": {"@type": "Brand", "name": "Chic Celebria"},
        "offers": {
            "@type": "Offer", "url": "https://www.etsy.com/shop/ChicCelebria",
            "priceCurrency": "EUR", "price": str(p.get("promo") or p["prix"]),
            "availability": availability,
            "itemCondition": "https://schema.org/NewCondition",
        },
    }, ensure_ascii=False)

    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": s(lang, "common.home"), "item": absolute(p_home(lang))},
    ]
    if first_coll and coll_label:
        breadcrumb_items.append({"@type": "ListItem", "position": 2, "name": coll_label,
                                  "item": absolute(p_collection(first_coll, lang))})
    breadcrumb_items.append({"@type": "ListItem", "position": len(breadcrumb_items) + 1,
                              "name": p["nom"][lang], "item": absolute(current_rootrel)})
    breadcrumb_ld = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items,
    }, ensure_ascii=False)

    extra_ld = (f'<script type="application/ld+json">\n{product_ld}\n</script>\n'
                f'<script type="application/ld+json">\n{breadcrumb_ld}\n</script>\n')

    head_html = head(lang, prefix, current_rootrel, alt_paths,
                      p["nom"][lang] + " | Chic Celebria", p["description"][lang],
                      "product", main_img, extra_ld)

    if len(images) > 1:
        thumbs = "\n          ".join(
            f'<button type="button" class="gallery-thumb{" is-active" if i == 0 else ""}" data-full="{prefix}{img}" data-alt="{esc(p["nom"][lang])}"><img src="{prefix}{img}" alt="" width="{image_dimensions(img)[0]}" height="{image_dimensions(img)[1]}" loading="lazy"></button>'
            for i, img in enumerate(images)
        )
        gallery_extra = f'\n        <div class="gallery-thumbs">\n          {thumbs}\n        </div>'
    else:
        gallery_extra = ""

    breadcrumb_html = f'<a href="{prefix}{p_home(lang)}">{s(lang, "common.home")}</a>'
    if first_coll and coll_label:
        breadcrumb_html += f' / <a href="{prefix}{p_collection(first_coll, lang)}">{esc(coll_label)}</a>'
    breadcrumb_html += f' / <span>{esc(p["nom"][lang])}</span>'

    body = f'''  <section class="section-tight">
    <div class="wrap">
      <div class="product-layout">
        <div class="product-gallery">
          <div class="gallery-main">
            <img src="{prefix}{main_img}" alt="{esc(p["nom"][lang])}" width="{main_w}" height="{main_h}" fetchpriority="high">
          </div>{gallery_extra}
        </div>
        <div class="product-info">
          <p class="breadcrumb">{breadcrumb_html}</p>
          <h1>{esc(p["nom"][lang])}</h1>
          <p class="product-price">{price_html(p)}</p>
          <p class="product-desc">{esc(p["description"][lang])}</p>{options_html(lang, p)}{personalisation_html(lang, p)}{accordion_html(lang, p)}
          <div class="product-cta">
            <a class="btn btn-primary btn-lg" href="#" data-etsy-cta>{s(lang, "common.shopOnEtsy")}</a>
            <p class="product-cta-note">{s(lang, "product.ctaNote")}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
{related_html(lang, prefix, p)}'''

    return page_shell(lang, prefix, f"product-{p['id']}", body, alt_paths, head_html)


# --------------------------------------------------------------------------
# Cartes produit (grilles collection / accueil / produits liés)
# --------------------------------------------------------------------------
def product_card(p, lang, prefix, lcp=False):
    ptype = "personalised" if "personalised" in p.get("collections", []) else "decor"
    img = p["images"][0] if p["images"] else ""
    w, h = image_dimensions(img) if img else (1000, 1000)
    badge = f'<span class="p-card-badge">{s(lang, "common.badgePersonalised")}</span>' if ptype == "personalised" else ""
    img_attrs = 'fetchpriority="high"' if lcp else 'loading="lazy"'
    return f'''        <article class="p-card" data-name="{esc(p['nom'][lang])}" data-price="{p['prix']}" data-type="{ptype}">
          <a class="p-card-media" href="{prefix}{p_product(p['id'], lang)}">
            {badge}
            <img class="img-main" src="{prefix}{img}" alt="{esc(p['nom'][lang])}" width="{w}" height="{h}" {img_attrs}>
          </a>
          <div class="p-card-body">
            <a class="p-card-title" href="{prefix}{p_product(p['id'], lang)}">{esc(p['nom'][lang])}</a>
            <p class="p-card-price">{price_html(p)}</p>
          </div>
        </article>'''


# --------------------------------------------------------------------------
# Pages collection
# --------------------------------------------------------------------------
def collection_page(c, lang):
    slug = c["slug"]
    prefix = "../../../"
    items = products_of(slug)
    cards = "\n".join(product_card(p, lang, prefix, lcp=(i == 0)) for i, p in enumerate(items))
    accent = " accent-halloween" if slug == "halloween" else ""
    current_rootrel = p_collection(slug, lang)
    alt_paths = alt_collection(slug)

    breadcrumb_ld = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": s(lang, "common.home"), "item": absolute(p_home(lang))},
            {"@type": "ListItem", "position": 2, "name": s(lang, "common.celebrations"), "item": absolute(p_collections_index(lang))},
            {"@type": "ListItem", "position": 3, "name": c["label"][lang], "item": absolute(current_rootrel)},
        ],
    }, ensure_ascii=False)
    extra_ld = f'<script type="application/ld+json">\n{breadcrumb_ld}\n</script>\n'

    title = c["label"][lang] + " | Chic Celebria"
    desc = STRINGS[lang].get("collections.desc", "")
    head_html = head(lang, prefix, current_rootrel, alt_paths, title, desc, "website", extra_ld=extra_ld)

    body = f'''  <section class="collection-hero{accent}">
    <div class="wrap">
      <p class="breadcrumb"><a href="{prefix}{p_home(lang)}">{s(lang, "common.home")}</a> / <a href="{prefix}{p_collections_index(lang)}">{s(lang, "common.celebrations")}</a> / <span>{esc(c["label"][lang])}</span></p>
      <span class="eyebrow">{s(lang, "common.seasonalEdit")}</span>
      <h1>{esc(c["label"][lang])}</h1>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="toolbar">
        <div class="toolbar-filters">
          <div class="toolbar-field">
            <label for="filter-type">{s(lang, "toolbar.type")}</label>
            <select id="filter-type">
              <option value="all">{s(lang, "toolbar.all")}</option>
              <option value="decor">{s(lang, "toolbar.decor")}</option>
              <option value="personalised">{s(lang, "toolbar.personalised")}</option>
            </select>
          </div>
          <div class="toolbar-field">
            <label for="filter-price">{s(lang, "toolbar.price")}</label>
            <select id="filter-price">
              <option value="all">{s(lang, "toolbar.all")}</option>
              <option value="under-15">{s(lang, "toolbar.under15")}</option>
              <option value="15-25">{s(lang, "toolbar.15to25")}</option>
              <option value="over-25">{s(lang, "toolbar.over25")}</option>
            </select>
          </div>
          <div class="toolbar-field">
            <label for="sort-by">{s(lang, "toolbar.sort")}</label>
            <select id="sort-by">
              <option value="name-asc">{s(lang, "toolbar.nameAsc")}</option>
              <option value="name-desc">{s(lang, "toolbar.nameDesc")}</option>
              <option value="price-asc">{s(lang, "toolbar.priceAsc")}</option>
              <option value="price-desc">{s(lang, "toolbar.priceDesc")}</option>
            </select>
          </div>
        </div>
        <p class="toolbar-count"><span data-result-count data-piece-singular="{esc(s(lang, "toolbar.piece"))}" data-piece-plural="{esc(s(lang, "toolbar.pieces"))}">{esc(s(lang, "toolbar.piece" if len(items) == 1 else "toolbar.pieces").replace("{n}", str(len(items))))}</span></p>
      </div>

      <div class="product-grid" data-collection-grid>
{cards}
      </div>

      <p class="collection-empty" data-collection-empty hidden>{s(lang, "collection.empty")}</p>
    </div>
  </section>'''

    return page_shell(lang, prefix, f"collection-{slug}", body, alt_paths, head_html)


# --------------------------------------------------------------------------
# Page Celebrations (index des collections)
# --------------------------------------------------------------------------
def celebrations_page(lang):
    prefix = "../../"
    current_rootrel = p_collections_index(lang)
    alt_paths = alt_collections_index()
    cards = ""
    for c in active_collections():
        cards += f'''        <a class="coll-card" href="{prefix}{p_collection(c["slug"], lang)}">{esc(c["label"][lang])}</a>\n'''

    title = s(lang, "collections.title")
    desc = s(lang, "collections.desc")
    head_html = head(lang, prefix, current_rootrel, alt_paths, title, desc, "website")

    body = f'''  <section class="collection-hero">
    <div class="wrap">
      <p class="breadcrumb"><a href="{prefix}{p_home(lang)}">{s(lang, "common.home")}</a> / <span>{s(lang, "common.celebrations")}</span></p>
      <span class="eyebrow">{s(lang, "common.seasonalEdit")}</span>
      <h1>{s(lang, "common.celebrations")}</h1>
      <p>{esc(s(lang, "common.footerTagline"))}</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="product-grid">
{cards}
      </div>
    </div>
  </section>'''

    return page_shell(lang, prefix, "collections", body, alt_paths, head_html)


# --------------------------------------------------------------------------
# Page d'accueil
# --------------------------------------------------------------------------
def home_page(lang):
    prefix = "../"
    current_rootrel = p_home(lang)
    alt_paths = alt_home()

    website_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebSite",
        "name": "Chic Celebria", "url": absolute(current_rootrel),
        "inLanguage": lang,
        "description": s(lang, "home.desc"),
    }, ensure_ascii=False)
    org_ld = json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": "Chic Celebria", "url": absolute(current_rootrel),
        "logo": absolute("assets/logo.png"),
        "sameAs": ["https://www.etsy.com/shop/ChicCelebria"],
    }, ensure_ascii=False)
    extra_ld = (f'<script type="application/ld+json">\n{website_ld}\n</script>\n'
                f'<script type="application/ld+json">\n{org_ld}\n</script>\n')

    og_image = "assets/produits/img-09.jpg"
    # Le hero est en arrière-plan CSS (LCP de la page d'accueil) : on le
    # précharge pour que le navigateur ne le découvre pas seulement après
    # avoir parsé style.css.
    preload = f'<link rel="preload" as="image" fetchpriority="high" href="{prefix}{og_image}">\n'
    head_html = head(lang, prefix, current_rootrel, alt_paths, s(lang, "home.title"), s(lang, "home.desc"),
                      "website", og_image, preload + extra_ld)

    # Collections grid — chaque tuile utilise l'image réelle du premier produit de la collection.
    tiles = []
    for c in active_collections():
        items = products_of(c["slug"])
        if not items:
            continue
        img = items[0]["images"][0] if items[0]["images"] else ""
        w, h = image_dimensions(img) if img else (1000, 1000)
        tiles.append(f'''      <a class="collection-tile reveal" href="{prefix}{p_collection(c["slug"], lang)}">
        <img src="{prefix}{img}" alt="{esc(c["label"][lang])}" width="{w}" height="{h}" loading="lazy">
        <span class="collection-tile-label">
          <h3>{esc(c["label"][lang])}</h3>
          <span>{s(lang, "common.shopTheEdit")}</span>
        </span>
      </a>''')
    tiles_html = "\n".join(tiles)

    # New In — les derniers produits actifs ajoutés au catalogue.
    newest = list(reversed(active_products()[-4:]))
    cards = "\n".join(product_card(p, lang, prefix) for p in newest)

    # Season band — première collection "occasion" par ordre, données réelles.
    season_html = ""
    occ = occasions()
    if occ:
        season_c = occ[0]
        season_items = products_of(season_c["slug"])
        if season_items:
            cta_label = s(lang, "home.season.ctaTemplate").format(label=season_c["label"][lang])
            season_html = f'''
  <section class="season-band" aria-labelledby="season-heading">
    <div class="wrap">
      <div class="season-band-inner">
        <span class="eyebrow">{s(lang, "common.seasonalEdit")}</span>
        <h2 id="season-heading">{esc(season_c["label"][lang])}</h2>
        <div class="season-band-actions">
          <a class="btn btn-light" href="{prefix}{p_collection(season_c["slug"], lang)}">{esc(cta_label)}</a>
        </div>
      </div>
    </div>
  </section>'''

    body = f'''  <section class="hero">
    <div class="wrap hero-inner">
      <h1 class="hero-title">{s(lang, "home.hero.title")}</h1>
      <p class="hero-lead">{s(lang, "home.hero.lead")}</p>
      <div class="hero-actions">
        <a class="btn btn-light" href="{prefix}{p_collections_index(lang)}">{s(lang, "home.hero.cta")}</a>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="collections-heading">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">{s(lang, "home.collections.eyebrow")}</span>
          <h2 class="section-title" id="collections-heading">{s(lang, "home.collections.title")}</h2>
        </div>
      </div>
    </div>
    <div class="collections-grid">
{tiles_html}
    </div>
  </section>

  <section class="section" id="new-in" aria-labelledby="new-in-heading">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">{s(lang, "home.newin.eyebrow")}</span>
          <h2 class="section-title" id="new-in-heading">{s(lang, "home.newin.title")}</h2>
        </div>
      </div>
      <div class="product-grid">
{cards}
      </div>
    </div>
  </section>

  <section class="section section-alt" aria-labelledby="editorial-heading">
    <div class="wrap editorial">
      <div class="editorial-media reveal">
        <img src="{prefix}assets/produits/img-11.jpg" alt="{esc(s(lang, "alt.livingroom"))}" width="{image_dimensions("assets/produits/img-11.jpg")[0]}" height="{image_dimensions("assets/produits/img-11.jpg")[1]}" loading="lazy">
      </div>
      <div class="editorial-copy reveal">
        <h2 class="section-title" id="editorial-heading">{s(lang, "home.editorial.title")}</h2>
        <p>{esc(s(lang, "home.editorial.body"))}</p>
      </div>
    </div>
  </section>
{season_html}

  <section class="newsletter" aria-labelledby="newsletter-heading">
    <div class="wrap newsletter-inner">
      <h2 class="section-title" id="newsletter-heading">{s(lang, "home.newsletter.title")}</h2>
      <p class="section-lead">{s(lang, "home.newsletter.lead")}</p>
      <form class="newsletter-form" novalidate data-thanks="{esc(s(lang, "home.newsletter.thanks"))}" data-error="{esc(s(lang, "home.newsletter.error"))}">
        <label class="sr-only" for="newsletter-email">{s(lang, "home.newsletter.emailLabel")}</label>
        <input type="email" id="newsletter-email" name="email" placeholder="{esc(s(lang, "home.newsletter.placeholder"))}" required autocomplete="email">
        <button type="submit" class="btn btn-primary">{s(lang, "home.newsletter.cta")}</button>
      </form>
      <p class="form-feedback" role="status"></p>
    </div>
  </section>'''

    return page_shell(lang, prefix, "home", body, alt_paths, head_html)


# --------------------------------------------------------------------------
# Page About
# --------------------------------------------------------------------------
def about_page(lang):
    prefix = "../"
    current_rootrel = p_about(lang)
    alt_paths = alt_about()

    org_ld = json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": "Chic Celebria", "url": absolute(p_home(lang)),
        "logo": absolute("assets/logo.png"),
        "sameAs": ["https://www.etsy.com/shop/ChicCelebria"],
    }, ensure_ascii=False)
    extra_ld = f'<script type="application/ld+json">\n{org_ld}\n</script>\n'

    head_html = head(lang, prefix, current_rootrel, alt_paths, s(lang, "about.title"), s(lang, "about.desc"),
                      "website", "assets/produits/img-10.jpg", extra_ld)

    has_personalisation = any(p.get("personalisation") or p.get("options") for p in active_products())
    perso_section = ""
    if has_personalisation:
        perso_section = f'''
      <h2>{s(lang, "about.perso.h2")}</h2>
      <p>{esc(s(lang, "about.perso.p"))}</p>'''

    body = f'''  <section class="page-hero">
    <div class="wrap">
      <h1>{s(lang, "about.hero.h1")}</h1>
      <p>{esc(s(lang, "about.hero.p"))}</p>
    </div>
  </section>

  <section class="story">
    <div class="wrap story-inner">
      <p>{esc(s(lang, "about.story.p1"))}</p>

      <h2>{s(lang, "about.how.h2")}</h2>
      <p>{esc(s(lang, "about.how.p"))}</p>{perso_section}
    </div>
  </section>

  <section class="section">
    <div class="wrap editorial">
      <div class="editorial-media reveal">
        <img src="{prefix}assets/produits/img-10.jpg" alt="{esc(s(lang, "alt.livingroom"))}" width="{image_dimensions("assets/produits/img-10.jpg")[0]}" height="{image_dimensions("assets/produits/img-10.jpg")[1]}" loading="lazy">
      </div>
      <div class="editorial-copy reveal">
        <h2 class="section-title">{s(lang, "about.editorial.h2")}</h2>
        <p>{esc(s(lang, "about.editorial.p"))}</p>
      </div>
    </div>
  </section>

  <section class="section cta-panel">
    <h2>{s(lang, "about.cta.h2")}</h2>
    <p>{esc(s(lang, "about.cta.p"))}</p>
    <div class="hero-actions" style="justify-content: center; display: flex; gap: 1rem; flex-wrap: wrap;">
      <a class="btn btn-primary" href="{prefix}{p_collections_index(lang)}">{s(lang, "about.cta.primary")}</a>
      <a class="btn btn-outline" href="#" data-etsy-cta>{s(lang, "common.shopOnEtsy")}</a>
    </div>
  </section>'''

    return page_shell(lang, prefix, "about", body, alt_paths, head_html)


# --------------------------------------------------------------------------
# 404 racine (une seule page, servie par l'hébergeur quelle que soit la
# langue de l'URL demandée — contenu en anglais, non indexée).
# --------------------------------------------------------------------------
def notfound_page():
    lang, prefix = DEFAULT_LANG, ""
    alt_paths = alt_home()
    head_html = head(lang, prefix, "404.html", None,
                      s(lang, "e404.title"), s(lang, "e404.desc"), "website")
    head_html = head_html.replace("</head>", '<meta name="robots" content="noindex">\n</head>')
    body = f'''  <section class="error-page">
    <div class="wrap">
      <p class="error-code" aria-hidden="true">404</p>
      <h1>{s(lang, "e404.h1")}</h1>
      <p>{esc(s(lang, "e404.p"))}</p>
      <div class="error-actions">
        <a class="btn btn-primary" href="{prefix}{p_home(lang)}">{s(lang, "e404.backHome")}</a>
        <a class="btn btn-outline" href="{prefix}{p_collections_index(lang)}">{s(lang, "about.cta.primary")}</a>
      </div>
    </div>
  </section>'''
    return page_shell(lang, prefix, "404", body, alt_paths, head_html)


# --------------------------------------------------------------------------
# Redirections racine (index.html / about.html) — la racine du site n'a pas
# de langue propre, elle renvoie vers /en/.
# --------------------------------------------------------------------------
def redirect_page(target_rootrel):
    target = absolute(target_rootrel)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={target_rootrel}">
<link rel="canonical" href="{target}">
<title>Chic Celebria</title>
</head>
<body>
<p><a href="{target_rootrel}">Continue to Chic Celebria</a></p>
</body>
</html>'''


# --------------------------------------------------------------------------
# sitemap.xml / robots.txt — générés depuis les mêmes données de build.
# --------------------------------------------------------------------------
def sitemap_entries():
    entries = [alt_home(), alt_about(), alt_collections_index()]
    for c in active_collections():
        entries.append(alt_collection(c["slug"]))
    for p in active_products():
        entries.append(alt_product(p["id"]))
    return entries


def gen_sitemap():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for alt in sitemap_entries():
        for lang in LANGS:
            lines.append("  <url>")
            lines.append(f"    <loc>{absolute(alt[lang])}</loc>")
            for l2 in LANGS:
                lines.append(f'    <xhtml:link rel="alternate" hreflang="{l2}" href="{absolute(alt[l2])}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{absolute(alt[DEFAULT_LANG])}"/>')
            lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def gen_robots():
    return f'''User-agent: *
Allow: /
Disallow: /fiches.html
Disallow: /fiches.json

Sitemap: {SITE}/sitemap.xml
'''


# --------------------------------------------------------------------------
# Écriture des fichiers
# --------------------------------------------------------------------------
def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    for lang in LANGS:
        write(p_home(lang), home_page(lang))
        write(p_about(lang), about_page(lang))
        write(p_collections_index(lang) + "index.html", celebrations_page(lang))
        for c in active_collections():
            write(p_collection(c["slug"], lang) + "index.html", collection_page(c, lang))
        for p in active_products():
            write(p_product(p["id"], lang) + "index.html", product_page(p, lang))

    write("index.html", redirect_page(p_home(DEFAULT_LANG)))
    write("about.html", redirect_page(p_about(DEFAULT_LANG)))
    write("404.html", notfound_page())
    write("sitemap.xml", gen_sitemap())
    write("robots.txt", gen_robots())

    print(f"OK — {len(active_products())} produits x {len(LANGS)} langues, "
          f"{len(active_collections())} collections x {len(LANGS)} langues, "
          f"+ index/about/404/sitemap/robots generes.")


if __name__ == "__main__":
    main()
