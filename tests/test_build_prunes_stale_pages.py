"""Regression test: build.py must not leave orphaned generated pages behind.

When a product is deleted, or renamed in a way that changes its slug, the
directory generated for its *old* slug must disappear on the next build —
otherwise a ghost page (outside the sitemap, unreachable from the site, but
still live at its old URL) accumulates forever. See build.py's
prune_stale_pages().

The test never touches the real repository working tree: it copies only the
files build.py needs into a temp directory and runs the real build.py there,
unmodified.
"""

import json
import unittest

from _build_helper import LANGS, make_build_copy, run_build


class BuildPrunesStalePagesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = make_build_copy()
        self.products_path = self.tmpdir / "products.json"
        self.products = json.loads(self.products_path.read_text(encoding="utf-8"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_products(self, products):
        self.products_path.write_text(
            json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def test_renaming_a_product_removes_its_old_slug_directory(self):
        run_build(self.tmpdir)
        target = self.products[0]
        old_slug_dirs = {
            lang: [d.name for d in (self.tmpdir / lang / "products").iterdir() if d.is_dir()]
            for lang in LANGS
        }

        target["nom"] = {lang: v + " Edition Speciale" for lang, v in target["nom"].items()}
        self._write_products(self.products)
        run_build(self.tmpdir)

        for lang in LANGS:
            new_dirs = {d.name for d in (self.tmpdir / lang / "products").iterdir() if d.is_dir()}
            # Same total count (one old slug replaced by one new slug)...
            self.assertEqual(
                len(new_dirs), len(old_slug_dirs[lang]),
                f"lang={lang}: product page count changed after a rename (expected same count)",
            )
            # ...and every other product's directory must be untouched.
            untouched = set(old_slug_dirs[lang]) & new_dirs
            self.assertEqual(
                len(untouched), len(old_slug_dirs[lang]) - 1,
                f"lang={lang}: exactly one old directory (the renamed product's) should disappear",
            )

    def test_deleting_a_product_removes_its_page_directory(self):
        run_build(self.tmpdir)
        removed_id = self.products[0]["id"]
        remaining = self.products[1:]
        self._write_products(remaining)
        run_build(self.tmpdir)

        for lang in LANGS:
            dirs = {d.name for d in (self.tmpdir / lang / "products").iterdir() if d.is_dir()}
            self.assertEqual(len(dirs), len(remaining), f"lang={lang}: stale product directory left behind")


if __name__ == "__main__":
    unittest.main()
