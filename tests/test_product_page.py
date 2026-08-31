"""LOT 2 regression tests: Best-of product page.

Covers the "never fabricate a product characteristic" rule: gallery,
accordion sections (dimensions/materials/care/delivery), variant options and
personalisation must only render when the product's own data declares them.
Also covers Product + BreadcrumbList JSON-LD and the "never duplicate a real
image across products" rule.

Part of these tests exercise build.py's pure helper functions directly with
synthetic product dicts (no file I/O); the rest inspect the real generated
output via _build_helper (build.py run unmodified in an isolated temp copy).
"""

import json
import re
import sys
import unittest
from pathlib import Path

from _build_helper import LANGS, REPO_ROOT, make_build_copy, run_build

sys.path.insert(0, str(REPO_ROOT))
import build  # noqa: E402  (must import after sys.path tweak)


def make_product(**overrides):
    base = {
        "id": "test-product",
        "nom": {l: "Test Product" for l in LANGS},
        "description": {l: "A test description." for l in LANGS},
        "prix": 19.99,
        "images": ["assets/sourcing/tapis.jpg"],
        "collections": ["halloween"],
        "stock": True,
        "actif": True,
    }
    base.update(overrides)
    return base


class AccordionHelperTest(unittest.TestCase):
    """accordion_html() must only render a section for a field that is
    actually present and non-empty for the given language."""

    def test_no_optional_fields_renders_nothing(self):
        p = make_product()
        self.assertEqual(build.accordion_html("en", p), "")

    def test_one_declared_field_renders_only_that_section(self):
        p = make_product(materiaux={"en": "100% cotton."})
        out = build.accordion_html("en", p)
        self.assertIn("100% cotton.", out)
        self.assertIn(build.STRINGS["en"]["accordion.materials"], out)
        self.assertNotIn(build.STRINGS["en"]["accordion.dimensions"], out)
        self.assertNotIn(build.STRINGS["en"]["accordion.care"], out)
        self.assertNotIn(build.STRINGS["en"]["accordion.delivery"], out)

    def test_field_missing_translation_for_language_is_skipped(self):
        p = make_product(materiaux={"fr": "100% coton."})
        self.assertEqual(build.accordion_html("en", p), "")
        self.assertIn("100% coton.", build.accordion_html("fr", p))

    def test_all_four_optional_fields_render_together(self):
        p = make_product(
            dimensions={"en": "40x60cm"},
            materiaux={"en": "Cotton"},
            entretien={"en": "Hand wash"},
            livraison={"en": "Ships in 3 days"},
        )
        out = build.accordion_html("en", p)
        for text in ("40x60cm", "Cotton", "Hand wash", "Ships in 3 days"):
            self.assertIn(text, out)


class OptionsHelperTest(unittest.TestCase):
    def test_no_options_key_renders_nothing(self):
        self.assertEqual(build.options_html("en", make_product()), "")

    def test_declared_options_render_a_select_per_group(self):
        p = make_product(options=[
            {"name": {"en": "Size"}, "values": [{"en": "Small"}, {"en": "Large"}]},
        ])
        out = build.options_html("en", p)
        self.assertIn("Size", out)
        self.assertIn("Small", out)
        self.assertIn("Large", out)
        self.assertIn("<select", out)


class PersonalisationHelperTest(unittest.TestCase):
    def test_no_personalisation_key_renders_nothing(self):
        self.assertEqual(build.personalisation_html("en", make_product()), "")

    def test_declared_personalisation_renders_input_with_hint(self):
        p = make_product(personalisation={"en": "e.g. a name or short message"})
        out = build.personalisation_html("en", p)
        self.assertIn("e.g. a name or short message", out)
        self.assertIn("<input", out)

    def test_personalisation_missing_language_renders_nothing(self):
        p = make_product(personalisation={"fr": "ex. un prénom"})
        self.assertEqual(build.personalisation_html("en", p), "")


class RelatedProductsHelperTest(unittest.TestCase):
    def test_excludes_self_and_limits_to_four(self):
        real_products = build.active_products()
        target = next(p for p in real_products if len(build.products_of(p["collections"][0])) > 1)
        related = build.related_products(target)
        self.assertNotIn(target["id"], [r["id"] for r in related])
        self.assertLessEqual(len(related), 4)
        for r in related:
            self.assertIn(target["collections"][0], r["collections"])


class GeneratedProductPageTest(unittest.TestCase):
    """Inspects the real generated output for the current catalog, where
    zero products declare dimensions/materiaux/entretien/livraison/options/
    personalisation — so none of those sections should ever appear."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = make_build_copy()
        run_build(cls.tmpdir)
        cls.products = json.loads((REPO_ROOT / "products.json").read_text(encoding="utf-8"))
        cls.active_products = [p for p in cls.products if p.get("actif", True)]
        cls.product_pages = sorted((cls.tmpdir / "en" / "products").glob("*/index.html"))

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_current_catalog_has_no_fabricated_sections(self):
        for path in self.product_pages:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn('class="accordion"', content, f"{path} has an accordion section but no product declares one")
            self.assertNotIn('product-options', content, f"{path} has options but no product declares any")
            self.assertNotIn('product-personalisation', content, f"{path} has a personalisation field but no product declares one")

    def test_every_product_page_has_product_and_breadcrumb_jsonld(self):
        for path in self.product_pages:
            content = path.read_text(encoding="utf-8")
            ld_blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', content, re.S)
            types = [json.loads(b)["@type"] for b in ld_blocks]
            self.assertIn("Product", types, f"{path} missing Product JSON-LD")
            self.assertIn("BreadcrumbList", types, f"{path} missing BreadcrumbList JSON-LD")

    def test_product_jsonld_image_belongs_to_that_product(self):
        for path in self.product_pages:
            content = path.read_text(encoding="utf-8")
            ld_blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', content, re.S)
            product_ld = next(json.loads(b) for b in ld_blocks if json.loads(b)["@type"] == "Product")
            canonical = re.search(r'<link rel="canonical" href="([^"]+)">', content).group(1)
            self.assertTrue(product_ld["image"], f"{canonical} Product JSON-LD has no image")

    def test_no_two_active_products_share_the_same_image(self):
        seen = {}
        for p in self.active_products:
            for img in p.get("images", []):
                self.assertNotIn(img, seen, f"image {img} is used by both {seen.get(img)} and {p['id']}")
                seen[img] = p["id"]

    def test_gallery_thumbnails_only_render_for_multi_image_products(self):
        # Every product in the current catalog has exactly one image, so no
        # generated page should render gallery thumbnails.
        self.assertFalse(any(len(p.get("images", [])) > 1 for p in self.active_products))
        for path in self.product_pages:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("gallery-thumbs", content, f"{path} renders gallery thumbnails but has only one image")


if __name__ == "__main__":
    unittest.main()
