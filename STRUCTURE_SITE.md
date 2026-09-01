# STRUCTURE COMPLÈTE DU SITE — CHIC CELEBRIA (Best-of, multilingue)

## 1. Vue d'ensemble
- Site statique (HTML/CSS/JS natifs, zéro framework, zéro dépendance), **data-driven** : toutes les pages sont GÉNÉRÉES par `build.py`, qui lit `products.json`, `collections.json` et `i18n-strings.json`.
- Déployé sur GitHub Pages : `projethermes/chiccelebria-demo` → https://projethermes.github.io/chiccelebria-demo/
- Vente via Etsy (pas de panier, pas de checkout). Tous les CTA renvoient vers la boutique Etsy via `window.CHIC.etsyShopUrl`.
- **5 langues avec de vraies URLs** : `/en/ /es/ /fr/ /it/ /de/`, chacune un site statique complet et 100 % indexable — plus d'i18n JS mono-URL. Chaque page est générée directement dans sa langue (pas de traduction côté client, pas de flash de contenu non traduit).
- `BRIEF_REFONTE_V3.md` (à la racine) : brief de direction artistique premium (palette, typo, interdit du « design IA ») — à respecter lors de toute refonte.

## 2. Arborescence des fichiers
```
chiccelebria-demo/
├── build.py                 ← GÉNÉRATEUR (lit les JSON, écrit tout le site)
├── products.json            ← DONNÉES produits (39 entrées, 39 actives)
├── collections.json         ← DONNÉES collections (7 entrées, 7 actives)
├── i18n-strings.json        ← DONNÉES textes d'interface communs (5 langues) — voir §4
├── script.js                ← Interactions : menu mobile, header sticky, sélecteur de langue,
│                                filtres/tri collections, CTA Etsy, newsletter, accordéon, galerie
├── style.css                ← Design system complet (variables CSS + tout le style)
├── index.html, about.html   ← GÉNÉRÉS : redirections (meta refresh + canonical) vers /en/…
├── 404.html                 ← GÉNÉRÉ : page 404 racine, en anglais, seule page volontairement
│                                noindex (page d'erreur technique, pas une page de contenu)
├── sitemap.xml               ← GÉNÉRÉ : toutes les URLs actives × 5 langues, hreflang inclus
├── robots.txt                 ← GÉNÉRÉ : Allow: /, référence le sitemap
├── assets/                   ← Inchangé par build.py : logo, photos produits, site-config.js
│   ├── site-config.js       ← window.CHIC = { etsyShopUrl, currency, locale }
│   ├── produits/, sourcing/ ← photos produits réelles
│   └── …
├── en/  es/  fr/  it/  de/   ← GÉNÉRÉS, un arbre complet par langue :
│   ├── index.html            ← Accueil
│   ├── about.html             ← About
│   ├── collections/index.html ← page "Celebrations" (index des collections)
│   ├── collections/<slug-langue>/index.html   ← une par collection active
│   └── products/<slug-langue>/index.html      ← une par produit actif
└── tests/                     ← voir §8
```
Les anciens répertoires racine `products/<id>/` et `collections/<slug>/` (structure
mono-langue, pré-Best-of) ainsi que `i18n.js` / `i18n-data.js` (moteur de traduction
côté client) ont été supprimés : ils sont entièrement remplacés par les arbres `en/ es/
fr/ it/ de/`.

## 3. Système data-driven — RÈGLE ABSOLUE
**Ne jamais éditer les pages générées à la main** (tout ce qui est sous `en/ es/ fr/ it/
de/`, plus `index.html`, `about.html`, `404.html`, `sitemap.xml`, `robots.txt` à la
racine). Le workflow :
1. On édite `products.json`, `collections.json` et/ou `i18n-strings.json`.
2. On lance `python3 build.py`.
3. Le script régénère l'intégralité du site ci-dessus, pour les 5 langues.

### Format products.json (39 entrées, 39 actives)
```json
{
  "id": "halloween-doormat",            // identifiant stable (dossier produit en anglais)
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

### Format collections.json (7 entrées actives)
```json
{
  "slug": "halloween",                  // identifiant stable (dossier collection en anglais)
  "label": { "en": "Halloween", "es": "Halloween", "fr": "Halloween", "it": "Halloween", "de": "Halloween" },
  "type": "occasion",                   // "occasion" (menu) ou "tag" (filtre uniquement)
  "ordre": 1,                           // ordre dans le menu / grille "Shop by Occasion"
  "actif": true
}
```
Collections actives : halloween, christmas, black-friday, winter, anniversaire (type
occasion) + gifts, personalised (type tag).

### Slugs traduits — dérivés, jamais une table séparée
Chaque produit/collection a une URL différente par langue, mais **aucune table de
traduction de slugs n'est maintenue à la main** : `build.py` dérive automatiquement le
slug de chaque langue à partir de `nom[lang]` (produits) ou `label[lang]` (collections)
via une fonction `slugify()` (minuscules, accents retirés, ponctuation → tirets), avec
dédoublonnage (`-2`, `-3`…) en cas de collision dans une même langue. Exemple :
`skeleton-hair-claw` (en) ↔ `pince-a-cheveux-squelette` (fr) ↔ `skelett-haarspange` (de).

## 4. i18n-strings.json — textes d'interface communs
Contient les chaînes qui ne dépendent pas d'un produit/collection précis (navigation,
boutons, page About, 404, filtres de collection, libellés d'accordéon…), pour les 5
langues, au format `{"en": {"cle": "valeur", ...}, "es": {...}, ...}`. Utilisé par
`build.py` via `s(lang, "cle")`. Les textes produit/collection viennent directement de
`products.json`/`collections.json` (`nom`, `description`, `label`) — jamais dupliqués
dans `i18n-strings.json`.

Le HTML généré est **déjà dans la bonne langue** (`<html lang="fr">`, textes en dur) :
il n'y a plus de traduction côté client, plus de `data-i18n`, plus de flash de contenu
non traduit. `script.js` ne fait que lire quelques textes déjà traduits posés en
attributs `data-*` par `build.py` (ex. `data-piece-singular` / `data-piece-plural` pour
le compteur de résultats, `data-thanks` / `data-error` pour la newsletter).

## 5. SEO structurel multilingue
- **Canonical auto-référent** sur chaque page (`<link rel="canonical">` pointe vers
  l'URL absolue de la page elle-même).
- **hreflang réciproques** : chaque page liste une alternance vers les 5 langues + un
  `hreflang="x-default"` pointant vers la version `/en/`. Testé par
  `tests/test_seo_multilang.py` (réciprocité stricte : si A référence B, B référence A
  avec exactement le même jeu d'alternates).
- **sitemap.xml** généré depuis les mêmes données que le site (produits/collections
  actifs × 5 langues + accueil/about/index des collections), avec les balises
  `<xhtml:link rel="alternate" hreflang="…">` par URL. Ne jamais le maintenir à la
  main.
- **robots.txt** : `Allow: /`, référence le sitemap. Aucune règle `Disallow` : il
  n'existe plus de page privée servie depuis la racine du dépôt (voir §11 pour la
  séparation public/privé du back-office).
- **Aucun `noindex`** sur les pages `en/ es/ fr/ it/ de/` ni sur les redirections
  racine `index.html`/`about.html`. La seule exception volontaire est `404.html`
  (page d'erreur technique servie par l'hébergeur quelle que soit la langue
  demandée, jamais un contenu de destination).
- JSON-LD : `WebSite` + `Organization` sur l'accueil et About, `Product` +
  `BreadcrumbList` sur les fiches produit, `BreadcrumbList` sur les pages
  collection — toujours avec des données réelles (prix, images, disponibilité).

## 6. Fiche produit Best-of (LOT 2)
- Galerie : image unique par défaut ; vignettes de galerie générées automatiquement
  si `images` contient plus d'une entrée (aucun produit actuel n'en a plusieurs).
- Sections accordéon (Dimensions / Materials / Care / Delivery) : générées
  **uniquement** si le champ optionnel correspondant existe pour la langue courante
  (voir §3). Aucune ne s'affiche aujourd'hui — c'est attendu, pas un bug.
- Sélecteurs d'options / champ de personnalisation : générés uniquement si
  `options`/`personalisation` sont déclarés sur le produit. 0 produit actuel n'en
  déclare — aucun sélecteur ne doit apparaître tant que la donnée n'existe pas.
- Produits liés (« You May Also Like ») : jusqu'à 4 produits actifs partageant la
  première collection du produit, jamais le produit courant.
- Aucune image n'est jamais partagée entre deux produits actifs (vérifié par un
  test dédié).

## 7. Performance images (LOT 4)
- `image_dimensions()` dans `build.py` lit les dimensions réelles de chaque image
  (JPEG/PNG/WebP, parsing d'en-têtes en stdlib pur — aucune dépendance externe
  disponible dans cet environnement de build) et les pose en `width`/`height`
  explicites partout (cartes produit, tuiles de collection, galerie, images
  éditoriales). Évite tout décalage de mise en page (CLS).
- L'image LCP de chaque page est marquée `fetchpriority="high"` et jamais
  `loading="lazy"` : image principale d'une fiche produit, première carte d'une
  grille de collection. Le hero de l'accueil (arrière-plan CSS) est préchargé via
  `<link rel="preload" as="image" fetchpriority="high">`.
- Conversion WebP **non appliquée** : aucun outil (Pillow, cwebp, ImageMagick) n'est
  disponible dans cet environnement sans installer une dépendance ; conformément au
  brief, les images existantes sont servies telles quelles plutôt que de casser le
  rendu ou d'ajouter une dépendance.
- Risque connu (préexistant, non introduit par le pipeline) : au moins une image
  produit (`assets/sourcing/skeleton-hair-claw.jpg`) est un visuel abstrait/cassé,
  pas une vraie photo produit ; au moins deux images produit portent du texte
  marketing gravé dans l'image (bannière « CUSTOM YOUR PICTURE », mention « 6 PCS »)
  — à re-sourcer côté `products.json`, hors périmètre du générateur.

## 8. Design system (style.css)
- Palette (variables CSS) : fond ivoire `#FAF7F1`, `--ink: #1C1917`, `--muted:
  #6E675D`, `--champagne: #C7AE7C`, `--sable: #E4DAC6`, `--line: #E0D8CA` ; accent
  saisonnier halloween `#B85C2E`, christmas `#8C2B2B`/`#3A5A40`. Pas de dégradé
  décoratif, pas de glassmorphism.
- Typo : Fraunces (titres/display) + Jost (texte/nav/boutons/prix), Google Fonts (un
  seul `<link>`).
- Sélecteur de langue (`.lang-switch select`) : bordure et chevron champagne,
  survol/focus discrets — cohérent avec le design system plutôt qu'un `<select>`
  neutre du navigateur.
- Menu mobile overlay : panneau plein-largeur, hauteur `80vh` avec défilement
  interne (dimensionné pour les 5 collections actives + New In/Celebrations/About,
  sans troncature si le catalogue de collections grandit encore).
- Accessibilité inchangée : skip-link, `:focus-visible`, `prefers-reduced-motion`.

## 9. Règles à respecter impérativement
1. **CTA produit = « SHOP ON ETSY »** → tous les liens passent par
   `window.CHIC.etsyShopUrl` (attribut `data-etsy-cta`). Pas de panier, pas de
   checkout, pas de prix fictif, pas de faux avis/badge/stock.
2. **Ne jamais éditer un fichier généré à la main** — voir §3.
3. Pas de librairie externe (pas de jQuery/framework). JS vanilla, pas de nouvelle
   dépendance Python (stdlib uniquement).
4. Après toute modification : `python3 build.py` sans erreur, puis
   `python3 -m unittest discover -s tests -v` entièrement au vert.
5. Ne jamais inventer une caractéristique produit (dimensions, matériaux, avis,
   options…) pour remplir l'interface — voir §6.

## 10. Tests
Tout tourne en `unittest` stdlib (pas de pytest) :
```
python3 -m unittest discover -s tests -v
```
- `tests/_build_helper.py` : helper partagé, exécute le vrai `build.py` (jamais
  réimplémenté) dans une copie temporaire isolée du dépôt — aucun test ne touche
  l'arbre de travail réel.
- `tests/test_build_idempotence.py` : deux builds consécutifs sans modification des
  sources doivent produire des fichiers strictement identiques, pour les 5 langues.
- `tests/test_build_prunes_stale_pages.py` : supprimer ou renommer un produit (donc
  changer son slug) doit faire disparaître son ancien dossier `products/<slug>/` au
  build suivant — sinon des pages fantômes (hors sitemap, plus liées depuis le site,
  mais toujours en ligne à leur ancienne URL) s'accumulent. Voir
  `prune_stale_pages()` dans `build.py`.
- `tests/test_seo_multilang.py` : canonical auto-référent, hreflang réciproques +
  x-default, absence de noindex en production, sitemap.xml synchronisé avec les
  pages générées, robots.txt indexable, slugs réellement traduits.
- `tests/test_product_page.py` : sections accordéon/options/personnalisation
  strictement conditionnelles aux données, JSON-LD Product + BreadcrumbList présent,
  aucune image partagée entre deux produits.
- `tests/test_images_performance.py` : dimensions d'image réelles, `fetchpriority`
  sur l'image LCP de chaque type de page, préchargement du hero de l'accueil.
- `tests/test_links_and_html.py` : aucun lien interne ou référence d'asset cassé sur
  l'ensemble du site généré (5 langues), HTML bien formé (balises équilibrées, un
  seul `<html>/<head>/<body>` par page), nombre exact de produits/collections actifs
  générés par langue.
- `tests/test_no_sourcing_leak.py` : garde-fou « Option A » — aucune donnée de
  sourcing (lien fournisseur, prix d'achat, marge…) ni outil d'admin ne doit
  jamais réapparaître dans `git ls-files` ou dans la sortie de `build.py`. C'est
  la spécification de référence pour la séparation public/privé — voir §11.

## 11. Back-office (admin) — conception, hors dépôt

Le back-office (`admin_server.py` + `admin/admin.html`) permet de gérer le
catalogue (produits/collections/réglages, upload photo, relance de build)
sans toucher à Git/JSON/Python — y compris les champs optionnels du schéma
Best-of (dimensions, matériaux, entretien, livraison, personnalisation ;
repliés dans un bloc « Détails complémentaires » de l'éditeur produit,
vide par défaut). Il tourne **uniquement en local** (jamais
déployé sur GitHub Pages) et son code n'est **pas suivi par Git** dans ce
dépôt (`.gitignore` : `admin/`, `admin_server.py`) — le dépôt étant servi
tel quel par GitHub Pages depuis la racine, tout fichier commité sous
`admin/` deviendrait automatiquement accessible publiquement. Le code
complet et à jour vit dans `~/.hermes/private/chiccelebria/admin/`.

**Séparation stricte des champs privés.** `products.json` est la source de
vérité du site *public* : il ne doit jamais contenir de champ de sourcing
interne (`lien_achat`, `prix_achat`, `marge_interne`, `fournisseur`,
`cout_sourcing`, `note_va` — la liste exacte vérifiée par
`tests/test_no_sourcing_leak.py`). `admin_server.py` retire ces champs de
tout produit avant de l'écrire dans `products.json` et les stocke à part
dans `~/.hermes/private/chiccelebria/products_prive.json` (une entrée par
id de produit) ; il les refusionne en mémoire uniquement pour la réponse
de `/api/state`, afin que l'éditeur du back-office les affiche sans jamais
les persister dans le dépôt. Toute nouvelle donnée sensible ajoutée à
l'éditeur doit suivre le même chemin (ajouter le champ à la liste
`PRIVATE_PRODUCT_FIELDS` dans `admin_server.py`), jamais un champ direct
dans le schéma `products.json`.

**Liste produits : recherche/filtres, aperçu, duplication.** Avec 39 fiches, la
liste produits du back-office propose une recherche (nom/id), un filtre par
collection et un filtre par état (actif/inactif). Chaque ligne propose un lien
« Voir ↗ » vers la fiche publique en ligne (calculé depuis `settings.site_url`
et le même algorithme de slug que `build.py`, uniquement si le produit est
actif — un produit inactif n'a pas de page générée) et un bouton « Dupliquer »
qui pré-remplit un nouveau produit avec toutes les données de la fiche source
(textes 5 langues, prix, collections, photos, champs privés) sauf l'id, à
définir. Pratique pour ajouter une variante ou un produit très proche d'un
existant sans tout retaper. L'éditeur produit avertit avant de quitter s'il y a
des modifications non enregistrées (bouton Retour/Annuler ou fermeture de
l'onglet).

**Serveur admin : sert aussi les images.** `admin_server.py` sert les fichiers
sous `/assets/…` (photos produits) en plus de `/admin.html` et de l'API — sans
cela, les vignettes de la liste produits et les photos de l'éditeur ne
s'affichent jamais dans le back-office. Pas d'auth requise sur ces fichiers
(déjà publics sur le site), protection anti-traversal (le chemin résolu doit
rester sous la racine du dépôt).
