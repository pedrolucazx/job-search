"""Tests for scripts/followup.py — stdlib unittest, no network.

Run with: python3 -m unittest discover -s tests
"""
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import followup  # noqa: E402

TODAY = date(2026, 11, 13)


def row(empresa, status, data, link="", feedback="", cargo="Dev"):
    return {"id": empresa, "empresa": empresa, "cargo": cargo, "status": status,
            "data": data, "link": link, "feedback": feedback, "fonte": "", "gaps": []}


class TestPlan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.apps = Path(self.tmp.name)
        folder = self.apps / "local_dev"
        folder.mkdir()
        (folder / "metadata.json").write_text(json.dumps({"empresa": "Local", "cargo": "Dev"}))
        (folder / "email.txt").write_text("Para: rh@local.com.br\nAssunto: x\n")

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self, rows):
        return followup.plan(rows, TODAY, applications_dir=self.apps)

    def test_followup_needs_a_channel_and_a_week(self):
        due, cold = self.plan([
            row("Mail", "Aplicado", "2026-11-05", link="mailto:a@b.com"),     # 8d, mailto
            row("Local", "Aplicado", "2026-11-01"),                            # 12d, email.txt
            row("Feed", "Aplicado", "2026-11-03", feedback="enviado p/ x@y.io"),
            row("Ats", "Aplicado", "2026-11-01"),                              # no channel
            row("Fresh", "Aplicado", "2026-11-10", link="mailto:c@d.com"),    # 3d, too early
        ])
        self.assertEqual([(r["empresa"], r["email"]) for r in due],
                         [("Local", "rh@local.com.br"), ("Feed", "x@y.io"), ("Mail", "a@b.com")])
        self.assertEqual(cold, [])

    def test_cold_after_threshold_regardless_of_channel(self):
        due, cold = self.plan([row("Old", "Aplicado", "2026-09-01"),
                               row("OldMail", "Aplicado", "2026-10-01", link="mailto:a@b.com")])
        self.assertEqual(due, [])
        self.assertEqual([r["empresa"] for r in cold], ["Old", "OldMail"])

    def test_only_applied_rows(self):
        due, cold = self.plan([row("R", "Rejeitado", "2026-09-01"), row("S", "Sumiu", "2026-08-01"),
                               row("E", "Entrevista cultural", "2026-10-01", link="mailto:a@b.com"),
                               row("N", "Aplicado", "")])
        self.assertEqual((due, cold), ([], []))

    def test_stage_ticked_locally_is_not_cold(self):
        folder = self.apps / "staged_dev"
        folder.mkdir()
        (folder / "metadata.json").write_text(json.dumps({"empresa": "Staged", "cargo": "Dev"}))
        (folder / "outcome.md").write_text("**Status:** Applied\n- [x] Phone screen\n")
        _, cold = self.plan([row("Staged", "Aplicado", "2026-08-01")])
        self.assertEqual(cold, [])

    def test_noreply_is_not_a_contact(self):
        due, _ = self.plan([row("Bot", "Aplicado", "2026-11-01", feedback="no-reply@gupy.com.br")])
        self.assertEqual(due, [])

    def test_bad_date_is_skipped(self):
        self.assertEqual(self.plan([row("X", "Aplicado", "13/11/2026")]), ([], []))

    def test_cold_days_is_configurable(self):
        _, cold = followup.plan([row("Mid", "Aplicado", "2026-10-01")], TODAY, cold_days=60,
                                applications_dir=self.apps)
        self.assertEqual(cold, [])


if __name__ == "__main__":
    unittest.main()
