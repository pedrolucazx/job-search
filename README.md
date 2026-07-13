# 🎯 Job Search — Recolocação Multi-Agente

<p align="center">
  <img src="https://img.shields.io/badge/agent--agnostic-Claude%20%7C%20Codex%20%7C%20OpenCode-1F497D?style=flat-square" alt="Agent-agnostic">
  <img src="https://img.shields.io/badge/CV-LaTeX%201%20p%C3%A1gina%20A4-1F497D?style=flat-square" alt="CV LaTeX 1 página">
  <img src="https://img.shields.io/badge/tracker-Notion%20%7C%20CSV%20%7C%20none-1F497D?style=flat-square" alt="Tracker plugável">
  <img src="https://img.shields.io/badge/license-MIT-1F497D?style=flat-square" alt="MIT license">
</p>

<p align="center"><em>Framework de busca de emprego que roda na sua máquina, com qualquer agente de código.</em></p>

Busca vagas, avalia fit, gera CV em LaTeX (1 página A4, ATS-safe) e acompanha
candidaturas — tudo a partir do **seu** profile em YAML. Nenhum dado de
candidato vive no motor: troque o profile e o mesmo pipeline serve pra
qualquer trilha (backend, frontend, mobile, IoT, dados...) e qualquer agente
de código com acesso a arquivo + shell (Claude Code, Codex, OpenCode, Cursor,
Cline, ou até um chat sem tool-use pro caminho manual).

## Como funciona

```
 /daily              /apply-batch <n>        /compile-today          /confirm <n>
    │                      │                       │                      │
    ▼                      ▼                       ▼                      ▼
 Busca vagas          Gera CV LaTeX           Compila → PDF          Registra no
 (LinkedIn+freehire)  pra vaga escolhida      ATS check, arquiva     tracker (Notion/
 Rankeia por fit      (gate: deal-breaker                            CSV/nenhum)
                       + score ≥60%)
```

Cada passo lê `profile/candidate.yaml` (seus dados) + `rules/` (regras
universais de CV/fit/ATS) — nada hardcoded no motor. Ver [AGENTS.md](AGENTS.md)
pra arquitetura completa.

## Pré-requisitos

- Um agente de código com acesso a arquivo + shell (Claude Code, Codex, OpenCode...)
- Python 3 + PyYAML — `python3 -c "import yaml"` pra checar
- [Bun](https://bun.sh) — pras CLIs de busca de vaga
- LaTeX (`pdflatex`) + `pdftotext` (poppler-utils) — pra compilar e checar ATS

Instalação detalhada: [SETUP.md](SETUP.md).

## Começando

```bash
# 1. Seu profile (nunca invente dado — deixe em branco o que não souber)
cp profile/candidate.example.yaml profile/candidate.yaml
# preencha profile/candidate.yaml com seus dados reais
python3 scripts/validate_profile.py

# 2. CLIs de busca
cd .agents/skills/linkedin-search/cli && bun install && cd ../../../..
cd .agents/skills/freehire-search/cli && bun install && cd ../../../..
```

Depois, dentro do seu agente de código:

```
/daily              → busca vagas, rankeia por fit score
/apply-batch 1,2,3  → gera CV pras vagas escolhidas
/compile-today      → compila, roda ATS check, arquiva
/confirm 1,2,3      → registra candidatura enviada no tracker
```

## Comandos

| Comando | O que faz |
|---|---|
| `/daily` | Scrape LinkedIn + freehire, deduplica, rankeia por fit score |
| `/apply-batch <índices\|url>` | Gera CV `.tex` pras vagas escolhidas — barra deal-breaker e score < 60% antes de gastar esforço |
| `/compile-today` | Compila `.tex` → PDF, roda ATS check, arquiva — **não toca no tracker** |
| `/confirm <índices>` | Único comando que registra "Aplicado" no tracker configurado |

## Arquitetura

| Pasta | Conteúdo |
|---|---|
| `profile/` | Seus dados (`candidate.yaml`, gitignored) — comece por `candidate.example.yaml` |
| `rules/` | Regras universais: CV, fit score, ATS, entrevista — sem dado de ninguém |
| `workflows/` | Passos operacionais de cada comando acima |
| `templates/` | Template LaTeX genérico (placeholders resolvidos pelo profile) |
| `scripts/` | Validação de profile, compilação em lote, tracker CSV |
| `.agents/skills/` | CLIs de busca (LinkedIn, freehire) |

Detalhe completo, incluindo por que cada pasta existe: [AGENTS.md](AGENTS.md).

## Se algo quebrar

| Sintoma | Onde olhar |
|---|---|
| `/daily` não acha vaga nenhuma | LinkedIn pode ter bloqueado — tenta só com freehire, ou cola a URL direto no `/apply-batch` |
| CV saiu com mais de 1 página | `/compile-today` já barra isso sozinho (não registra, não arquiva, aparece no relatório) — corte conteúdo seguindo `rules/cv-rules.md` e rode `/compile-today` de novo |
| `/compile-today` deu erro de compilação | Log do pdflatex aparece no relatório — geralmente é caractere especial não escapado |
| Vaga já apareceu antes | `/daily` filtra pelo tracker **e** pelos arquivos locais (`documents/applications/`, `daily/*/*.json`) pra pegar candidatura em andamento ainda não confirmada |
| Esqueci de rodar `/confirm` | Sem problema — o CV já tá compilado e arquivado localmente, o tracker só fica desatualizado até você rodar `/confirm <número>`, não precisa ser no mesmo dia |

## Outros documentos

- [AGENTS.md](AGENTS.md) — arquitetura completa, agnóstica de agente/LLM
- [SETUP.md](SETUP.md) — instalar dependências
- [OPENCODE.md](OPENCODE.md) — modelos grátis do OpenCode e qual usar em cada tarefa
- [documents/README.md](documents/README.md) — como fica organizada a pasta de candidaturas (local, gitignored)

## Créditos

As CLIs de busca (`.agents/skills/linkedin-search/`, `.agents/skills/freehire-search/`)
foram adaptadas a partir de trechos de [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (não é um fork).
