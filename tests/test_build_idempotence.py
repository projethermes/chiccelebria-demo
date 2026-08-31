"""Regression test: python3 build.py must be idempotent.

Guards against the bug fixed in commit d89d056, where static_page()
re-injected a duplicate <script src="i18n-data.js"></script> tag into
index.html / about.html / 404.html on every run of build.py.

Run with either:
    python3 -m unittest tests/test_build_idempotence.py -v
    python3 -m unittest discover -s tests -v
    pytest tests/test_build_idempotence.py -v   (pytest is optional; unittest needs no extra deps)

The test never touches the real repository working tree: it copies only
the files build.py needs (build.py, products.json, collections.json,
index.html, about.html, 404.html) into a temp directory and runs the
real build.py there, unmodified. It does not reimplement build.py's
generation logic — it only invokes it as a subprocess and inspects the
files it writes.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_INPUTS = [
    "build.py",
    "products.json",
    "collections.json",
    "index.html",
    "about.html",
    "404.html",
]


def run_build(cwd):
    result = subprocess.run(
        [sys.executable, "build.py"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"build.py failed (exit {result.returncode}):\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def hash_generated_files(root):
    """SHA-256 of every file build.py is expected to (re)generate, keyed by relative path."""
    hashes = {}
    generated_patterns = ["i18n-data.js", "index.html", "about.html", "404.html"]
    for name in generated_patterns:
        path = root / name
        if path.is_file():
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    for sub in ("products", "collections"):
        base = root / sub
        if base.is_dir():
            for html_file in sorted(base.rglob("index.html")):
                rel = html_file.relative_to(root).as_posix()
                hashes[rel] = hashlib.sha256(html_file.read_bytes()).hexdigest()
    return hashes


class BuildIdempotenceTest(unittest.TestCase):
    """Two consecutive `python3 build.py` runs on unchanged sources must
    produce byte-identical output."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="chiccelebria-build-test-"))
        for name in BUILD_INPUTS:
            shutil.copy2(REPO_ROOT / name, cls.tmpdir / name)

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
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_second_build_is_byte_identical_to_first(self):
        self.assertEqual(
            self.hashes_after_first_build,
            self.hashes_after_second_build,
            "build.py produced different output on a second run with unchanged sources "
            "(non-idempotent build).",
        )

    def test_no_duplicate_script_tags_in_static_pages(self):
        for name in ("index.html", "about.html", "404.html"):
            content = (self.tmpdir / name).read_text(encoding="utf-8")
            for tag in (
                '<script src="i18n-data.js"></script>',
                '<script src="i18n.js"></script>',
            ):
                count = content.count(tag)
                self.assertEqual(
                    count, 1,
                    f"{name} should contain exactly one {tag!r}, found {count}",
                )

    def test_all_active_products_and_collections_generated(self):
        product_dirs = [d for d in (self.tmpdir / "products").iterdir() if d.is_dir()]
        collection_dirs = [d for d in (self.tmpdir / "collections").iterdir() if d.is_dir()]
        self.assertEqual(len(product_dirs), self.expected_active_products)
        self.assertEqual(len(collection_dirs), self.expected_active_collections)


if __name__ == "__main__":
    unittest.main()
