"""Tests for gupy_search.py, jd_years.py and cv_voice.py — no network.

Run with: python3 -m unittest discover -s tests
"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import cv_voice  # noqa: E402
import gupy_search  # noqa: E402
import jd_years  # noqa: E402


def raw(jid, name, workplace="remote", published="2026-11-10", company="Acme", description="<p>Node</p>"):
    return {"id": jid, "name": name, "careerPageName": company, "workplaceType": workplace,
            "publishedDate": published + "T10:00:00.000Z", "description": description,
            "jobUrl": f"https://acme.gupy.io/job/{jid}?jobBoardSource=gupy_portal", "city": "", "state": ""}


class TestGupy(unittest.TestCase):
    def run_search(self, by_term):
        return gupy_search.search(list(by_term), days=14, today=date(2026, 11, 13),
                                  fetch=lambda term: by_term[term])

    def test_keeps_recent_remote_within_ceiling_and_dedups(self):
        out = self.run_search({
            "node": [raw(1, "Desenvolvedor Node Pleno"), raw(2, "Desenvolvedor Node Sênior"),
                     raw(3, "Dev Node", workplace="hybrid"), raw(4, "Dev Node", published="2026-10-01")],
            "react": [raw(1, "Desenvolvedor Node Pleno"), raw(5, "Desenvolvedor PL/SR React")],
        })
        self.assertEqual([r["id"] for r in out["results"]], ["1", "5"])
        self.assertEqual(out["meta"]["scanned"], 5)
        first = out["results"][0]
        self.assertEqual(first["url"], "https://acme.gupy.io/job/1")
        self.assertEqual((first["source"], first["workplaceType"], first["description"]), ("gupy", "remote", "Node"))

    def test_ceiling(self):
        for title in ("Dev Sênior", "Tech Lead", "Especialista Java", "Software Engineer III", "Staff Engineer"):
            self.assertTrue(gupy_search.above_ceiling(title), title)
        for title in ("Dev Pleno", "Dev Pleno/Sênior", "Engineer II", "Dev Júnior", "Desenvolvedor Full Stack"):
            self.assertFalse(gupy_search.above_ceiling(title), title)
        # "PL/SQL", "Middleware", "Midlands" are not levels; "Team Leader" is above.
        for title in ("Desenvolvedor Middleware Sênior", "Desenvolvedor PL/SQL Sênior", "Dev Oracle PL SQL Senior",
                      "Desenvolvedor Sênior | Midlands", "Team Leader"):
            self.assertTrue(gupy_search.above_ceiling(title), title)

    def test_pagination_ignores_the_reported_total(self):
        pages = {0: [raw(i, "Dev") for i in range(100)], 100: [raw(100 + i, "Dev") for i in range(50)]}

        class Resp:
            def __init__(self, data): self.data = data
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return __import__("json").dumps({"data": self.data, "pagination": {"total": 100}}).encode()

        def opener(request, timeout):
            offset = int(dict(__import__("urllib.parse").parse.parse_qsl(request.full_url.split("?")[1]))["offset"])
            return Resp(pages.get(offset, []))
        self.assertEqual(len(gupy_search.fetch_term("dev", opener=opener)), 150)

    def test_one_failing_term_does_not_drop_the_source(self):
        import urllib.error

        def fetch(term):
            if term == "bad":
                raise urllib.error.URLError("dns")
            return [raw(1, "Dev Pleno")]
        out = gupy_search.search(["bad", "good"], days=14, today=date(2026, 11, 13), fetch=fetch)
        self.assertEqual((out["meta"]["count"], out["meta"]["failed_terms"]), (1, ["bad"]))


class TestJdYears(unittest.TestCase):
    def test_reads_requirements(self):
        cases = {
            "Experiência de pelo menos 5 anos com backend.": 5,
            "3+ anos de experiência com React.": 3,
            "5+ years of experience building web apps": 5,
            "Mínimo de quatro anos de atuação em front-end.": 4,
            "2 anos de experiência. Empresa fundada há 15 anos.": 2,
        }
        for text, years in cases.items():
            self.assertEqual(jd_years.required_years(text)[0], years, text)

    def test_years_that_are_not_requirements(self):
        for text in ("Empresa com 20 anos de mercado e um plano de 5 anos.", "Inglês avançado.",
                     "Empresa com 10 anos de experiência no mercado", "Com 10 anos de atuação no Brasil",
                     "Experiência de até 5 anos para a vaga de pleno", "Experiência de 5 anos é um diferencial",
                     "Experiência com AWS; programa de carreira em 5 anos"):
            self.assertIsNone(jd_years.required_years(text)[0], text)

    def test_range_lower_end_in_any_order(self):
        for text in ("Experiência de 3 a 5 anos com backend", "Experiência entre 3 e 5 anos",
                     "Experiência: 3-5 anos", "Experience: 3 to 5 years", "3 a 5 anos de experiência"):
            self.assertEqual(jd_years.required_years(text)[0], 3, text)

    def test_company_age_does_not_beat_the_real_requirement(self):
        text = "Requisitos: 2 anos de experiência. Nossa empresa tem 12 anos de experiência"
        self.assertEqual(jd_years.required_years(text)[0], 2)

    def test_soft_requirement_never_excludes(self):
        v = jd_years.verdict("Experiência de 6 anos é um diferencial. Requisito: 3 anos de experiência.", 4)
        self.assertEqual((v["verdict"], v["required"], v["soft_required"]), ("within", 3, [6]))
        v = jd_years.verdict("Desejável 3 a 5 anos de experiência em Node.js", 2)
        self.assertEqual((v["verdict"], v["soft_required"]), ("unknown", [3]))

    def test_verdict(self):
        self.assertEqual(jd_years.verdict("5+ anos de experiência", 4)["verdict"], "above")
        self.assertEqual(jd_years.verdict("4 anos de experiência", 4)["verdict"], "within")
        self.assertEqual(jd_years.verdict("Inglês", 4)["verdict"], "unknown")


class TestCvVoice(unittest.TestCase):
    def test_first_person_and_no_dash_pass(self):
        self.assertEqual(cv_voice.problems("• Implementei APIs. Migrei a produção. Meu foco é backend."), [])
        self.assertEqual(cv_voice.problems("• Built the API. Migrated production to AWS."), [])

    def test_third_person_and_dash_fail(self):
        found = cv_voice.problems("• Desenvolveu APIs; Implementou testes. Aprova UFC — Russas")
        self.assertEqual(len(found), 3)
        self.assertIn("Implementei", " ".join(found))


if __name__ == "__main__":
    unittest.main()


import inhire_search  # noqa: E402


class TestInhire(unittest.TestCase):
    def page(self, *jobs):
        return {"jobsPage": [{"jobId": jid, "displayName": name, "workplaceType": wp, "status": "published"}
                             for jid, name, wp in jobs]}

    def test_list_filter(self):
        page = self.page(("a", "🚀 | Desenvolvedor Full Stack Pleno", "Remote"),
                         ("b", "Desenvolvedor Pleno", "Hybrid"),
                         ("c", "People Partner | Mid-Level", "Remote"),
                         ("d", "Desenvolvedor Sênior", "Remote"),
                         ("e", "Pessoa Coordenadora de Engenharia de Software", "Remote"))
        self.assertEqual([j["jobId"] for j in inhire_search.candidate_jobs(page)], ["a"])

    def test_search_reads_detail_filters_date_and_isolates_failures(self):
        import urllib.error
        details = {"a": {"jobId": "a", "displayName": "🚀 | Dev Node Pleno", "tenantName": "Acme",
                         "publishedAt": "2026-11-10T10:00:00Z", "description": "<p>Node</p>", "location": "BR"},
                   "b": {"jobId": "b", "displayName": "Dev Java Pleno", "tenantName": "Acme",
                         "publishedAt": "2026-09-01T10:00:00Z", "description": "", "location": "BR"}}

        def get(url, tenant):
            if tenant == "down":
                raise urllib.error.URLError("dns")
            if url.endswith("/pages"):
                return self.page(("a", "Dev Node Pleno", "Remote"), ("b", "Dev Java Pleno", "Remote"))
            return details[url.rsplit("/", 1)[1]]
        out = inhire_search.search(["down", "acme"], days=14, today=date(2026, 11, 13), get=get)
        self.assertEqual(out["meta"]["failed_tenants"], ["down"])
        self.assertEqual(len(out["results"]), 1)
        r = out["results"][0]
        self.assertEqual((r["title"], r["company"], r["url"], r["description"], r["source"]),
                         ("Dev Node Pleno", "Acme", "https://acme.inhire.app/vagas/a/vaga", "Node", "inhire"))

    def test_tenant_list_grows_from_history(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "documents" / "applications" / "x").mkdir(parents=True)
            (root / "daily" / "2026-11-13").mkdir(parents=True)
            tenants = root / "documents" / "inhire_tenants.txt"
            tenants.write_text("radix\n")
            (root / "daily" / "2026-11-13" / "j.json").write_text('{"url": "https://gx2.inhire.app/vagas/1"}')
            (root / "documents" / "applications" / "x" / "metadata.json").write_text(
                '{"url": "https://api.inhire.app/x https://db1.inhire.app/vagas/2"}')
            self.assertEqual(inhire_search.known_tenants(tenants, root), ["db1", "gx2", "radix"])
            self.assertEqual(tenants.read_text().split(), ["db1", "gx2", "radix"])
