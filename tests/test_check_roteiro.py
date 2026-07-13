"""Tests for scripts/check_roteiro.py — stdlib unittest only, zero deps.

Run with: python3 -m unittest discover -s tests
"""
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("check_roteiro", SCRIPTS_DIR / "check_roteiro.py")
check_roteiro = importlib.util.module_from_spec(spec)
sys.modules["check_roteiro"] = check_roteiro
spec.loader.exec_module(check_roteiro)


def make_valid_roteiro(**overrides) -> str:
    text = """# Roteiro de Apresentação — Acme Corp (Backend Pleno)

## 1. Roteiro PT-BR (~75s)

**PRESENTE (~25s)**
"Oi, sou dev backend com foco em Node.js e TypeScript."

**PASSADO (~30s)**
"Trabalhei num projeto de pagamentos com integrações críticas."

**FUTURO (~20s)**
"Quero crescer em arquitetura e continuar minha formação em Ciência da Computação."

## 2. Roteiro EN (~75 seconds)

**PRESENT (~25s)**
"Hi, I'm a backend developer focused on Node.js and TypeScript."

**PAST (~30s)**
"I worked on a payments project with critical integrations."

**FUTURE (~20s)**
"I want to grow in architecture and keep studying Computer Science."

## 3. Pontos-chave para anotar no papel

- Experiência com pagamentos — relevante pro domínio da vaga.
- Testes automatizados — reforça confiabilidade.
- AWS é gap real — ter resposta pronta.

## 4. Perguntas para fazer ao recrutador

- Sobre stack: "Como funciona a infraestrutura cloud do time?"
- Sobre processo: "Como é o dia a dia do time?"
- Sobre senioridade: "O que se espera de alguém pleno aqui?"
- Sobre AWS: "Quanto da rotina depende de AWS na prática?"

## 5. Checklist de preparação

- [ ] Cronometrar a apresentação (deve ficar entre 60–90s)
- [ ] Gravar áudio/vídeo de si mesmo apresentando
- [ ] Se for apresentar em inglês: usar Google Tradutor (modo áudio) para validar pronúncia
- [ ] Usar o app "Interview Warmup" do Google para praticar
- [ ] Anotar em papel os 3 pontos-chave ANTES da entrevista
- [ ] Pesquisar a Acme Corp: site, LinkedIn, Glassdoor, produto principal
- [ ] Revisar fundamentos de AWS
- [ ] Ter o projeto de pagamentos rodando localmente

## 6. Análise crítica de compatibilidade

**Requisitos obrigatórios atendidos**
- Node.js/TypeScript — projeto de pagamentos.

**Diferenciais atendidos**
- Testes automatizados — Jest/Supertest.

**Atende parcialmente**
- AWS — risco baixo. Ação: revisar fundamentos antes da entrevista.

**Não atende**
- Kubernetes — risco médio. Ação: estudar conceitos básicos.

**Veredicto honesto**
Compatibilidade ~75%. Vale a pena seguir.
"""
    for key, value in overrides.items():
        text = text.replace(key, value)
    return text


def make_metadata(**overrides) -> dict:
    metadata = {
        "empresa": "Acme Corp",
        "cargo": "Backend Pleno",
        "gaps": [
            {"skill": "AWS", "status": "partial", "nota": "gap real"},
            {"skill": "Kubernetes", "status": "absent", "nota": "gap real"},
        ],
    }
    metadata.update(overrides)
    return metadata


class TestValidRoteiroPasses(unittest.TestCase):
    def test_valid_roteiro_has_no_errors(self):
        self.assertEqual(check_roteiro.check(make_valid_roteiro(), make_metadata()), [])


class TestMissingSections(unittest.TestCase):
    def test_missing_h1_title_is_an_error(self):
        text = make_valid_roteiro().replace("# Roteiro de Apresentação — Acme Corp (Backend Pleno)", "# Something Else")
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("H1 title" in e for e in errors))

    def test_missing_a_required_section_is_an_error(self):
        text = make_valid_roteiro().replace("## 4. Perguntas para fazer ao recrutador", "## 4. Something Else")
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("## 4. Perguntas" in e for e in errors))

    def test_sections_out_of_order_is_an_error(self):
        # Swap sections 1 and 2 wholesale so "## 2." now appears before "## 1."
        text = make_valid_roteiro()
        text = text.replace("## 1. Roteiro PT-BR", "## X. Roteiro PT-BR TEMP")
        text = text.replace("## 2. Roteiro EN", "## 1. Roteiro PT-BR")
        text = text.replace("## X. Roteiro PT-BR TEMP", "## 2. Roteiro EN")
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("out of order" in e for e in errors))


class TestPlaceholderDetection(unittest.TestCase):
    def test_leftover_placeholder_is_an_error(self):
        text = make_valid_roteiro().replace(
            "Compatibilidade ~75%. Vale a pena seguir.",
            "Compatibilidade ~[X]%. [PARAGRAFO PENDENTE]",
        )
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("placeholder" in e for e in errors))

    def test_real_checkboxes_are_not_flagged_as_placeholders(self):
        # The valid fixture is full of "- [ ]" checkboxes — none should trip
        # the placeholder detector (it must only catch ALL-CAPS brackets).
        errors = check_roteiro.check(make_valid_roteiro(), make_metadata())
        self.assertFalse(any("placeholder" in e for e in errors))


class TestMinimumCounts(unittest.TestCase):
    def test_too_few_recruiter_questions_is_an_error(self):
        text = make_valid_roteiro()
        # Cut the questions section down to 2 items
        start = text.find("## 4. Perguntas")
        end = text.find("## 5. Checklist")
        text = text[:start] + '## 4. Perguntas para fazer ao recrutador\n\n- Sobre X: "Y?"\n- Sobre A: "B?"\n\n' + text[end:]
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("recruiter question" in e for e in errors))

    def test_too_few_checklist_items_is_an_error(self):
        text = make_valid_roteiro()
        start = text.find("## 5. Checklist")
        end = text.find("## 6. Análise crítica")
        text = text[:start] + "## 5. Checklist de preparação\n\n- [ ] Cronometrar a apresentação\n\n" + text[end:]
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("checklist item" in e for e in errors))


class TestSection6Contract(unittest.TestCase):
    def test_missing_subheading_is_an_error(self):
        text = make_valid_roteiro().replace("**Veredicto honesto**", "**Conclusão**")
        errors = check_roteiro.check(text, make_metadata())
        self.assertTrue(any("Veredicto honesto" in e for e in errors))

    def test_gap_not_mentioned_in_section_6_is_an_error(self):
        metadata = make_metadata(gaps=[{"skill": "GraphQL", "status": "absent", "nota": "not covered"}])
        errors = check_roteiro.check(make_valid_roteiro(), metadata)
        self.assertTrue(any("GraphQL" in e for e in errors))

    def test_gap_mentioned_case_insensitively_passes(self):
        # "AWS" appears as "AWS" in the fixture already — confirm case-insensitive match works
        metadata = make_metadata(gaps=[{"skill": "aws", "status": "partial", "nota": "x"}])
        errors = check_roteiro.check(make_valid_roteiro(), metadata)
        self.assertFalse(any("aws" in e.lower() and "not mentioned" in e for e in errors))


class TestRealGeneratedRoteiro(unittest.TestCase):
    """Guards against the actually-generated Dexian roteiro ever regressing."""

    def test_dexian_roteiro_passes_structural_check(self):
        folder = SCRIPTS_DIR.parent / "documents" / "applications" / "dexian_fullstack_developer_react_node_aws"
        roteiro_path = folder / "roteiro.md"
        metadata_path = folder / "metadata.json"
        if not roteiro_path.exists() or not metadata_path.exists():
            self.skipTest("Dexian application folder not present in this checkout")
        import json
        roteiro_text = roteiro_path.read_text(encoding="utf-8")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(check_roteiro.check(roteiro_text, metadata), [])


if __name__ == "__main__":
    unittest.main()
