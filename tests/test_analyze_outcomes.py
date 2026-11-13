"""Tests for scripts/analyze_outcomes.py — stdlib unittest, no network.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
spec = importlib.util.spec_from_file_location("analyze_outcomes", SCRIPTS_DIR / "analyze_outcomes.py")
ao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ao)


def row(empresa, status, fonte="LinkedIn", feedback="", gaps=(), data="2026-10-01", cargo="Dev"):
    return {"empresa": empresa, "cargo": cargo, "status": status, "fonte": fonte,
            "data": data, "feedback": feedback, "gaps": list(gaps)}


class TestAnalyze(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.apps = Path(self.tmp.name)
        # Local record: score 85, and a technical stage ticked despite the rejection.
        folder = self.apps / "acme_dev"
        folder.mkdir()
        (folder / "metadata.json").write_text(json.dumps({"empresa": "Acme", "cargo": "Dev", "score": 85}))
        (folder / "outcome.md").write_text("**Status:** Rejected\n- [x] Technical interview\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_rows(self, rows):
        return ao.analyze(rows, applications_dir=self.apps, today=date(2026, 11, 13))

    def test_funnel_and_bands(self):
        f = self.run_rows([
            row("Acme", "Rejeitado", gaps=["AWS"]),                      # local score 85, advanced via stage
            row("Beta", "Aplicado", feedback="Score real 72% (5 full)"),  # score from feedback
            row("Gama", "Entrevista cultural", fonte="Gupy", feedback="Score: 65%"),
            row("Delta", "Sumiu", gaps=["AWS", "Kafka"]),                 # no score
        ])
        self.assertEqual(f["total"]["sent"], 4)
        self.assertAlmostEqual(f["total"]["response_rate"], 0.5)  # Acme rejected + Gama screening
        self.assertAlmostEqual(f["total"]["advance_rate"], 0.5)   # Acme (stage) + Gama
        bands = {b["group"]: b for b in f["by_score"]}
        self.assertEqual(bands["80+"]["advanced"], 1)
        self.assertEqual(bands["70-79"]["responded"], 0)
        self.assertEqual(bands["60-69"]["sent"], 1)
        self.assertEqual(bands["sem score"]["sent"], 1)
        self.assertNotIn("<60", bands)  # empty bands are dropped
        self.assertEqual([b["group"] for b in f["by_score"]], ["80+", "70-79", "60-69", "sem score"])
        self.assertEqual(f["by_state"], {"rejected": 1, "applied": 1, "screening": 1, "ghosted": 1})
        aws = next(g for g in f["gaps"] if g["gap"] == "AWS")
        self.assertEqual((aws["sent"], aws["rejected"], aws["advanced"]), (2, 1, 1))
        self.assertEqual(f["no_score"], 1)
        self.assertEqual(f["score_from_feedback"], 2)

    def test_candidate_decisions_are_not_answers(self):
        f = self.run_rows([row("A", "Desisti"), row("B", "Congelado"), row("C", "Referência para colega")])
        self.assertEqual(f["total"]["sent"], 1)          # withdrew is not "sent"
        self.assertEqual(f["total"]["response_rate"], 0)  # frozen is not an answer

    def test_unknown_status_is_reported_not_counted(self):
        f = self.run_rows([row("A", ""), row("B", "Aplicado")])
        self.assertEqual(f["total"]["sent"], 1)
        self.assertEqual(f["unknown_status"], [""])
        self.assertIn("ATENÇÃO", ao.report(f))

    def test_ats_score_is_not_fit_score(self):
        f = self.run_rows([row("A", "Aplicado", feedback="ATS score 95% no PDF")])
        self.assertEqual(f["by_score"][0]["group"], "sem score")
        f = self.run_rows([row("B", "Aplicado", feedback="Fit 90% (6 full)")])
        self.assertEqual(f["by_score"][0]["group"], "80+")

    def test_reapplication_does_not_inherit_stages(self):
        f = self.run_rows([row("Acme", "Aplicado"), row("Acme", "Rejeitado")])
        self.assertEqual(f["total"]["advanced"], 1)
        self.assertEqual(f["shared_local_record"], 2)

    def test_simplify_rejects_missing_properties(self):
        with self.assertRaises(KeyError):
            ao.simplify({"properties": {"Empresa": {"type": "title", "title": []}}})

    def test_network_error_exits_cleanly(self):
        import urllib.error
        from unittest import mock
        with mock.patch.object(ao, "load_token", return_value="t"), \
             mock.patch.object(ao, "data_source_id", return_value="ds"), \
             mock.patch.object(ao, "fetch_pages", side_effect=urllib.error.URLError("dns")):
            self.assertEqual(ao.main(["--out", str(self.apps / "f.json")]), 1)

    def test_by_source(self):
        f = self.run_rows([row("A", "Aplicado"), row("B", "Rejeitado"), row("C", "Aplicado", fonte="Gupy")])
        src = {s["group"]: s for s in f["by_source"]}
        self.assertEqual(src["LinkedIn"]["sent"], 2)
        self.assertAlmostEqual(src["LinkedIn"]["response_rate"], 0.5)
        self.assertEqual(src["Gupy"]["responded"], 0)

    def test_empty(self):
        f = self.run_rows([])
        self.assertEqual(f["total"]["sent"], 0)
        self.assertIn("0 enviadas", ao.report(f))

    def test_simplify_notion_page(self):
        page = {"properties": {
            "Empresa": {"type": "title", "title": [{"plain_text": "Kraken"}]},
            "Cargo": {"type": "rich_text", "rich_text": [{"plain_text": "SE "}, {"plain_text": "II"}]},
            "Status": {"type": "select", "select": {"name": "Aplicado"}},
            "Fonte": {"type": "select", "select": None},
            "Data": {"type": "date", "date": {"start": "2026-11-13"}},
            "Gaps identificados": {"type": "multi_select", "multi_select": [{"name": "AWS"}]},
        }}
        self.assertEqual(ao.simplify(page), {
            "id": "", "link": "", "empresa": "Kraken", "cargo": "SE II", "status": "Aplicado", "fonte": "",
            "data": "2026-11-13", "feedback": "", "gaps": ["AWS"]})

    def test_main_from_json_writes_funnel(self):
        src = self.apps / "rows.json"
        out = self.apps / "funnel.json"
        src.write_text(json.dumps([row("Zeta", "Aplicado")]))
        self.assertEqual(ao.main(["--from-json", str(src), "--out", str(out)]), 0)
        self.assertEqual(json.loads(out.read_text())["total"]["sent"], 1)


if __name__ == "__main__":
    unittest.main()
