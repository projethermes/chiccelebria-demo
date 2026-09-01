"""Regression test: python3 build.py must be idempotent.

Two consecutive runs of `python3 build.py` on unchanged sources must produce
byte-identical output across every language directory (en/es/fr/it/de),
plus the root redirect/404/sitemap/robots files.

The test never touches the real repository working tree: it copies only the
files build.py needs into a temp directory and runs the real build.py there,
unmodified. It does not reimplement build.py's generation logic — it only
invokes it as a subprocess and inspects the files it writes.

Run with:
    python3 -m unittest discover -s tests -v
"""

import hashlib
import json
import unittest
from pathlib import Path

from _build_helper import LANGS, REPO_ROOT, make_build_copy, run_build

ROOT_GENERATED = ["index.html", "about.html", "404.html", "sitemap.xml", "robots.txt"]


def hash_generated_files(root):
    """SHA-256 of every file build.py is expected to (re)generate, keyed by relative path."""
    hashes = {}
    for name in ROOT_GENERATED:
        path = root / name
        if path.is_file():
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    for lang in LANGS:
        lang_dir = root / lang
        if lang_dir.is_dir():
            for html_file in sorted(lang_dir.rglob("*.html")):
                rel = html_file.relative_to(root).as_posix()
                hashes[rel] = hashlib.sha256(html_file.read_bytes()).hexdigest()
    return hashes


class BuildIdempotenceTest(unittest.TestCase):
    """Two consecutive `python3 build.py` runs on unchanged sources must
    produce byte-identical output."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = make_build_copy()

        cls.products = json.loads((REPO_ROOT / "products.json").read_text(encoding="utf-8"))
        cls.collections = json.loads((REPO_ROOT / "collections.json").read_text(encoding="utf-8"))
        cls.expected_active_products = sum(1 for p in cls.products if p.get("actif", True))
        cls.expected_active_collections = sum(1 for c in cls.collections if c.get("actif", True))

        # First build establishes the "clean generated state" baseline.
        run_build(cls.tmpdir)
        cls.hashes_after_first_build = hash_generated_files(cls.tmpdir)

        # Second build: same sources, no edits in between.
        run_build(cls.tmpdir)
        cls.hashes_after_second_build = hash_generated_files(cls.tmpdir)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_second_build_is_byte_identical_to_first(self):
        self.assertEqual(
            self.hashes_after_first_build,
            self.hashes_after_second_build,
            "build.py produced different output on a second run with unchanged sources "
            "(non-idempotent build).",
        )

    def test_no_duplicate_script_tags_in_generated_pages(self):
        for rel in ("en/index.html", "en/about.html"):
            path = self.tmpdir / rel
            content = path.read_text(encoding="utf-8")
            for needle in ("site-config.js", "script.js"):
                count = content.count(needle)
                self.assertEqual(count, 1, f"{rel} should reference {needle} exactly once, found {count}")

    def test_all_active_products_and_collections_generated_per_language(self):
        for lang in LANGS:
            product_dirs = [d for d in (self.tmpdir / lang / "products").iterdir() if d.is_dir()]
            collection_dirs = [
                d for d in (self.tmpdir / lang / "collections").iterdir()
                if d.is_dir()
            ]
            self.assertEqual(
                len(product_dirs), self.expected_active_products,
                f"expected {self.expected_active_products} product pages for lang={lang}",
            )
            self.assertEqual(
                len(collection_dirs), self.expected_active_collections,
                f"expected {self.expected_active_collections} collection pages for lang={lang}",
            )


if __name__ == "__main__":
    unittest.main()
