# STRUCTURE COMPLÈTE DU SITE — CHIC CELEBRIA

## 1. Vue d'ensemble
- Site statique (HTML/CSS/JS natifs, zéro framework, zéro dépendance), **data-driven** : les pages produit et collection sont GÉNÉRÉES par un script Python `build.py` qui lit deux fichiers JSON.
- Déployé sur GitHub Pages : `projethermes/chiccelebria-demo` → https://projethermes.github.io/chiccelebria-demo/
- Vente via Etsy (pas de panier, pas de checkout). Tous les CTA renvoient vers la boutique Etsy.
- 5 langues : en / es / fr / it / de, bascule côté client.
- Le contenu du site est en ANGLAIS (le multilingue est une couche de traduction par-dessus).
- `BRIEF_REFONTE_V3.md` (à la racine) : brief de direction artistique premium (palette, typo, interdit du « design IA ») — à respecter lors de toute refonte.

## 2. Arborescence des fichiers
```
chiccelebria-demo/
├── build.py                 ← GÉNÉRATEUR (lit les JSON, écrit les pages HTML)
├── products.json            ← DONNÉES produits (18 entrées)
├── collections.json         ← DONNÉES collections (7 entrées)
├── i18n-data.js             ← GÉNÉRÉ par build.py (toutes les traductions, 5 langues)
├── i18n.js                  ← Moteur de traduction côté client (bascule de langue, localStorage)
├── script.js                ← Interactions : menu mobile, header sticky, filtres/tri collections, CTA Etsy, newsletter
├── style.css                ← Design system complet (variables CSS + tout le style)
├── index.html               ← Homepage (header/footer régénérés par build.py)
├── about.html               ← Page About (header/footer régénérés)
├── 404.html                 ← Page 404 (header/footer régénérés)
├── fiches.html              ← ⚠️ ESPACE VENDEUR INTERNE — NE PAS TOUCHER
├── fiches.json              ← ⚠️ NE PAS TOUCHER (données de l'espace vendeur)
├── sitemap.xml
├── robots.txt               ← disallow /fiches.html et /fiches.json
├── assets/
│   ├── site-config.js       ← window.CHIC = { etsyShopUrl, currency, locale } — lien Etsy centralisé
│   ├── logo.png, banniere1.png, banniere2.png, deco2.webp, macrame.webp, tapestry.jpg
│   ├── produits/img-01.jpg … img-12.jpg
│   └── sourcing/*.jpg       ← photos produits actuelles
├── collections/
│   ├── index.html           ← GÉNÉRÉ : page « Celebrations » (index des collections)
│   ├── halloween/index.html ← GÉNÉRÉ
│   ├── christmas/index.html ← GÉNÉRÉ
│   ├── gifts/index.html     ← GÉNÉRÉ
│   ├── personalised/index.html ← GÉNÉRÉ
│   └── winter/index.html    ← GÉNÉRÉ
└── products/<id>/index.html ← GÉNÉRÉ, un dossier par produit (17 produits actifs)
```

## 3. Système data-driven — RÈGLE ABSOLUE
**Ne jamais éditer les pages générées à la main.** Le workflow :
1. On édite `products.json` et/ou `collections.json`.
2. On lance `python3 build.py`.
3. Le script régénère : `i18n-data.js`, toutes les pages `products/<id>/`, toutes les pages `collections/<slug>/`, `collections/index.html`, et réinjecte header/footer dans `index.html`, `about.html`, `404.html` (les contenus `<main>` de ces 3 pages statiques sont préservés).

### Format products.json (39 entrées, 38 actifs)
```json
{
  "id": "halloween-doormat",            // slug de base (utilisé pour l'URL en anglais)
  "nom": { "en": "…", "es": "…", "fr": "…", "it": "…", "de": "…" },
  "description": { "en": "…", "es": "…", "fr": "…", "it": "…", "de": "…" },
  "prix": 34.99,                        // en EUR
  "images": ["assets/sourcing/tapis.jpg"],  // 1 ou plusieurs — >1 active la galerie avec vignettes
  "collections": ["halloween"],         // slugs de collections
  "stock": true,
  "actif": true,                        // false = masqué du site
  "promo": 27.99                        // optionnel — prix barré si présent

  // Champs optionnels Best-of (LOT 2) — chacun n'est rendu sur la fiche
  // produit QUE s'il est présent pour la langue courante. Aucun produit du
  // catalogue actuel ne les déclare : ne jamais en inventer une valeur.
  , "dimensions": { "en": "…" }         // accordéon "Dimensions"
  , "materiaux": { "en": "…" }          // accordéon "Materials"
  , "entretien": { "en": "…" }          // accordéon "Care"
  , "livraison": { "en": "…" }          // accordéon "Delivery"
  , "options": [                        // sélecteurs de variantes (taille, coloris…)
      {"name": {"en": "Size"}, "values": [{"en": "Small"}, {"en": "Large"}]}
    ]
  , "personalisation": { "en": "e.g. a name or short message" }  // champ + indice de personnalisation
}
```

Les URLs produit sont désormais localisées : le slug de chaque langue est
dérivé automatiquement de `nom[lang]` (jamais d'une table séparée), avec
dédoublonnage si deux produits traduisent vers le même slug dans une langue.

### Format collections.json (7 entrées)
```json
{
  "slug": "halloween",
  "label": { "en": "Halloween", "es": "Navidad", "fr": "Noël", "it": "Natale", "de": "Weihnachten" },
  "type": "occasion",                   // "occasion" ou "tag"
  "ordre": 1,                           // ordre dans le menu
  "actif": true
}
```
Collections actuelles : halloween (actif, 9 produits), christmas (actif, 3), winter (actif, 4), gifts (actif, 3), personalised (actif, 3) — black-friday et anniversaire existent mais `actif: false`.

## 4. Système i18n (5 langues)
- `build.py` génère `i18n-data.js` : un objet `window.CHIC_I18N_DATA` avec des clés `p.<id>.title/desc`, `coll.<slug>.label/hero/metaTitle`, + clés communes.
- `i18n.js` (côté client) : sélecteur de langue dans le header (EN/ES/FR/IT/DE), remplace les textes via attributs `data-i18n`, choix mémorisé (localStorage).
- Le HTML de base est en anglais ; chaque texte traduisible porte `data-i18n="clé"`.

## 5. URLs et pages
- `/` (homepage) · `/about.html` · `/404.html` · `/fiches.html` (interne)
- `/collections/` · `/collections/halloween/` · `/collections/christmas/` · `/collections/gifts/` · `/collections/personalised/` · `/collections/winter/`
- `/products/<id>/` (17 produits actifs)

## 6. Design system (style.css)
- Palette (variables CSS) : fond ivoire `#FAF7F1`, `--ink: #1C1917`, `--muted: #6E675D`, `--champagne: #C7AE7C`, `--sable: #E4DAC6`, `--line: #E0D8CA` ; accent saisonnier halloween `#B85C2E`, christmas `#8C2B2B`/`#3A5A40`.
- Typo : Fraunces (titres/display) + Jost (texte/nav/boutons/prix), Google Fonts (un seul <link>).
- Style : premium clair, espaces blancs, l'image domine, animations discrètes, `prefers-reduced-motion` respecté.

## 7. Règles à respecter impérativement
1. **CTA produit = « SHOP ON ETSY »** → tous les liens passent par `window.CHIC.etsyShopUrl` (attribut `data-etsy-cta`). Pas de panier, pas de checkout, pas de prix fictif, pas de faux avis/badge/stock.
2. **`fiches.html` et `fiches.json` : ne pas toucher.**
3. SEO : <title> + meta description uniques par page, canonical, OG, JSON-LD (WebSite + Organization sur toutes les pages, Product + Offer sur les pages produit), sitemap.xml, robots.txt.
4. Pas de librairie externe (pas de jQuery/framework). JS vanilla.
5. Après toute refonte : vérifier que `python3 build.py` tourne sans erreur et régénère tout.
6. Images : garder les fichiers `assets/` existants (logo.png, produits/, sourcing/).

## 8. Tests
- `tests/test_build_idempotence.py` : test de non-régression garantissant que `python3 build.py` est idempotent (deux exécutions consécutives sans modification des sources produisent des fichiers générés strictement identiques) et qu'`index.html`/`about.html`/`404.html` ne contiennent chacun qu'une seule balise `<script src="i18n-data.js"></script>` et une seule `<script src="i18n.js"></script>`.
- Exécution : `python3 -m unittest tests/test_build_idempotence.py -v` (ou `pytest tests/test_build_idempotence.py -v`, aucune dépendance supplémentaire requise).
