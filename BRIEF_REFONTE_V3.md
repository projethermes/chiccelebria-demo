# REFONTE COMPLÈTE — CHIC CELEBRIA (v3 premium)

Tu es le designer + développeur d'une refonte complète. Le dossier courant contient un site « démo IA » qu'il faut remplacer par une vraie marque internationale premium. Lis ce brief, puis DÉTRUIS et RECONSTRUIS le site. Tu as tous les droits d'écriture dans ce dossier.

## ⚠️ LANGUE
Le CONTENU du site (textes, titres, navigation, CTA, SEO) est **100 % en ANGLAIS**.
Tes commentaires/raisonnements internes peuvent être en français.

## IDENTITÉ DE MARQUE (à incarner, pas juste à afficher)
- Nom : **CHIC CELEBRIA**
- Signature : **"Make Every Celebration Yours"**
- Territoire : marque lifestyle de célébrations — Halloween, Noël, anniversaires, mariages, cadeaux, déco saisonnière, produits personnalisables.
- La marque N'EST PAS : du macramé, de la broderie, de l'artisanat français, un « fait main dans notre atelier ». Ne répète JAMAIS ces clichés.
- Ton : sobre, élégant, international, orienté client. Pas de phrases IA creuses (« every piece tells a story », « craftsmanship meets elegance »).

## SURFACE-FIRST (règle anti-« design IA »)
Commit-toi explicitement sur la composition AVANT les couleurs :
- Homepage = surface **Decide/Learn** (une idée par section, hero éditorial).
- Pages collections = surface **Explore** (grille + filtres, pas de blabla).
- Pages produit = surface **Decide/Learn** (photo dominante, infos, CTA).
INTERDIT : le réflexe « hero centré + 3 cartes égales » partout. Chaque section doit avoir UNE intention claire et une composition propre.

## INTERDICTIONS ABSOLUES (design IA / slop)
- Pas de gradients génériques, pas de glassmorphism, pas d'emojis.
- Pas d'icônes décoratives inutiles, pas de « feature grid » avec icône au-dessus de chaque titre.
- Pas de faux chiffres/métriques (« 10 000 clients », « 4.9/5 », « +500% »).
- Pas de cartes empilées partout, pas d'ombres excessives, pas de boutons arrondis partout.
- Pas de carrousels inutiles, pas de parallax lourd, pas de scroll hijacking.
- Pas de faux témoignages, pas de faux avis, pas de faux « best-seller », pas de faux « sold out », pas de faux compte à rebours, pas de faux stock.
- Pas de faux numéro de téléphone, pas de faux email, pas de fausse adresse d'atelier, pas de faux historique de société.
- Pas de « stock-photo hero » générique : les images doivent être posées comme un édito.

## DIRECTION ARTISTIQUE
Mélange : mode/lifestyle premium × maison contemporaine × éditorial. Inspirations (sans copier) : Anthropologie, Zara Home, COS, Sézane, boutiques Etsy haut de gamme.
- Grands espaces blancs, photographies importantes, grille propre, sections aérées, contrastes maîtrisés, animations très discrètes (fade léger, hover image).
- L'IMAGE est l'élément principal.

## TYPOGRAPHIE (2 familles max)
- Display/titres (H1, H2, titres de collection) : **Fraunces** (serif éditoriale, graisses 400/500/600, pas d'italique fantaisie).
- Texte/nav/boutons/prix : **Jost** (sans-serif géométrique lisible, 400/500/600).
- SUPPRIMER la police Caveat. Hiérarchie typographique stricte, pas 5 tailles/graisses sans raison.

## PALETTE (fond clair, premium)
Variables CSS à la racine :
- --bg: #FAF7F1 (ivoire) · --bg-alt: #F3EEE4 (blanc cassé)
- --ink: #1C1917 (noir doux) · --muted: #6E675D
- --champagne: #C7AE7C · --sable: #E4DAC6 · --line: #E0D8CA
- Accents SAISONNIERS (uniquement dans les collections, jamais dans la structure globale) :
  - halloween: #B85C2E (orange brûlé) · christmas: #8C2B2B (rouge profond) / #3A5A40 (vert sapin)
- Pas de violet/indigo/bleu générique. Les couleurs saisonnières ne détruisent pas l'identité.

## HEADER (fin, élégant)
- Mot-symbole : **CHIC CELEBRIA** (logo existant `assets/logo.png` + texte, alignés proprement).
- Navigation : New In · Celebrations · Halloween · Christmas · Gifts · Personalised · About
- Actions : PAS de search (non implémentée), PAS de bag/panier (checkout pas activé), PAS de wishlist. Juste le mot-symbole + nav + menu mobile.
- Sticky discret, pas de barre massive. Mobile : hamburger propre.

## HOMEPAGE (structure exacte, dans l'ordre)
1. **Hero** : photographie éditoriale grand format (occupe la majeure partie de l'écran), texte court.
   - H1 : « Make Every Celebration Yours »
   - Sous-titre : « Distinctive details for life's favourite moments. »
   - CTA : « SHOP THE COLLECTION » (lien vers /collections/)
   - Pas de paragraphe de 15 lignes. Le hero vend une émotion.
2. **Collections** : 3-4 GRANDES catégories visuelles (grandes photos, pas de petites cartes SaaS) : Halloween · Christmas · Gifts · Personalised → liens vers /collections/xxx/.
3. **Produits** : titre « Discover What's New » — sélection courte. Desktop 4/colonne, mobile 2/colonne. Chaque carte : photo + nom + prix + (variante) + (badge réel si applicable). Hover discret (image secondaire si dispo).
4. **Éditorial** : grande image + texte. Titre « Celebrate It Your Way » + texte court sur le principe de la marque (PAS de storytelling fictif).
5. **Seasonal storytelling** : zone immersive « The Halloween Edit » (photo pleine largeur + CTA vers /collections/halloween/). Prévoir qu'elle puisse changer (Christmas plus tard).
6. **Newsletter** : minimaliste. Titre « A little celebration in your inbox » + « New collections, seasonal inspiration and special releases. » + champ email + CTA « JOIN US ». Pas de popup.

## PAGES COLLECTIONS (/collections/<slug>/index.html)
Slugs : halloween, christmas, gifts, personalised.
Chaque page : H1 unique + intro courte + grille produits (2-4 colonnes) + filtres UTILES (catégorie/prix) + tri (nom/prix) + lien retour.
URLs : /collections/halloween/ , /collections/christmas/ , /collections/gifts/ , /collections/personalised/

## PAGES PRODUITS (/products/<slug>/index.html)
Structure : galerie (4-8 photos si dispo, sinon 2-3) + nom + prix + variantes (taille/couleur si pertinent) + champ personnalisation (si pertinent) + CTA principal « SHOP ON ETSY » + description courte + blocs : Details / Dimensions / Materials / Care / Delivery / Returns (uniquement les blocs pertinents, ne pas inventer de contenu : mettons du contenu générique honnête type « See product page on Etsy for details » si on n'a pas la donnée).

## ETSY — PHASE 1 (CRITIQUE)
- La vente se fait sur Etsy pour l'instant. TOUS les CTA produit renvoient vers la boutique Etsy.
- CTA : « SHOP ON ETSY » / « VIEW ON ETSY ».
- **Liens configurables dans UN seul fichier** : `assets/site-config.js` :
  ```js
  window.CHIC = {
    etsyShopUrl: "https://www.etsy.com/shop/ChicCelebria",
    currency: "EUR",
    locale: "en"
  };
  ```
  Tous les liens Etsy du site passent par `window.CHIC.etsyShopUrl` (ou un lien produit via `?listing_id=` si dispo).
- **SUPPRIMER** le faux panier/checkout (localStorage, compteur bag). Pas de faux checkout aujourd'hui.

## SEO (complet, par page)
- <title> unique : « Halloween Cat Costumes | ChicCelebria » (jamais « Home | ChicCelebria » partout).
- meta description unique, humaine, spécifique (pas de bourrage de mots-clés).
- Un seul H1 par page. Canonical correct. OG (og:title/description/image/url/type).
- JSON-LD : WebSite, Organization, BreadcrumbList (sur collections+produits), Product + Offer (sur produits), ProductGroup si variantes.
- Pas de Review/AggregateRating (aucun vrai avis).
- ALT descriptifs (jamais « cheap halloween costume buy »).
- **sitemap.xml** à la racine (URLs indexables, base https://projethermes.github.io/chiccelebria-demo/).
- **robots.txt** à la racine (autoriser CSS/JS/images, pointer le sitemap, disallow /fiches.html et /fiches.json).

## PRODUITS (sélection, répartis dans les collections)
Réutilise les images locales existantes (assets/produits/img-*.jpg, tapestry.jpg, macrame.webp, deco2.webp, banniere1/2.png). ~6-8 produits, exemples :
- Personalised Halloween Tapestry (halloween, personalisable, ~15,99 €)
- Macramé Wall Hanging (gifts/deco)
- Personalised Candle (gifts, personalisable)
- Halloween Felt Garland (halloween)
- Personalised Christmas Banner (christmas, personalisable)
- etc.
Chaque produit : slug propre (/products/personalised-halloween-tapestry/), nom, prix (€), variantes si pertinent, lien Etsy.
PAS de notes étoiles, PAS de « X sold », PAS de « best-seller ».

## PERFORMANCE / TECH
- HTML/CSS/JS natifs, AUCUNE librairie externe (pas de jQuery, pas de framework). Google Fonts = 1 seul <link> (Fraunces + Jost).
- Mobile-first, tester 320/375/390/768/1024/1440/1920. Zéro débordement horizontal, zéro texte coupé, menu utilisable.
- Hero : image LCP PAS lazy-loadée, bien dimensionnée/compressée. Sous le fold : lazy loading.
- Images : WebP/AVIF si dispo (déjà des .webp/.jpg locaux), width/height définis.
- CSS : variables globales (couleurs, spacing, container, typo, radius, breakpoints).
- prefers-reduced-motion respecté.

## ACCESSIBILITÉ / SÉMANTIQUE
- WCAG AA : contraste, focus visible, labels de formulaire, navigation clavier.
- HTML sémantique : header/nav/main/section/article/footer. Boutons = <button>, liens = <a>. Pas de <div> partout.

## STRUCTURE FICHIERS FINALE (ne PAS créer autre chose)
```
index.html
collections/halloween/index.html
collections/christmas/index.html
collections/gifts/index.html
collections/personalised/index.html
products/<slug>/index.html        (un dossier par produit, ~6-8 produits)
about.html
style.css
script.js
assets/site-config.js
assets/ (logo.png, banniere*.png, produits/*.jpg, sourcing/*.jpg, tapestry.jpg, macrame.webp, deco2.webp)
sitemap.xml
robots.txt
fiches.html  (NE PAS TOUCHER — espace vendeur interne, laissé tel quel)
fiches.json  (NE PAS TOUCHER)
```

## VALIDATION AVANT DE FINIR (fais-la toi-même)
1. Toutes les pages se chargent, tous les liens internes marchent (pas de 404).
2. Console navigateur sans erreur (teste avec `node -c script.js` + ouvre les pages).
3. Mobile OK (pas de débordement).
4. Aucun lorem ipsum, aucun placeholder visible, aucun emoji, aucun faux avis, aucun faux numéro/téléphone, aucun contenu commercial inventé.
5. titles + descriptions uniques, canonicals, sitemap, robots, JSON-LD présents.
6. Header/nav/footer cohérents sur toutes les pages.
7. Fais le « slop diagnostic » : note-toi /10 sur les 10 tells du design IA et corrige ce qui est flagrant (re-compose plutôt que re-colorer si la composition est le problème).

## LIVRABLE FINAL
À la fin, écris un récap : fichiers créés/modifiés, structure des URLs, produits créés, et la liste des points que TU n'as pas pu valider toi-même.
