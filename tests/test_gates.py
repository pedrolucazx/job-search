"""Tests for scripts/check_liveness.py and scripts/fact_check.py — no network.

Run with: python3 -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_liveness  # noqa: E402
import fact_check  # noqa: E402


class TestLiveness(unittest.TestCase):
    def verdict(self, status=200, url="https://x/jobs/1", text="<html>job</html>"):
        return check_liveness.classify(status, url, text)[0]

    def test_signals_measured_on_real_sources(self):
        self.assertEqual(self.verdict(url="https://br.linkedin.com/jobs/dev-vagas?trk=expired_jd_redirect"), "closed")
        self.assertEqual(self.verdict(text='{"status":"closed","code":"X-1"}'), "closed")
        self.assertEqual(self.verdict(text='{"status":"published","code":"X-1"}'), "live")
        self.assertEqual(self.verdict(status=404), "closed")
        self.assertEqual(self.verdict(text='{"status":"frozen","code":"X-1"}'), "closed")
        self.assertEqual(self.verdict(text='{"status":"draft","code":"X-1"}'), "uncertain")

    def test_failed_fetch_is_not_live(self):
        for status in (999, 429, 403, 500):
            self.assertEqual(self.verdict(status=status, text=""), "uncertain", status)

    def test_closure_phrases(self):
        for text in ("No longer accepting applications", "Esta vaga não está mais disponível",
                     "Esta vaga foi encerrada", "Não aceita mais candidaturas", "The position has been filled"):
            self.assertEqual(self.verdict(text=text), "closed", text)

    def test_prose_that_is_not_a_closure(self):
        for text in ("once the application form has been filled out", "closed-loop control systems",
                     "Mais de 200 candidaturas", "A vaga preenchida por PCD terá benefícios",
                     "A vaga expirada será removida", "O processo seletivo encerrado anteriormente foi reaberto",
                     "this position is no longer required to be onsite",
                     "<script>var t='Esta vaga foi encerrada'</script><p>Requisitos</p>"):
            self.assertEqual(self.verdict(text=text), "live", text)

    def test_non_http_is_uncertain(self):
        self.assertEqual(check_liveness.check("mailto:a@b.com")[0], "uncertain")


PROFILE = """
skills:
  - name: "React"
    years: 4
  - name: "Next.js"
    years: 2
# Deliver IT exigiu mais de 5 anos de experiência (comentário, não fato)
responsibilities:
  - "Testes Jest (80%+ cobertura); 100% em componente crítico"
  - "equipe de 4 devs; mapeou ~1000 linhas de código morto"
duration_note: "4+ anos"
"""


class TestFactCheck(unittest.TestCase):
    def missing(self, cv):
        return fact_check.unsupported(cv, PROFILE)

    def test_real_facts_pass_in_both_languages(self):
        self.assertEqual(self.missing("4+ years of experience, 80%+ coverage, 100% on a critical "
                                      "component, teams of 4 developers, about 1,000 lines, 2 years Next.js"), [])
        self.assertEqual(self.missing("4+ anos, time de 4 pessoas, cerca de 1000 linhas"), [])

    def test_invented_quantities_fail(self):
        self.assertEqual(self.missing("5 years of experience"), ["5 years"])
        self.assertEqual(self.missing("95% coverage, 12 developers"), ["12 people", "95 %"])

    def test_yaml_comments_are_not_facts(self):
        self.assertIn("5 years", self.missing("5 anos de experiência"))

    def test_decimals_are_whole_numbers(self):
        self.assertEqual(fact_check.quantities("1,5 anos"), {("1.5", "years")})
        self.assertEqual(fact_check.quantities("1.000 linhas"), {("1000", "lines")})
        self.assertEqual(self.missing("3.5 years"), ["3.5 years"])

    def test_bare_numbers_are_ignored(self):
        self.assertEqual(self.missing("React 19, Next.js 15, PostgreSQL 16, Gemini 2.5"), [])


if __name__ == "__main__":
    unittest.main()
