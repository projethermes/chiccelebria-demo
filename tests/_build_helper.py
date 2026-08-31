"""Shared helper: run the real build.py, unmodified, in an isolated temp copy
of the repo. Used by every test module so no test ever touches the real
working tree, and none of them reimplement build.py's generation logic.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_INPUTS = [
    "build.py",
    "products.json",
    "collections.json",
    "i18n-strings.json",
]
LANGS = ["en", "es", "fr", "it", "de"]


def make_build_copy():
    """Copy only the files build.py needs into a fresh temp directory."""
    tmpdir = Path(tempfile.mkdtemp(prefix="chiccelebria-build-test-"))
    for name in BUILD_INPUTS:
        shutil.copy2(REPO_ROOT / name, tmpdir / name)
    return tmpdir


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
