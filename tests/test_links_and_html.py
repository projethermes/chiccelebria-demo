"""LOT 5 regression tests: final integrity checks.

- No broken internal links or asset references in the generated site.
- Every generated page is well-formed HTML (balanced tags, single
  doctype/html/head/body).
- The exact active product/collection counts match products.json /
  collections.json, across every generated language.

Builds the real build.py, unmodified, into an isolated temp copy that also
contains assets/, style.css and script.js (see _build_helper.make_full_site_copy)
so relative links can actually be resolved on disk.
"""

import json
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit

from _build_helper import LANGS, REPO_ROOT, make_full_site_copy, run_build

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

LINK_ATTR_RE = re.compile(r'\b(?:href|src)="([^"]*)"')


class StructureChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.tag_counts = {"html": 0, "head": 0, "body": 0}

    def handle_starttag(self, tag, attrs):
        if tag in self.tag_counts:
            self.tag_counts[tag] += 1
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass  # self-closed, nothing to push

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (stack: {self.stack})")
            return
        self.stack.pop()


class LinksAndHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = make_full_site_copy()
        run_build(cls.tmpdir)
        cls.all_pages = sorted(cls.tmpdir.rglob("*.html"))
        cls.products = json.loads((REPO_ROOT / "products.json").read_text(encoding="utf-8"))
        cls.collections = json.loads((REPO_ROOT / "collections.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_found_generated_pages(self):
        self.assertGreater(len(self.all_pages), 200)

    def test_no_broken_internal_links_or_assets(self):
        broken = []
        for path in self.all_pages:
            content = path.read_text(encoding="utf-8")
            for match in LINK_ATTR_RE.findall(content):
                if not match or match.startswith("#"):
                    continue
                parsed = urlsplit(match)
                if parsed.scheme or match.startswith("//"):
                    continue  # external (https://..., mailto:, etc.)
                target = (path.parent / parsed.path).resolve()
                if not target.exists():
                    broken.append((str(path.relative_to(self.tmpdir)), match))
        self.assertEqual(broken, [], f"broken internal references found: {broken[:20]}")

    def test_every_page_is_well_formed_html(self):
        malformed = []
        for path in self.all_pages:
            content = path.read_text(encoding="utf-8")
            if not content.lstrip().lower().startswith("<!doctype html>"):
                malformed.append((str(path.relative_to(self.tmpdir)), "missing <!DOCTYPE html>"))
                continue
            checker = StructureChecker()
            checker.feed(content)
            if checker.stack:
                malformed.append((str(path.relative_to(self.tmpdir)), f"unclosed tags: {checker.stack}"))
            if checker.errors:
                malformed.append((str(path.relative_to(self.tmpdir)), checker.errors))
            for tag, count in checker.tag_counts.items():
                if count != 1:
                    malformed.append((str(path.relative_to(self.tmpdir)), f"<{tag}> appears {count} times"))
        self.assertEqual(malformed, [], f"malformed pages found: {malformed[:20]}")

    def test_exact_active_product_and_collection_counts(self):
        active_products = [p for p in self.products if p.get("actif", True)]
        active_collections = [c for c in self.collections if c.get("actif", True)]
        for lang in LANGS:
            product_dirs = [d for d in (self.tmpdir / lang / "products").iterdir() if d.is_dir()]
            collection_dirs = [d for d in (self.tmpdir / lang / "collections").iterdir() if d.is_dir()]
            self.assertEqual(len(product_dirs), len(active_products))
            self.assertEqual(len(collection_dirs), len(active_collections))


if __name__ == "__main__":
    unittest.main()
