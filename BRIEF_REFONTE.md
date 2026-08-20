# ChicCelebria — Refonte complète (projet premium)

Refonds COMPLÈTEMENT le site situé dans ce dossier (actuellement un simple vitrine 3 pages : index.html, produits.html, a-propos.html) en une boutique en ligne premium digne de Ferm Living / Oliver Bonas / Anthropologie. Tu remplaces tout.

## Identité de marque (GARDER)
- Décoration et cadeaux personnalisés (thème Halloween + toute l'année).
- Palette : fond encre prune profond (#1a0f1e), accents bijou terracotta (#c96f4a), or (#c9a227), vert jungle ; accents papier/ivoire (#f4ede1).
- Typographies : Fraunces (display), Jost (texte), Caveat (manuscrite, touches perso).
- Signatures : étiquette-cadeau suspendue, bordures pointillé-couture, ruban.

## Pages à construire (remplacer tout le contenu existant)
1. **index.html** — Landing premium :
   - Header sticky (logo + nav + icône panier avec compteur en direct)
   - Bandeau promo (ex. « Livraison offerte dès 35 € · Personnalisation offerte »)
   - Hero plein écran : grande image en fond avec dégradé, titre display Fraunces, double CTA, badge qualité
   - Section « Collections » : 3-4 grandes cartes image cliquables (Halloween, Décoration, Cadeaux, Saison)
   - Section « Best-sellers » : grille 4 produits (tapisserie, macramé, déco) avec hover zoom + prix + badge « Personnalisable »
   - Section « Pourquoi ChicCelebria » : 4 piliers avec icônes (Personnalisation à la demande, Qualité artisanale, Livraison rapide, Paiement sécurisé)
   - Section avis clients (3 cartes, étoiles, noms, villes)
   - Section newsletter (email + confirmation JS)
   - Footer riche : 4 colonnes (Marque, Aide, Collections, Contact + paiements)
2. **boutique.html** — Catalogue :
   - Filtres : catégorie, prix min/max, tri (populaire, prix croissant/décroissant), recherche
   - Grille 8+ produits fictifs réalistes (12-30 €) avec badges (Nouveau, -15 %, Personnalisable, Best-seller)
   - Carte produit : image, titre, prix, note étoiles, bouton ajout panier au survol
   - Filtres fonctionnels en JS pur
3. **produit.html** — Fiche produit :
   - Galerie 2-3 images avec vignettes
   - Titre, prix, note, description, options (taille/couleur), champ « Personnalisation (prénom/texte) », quantité, bouton « Ajouter au panier » (feedback + compteur header)
   - Accordéon : Description / Livraison & retours / Personnalisation
   - Section « Vous aimerez aussi » (4 produits)
4. **a-propos.html** — Histoire de la marque, valeurs, image signature
5. **contact.html** — Formulaire (nom, email, message, validation JS), FAQ accordéon, infos
6. **panier.html** — Panier complet :
   - Liste articles (image, nom, perso, prix, quantité +/-), sous-total, « livraison offerte dès 35 € » avec barre de progression, bouton commander (simulation avec confirmation), bouton vider
   - Persistance localStorage : le panier survit à la navigation et au rechargement
7. **404.html** — page d'erreur élégante
8. **assets/** — réutiliser les images existantes (logo.png, banniere1.png, banniere2.png, tapestry.jpg, macrame.webp, deco2.webp) + compléter avec des URLs Unsplash si besoin

## Fonctionnalités JS (un seul fichier script.js, refondu proprement)
- Panier localStorage : ajouter/retirer/quantité, compteur header, prix recalculés
- Filtres + tri + recherche sur boutique.html
- Menu mobile hamburger, header opaque au scroll
- Animations reveal au scroll (IntersectionObserver, fade+translate léger)
- Hover cartes produits (zoom image, bouton apparition)
- Bandes promo simples, validation formulaires, toasts « Ajouté au panier ✓ »

## Qualité / standards
- Mobile-first responsive (320px → desktop), menu hamburger sous 768px
- SEO : meta title/description uniques par page, Open Graph, favicon, JSON-LD (Organization + Product)
- Perf : lazy loading images, pas de librairie externe (JS vanilla), Google Fonts (Fraunces/Jost/Caveat) en un seul link
- Micro-interactions 200-300ms, focus visible, aria-labels, HTML sémantique
- Aucun build, aucun npm : HTML/CSS/JS purs qui marchent en double-cliquant le fichier

## Structure finale (ne PAS créer d'autres fichiers)
index.html, boutique.html, produit.html, a-propos.html, contact.html, panier.html, 404.html, style.css, script.js, assets/

## Règles
- Site 100 % en FRANÇAIS, ton chaleureux et premium, pas de lorem ipsum.
- Si une image manque : placeholder élégant (dégradé + initiales) plutôt qu'un fichier cassé.
- Vérifie en fin : nav + footer cohérents sur toutes les pages, chemins d'images valides, JS sans erreur de syntaxe.
