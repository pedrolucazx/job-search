"""Tests for scripts/application_id.py — stdlib unittest only, zero deps.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("application_id", SCRIPTS_DIR / "application_id.py")
application_id = importlib.util.module_from_spec(spec)
sys.modules["application_id"] = application_id
spec.loader.exec_module(application_id)


class TestSlug(unittest.TestCase):
    def test_company_and_role(self):
        self.assertEqual(
            application_id.slug("Acme Health", "AI Engineer II (Remote)"),
            "acme_health_ai_engineer_ii_remote",
        )

    def test_matches_the_shell_slugify_it_replaced(self):
        cases = [
            (("Acme & Co", "Senior Full-Stack Engineer with Node.js 1234 B"),
             "acme_co_senior_full_stack_engineer_with_node_js_1234_b"),
            (("Globex", "Senior Fullstack Developer (NodeJS/React) - Brazil"),
             "globex_senior_fullstack_developer_nodejs_react_brazil"),
            (("Initech", "Senior Software Engineer"),
             "initech_senior_software_engineer"),
        ]
        for parts, expected in cases:
            with self.subTest(parts=parts):
                self.assertEqual(application_id.slug(*parts), expected)

    def test_strips_accents(self):
        self.assertEqual(
            application_id.slug("Ação Digital", "Desenvolvedor Backend Sênior"),
            "acao_digital_desenvolvedor_backend_senior",
        )

    def test_single_part(self):
        self.assertEqual(application_id.slug("Initech"), "initech")

    def test_empty_role_leaves_no_trailing_separator(self):
        self.assertEqual(application_id.slug("Initech", ""), "initech")
        self.assertEqual(application_id.slug("Initech", "   "), "initech")

    def test_collapses_runs_of_punctuation(self):
        self.assertEqual(
            application_id.slug("Foo // Bar", "--Dev--"),
            "foo_bar_dev",
        )

    def test_all_punctuation_is_dropped(self):
        self.assertEqual(application_id.slug("///", "***"), "")


class TestFilename(unittest.TestCase):
    def test_keeps_capitalisation(self):
        self.assertEqual(
            application_id.filename("Ana Souza"),
            "Ana_Souza",
        )

    def test_strips_accents_and_punctuation(self):
        self.assertEqual(
            application_id.filename("José da Silva-Júnior"),
            "Jose_da_Silva_Junior",
        )

    def test_no_leading_or_trailing_separator(self):
        self.assertEqual(application_id.filename("  Ana  "), "Ana")


class TestFind(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def _folder(self, name, empresa=None, cargo=None):
        folder = self.base / name
        folder.mkdir(parents=True)
        if empresa is not None:
            (folder / "metadata.json").write_text(
                json.dumps({"empresa": empresa, "cargo": cargo}), encoding="utf-8"
            )
        return folder

    def test_exact_slug_match(self):
        expected = self._folder("acme_health_ai_engineer_ii_remote")
        found = application_id.find("Acme Health", "AI Engineer II (Remote)", self.base)
        self.assertEqual(found, expected)

    def test_falls_back_to_metadata_when_folder_name_diverges(self):
        expected = self._folder(
            "acme_health_ai_engineer_ii", empresa="Acme Health", cargo="AI Engineer II (Remote)"
        )
        found = application_id.find("Acme Health", "AI Engineer II (Remote)", self.base)
        self.assertEqual(found, expected)

    def test_metadata_match_ignores_case_and_padding(self):
        expected = self._folder("whatever", empresa="Acme Health", cargo="AI Engineer II (Remote)")
        found = application_id.find("  acme health ", "ai engineer ii (remote)", self.base)
        self.assertEqual(found, expected)

    def test_returns_none_when_nothing_matches(self):
        self._folder("other_company_other_role", empresa="Other", cargo="Other Role")
        self.assertIsNone(application_id.find("Acme Health", "AI Engineer II", self.base))

    def test_does_not_match_company_alone(self):
        self._folder("acme_health_data_engineer", empresa="Acme Health", cargo="Data Engineer")
        self.assertIsNone(application_id.find("Acme Health", "AI Engineer II", self.base))

    def test_survives_broken_metadata(self):
        broken = self.base / "broken"
        broken.mkdir()
        (broken / "metadata.json").write_text("{not json", encoding="utf-8")
        expected = self._folder("good", empresa="Acme Health", cargo="AI Engineer II")
        self.assertEqual(application_id.find("Acme Health", "AI Engineer II", self.base), expected)


class TestCLI(unittest.TestCase):
    def test_slug_mode(self):
        self.assertEqual(application_id.main(["Acme Health", "AI Engineer II (Remote)"]), 0)

    def test_filename_mode(self):
        self.assertEqual(application_id.main(["--filename", "Ana Souza"]), 0)

    def test_find_requires_two_arguments(self):
        with self.assertRaises(SystemExit):
            application_id.main(["--find", "Acme Health"])

    def test_find_missing_folder_exits_nonzero(self):
        self.assertEqual(application_id.main(["--find", "Nope Ltd", "Nope Role"]), 1)


if __name__ == "__main__":
    unittest.main()
