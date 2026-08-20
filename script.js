/* ==========================================================================
   ChicCelebria — script.js
   Panier localStorage, catalogue, filtres, rendu produit, UI (nav, reveal,
   toasts, accordéons, formulaires). Vanilla JS, sans dépendance externe.
   ========================================================================== */
(function () {
  "use strict";

  var CART_KEY = "chiccelebria_cart_v1";
  var FREE_SHIPPING_THRESHOLD = 35;
  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------------
     Catalogue produits
     ------------------------------------------------------------------ */
  var PRODUCTS = [
    {
      id: "tapisserie-halloween-hantee",
      name: "Tapisserie Halloween — Maison Hantée",
      category: "halloween",
      price: 32,
      oldPrice: null,
      rating: 4.8,
      reviews: 46,
      badges: ["best-seller", "personnalisable"],
      images: ["assets/tapestry.jpg", "assets/tapestry.jpg"],
      short: "Votre prénom, votre maison hantée ou votre chat noir brodés sur coton épais.",
      description: "Votre prénom, votre maison hantée ou votre chat noir préféré, imprimés et surpiqués sur une tapisserie murale en coton épais. Un frisson chic qui habille tout un pan de mur, du salon à la chambre.",
      materials: "Coton épais, ourlet cousu main, tringle bois offerte",
      sizes: ["100×150 cm", "150×200 cm"],
      colors: null,
      personalizable: true,
      delivery: "Expédiée sous 5 à 8 jours ouvrés. Retours acceptés sous 14 jours pour les pièces non personnalisées.",
      personalizationInfo: "Indiquez le prénom, le texte ou le motif souhaité en commande. Une confirmation vous est envoyée avant fabrication."
    },
    {
      id: "guirlande-fantomes-macrame",
      name: "Guirlande de Fantômes en Macramé",
      category: "halloween",
      price: 26,
      oldPrice: null,
      rating: 4.9,
      reviews: 38,
      badges: ["nouveau", "personnalisable"],
      images: ["assets/macrame.webp", "assets/macrame.webp"],
      short: "Cinq fantômes noués main, expressions brodées une à une.",
      description: "Cinq fantômes noués main en coton macramé, chacun avec sa propre expression brodée — mignonne, coquine ou carrément effrayante. Se suspendent en cascade à un mur, une fenêtre ou un manteau de cheminée.",
      materials: "Corde de coton naturel, détails feutrine noire",
      sizes: null,
      colors: ["Écru", "Noir charbon", "Terracotta"],
      personalizable: true,
      delivery: "Expédiée sous 4 à 6 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Choisissez les expressions du visage (doux, coquin, effrayant) pour chacun des 5 fantômes."
    },
    {
      id: "chapeaux-sorciere-macrame",
      name: "Duo de Chapeaux de Sorcière en Macramé",
      category: "halloween",
      price: 24,
      oldPrice: null,
      rating: 4.7,
      reviews: 22,
      badges: ["personnalisable"],
      images: ["assets/deco2.webp", "assets/deco2.webp"],
      short: "Deux chapeaux en feutrine, ruban organza et franges macramé.",
      description: "Deux chapeaux de sorcière en feutrine noire, nœud en organza et longues franges en macramé tissées main. Un duo grand format et un format compact, à accrocher ensemble pour une scène digne d'Halloween Chic.",
      materials: "Feutrine, ruban organza, franges coton macramé",
      sizes: null,
      colors: ["Noir & or", "Noir & bordeaux"],
      personalizable: true,
      delivery: "Expédiée sous 4 à 6 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Choisissez la couleur du ruban pour assortir le duo à votre déco."
    },
    {
      id: "coffret-cadeau-personnalise",
      name: "Coffret Cadeau Personnalisé Clé en Main",
      category: "cadeaux",
      price: 19,
      oldPrice: null,
      rating: 5.0,
      reviews: 61,
      badges: ["personnalisable", "best-seller"],
      images: ["assets/banniere2.png", "assets/banniere1.png"],
      short: "Étiquette manuscrite et ruban en lin, prêt à offrir.",
      description: "Un objet ChicCelebria de votre choix, une étiquette manuscrite à votre nom et un ruban en lin noué main : le cadeau tout prêt pour un anniversaire, une pendaison de crémaillère ou juste pour dire merci — sans un seul ruban à nouer vous-même.",
      materials: "Papier kraft, ruban en lin, étiquette manuscrite",
      sizes: null,
      colors: null,
      personalizable: true,
      delivery: "Expédiée sous 3 à 5 jours ouvrés. Retours acceptés sous 14 jours pour l'emballage seul.",
      personalizationInfo: "Ajoutez le prénom du destinataire et un court message pour l'étiquette manuscrite."
    },
    {
      id: "guirlande-lumineuse-doree",
      name: "Guirlande Lumineuse Dorée Fête",
      category: "deco",
      price: 22,
      oldPrice: null,
      rating: 4.6,
      reviews: 19,
      badges: ["best-seller"],
      images: ["assets/banniere1.png", "assets/banniere2.png"],
      short: "3 mètres de lumière chaude façon laiton brossé.",
      description: "Une guirlande lumineuse à LED chaudes sur fil laiton brossé, pour souligner une étagère, un miroir ou une tête de lit. Douce le jour, magique la nuit — toute l'année, pas seulement aux fêtes.",
      materials: "Guirlande LED, fil laiton, 3 m, pile incluse",
      sizes: null,
      colors: null,
      personalizable: false,
      delivery: "Expédiée sous 2 à 4 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Ce modèle n'est pas personnalisable, il est prêt à l'envoi."
    },
    {
      id: "suspension-macrame-jungle",
      name: "Suspension Murale Macramé Jungle",
      category: "deco",
      price: 28,
      oldPrice: null,
      rating: 4.8,
      reviews: 27,
      badges: ["nouveau"],
      images: [
        "assets/produits/img-12.jpg",
        "assets/produits/img-10.jpg"
      ],
      short: "Anneau bois et feuillage séché pour un mur végétal doux.",
      description: "Une suspension murale en macramé tissée main, anneau de bois clair et feuillage séché glissé dans les mailles. Elle apporte une touche bohème et végétale à n'importe quel mur, toute l'année.",
      materials: "Corde de coton, anneau de bois, feuillage séché",
      sizes: null,
      colors: null,
      personalizable: false,
      delivery: "Expédiée sous 4 à 6 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Ce modèle n'est pas personnalisable, il est prêt à l'envoi."
    },
    {
      id: "bougie-parfumee-personnalisee",
      name: "Bougie Parfumée Personnalisée",
      category: "cadeaux",
      price: 14,
      oldPrice: 16.5,
      rating: 4.7,
      reviews: 54,
      badges: ["promo", "personnalisable"],
      images: [
        "assets/produits/img-08.jpg",
        "assets/produits/img-09.jpg"
      ],
      short: "Cire de soja, mèche coton, étiquette à votre prénom.",
      description: "Une bougie en cire de soja coulée à la main, parfum bois de santal ou figue selon la saison, avec une étiquette à votre prénom. Le petit cadeau qui fait toujours son effet, seul ou en duo.",
      materials: "Cire de soja, mèche coton, verre réutilisable",
      sizes: null,
      colors: ["Bois de santal", "Figue", "Vanille ambrée"],
      personalizable: true,
      delivery: "Expédiée sous 2 à 4 jours ouvrés. Retours acceptés sous 14 jours pour les bougies non entamées.",
      personalizationInfo: "Ajoutez un prénom ou un court mot pour l'étiquette de la bougie."
    },
    {
      id: "guirlande-citrouilles-feutrine",
      name: "Guirlande de Citrouilles en Feutrine",
      category: "halloween",
      price: 21,
      oldPrice: null,
      rating: 4.5,
      reviews: 15,
      badges: ["nouveau"],
      images: [
        "assets/produits/img-01.jpg",
        "assets/produits/img-07.jpg"
      ],
      short: "Sept citrouilles en feutrine épaisse, coutures apparentes.",
      description: "Sept citrouilles en feutrine épaisse, cousues main avec des coutures apparentes façon patchwork, à suspendre au-dessus d'une cheminée ou d'une fenêtre. Douce et chic, jamais criarde.",
      materials: "Feutrine épaisse, fil de coton",
      sizes: null,
      colors: null,
      personalizable: false,
      delivery: "Expédiée sous 3 à 5 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Ce modèle n'est pas personnalisable, il est prêt à l'envoi."
    },
    {
      id: "etagere-boheme-macrame",
      name: "Étagère Murale Bohème en Macramé",
      category: "deco",
      price: 30,
      oldPrice: null,
      rating: 4.9,
      reviews: 33,
      badges: ["best-seller"],
      images: [
        "assets/produits/img-04.jpg",
        "assets/produits/img-11.jpg"
      ],
      short: "Bois clair suspendu par des cordes macramé tissées main.",
      description: "Une étagère en bois clair suspendue par des cordes en macramé tissées main, parfaite pour une petite plante, quelques bougies ou vos objets préférés. Un rangement qui a l'air d'une décoration.",
      materials: "Bois clair, corde de coton macramé",
      sizes: null,
      colors: null,
      personalizable: false,
      delivery: "Expédiée sous 5 à 7 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Ce modèle n'est pas personnalisable, il est prêt à l'envoi."
    },
    {
      id: "sachets-senteur-personnalises",
      name: "Set de 3 Sachets Senteur Personnalisés",
      category: "cadeaux",
      price: 12,
      oldPrice: 14,
      rating: 4.6,
      reviews: 29,
      badges: ["promo", "personnalisable"],
      images: [
        "assets/produits/img-06.jpg",
        "assets/produits/img-05.jpg"
      ],
      short: "Lin naturel, fleurs séchées, ruban brodé à votre prénom.",
      description: "Trois sachets senteur en lin naturel garnis de fleurs séchées et de bois de cèdre, fermés par un ruban brodé à votre prénom. À glisser dans une armoire, un tiroir ou une valise.",
      materials: "Lin naturel, fleurs séchées, ruban coton",
      sizes: null,
      colors: null,
      personalizable: true,
      delivery: "Expédiée sous 2 à 4 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Le prénom ou l'initiale de votre choix est brodé sur le ruban des 3 sachets."
    },
    {
      id: "guirlande-noel-tropical-ananas",
      name: "Guirlande Noël Tropical — Ananas Doré",
      category: "saison",
      price: 23,
      oldPrice: null,
      rating: 4.8,
      reviews: 12,
      badges: ["nouveau", "personnalisable"],
      images: [
        "assets/produits/img-03.jpg",
        "assets/produits/img-02.jpg"
      ],
      short: "Ananas en papier doré et perles de bois, esprit Noël tropical.",
      description: "Une guirlande de petits ananas en papier doré et de perles de bois naturel, pour un Noël tropical chic — celui qui préfère le soleil aux sapins givrés. Se suspend au-dessus d'une table ou d'un miroir.",
      materials: "Papier doré, perles de bois, fil de coton",
      sizes: null,
      colors: null,
      personalizable: true,
      delivery: "Expédiée sous 4 à 6 jours ouvrés. Retours acceptés sous 14 jours.",
      personalizationInfo: "Ajoutez un petit fanion prénom en début de guirlande, sur demande en commande."
    }
  ];

  window.CHICCELEBRIA = window.CHICCELEBRIA || {};
  window.CHICCELEBRIA.PRODUCTS = PRODUCTS;

  var BADGE_LABELS = {
    nouveau: "Nouveau",
    "best-seller": "Best-seller",
    personnalisable: "Personnalisable"
  };
  var CATEGORY_LABELS = {
    halloween: "Halloween",
    deco: "Décoration",
    cadeaux: "Cadeaux",
    saison: "Saison"
  };

  function euros(n) {
    return n.toFixed(2).replace(".", ",").replace(",00", "") + " €";
  }

  function getProduct(id) {
    for (var i = 0; i < PRODUCTS.length; i++) {
      if (PRODUCTS[i].id === id) return PRODUCTS[i];
    }
    return null;
  }

  function badgeMarkup(product) {
    var out = "";
    (product.badges || []).forEach(function (b) {
      if (b === "promo" && product.oldPrice) {
        var pct = Math.round((1 - product.price / product.oldPrice) * 100);
        out += '<span class="badge badge-promo">-' + pct + "%</span>";
      } else if (BADGE_LABELS[b]) {
        out += '<span class="badge badge-' + b + '">' + BADGE_LABELS[b] + "</span>";
      }
    });
    return out;
  }

  function starsMarkup(rating) {
    var full = Math.round(rating * 2) / 2;
    var html = '<span class="stars" aria-hidden="true">';
    for (var i = 1; i <= 5; i++) {
      if (full >= i) html += "★";
      else if (full >= i - 0.5) html += "★";
      else html += "☆";
    }
    html += "</span>";
    return html;
  }

  function imgAttrs(src) {
    return 'src="' + src + '" onerror="window.CHICCELEBRIA.imgFallback(this)"';
  }

  window.CHICCELEBRIA.imgFallback = function (img) {
    if (img.dataset.fallbackApplied) return;
    img.dataset.fallbackApplied = "1";
    var wrap = document.createElement("div");
    wrap.className = "img-placeholder";
    var alt = img.getAttribute("alt") || "ChicCelebria";
    var initials = alt
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(function (w) { return w[0]; })
      .join("")
      .toUpperCase();
    wrap.textContent = initials || "CC";
    if (img.className) wrap.className += " " + img.className;
    img.parentNode.replaceChild(wrap, img);
  };

  /* ------------------------------------------------------------------
     Panier — localStorage
     ------------------------------------------------------------------ */
  function readCart() {
    try {
      var raw = localStorage.getItem(CART_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function writeCart(cart) {
    try {
      localStorage.setItem(CART_KEY, JSON.stringify(cart));
    } catch (e) {
      /* stockage indisponible : le panier reste en mémoire pour la session */
    }
    updateCartCount();
  }

  function cartLines() {
    return readCart()
      .map(function (line) {
        var product = getProduct(line.productId);
        if (!product) return null;
        return {
          lineId: line.lineId,
          product: product,
          qty: line.qty,
          personalization: line.personalization || "",
          variant: line.variant || ""
        };
      })
      .filter(Boolean);
  }

  function cartCount() {
    return readCart().reduce(function (sum, l) { return sum + l.qty; }, 0);
  }

  function cartSubtotal() {
    return cartLines().reduce(function (sum, l) { return sum + l.product.price * l.qty; }, 0);
  }

  function addToCart(productId, opts) {
    opts = opts || {};
    var qty = opts.qty || 1;
    var personalization = opts.personalization || "";
    var variant = opts.variant || "";
    var cart = readCart();
    var existing = cart.filter(function (l) {
      return l.productId === productId && l.personalization === personalization && l.variant === variant;
    })[0];
    if (existing) {
      existing.qty += qty;
    } else {
      cart.push({
        lineId: "l" + Date.now() + Math.random().toString(16).slice(2),
        productId: productId,
        qty: qty,
        personalization: personalization,
        variant: variant
      });
    }
    writeCart(cart);
  }

  function removeLine(lineId) {
    writeCart(readCart().filter(function (l) { return l.lineId !== lineId; }));
  }

  function setLineQty(lineId, qty) {
    var cart = readCart();
    cart.forEach(function (l) {
      if (l.lineId === lineId) l.qty = Math.max(1, qty);
    });
    writeCart(cart);
  }

  function clearCart() {
    writeCart([]);
  }

  function updateCartCount() {
    var n = cartCount();
    document.querySelectorAll(".cart-count").forEach(function (el) {
      el.textContent = String(n);
      el.classList.toggle("is-visible", n > 0);
    });
  }

  window.CHICCELEBRIA.cart = {
    lines: cartLines,
    count: cartCount,
    subtotal: cartSubtotal,
    add: addToCart,
    remove: removeLine,
    setQty: setLineQty,
    clear: clearCart
  };

  /* ------------------------------------------------------------------
     Toasts
     ------------------------------------------------------------------ */
  function toast(message) {
    var host = document.getElementById("toast-host");
    if (!host) {
      host = document.createElement("div");
      host.id = "toast-host";
      host.className = "toast-host";
      host.setAttribute("aria-live", "polite");
      document.body.appendChild(host);
    }
    var el = document.createElement("div");
    el.className = "toast";
    el.textContent = message;
    host.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("is-visible"); });
    setTimeout(function () {
      el.classList.remove("is-visible");
      setTimeout(function () { el.remove(); }, 300);
    }, 2600);
  }
  window.CHICCELEBRIA.toast = toast;

  /* ------------------------------------------------------------------
     Navigation, header scroll, reveal, accordéons — communs à toutes les pages
     ------------------------------------------------------------------ */
  function initNav() {
    var navToggle = document.getElementById("nav-toggle");
    var mainNav = document.getElementById("main-nav");
    if (!navToggle || !mainNav) return;
    navToggle.addEventListener("click", function () {
      var isOpen = mainNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
    mainNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        mainNav.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  function initHeaderScroll() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    function onScroll() {
      header.classList.toggle("is-scrolled", window.scrollY > 12);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function initReveal() {
    var targets = document.querySelectorAll(".reveal");
    if (!targets.length) return;
    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      targets.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    targets.forEach(function (el) { observer.observe(el); });
  }

  function markRevealables(selector) {
    document.querySelectorAll(selector).forEach(function (el) {
      el.classList.add("reveal");
    });
  }

  function initAccordions() {
    document.querySelectorAll(".accordion-trigger").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var panel = document.getElementById(btn.getAttribute("aria-controls"));
        var expanded = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", String(!expanded));
        if (panel) panel.hidden = expanded;
      });
    });
  }

  function initNewsletter() {
    var form = document.querySelector(".newsletter-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector("input[type='email']");
      var feedback = form.querySelector(".form-feedback");
      if (!input.checkValidity()) {
        if (feedback) { feedback.textContent = "Merci d'indiquer une adresse e-mail valide."; feedback.classList.add("is-error"); }
        input.focus();
        return;
      }
      if (feedback) {
        feedback.textContent = "Merci ! Vérifiez votre boîte mail pour confirmer votre inscription. ✓";
        feedback.classList.remove("is-error");
      }
      form.reset();
    });
  }

  /* ------------------------------------------------------------------
     Rendu des cartes produit (accueil, boutique, produits liés)
     ------------------------------------------------------------------ */
  function productCardMarkup(product) {
    var priceHtml = product.oldPrice
      ? '<span class="price-old">' + euros(product.oldPrice) + '</span><span class="price-now">' + euros(product.price) + "</span>"
      : '<span class="price-now">' + euros(product.price) + "</span>";
    return (
      '<article class="shop-card reveal" data-id="' + product.id + '" data-category="' + product.category + '" data-price="' + product.price + '">' +
        '<a class="shop-card-media" href="produit.html?id=' + product.id + '">' +
          '<span class="shop-card-badges">' + badgeMarkup(product) + "</span>" +
          '<img ' + imgAttrs(product.images[0]) + ' alt="' + product.name + '" loading="lazy" decoding="async">' +
          '<button type="button" class="btn btn-primary btn-sm shop-card-add" data-add-id="' + product.id + '">Ajouter au panier</button>' +
        "</a>" +
        '<div class="shop-card-body">' +
          '<a class="shop-card-title" href="produit.html?id=' + product.id + '">' + product.name + "</a>" +
          '<div class="shop-card-rating">' + starsMarkup(product.rating) + '<span class="rating-count">(' + product.reviews + ")</span></div>" +
          '<div class="shop-card-price">' + priceHtml + "</div>" +
        "</div>" +
      "</article>"
    );
  }

  function bindQuickAdd(container) {
    container.querySelectorAll("[data-add-id]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var product = getProduct(btn.getAttribute("data-add-id"));
        if (!product) return;
        addToCart(product.id, { qty: 1 });
        toast("Ajouté au panier ✓ — " + product.name);
      });
    });
  }

  /* ------------------------------------------------------------------
     Page : accueil
     ------------------------------------------------------------------ */
  function initHome() {
    var grid = document.getElementById("best-sellers-grid");
    if (grid) {
      var bestSellers = PRODUCTS.filter(function (p) { return p.badges.indexOf("best-seller") !== -1; }).slice(0, 4);
      grid.innerHTML = bestSellers.map(productCardMarkup).join("");
      bindQuickAdd(grid);
    }
    initReveal();
  }

  /* ------------------------------------------------------------------
     Page : boutique (catalogue + filtres)
     ------------------------------------------------------------------ */
  function initBoutique() {
    var grid = document.getElementById("boutique-grid");
    var countEl = document.getElementById("boutique-count");
    var emptyEl = document.getElementById("boutique-empty");
    if (!grid) return;

    var form = document.getElementById("filters-form");
    var categorySelect = document.getElementById("filter-category");
    var sortSelect = document.getElementById("filter-sort");
    var searchInput = document.getElementById("filter-search");
    var minInput = document.getElementById("filter-min");
    var maxInput = document.getElementById("filter-max");
    var resetBtn = document.getElementById("filter-reset");

    var params = new URLSearchParams(window.location.search);
    if (params.get("cat") && categorySelect) categorySelect.value = params.get("cat");
    if (params.get("q") && searchInput) searchInput.value = params.get("q");

    function render() {
      var cat = categorySelect ? categorySelect.value : "";
      var sort = sortSelect ? sortSelect.value : "popularite";
      var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
      var min = minInput && minInput.value !== "" ? parseFloat(minInput.value) : null;
      var max = maxInput && maxInput.value !== "" ? parseFloat(maxInput.value) : null;

      var list = PRODUCTS.filter(function (p) {
        if (cat && p.category !== cat) return false;
        if (min !== null && p.price < min) return false;
        if (max !== null && p.price > max) return false;
        if (q && p.name.toLowerCase().indexOf(q) === -1 && p.short.toLowerCase().indexOf(q) === -1) return false;
        return true;
      });

      list.sort(function (a, b) {
        if (sort === "prix-asc") return a.price - b.price;
        if (sort === "prix-desc") return b.price - a.price;
        if (sort === "note") return b.rating - a.rating;
        return b.reviews - a.reviews; // popularité par défaut
      });

      grid.innerHTML = list.map(productCardMarkup).join("");
      bindQuickAdd(grid);
      markRevealables(".shop-card");
      initReveal();

      if (countEl) countEl.textContent = list.length + (list.length > 1 ? " créations" : " création");
      if (emptyEl) emptyEl.hidden = list.length !== 0;
    }

    if (form) form.addEventListener("submit", function (e) { e.preventDefault(); render(); });
    [categorySelect, sortSelect, minInput, maxInput].forEach(function (el) {
      if (el) el.addEventListener("change", render);
    });
    if (searchInput) searchInput.addEventListener("input", debounce(render, 200));
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        if (form) form.reset();
        render();
      });
    }

    render();
  }

  function debounce(fn, delay) {
    var timer;
    return function () {
      clearTimeout(timer);
      var args = arguments;
      timer = setTimeout(function () { fn.apply(null, args); }, delay);
    };
  }

  /* ------------------------------------------------------------------
     Page : fiche produit
     ------------------------------------------------------------------ */
  function initProduit() {
    var params = new URLSearchParams(window.location.search);
    var product = getProduct(params.get("id")) || PRODUCTS[0];
    if (!product) return;

    document.title = product.name + " — ChicCelebria";
    var metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute("content", product.short);

    var mount = document.getElementById("produit-mount");
    if (mount) {
      var galleryThumbs = product.images
        .map(function (src, i) {
          return '<button type="button" class="gallery-thumb' + (i === 0 ? " is-active" : "") + '" data-src="' + src + '" aria-label="Image ' + (i + 1) + '">' +
            '<img ' + imgAttrs(src) + ' alt="' + product.name + " — vue " + (i + 1) + '" loading="lazy" decoding="async">' +
          "</button>";
        })
        .join("");

      var optionsHtml = "";
      if (product.sizes) {
        optionsHtml += '<div class="option-group"><label for="opt-size">Taille</label><select id="opt-size" name="taille">' +
          product.sizes.map(function (s) { return '<option value="' + s + '">' + s + "</option>"; }).join("") +
        "</select></div>";
      }
      if (product.colors) {
        optionsHtml += '<div class="option-group"><label for="opt-color">Couleur</label><select id="opt-color" name="couleur">' +
          product.colors.map(function (c) { return '<option value="' + c + '">' + c + "</option>"; }).join("") +
        "</select></div>";
      }

      var priceHtml = product.oldPrice
        ? '<span class="price-old">' + euros(product.oldPrice) + '</span><span class="price-now price-now-lg">' + euros(product.price) + "</span>"
        : '<span class="price-now price-now-lg">' + euros(product.price) + "</span>";

      mount.innerHTML =
        '<div class="produit-gallery">' +
          '<div class="gallery-main">' +
            '<img id="gallery-main-img" ' + imgAttrs(product.images[0]) + ' alt="' + product.name + '" loading="eager" decoding="async">' +
          "</div>" +
          '<div class="gallery-thumbs">' + galleryThumbs + "</div>" +
        "</div>" +
        '<div class="produit-info">' +
          '<p class="breadcrumb"><a href="index.html#top">Accueil</a> / <a href="boutique.html">Boutique</a> / ' + product.name + "</p>" +
          '<div class="produit-badges">' + badgeMarkup(product) + "</div>" +
          "<h1>" + product.name + "</h1>" +
          '<div class="shop-card-rating produit-rating">' + starsMarkup(product.rating) + '<span class="rating-count">' + product.reviews + " avis</span></div>" +
          '<div class="produit-price">' + priceHtml + "</div>" +
          "<p class=\"produit-desc\">" + product.description + "</p>" +
          '<form id="add-to-cart-form" class="produit-form">' +
            optionsHtml +
            (product.personalizable
              ? '<div class="option-group"><label for="opt-personnalisation">Personnalisation (prénom / texte)</label>' +
                '<input type="text" id="opt-personnalisation" name="personnalisation" placeholder="Ex. : Prénom, texte ou motif souhaité" maxlength="60"></div>'
              : "") +
            '<div class="option-group option-qty"><label for="opt-qty">Quantité</label>' +
              '<div class="qty-stepper">' +
                '<button type="button" class="qty-btn" data-qty-decrease aria-label="Diminuer la quantité">−</button>' +
                '<input type="number" id="opt-qty" name="quantite" value="1" min="1" max="20" inputmode="numeric">' +
                '<button type="button" class="qty-btn" data-qty-increase aria-label="Augmenter la quantité">+</button>' +
              "</div></div>" +
            '<button type="submit" class="btn btn-primary btn-lg produit-add-btn">Ajouter au panier</button>' +
            '<p class="form-feedback" role="status" aria-live="polite"></p>' +
          "</form>" +
        "</div>";

      mount.querySelectorAll(".gallery-thumb").forEach(function (thumb) {
        thumb.addEventListener("click", function () {
          mount.querySelectorAll(".gallery-thumb").forEach(function (t) { t.classList.remove("is-active"); });
          thumb.classList.add("is-active");
          var mainImg = document.getElementById("gallery-main-img");
          if (mainImg) mainImg.src = thumb.getAttribute("data-src");
        });
      });

      var qtyInput = document.getElementById("opt-qty");
      var decBtn = mount.querySelector("[data-qty-decrease]");
      var incBtn = mount.querySelector("[data-qty-increase]");
      if (decBtn) decBtn.addEventListener("click", function () { qtyInput.value = Math.max(1, (parseInt(qtyInput.value, 10) || 1) - 1); });
      if (incBtn) incBtn.addEventListener("click", function () { qtyInput.value = Math.min(20, (parseInt(qtyInput.value, 10) || 1) + 1); });

      var addForm = document.getElementById("add-to-cart-form");
      addForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var qty = parseInt(qtyInput.value, 10) || 1;
        var sizeEl = document.getElementById("opt-size");
        var colorEl = document.getElementById("opt-color");
        var variantParts = [];
        if (sizeEl) variantParts.push(sizeEl.value);
        if (colorEl) variantParts.push(colorEl.value);
        var personalizationEl = document.getElementById("opt-personnalisation");
        addToCart(product.id, {
          qty: qty,
          variant: variantParts.join(" · "),
          personalization: personalizationEl ? personalizationEl.value.trim() : ""
        });
        toast("Ajouté au panier ✓ — " + product.name);
        var feedback = addForm.querySelector(".form-feedback");
        if (feedback) feedback.textContent = "Ajouté à votre panier (" + qty + (qty > 1 ? " articles)." : " article).");
      });
    }

    // Accordéon description / livraison / personnalisation
    var descPanel = document.getElementById("panel-description");
    var deliveryPanel = document.getElementById("panel-livraison");
    var persoPanel = document.getElementById("panel-personnalisation");
    if (descPanel) descPanel.innerHTML = "<p>" + product.description + "</p><p><strong>Matières :</strong> " + product.materials + "</p>";
    if (deliveryPanel) deliveryPanel.innerHTML = "<p>" + product.delivery + "</p>";
    if (persoPanel) persoPanel.innerHTML = "<p>" + product.personalizationInfo + "</p>";
    initAccordions();

    // JSON-LD produit
    var ld = document.getElementById("product-jsonld");
    if (ld) {
      ld.textContent = JSON.stringify({
        "@context": "https://schema.org/",
        "@type": "Product",
        name: product.name,
        description: product.short,
        image: product.images,
        offers: {
          "@type": "Offer",
          priceCurrency: "EUR",
          price: product.price,
          availability: "https://schema.org/InStock"
        },
        aggregateRating: {
          "@type": "AggregateRating",
          ratingValue: product.rating,
          reviewCount: product.reviews
        }
      });
    }

    // Vous aimerez aussi
    var relatedGrid = document.getElementById("related-grid");
    if (relatedGrid) {
      var related = PRODUCTS.filter(function (p) { return p.category === product.category && p.id !== product.id; }).slice(0, 4);
      if (related.length < 4) {
        PRODUCTS.filter(function (p) { return p.id !== product.id && related.indexOf(p) === -1; }).forEach(function (p) {
          if (related.length < 4) related.push(p);
        });
      }
      relatedGrid.innerHTML = related.map(productCardMarkup).join("");
      bindQuickAdd(relatedGrid);
      markRevealables("#related-grid .shop-card");
    }

    initReveal();
  }

  /* ------------------------------------------------------------------
     Page : panier
     ------------------------------------------------------------------ */
  function initPanier() {
    var listEl = document.getElementById("cart-list");
    var emptyEl = document.getElementById("cart-empty");
    var summaryEl = document.getElementById("cart-summary");
    var subtotalEl = document.getElementById("cart-subtotal");
    var progressBar = document.getElementById("shipping-progress-bar");
    var progressText = document.getElementById("shipping-progress-text");
    var clearBtn = document.getElementById("cart-clear");
    var checkoutBtn = document.getElementById("cart-checkout");
    var confirmEl = document.getElementById("checkout-confirm");
    if (!listEl) return;

    function render() {
      var lines = cartLines();
      listEl.innerHTML = "";
      if (!lines.length) {
        if (emptyEl) emptyEl.hidden = false;
        if (summaryEl) summaryEl.hidden = true;
        listEl.hidden = true;
        return;
      }
      listEl.hidden = false;
      if (emptyEl) emptyEl.hidden = true;
      if (summaryEl) summaryEl.hidden = false;

      lines.forEach(function (line) {
        var li = document.createElement("li");
        li.className = "cart-line";
        li.innerHTML =
          '<a class="cart-line-media" href="produit.html?id=' + line.product.id + '">' +
            '<img ' + imgAttrs(line.product.images[0]) + ' alt="' + line.product.name + '" loading="lazy" decoding="async">' +
          "</a>" +
          '<div class="cart-line-body">' +
            '<a class="cart-line-title" href="produit.html?id=' + line.product.id + '">' + line.product.name + "</a>" +
            (line.variant ? '<p class="cart-line-meta">Option : ' + line.variant + "</p>" : "") +
            (line.personalization ? '<p class="cart-line-meta">Personnalisation : « ' + line.personalization + " »</p>" : "") +
            '<div class="qty-stepper qty-stepper-sm">' +
              '<button type="button" class="qty-btn" data-line-decrease="' + line.lineId + '" aria-label="Diminuer la quantité">−</button>' +
              '<span class="qty-value">' + line.qty + "</span>" +
              '<button type="button" class="qty-btn" data-line-increase="' + line.lineId + '" aria-label="Augmenter la quantité">+</button>' +
            "</div>" +
          "</div>" +
          '<div class="cart-line-price">' + euros(line.product.price * line.qty) + "</div>" +
          '<button type="button" class="cart-line-remove" data-line-remove="' + line.lineId + '" aria-label="Retirer ' + line.product.name + " du panier\">✕</button>";
        listEl.appendChild(li);
      });

      var subtotal = cartSubtotal();
      if (subtotalEl) subtotalEl.textContent = euros(subtotal);
      var remaining = Math.max(0, FREE_SHIPPING_THRESHOLD - subtotal);
      var pct = Math.min(100, (subtotal / FREE_SHIPPING_THRESHOLD) * 100);
      if (progressBar) progressBar.style.width = pct + "%";
      if (progressText) {
        progressText.textContent = remaining > 0
          ? "Plus que " + euros(remaining) + " pour la livraison offerte !"
          : "Livraison offerte débloquée ✓";
      }

      listEl.querySelectorAll("[data-line-remove]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          removeLine(btn.getAttribute("data-line-remove"));
          render();
        });
      });
      listEl.querySelectorAll("[data-line-increase]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var id = btn.getAttribute("data-line-increase");
          var line = readCart().filter(function (l) { return l.lineId === id; })[0];
          if (line) setLineQty(id, line.qty + 1);
          render();
        });
      });
      listEl.querySelectorAll("[data-line-decrease]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var id = btn.getAttribute("data-line-decrease");
          var line = readCart().filter(function (l) { return l.lineId === id; })[0];
          if (line && line.qty > 1) setLineQty(id, line.qty - 1);
          else { removeLine(id); }
          render();
        });
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        clearCart();
        if (confirmEl) confirmEl.hidden = true;
        render();
      });
    }

    if (checkoutBtn) {
      checkoutBtn.addEventListener("click", function () {
        if (!cartCount()) return;
        if (confirmEl) {
          confirmEl.hidden = false;
          confirmEl.textContent = "Commande simulée avec succès ✓ Merci pour votre confiance — un e-mail de confirmation fictif vous serait envoyé ici.";
        }
        clearCart();
        render();
      });
    }

    render();
  }

  /* ------------------------------------------------------------------
     Page : contact (formulaire + FAQ)
     ------------------------------------------------------------------ */
  function initContact() {
    var form = document.getElementById("contact-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var feedback = form.querySelector(".form-feedback");
        var name = form.querySelector("#contact-nom");
        var email = form.querySelector("#contact-email");
        var message = form.querySelector("#contact-message");
        var valid = true;
        [name, email, message].forEach(function (field) {
          var errorEl = document.getElementById(field.id + "-error");
          if (!field.checkValidity()) {
            valid = false;
            if (errorEl) errorEl.textContent = field.validationMessage || "Ce champ est requis.";
            field.setAttribute("aria-invalid", "true");
          } else {
            if (errorEl) errorEl.textContent = "";
            field.removeAttribute("aria-invalid");
          }
        });
        if (!valid) {
          if (feedback) { feedback.textContent = "Merci de corriger les champs signalés."; feedback.classList.add("is-error"); }
          return;
        }
        if (feedback) {
          feedback.textContent = "Message envoyé ✓ Nous vous répondons sous 24 à 48 h ouvrées.";
          feedback.classList.remove("is-error");
        }
        form.reset();
      });
    }
    initAccordions();
  }

  /* ------------------------------------------------------------------
     Initialisation générale
     ------------------------------------------------------------------ */
  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initHeaderScroll();
    updateCartCount();
    initNewsletter();
    markRevealables(".product-card, .why-item, .review-card, .collection-card");

    var page = document.body.getAttribute("data-page");
    if (page === "home") initHome();
    else if (page === "boutique") initBoutique();
    else if (page === "produit") initProduit();
    else if (page === "panier") initPanier();
    else if (page === "contact") initContact();
    else if (page === "a-propos") initAccordions();

    initReveal();
  });
})();
