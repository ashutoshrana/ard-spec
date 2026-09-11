"""Exercise the CLI boundary, including runs where site-packages are disabled."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin/conformance-test"
MANIFEST = ROOT / "examples/ai-catalog.json"


class ConformanceResults(unittest.TestCase):
    def run_cli(self, path, *flags, isolated=False):
        return subprocess.run(
            [sys.executable, *(["-S"] if isolated else []), str(CLI), "manifest", str(path), *flags],
            capture_output=True, text=True, check=False,
        )

    def test_strict_missing_dependency_is_incomplete(self):
        result = self.run_cli(MANIFEST, isolated=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("INCOMPLETE", result.stdout)
        self.assertNotIn("STATUS: PASS", result.stdout)

    def test_explicit_basic_mode_is_labeled(self):
        result = self.run_cli(MANIFEST, "--basic", isolated=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("BASIC CHECKS PASSED", result.stdout)

    def test_strict_valid_manifest(self):
        result = self.run_cli(MANIFEST)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS (implemented checks only)", result.stdout)

    def test_malformed_manifests_fail_without_traceback(self):
        valid = json.loads(MANIFEST.read_text())
        invalid_entries = [None, 1, "entry", {"identifier": 7}]
        cases = ["{", "null", "[]", json.dumps({"entries": invalid_entries})]
        entry = dict(valid["entries"][0], data={"unexpected": True}, url="https://example.invalid")
        cases.append(json.dumps(dict(valid, entries=[entry])))
        for content in cases:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "bad.json"
                path.write_text(content)
                for flags in [(), ("--basic",)]:
                    result = self.run_cli(path, *flags)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
