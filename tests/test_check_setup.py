"""Tests for scripts/check_setup.py — stdlib unittest only, zero deps.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("check_setup", SCRIPTS_DIR / "check_setup.py")
check_setup = importlib.util.module_from_spec(spec)
sys.modules["check_setup"] = check_setup
spec.loader.exec_module(check_setup)


class TestCheckCommand(unittest.TestCase):
    def test_known_missing_binary_returns_false(self):
        found = check_setup.check_command(
            "nonexistent-tool", "definitely-not-a-real-binary-xyz", "brew install nothing", "test"
        )
        self.assertFalse(found)

    def test_python3_itself_is_found(self):
        found = check_setup.check_command("python3", "python3", "n/a", "test")
        self.assertTrue(found)


class TestCheckPyyaml(unittest.TestCase):
    def test_pyyaml_is_importable_in_this_env(self):
        # If this fails, the whole pipeline is broken anyway (validate_profile.py
        # needs it too) — this is really a sanity check on the dev environment.
        self.assertTrue(check_setup.check_pyyaml())


if __name__ == "__main__":
    unittest.main()
