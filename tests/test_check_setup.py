"""Tests for scripts/check_setup.py — stdlib unittest only, zero deps.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

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


class TestInstallPrompt(unittest.TestCase):
    @patch("builtins.input", return_value="y")
    def test_accepts_short_yes(self, mocked_input):
        self.assertTrue(check_setup.ask_to_install())
        mocked_input.assert_called_once()

    @patch("builtins.input", return_value="yes")
    def test_accepts_yes(self, mocked_input):
        self.assertTrue(check_setup.ask_to_install())
        mocked_input.assert_called_once()

    @patch("builtins.input", return_value="")
    def test_defaults_to_no(self, mocked_input):
        self.assertFalse(check_setup.ask_to_install())
        mocked_input.assert_called_once()

    @patch.object(check_setup.sys.stdin, "isatty", return_value=True)
    def test_offer_is_enabled_in_terminal(self, mocked_isatty):
        self.assertTrue(check_setup.should_offer_install())

    @patch.object(check_setup.sys.stdin, "isatty", return_value=False)
    def test_offer_is_disabled_outside_terminal(self, mocked_isatty):
        self.assertFalse(check_setup.should_offer_install())

    @patch.object(check_setup.sys.stdin, "isatty", return_value=True)
    def test_no_prompt_always_disables_offer(self, mocked_isatty):
        self.assertFalse(check_setup.should_offer_install(no_prompt=True))


class TestInstallerRunner(unittest.TestCase):
    @patch.object(check_setup.subprocess, "run")
    def test_runs_the_repository_installer(self, mocked_run):
        mocked_run.return_value = MagicMock(returncode=0)

        self.assertTrue(check_setup.run_installer())
        mocked_run.assert_called_once_with(
            [str(check_setup.INSTALL_SCRIPT)],
            cwd=check_setup.REPO_ROOT,
            check=False,
        )


class TestMain(unittest.TestCase):
    @patch.object(check_setup, "check_profile", return_value=True)
    @patch.object(check_setup, "check_dependencies", return_value=[True, True])
    def test_complete_environment_does_not_offer_install(self, mocked_checks, mocked_profile):
        with patch.object(check_setup, "ask_to_install") as mocked_prompt:
            self.assertEqual(check_setup.main([]), 0)
            mocked_prompt.assert_not_called()

    @patch.object(check_setup, "should_offer_install", return_value=False)
    @patch.object(check_setup, "check_profile", return_value=True)
    @patch.object(check_setup, "check_dependencies", return_value=[True, False])
    def test_noninteractive_missing_environment_reports_failure(
        self, mocked_checks, mocked_profile, mocked_offer
    ):
        with patch.object(check_setup, "run_installer") as mocked_installer:
            self.assertEqual(check_setup.main([]), 1)
            mocked_installer.assert_not_called()

    @patch.object(check_setup, "run_installer", return_value=True)
    @patch.object(check_setup, "check_profile", return_value=True)
    @patch.object(
        check_setup,
        "check_dependencies",
        side_effect=[[True, False], [True, True]],
    )
    def test_install_flag_installs_and_rechecks(
        self, mocked_checks, mocked_profile, mocked_installer
    ):
        self.assertEqual(check_setup.main(["--install"]), 0)
        mocked_installer.assert_called_once()
        self.assertEqual(mocked_checks.call_count, 2)


if __name__ == "__main__":
    unittest.main()
