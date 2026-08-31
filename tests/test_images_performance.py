"""LOT 4 regression tests: image dimensions and loading performance.

Covers: every generated <img> has explicit width/height read from the real
file (no guessed placeholder aspect ratio), the LCP candidate on each page
type gets fetchpriority="high" (and is never also marked loading="lazy"),
and the homepage preloads its CSS hero background image.
"""

import re
import sys
import unittest
from pathlib import Path

from _build_helper import REPO_ROOT, make_build_copy, run_build

sys.path.insert(0, str(REPO_ROOT))
import build  # noqa: E402

IMG_RE = re.compile(r"<img\b[^>]*>")
WIDTH_RE = re.compile(r'\bwidth="(\d+)"')
HEIGHT_RE = re.compile(r'\bheight="(\d+)"')


class ImageDimensionsHelperTest(unittest.TestCase):
    def test_reads_real_jpeg_dimensions(self):
        self.assertEqual(build.image_dimensions("assets/sourcing/tapis.jpg"), (1600, 1600))

    def test_reads_real_webp_dimensions(self):
        self.assertEqual(build.image_dimensions("assets/macrame.webp"), (1000, 1000))

    def test_reads_non_square_jpeg_dimensions(self):
        self.assertEqual(build.image_dimensions("assets/produits/img-10.jpg"), (900, 506))

    def test_unknown_file_falls_back_without_raising(self):
        self.assertEqual(build.image_dimensions("assets/does-not-exist.jpg"), (1000, 1000))

    def test_dimensions_are_cached(self):
        build.image_dimensions("assets/produits/img-09.jpg")
        self.assertIn("assets/produits/img-09.jpg", build._IMAGE_DIM_CACHE)


class GeneratedPageImageAttributesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = make_build_copy()
        run_build(cls.tmpdir)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_every_img_tag_has_explicit_width_and_height(self):
        sample_pages = [
            self.tmpdir / "en" / "index.html",
            self.tmpdir / "en" / "about.html",
            self.tmpdir / "en" / "collections" / "halloween" / "index.html",
            self.tmpdir / "en" / "products" / "halloween-doormat" / "index.html",
        ]
        for path in sample_pages:
            content = path.read_text(encoding="utf-8")
            tags = IMG_RE.findall(content)
            self.assertGreater(len(tags), 0, f"{path} has no <img> tags")
            for tag in tags:
                self.assertRegex(tag, WIDTH_RE, f"{path} has an <img> with no width: {tag}")
                self.assertRegex(tag, HEIGHT_RE, f"{path} has an <img> with no height: {tag}")

    def test_product_page_main_image_is_fetchpriority_high_and_not_lazy(self):
        path = self.tmpdir / "en" / "products" / "halloween-doormat" / "index.html"
        content = path.read_text(encoding="utf-8")
        main_img = re.search(r'<div class="gallery-main">\s*(<img\b[^>]*>)', content).group(1)
        self.assertIn('fetchpriority="high"', main_img)
        self.assertNotIn("loading=\"lazy\"", main_img)

    def test_collection_page_first_card_is_lcp_others_are_lazy(self):
        path = self.tmpdir / "en" / "collections" / "halloween" / "index.html"
        content = path.read_text(encoding="utf-8")
        card_imgs = re.findall(r'<img class="img-main"[^>]*>', content)
        self.assertGreater(len(card_imgs), 1, "expected multiple product cards in the halloween collection")
        self.assertIn('fetchpriority="high"', card_imgs[0])
        self.assertNotIn("loading=\"lazy\"", card_imgs[0])
        for later in card_imgs[1:]:
            self.assertIn('loading="lazy"', later)
            self.assertNotIn("fetchpriority", later)

    def test_home_page_preloads_hero_background(self):
        content = (self.tmpdir / "en" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="preload" as="image" fetchpriority="high"', content)
        self.assertIn("img-09.jpg", content)

    def test_no_image_is_both_lazy_and_high_priority(self):
        for path in (self.tmpdir / "en").rglob("*.html"):
            content = path.read_text(encoding="utf-8")
            for tag in IMG_RE.findall(content):
                if 'fetchpriority="high"' in tag:
                    self.assertNotIn("loading=\"lazy\"", tag, f"{path}: {tag}")


if __name__ == "__main__":
    unittest.main()
