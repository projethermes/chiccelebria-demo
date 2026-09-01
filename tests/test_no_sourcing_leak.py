"""Non-regression tests for the PUBLIC/PRIVATE split (Option A).

The GitHub repo is public: no internal sourcing data (supplier links,
purchase prices, margins) and no back-office/admin tooling may ever be
tracked in git or show up in anything build.py generates.

Two independent checks:
- the tracked file list (`git ls-files`) never re-adds a known-private
  path, and no tracked text file's *content* contains a forbidden marker;
- the real build.py output (run unmodified in an isolated temp copy) is
  scanned the same way.

Image assets under assets/sourcing/*.jpg are product photos referenced by
the public site, not confidential, and are explicitly exempt — as are
official Etsy listing URLs, which are meant to be public.
"""

import subprocess
import unittest
from pathlib import Path

from _build_helper import REPO_ROOT, make_build_copy, run_build

# Markers of internal sourcing data / admin tooling that must never appear
# in a tracked file's content or in build.py's generated output.
FORBIDDEN_CONTENT_MARKERS = [
    "lien_achat",
    "aliexpress.com",
    "alibaba.com",
    "prix_achat",
    "src_prix",
    "marge_interne",
    "fournisseur",
    "cout_sourcing",
    "note_va",
]

# Paths that must never be tracked in the public repo again.
FORBIDDEN_TRACKED_PATHS = [
    "fiches.json",
    "fiches.html",
    "admin_server.py",
    "ajout_chaussettes_noel.py",
    "ajout_produits_halloween.py",
    "ajout_produits_noel.py",
]
FORBIDDEN_TRACKED_PREFIXES = ["admin/", "sourcing/"]

# Product images under assets/sourcing/ are public content, not leaks —
# some filenames legitimately contain "aliexpress" etc.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico", ".svg"}

# Files whose whole purpose is to document/enforce this split — they are
# expected to *name* the forbidden markers, not leak them as live data.
CONTENT_SCAN_EXEMPT = {".gitignore"}


def _tracked_files():
    result = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _scan_dir_for_markers(root, extra_exempt_names=frozenset()):
    """Return {relative_path: [markers found]} for every non-image file
    under root whose content contains a forbidden marker."""
    hits = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            continue
        if path.name in CONTENT_SCAN_EXEMPT or rel in extra_exempt_names:
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except (UnicodeDecodeError, ValueError):
            continue
        found = [m for m in FORBIDDEN_CONTENT_MARKERS if m in text]
        if found:
            hits[rel] = found
    return hits


class NoPrivateFilesTrackedTest(unittest.TestCase):
    def test_forbidden_paths_are_not_tracked(self):
        tracked = _tracked_files()
        offenders = [
            t for t in tracked
            if t in FORBIDDEN_TRACKED_PATHS
            or any(t.startswith(prefix) for prefix in FORBIDDEN_TRACKED_PREFIXES)
        ]
        self.assertEqual(offenders, [], f"private paths re-appeared in git ls-files: {offenders}")

    def test_no_tracked_file_content_leaks_sourcing_data(self):
        hits = _scan_dir_for_markers(
            REPO_ROOT,
            extra_exempt_names={"tests/test_no_sourcing_leak.py"},
        )
        # Exclude everything under .git/ and __pycache__/ noise picked up by rglob.
        hits = {
            k: v for k, v in hits.items()
            if not k.startswith(".git/") and "__pycache__" not in k
        }
        # Only tracked files matter for the public-repo guarantee.
        tracked = set(_tracked_files())
        hits = {k: v for k, v in hits.items() if k in tracked}
        self.assertEqual(hits, {}, f"forbidden sourcing markers found in tracked files: {hits}")


class BuildOutputHasNoSourcingLeakTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = make_build_copy()
        run_build(cls.tmpdir)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_build_does_not_require_fiches_json(self):
        # fiches.json is intentionally absent from make_build_copy()'s inputs;
        # a successful run_build() above already proves build.py doesn't need it.
        self.assertFalse((self.tmpdir / "fiches.json").exists())

    def test_generated_site_has_no_sourcing_leak(self):
        hits = _scan_dir_for_markers(self.tmpdir)
        self.assertEqual(hits, {}, f"forbidden sourcing markers found in generated output: {hits}")

    def test_generated_site_has_no_admin_or_sourcing_pages(self):
        offenders = [
            str(p.relative_to(self.tmpdir))
            for p in self.tmpdir.rglob("*")
            if p.is_file() and (
                "admin" in p.relative_to(self.tmpdir).parts
                or "sourcing" in p.relative_to(self.tmpdir).parts
                or p.name in ("fiches.html", "fiches.json")
            )
        ]
        self.assertEqual(offenders, [], f"admin/sourcing artifacts found in build output: {offenders}")


if __name__ == "__main__":
    unittest.main()
