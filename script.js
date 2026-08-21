/* ==========================================================================
   Chic Celebria — script.js
   Vanilla JS, no dependencies. Handles: sticky header state, mobile nav,
   active nav link, Etsy CTA wiring, reveal-on-scroll, accordions, product
   gallery thumbnails, collection filter/sort, newsletter form feedback.
   No cart, no checkout, no fake reviews/ratings — phase 1 sells on Etsy.
   ========================================================================== */
(function () {
  "use strict";

  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------------
     Sticky header — border appears once the page has scrolled
     ------------------------------------------------------------------ */
  function initHeader() {
    var header = document.querySelector("[data-site-header]");
    if (!header) return;

    function onScroll() {
      header.classList.toggle("is-scrolled", window.scrollY > 4);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    var toggle = document.getElementById("nav-toggle");
    var nav = document.getElementById("main-nav");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        var isOpen = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      });
      nav.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          nav.classList.remove("is-open");
          toggle.setAttribute("aria-expanded", "false");
        });
      });
    }

    // Mark the current page's nav link.
    var here = window.location.pathname.replace(/index\.html$/, "");
    nav && nav.querySelectorAll("a[href]").forEach(function (link) {
      var linkPath = link.pathname.replace(/index\.html$/, "");
      if (linkPath && linkPath === here) {
        link.setAttribute("aria-current", "page");
      }
    });
  }

  /* ------------------------------------------------------------------
     Etsy CTAs — every "Shop on Etsy" / "View on Etsy" link reads its
     target from the single source of truth in assets/site-config.js
     ------------------------------------------------------------------ */
  function initEtsyLinks() {
    var shopUrl = window.CHIC && window.CHIC.etsyShopUrl;
    if (!shopUrl) return;
    document.querySelectorAll("[data-etsy-cta]").forEach(function (link) {
      link.setAttribute("href", shopUrl);
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener");
    });
  }

  /* ------------------------------------------------------------------
     Reveal-on-scroll — very small fade/slide-in, disabled for users
     who prefer reduced motion
     ------------------------------------------------------------------ */
  function initReveal() {
    var items = document.querySelectorAll(".reveal");
    if (!items.length) return;

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });

    items.forEach(function (el) { observer.observe(el); });
  }

  /* ------------------------------------------------------------------
     Accordion — Details / Dimensions / Materials / Care / Delivery /
     Returns on product pages
     ------------------------------------------------------------------ */
  function initAccordions() {
    document.querySelectorAll(".accordion-trigger").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var panel = document.getElementById(trigger.getAttribute("aria-controls"));
        var isOpen = trigger.getAttribute("aria-expanded") === "true";
        trigger.setAttribute("aria-expanded", isOpen ? "false" : "true");
        if (panel) panel.hidden = isOpen;
      });
    });
  }

  /* ------------------------------------------------------------------
     Product gallery — swap main image on thumbnail click
     ------------------------------------------------------------------ */
  function initGallery() {
    var main = document.querySelector(".gallery-main img");
    var thumbs = document.querySelectorAll(".gallery-thumb");
    if (!main || !thumbs.length) return;

    thumbs.forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        var full = thumb.getAttribute("data-full");
        var alt = thumb.getAttribute("data-alt");
        if (!full) return;
        main.setAttribute("src", full);
        if (alt) main.setAttribute("alt", alt);
        thumbs.forEach(function (t) { t.classList.remove("is-active"); });
        thumb.classList.add("is-active");
      });
    });
  }

  /* ------------------------------------------------------------------
     Collection filter + sort — operates on any [data-collection-grid]
     containing cards with data-name / data-price / data-type
     ------------------------------------------------------------------ */
  function initCollectionToolbar() {
    var grid = document.querySelector("[data-collection-grid]");
    if (!grid) return;

    var cards = Array.prototype.slice.call(grid.querySelectorAll(".p-card"));
    var typeSelect = document.getElementById("filter-type");
    var priceSelect = document.getElementById("filter-price");
    var sortSelect = document.getElementById("sort-by");
    var countEl = document.querySelector("[data-result-count]");
    var emptyEl = document.querySelector("[data-collection-empty]");

    function priceInRange(price, range) {
      if (range === "under-15") return price < 15;
      if (range === "15-25") return price >= 15 && price <= 25;
      if (range === "over-25") return price > 25;
      return true;
    }

    function apply() {
      var type = typeSelect ? typeSelect.value : "all";
      var price = priceSelect ? priceSelect.value : "all";
      var sort = sortSelect ? sortSelect.value : "name-asc";

      var visible = cards.filter(function (card) {
        var cardType = card.getAttribute("data-type");
        var cardPrice = parseFloat(card.getAttribute("data-price"));
        var typeOk = type === "all" || cardType === type;
        var priceOk = priceInRange(cardPrice, price);
        return typeOk && priceOk;
      });

      visible.sort(function (a, b) {
        if (sort === "price-asc") return parseFloat(a.getAttribute("data-price")) - parseFloat(b.getAttribute("data-price"));
        if (sort === "price-desc") return parseFloat(b.getAttribute("data-price")) - parseFloat(a.getAttribute("data-price"));
        if (sort === "name-desc") return b.getAttribute("data-name").localeCompare(a.getAttribute("data-name"));
        return a.getAttribute("data-name").localeCompare(b.getAttribute("data-name"));
      });

      cards.forEach(function (card) { card.hidden = true; });
      visible.forEach(function (card) {
        card.hidden = false;
        grid.appendChild(card);
      });

      if (countEl) {
        var pieceKey = visible.length === 1 ? "toolbar.piece" : "toolbar.pieces";
        countEl.textContent = window.I18N ? window.I18N.t(pieceKey, { n: visible.length }) : (visible.length + " pieces");
      }
      if (emptyEl) emptyEl.hidden = visible.length !== 0;
    }

    [typeSelect, priceSelect, sortSelect].forEach(function (select) {
      if (select) select.addEventListener("change", apply);
    });

    apply();

    document.addEventListener("chic:lang", function () { apply(); });
  }

  /* ------------------------------------------------------------------
     Newsletter — client-side only, no backend in phase 1
     ------------------------------------------------------------------ */
  function initNewsletter() {
    var form = document.querySelector(".newsletter-form");
    if (!form) return;
    var feedback = document.querySelector(".form-feedback");
    var input = form.querySelector("input[type=email]");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var value = input ? input.value.trim() : "";
      var isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
      if (!feedback) return;
      if (isValid) {
        feedback.textContent = window.I18N ? window.I18N.t("home.newsletter.thanks") : "Thank you — you're on the list.";
        feedback.classList.remove("is-error");
        form.reset();
      } else {
        feedback.textContent = window.I18N ? window.I18N.t("home.newsletter.error") : "Please enter a valid email address.";
        feedback.classList.add("is-error");
      }
    });
  }

  /* ------------------------------------------------------------------
     Footer year
     ------------------------------------------------------------------ */
  function initFooterYear() {
    var el = document.getElementById("year");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  document.addEventListener("DOMContentLoaded", function () {
    initHeader();
    initEtsyLinks();
    initReveal();
    initAccordions();
    initGallery();
    initCollectionToolbar();
    initNewsletter();
    initFooterYear();
  });
})();
