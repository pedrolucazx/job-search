"""Tests for scripts/validate_profile.py — stdlib unittest only, zero deps.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("validate_profile", SCRIPTS_DIR / "validate_profile.py")
validate_profile = importlib.util.module_from_spec(spec)
sys.modules["validate_profile"] = validate_profile
spec.loader.exec_module(validate_profile)


def make_valid_profile(**overrides):
    profile = {
        "profile_version": "1.1",
        "personal": {
            "name": "Test Person",
            "email": "test@example.com",
            "phone": "+1 555 0000",
            "location": "Nowhere",
        },
        "education": [],
        "languages": [],
        "skills": {"backend": [{"name": "Node.js", "level": "advanced", "years": 3}]},
        "professional_experience": [{"company": "Acme", "role": "Dev", "period": "2020-2023"}],
        "personal_projects": [],
        "soft_skills": [{"pt": "Comunicação", "en": "Communication"}],
        "preferences": {"deal_breakers": []},
        "tracker": {"backend": "csv", "csv": {"path": "documents/applications.csv"}},
    }
    profile.update(overrides)
    return profile


class TestValidate(unittest.TestCase):
    def test_valid_profile_has_no_errors(self):
        self.assertEqual(validate_profile.validate(make_valid_profile()), [])

    def test_missing_top_level_field(self):
        profile = make_valid_profile()
        del profile["skills"]
        errors = validate_profile.validate(profile)
        self.assertTrue(any("skills" in e for e in errors))

    def test_missing_personal_field(self):
        profile = make_valid_profile()
        profile["personal"] = {"name": "Test", "email": "", "phone": "x", "location": "x"}
        errors = validate_profile.validate(profile)
        self.assertTrue(any("personal.email" in e for e in errors))

    def test_soft_skills_must_be_bilingual(self):
        profile = make_valid_profile(soft_skills=[{"pt": "Comunicação"}])
        errors = validate_profile.validate(profile)
        self.assertTrue(any("soft_skills[0]" in e for e in errors))

    def test_empty_soft_skills_is_an_error(self):
        profile = make_valid_profile(soft_skills=[])
        errors = validate_profile.validate(profile)
        self.assertTrue(any("soft_skills is empty" in e for e in errors))

    def test_no_experience_and_no_projects_is_an_error(self):
        profile = make_valid_profile(professional_experience=[], personal_projects=[])
        errors = validate_profile.validate(profile)
        self.assertTrue(any("professional_experience" in e for e in errors))

    def test_invalid_tracker_backend(self):
        profile = make_valid_profile(tracker={"backend": "airtable"})
        errors = validate_profile.validate(profile)
        self.assertTrue(any("invalid tracker.backend" in e for e in errors))

    def test_notion_backend_requires_ids(self):
        profile = make_valid_profile(tracker={"backend": "notion", "notion": {}})
        errors = validate_profile.validate(profile)
        self.assertTrue(any("database_id" in e for e in errors))

    def test_csv_backend_requires_path(self):
        profile = make_valid_profile(tracker={"backend": "csv", "csv": {}})
        errors = validate_profile.validate(profile)
        self.assertTrue(any("tracker.csv.path" in e for e in errors))

    def test_none_backend_is_valid_without_extra_config(self):
        profile = make_valid_profile(tracker={"backend": "none"})
        self.assertEqual(validate_profile.validate(profile), [])


class TestGetField(unittest.TestCase):
    def test_get_nested_field(self):
        profile = make_valid_profile()
        self.assertEqual(validate_profile.get_field(profile, "personal.email"), "test@example.com")

    def test_get_missing_field_returns_none(self):
        profile = make_valid_profile()
        self.assertIsNone(validate_profile.get_field(profile, "personal.nonexistent"))

    def test_get_missing_top_level_returns_none(self):
        profile = make_valid_profile()
        self.assertIsNone(validate_profile.get_field(profile, "nonexistent.field"))


class TestRealExampleProfile(unittest.TestCase):
    """Guards against the shipped example ever silently breaking the schema."""

    def test_example_profile_is_valid(self):
        example_path = SCRIPTS_DIR.parent / "profile" / "candidate.example.yaml"
        data = validate_profile.load_profile(example_path)
        self.assertEqual(validate_profile.validate(data), [])


if __name__ == "__main__":
    unittest.main()
