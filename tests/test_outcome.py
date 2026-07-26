"""Tests for scripts/outcome.py — stdlib unittest only, zero deps.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("outcome", SCRIPTS_DIR / "outcome.py")
outcome = importlib.util.module_from_spec(spec)
sys.modules["outcome"] = outcome
spec.loader.exec_module(outcome)

RECORD = {
    "empresa": "Acme Corp",
    "cargo": "Backend Engineer (Remote)",
    "url": "https://jobs.example.com/acme/backend-engineer?utm_source=example",
    "data": "2026-07-24",
}

EXPECTED_DEFAULT = """# Outcome: Acme Corp — Backend Engineer (Remote)

**URL:** https://jobs.example.com/acme/backend-engineer?utm_source=example — submit the CV manually here
**Status:** waiting for send confirmation (run workflows/confirm.md)
**Compilation date:** 2026-07-24
**Resolution date:** —

## Interview stages reached
- [ ] Phone screen
- [ ] Technical interview
- [ ] System design
- [ ] Final round
- [ ] Offer received

## Notes
"""

COMPILED_FIXTURE = """# Outcome: Acme Corp — AI Engineer II (Remote)

**URL:** https://job-boards.example.com/acme/jobs/7633986003?utm_source=example — submit the CV manually here
**Status:** waiting for send confirmation (run workflows/confirm.md)
**Compilation date:** 2026-07-24
**Resolution date:** —

## Interview stages reached
- [ ] Phone screen
- [ ] Technical interview
- [ ] System design
- [ ] Final round
- [ ] Offer received

## Notes
"""

APPLIED_FIXTURE = """# Outcome: Globex — Desenvolvedor Backend Node.js Pleno/Sênior

**URL:** https://www.example.com/jobs/view/4444371841 — submit the CV manually here
**Status:** Applied
**Compilation date:** 2026-07-24
**Resolution date:** 2026-07-24

## Interview stages reached
- [ ] Phone screen
- [ ] Technical interview
- [ ] System design
- [ ] Final round
- [ ] Offer received

## Notes
"""

NO_CV_FIXTURE = """# Outcome: Initech — Staff Platform Engineer

**URL:** https://jobs.example.com/initech/staff-platform
**Status:** Applied (no CV — applied via existing platform profile)
**Application date:** 2026-07-25
**Resolution date:** —

## Interview stages reached
- [x] Phone screen
- [ ] Technical interview
- [ ] System design
- [ ] Final round
- [ ] Offer received

## Notes
"""


class TestRender(unittest.TestCase):
    def test_default_output_matches_compile_all_heredoc(self):
        self.assertEqual(outcome.render(RECORD), EXPECTED_DEFAULT)

    def test_stages_done_marks_only_those_checkboxes(self):
        text = outcome.render(RECORD, stages_done=["Technical interview"])
        self.assertIn("- [ ] Phone screen", text)
        self.assertIn("- [x] Technical interview", text)
        self.assertIn("- [ ] System design", text)

    def test_notes_are_appended_under_the_trailer(self):
        text = outcome.render(RECORD, notes="Recruiter asked about Kafka.")
        self.assertTrue(text.endswith("## Notes\nRecruiter asked about Kafka.\n"))


class TestRoundTrip(unittest.TestCase):
    def test_parse_reads_back_what_render_wrote(self):
        status = "Interviewing (2nd round scheduled)"
        stages_done = ["Phone screen", "Technical interview", "Final round"]
        resolution = "2026-08-03"
        parsed = outcome.parse(outcome.render(
            RECORD, status=status, stages_done=stages_done, resolution=resolution))
        self.assertEqual(parsed["status"], status)
        self.assertEqual(parsed["stages_done"], stages_done)
        self.assertEqual(parsed["furthest"], "Final round")
        self.assertEqual(parsed["resolution"], resolution)


class TestParse(unittest.TestCase):
    def test_freshly_compiled_outcome(self):
        parsed = outcome.parse(COMPILED_FIXTURE)
        self.assertEqual(parsed["status"], "waiting for send confirmation (run workflows/confirm.md)")
        self.assertIsNone(parsed["furthest"])
        self.assertEqual(parsed["resolution"], "")
        self.assertEqual(parsed["stages_done"], [])

    def test_applied_outcome(self):
        parsed = outcome.parse(APPLIED_FIXTURE)
        self.assertEqual(parsed["status"], "Applied")
        self.assertIsNone(parsed["furthest"])
        self.assertEqual(parsed["resolution"], "2026-07-24")

    def test_application_date_variant_does_not_break(self):
        parsed = outcome.parse(NO_CV_FIXTURE)
        self.assertEqual(parsed["status"], "Applied (no CV — applied via existing platform profile)")
        self.assertEqual(parsed["furthest"], "Phone screen")
        self.assertEqual(parsed["resolution"], "")

    def test_furthest_is_the_last_checked_stage_not_the_first(self):
        text = outcome.render(RECORD, stages_done=["Phone screen", "System design"])
        self.assertEqual(outcome.parse(text)["furthest"], "System design")

    def test_furthest_is_none_when_nothing_is_checked(self):
        self.assertIsNone(outcome.parse(outcome.render(RECORD))["furthest"])

    def test_furthest_follows_stages_order_not_file_order(self):
        shuffled = "\n".join([
            "**Status:** Interviewing",
            "**Resolution date:** —",
            "- [x] Final round",
            "- [x] Phone screen",
        ])
        self.assertEqual(outcome.parse(shuffled)["furthest"], "Final round")


class TestWriteCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name) / "acme_backend_engineer_remote"
        self.folder.mkdir()
        (self.folder / "metadata.json").write_text(json.dumps(RECORD), encoding="utf-8")
        self.target = self.folder / "outcome.md"
        self.addCleanup(self.tmp.cleanup)

    def test_writes_when_there_is_no_outcome_yet(self):
        self.assertEqual(outcome.main(["--write", str(self.folder)]), 0)
        self.assertEqual(self.target.read_text(encoding="utf-8"), EXPECTED_DEFAULT)

    def test_refuses_to_overwrite_without_force(self):
        manual = outcome.render(RECORD, status="Applied", stages_done=["Phone screen"])
        self.target.write_text(manual, encoding="utf-8")
        self.assertEqual(outcome.main(["--write", str(self.folder)]), 1)
        self.assertEqual(self.target.read_text(encoding="utf-8"), manual)

    def test_force_overwrites(self):
        self.target.write_text(outcome.render(RECORD, status="Applied"), encoding="utf-8")
        self.assertEqual(outcome.main(["--write", str(self.folder), "--force"]), 0)
        self.assertEqual(self.target.read_text(encoding="utf-8"), EXPECTED_DEFAULT)

    def test_missing_metadata_exits_nonzero(self):
        (self.folder / "metadata.json").unlink()
        self.assertEqual(outcome.main(["--write", str(self.folder)]), 1)


if __name__ == "__main__":
    unittest.main()
