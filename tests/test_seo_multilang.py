"""LOT 1 regression tests: multilingual URL structure, canonical/hreflang
correctness, sitemap/robots generation, and the "no noindex in production"
rule.

Builds the real build.py, unmodified, into an isolated temp copy of the repo
(see _build_helper) and inspects the generated files. Does not reimplement
build.py's generation logic.
"""

import json
import re
import shutil
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from _build_helper import LANGS, REPO_ROOT, make_build_copy, run_build

SITE = "https://projethermes.github.io/chiccelebria-demo"
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)">')
HREFLANG_RE = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')
NOINDEX_RE = re.compile(r'<meta name="robots"[^>]*noindex')


class SeoMultilangTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = make_build_copy()
        run_build(cls.tmpdir)

        cls.products = json.loads((REPO_ROOT / "products.json").read_text(encoding="utf-8"))
        cls.collections = json.loads((REPO_ROOT / "collections.json").read_text(encoding="utf-8"))
        cls.active_products = [p for p in cls.products if p.get("actif", True)]
        cls.active_collections = [c for c in cls.collections if c.get("actif", True)]

        # Every generated *.html page under a language directory, plus the
        # collections index — these are the "production" pages.
        cls.lang_pages = []
        for lang in LANGS:
            for html_file in sorted((cls.tmpdir / lang).rglob("*.html")):
                cls.lang_pages.append(html_file)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_every_language_has_a_directory_tree(self):
        for lang in LANGS:
            self.assertTrue((self.tmpdir / lang / "index.html").is_file())
            self.assertTrue((self.tmpdir / lang / "about.html").is_file())
            self.assertTrue((self.tmpdir / lang / "collections" / "index.html").is_file())

    def test_no_lang_page_is_empty(self):
        self.assertGreater(len(self.lang_pages), 0)

    def test_canonical_is_self_referent_on_every_page(self):
        """The canonical URL of a page must resolve back to that same page."""
        for path in self.lang_pages:
            content = path.read_text(encoding="utf-8")
            match = CANONICAL_RE.search(content)
            self.assertIsNotNone(match, f"{path} has no canonical tag")
            canonical = match.group(1)
            self.assertTrue(canonical.startswith(SITE + "/"), f"{path} canonical is not absolute: {canonical}")
            rel = canonical[len(SITE) + 1:]
            # The canonical path must point at the file itself (or its
            # directory-index equivalent).
            expected = path.relative_to(self.tmpdir).as_posix()
            expected_dir_form = expected[: -len("index.html")] if expected.endswith("index.html") else expected
            self.assertIn(rel, {expected, expected_dir_form}, f"{path} canonical {canonical!r} does not match its own URL")

    def test_hreflang_is_reciprocal_and_covers_all_languages(self):
        for path in self.lang_pages:
            content = path.read_text(encoding="utf-8")
            tags = HREFLANG_RE.findall(content)
            self.assertTrue(tags, f"{path} has no hreflang tags")
            langs_seen = {lang for lang, _ in tags if lang != "x-default"}
            self.assertEqual(langs_seen, set(LANGS), f"{path} hreflang does not cover all 5 languages")
            xdefaults = [href for lang, href in tags if lang == "x-default"]
            self.assertEqual(len(xdefaults), 1, f"{path} must have exactly one x-default hreflang")
            en_href = dict(tags)["en"]
            self.assertEqual(xdefaults[0], en_href, f"{path} x-default must point at the English version")

    def test_hreflang_targets_are_mutually_consistent_across_alternates(self):
        """If page A in lang X lists an hreflang alternate to page B in lang
        Y, then page B must list the same set of alternates back (the
        canonical definition of "reciprocal")."""
        alt_sets = {}
        for path in self.lang_pages:
            content = path.read_text(encoding="utf-8")
            tags = HREFLANG_RE.findall(content)
            urls = frozenset(href for lang, href in tags if lang != "x-default")
            canonical = CANONICAL_RE.search(content).group(1)
            alt_sets[canonical] = urls

        for canonical, urls in alt_sets.items():
            self.assertIn(canonical, urls, f"{canonical} does not list itself among its own hreflang alternates")
            for other in urls:
                if other == canonical:
                    continue
                self.assertIn(other, alt_sets, f"{canonical} links to {other} which was not generated")
                self.assertEqual(
                    alt_sets[other], urls,
                    f"hreflang not reciprocal between {canonical} and {other}",
                )

    def test_no_noindex_on_production_pages(self):
        """Only the root 404.html (not a real language/content page) may be
        noindex. Every generated language page must be indexable."""
        for path in self.lang_pages:
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(NOINDEX_RE.search(content), f"{path} must not contain a noindex directive")

        root_index = (self.tmpdir / "index.html").read_text(encoding="utf-8")
        root_about = (self.tmpdir / "about.html").read_text(encoding="utf-8")
        self.assertIsNone(NOINDEX_RE.search(root_index))
        self.assertIsNone(NOINDEX_RE.search(root_about))

    def test_root_redirects_point_at_english_pages(self):
        root_index = (self.tmpdir / "index.html").read_text(encoding="utf-8")
        root_about = (self.tmpdir / "about.html").read_text(encoding="utf-8")
        self.assertIn('url=en/index.html', root_index)
        self.assertIn('url=en/about.html', root_about)

    def test_robots_txt_allows_indexing_and_references_sitemap(self):
        robots = (self.tmpdir / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /", robots)
        self.assertNotIn("Disallow: /\n", robots)
        self.assertIn(f"Sitemap: {SITE}/sitemap.xml", robots)

    def test_sitemap_is_well_formed_and_synced_with_generated_pages(self):
        sitemap_path = self.tmpdir / "sitemap.xml"
        self.assertTrue(sitemap_path.is_file())
        tree = ET.parse(sitemap_path)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = {el.text for el in tree.getroot().findall("sm:url/sm:loc", ns)}

        expected_locs = set()
        for path in self.lang_pages:
            content = path.read_text(encoding="utf-8")
            match = CANONICAL_RE.search(content)
            expected_locs.add(match.group(1))

        self.assertEqual(locs, expected_locs, "sitemap.xml URLs do not exactly match generated page canonicals")

    def test_sitemap_url_count_matches_active_catalog(self):
        sitemap_path = self.tmpdir / "sitemap.xml"
        tree = ET.parse(sitemap_path)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = tree.getroot().findall("sm:url", ns)
        # home + about + collections-index + collections + products, x5 langs
        expected = (3 + len(self.active_collections) + len(self.active_products)) * len(LANGS)
        self.assertEqual(len(urls), expected)

    def test_product_and_collection_slugs_are_translated_where_names_differ(self):
        """Spot-check: when a product's translated name differs across
        languages, its URL slug must differ too (real translation, not a
        copy-pasted English slug)."""
        sample = self.active_products[0]
        en_name = sample["nom"]["en"]
        fr_name = sample["nom"]["fr"]
        if en_name.strip().lower() == fr_name.strip().lower():
            self.skipTest("sample product name is identical in en/fr")
        en_path = self.tmpdir / "en" / "products"
        fr_path = self.tmpdir / "fr" / "products"
        en_slugs = {d.name for d in en_path.iterdir() if d.is_dir()}
        fr_slugs = {d.name for d in fr_path.iterdir() if d.is_dir()}
        self.assertNotEqual(en_slugs, fr_slugs, "French product slugs are identical to English — not translated")


if __name__ == "__main__":
    unittest.main()
