# Job Search Agent

Sou um assistente de busca de emprego: leio dados estruturados de um
candidato e gero CVs em LaTeX (1 página A4, ATS-safe), avalio fit de vagas e
registro candidaturas confirmadas num tracker.

Funciono com qualquer agente de código (Claude Code, Codex, Copilot CLI,
Cursor, Cline, OpenCode, ou um chat sem tool-use pro caminho manual) — desde
que tenha acesso a arquivo + shell pra automação completa. Nada aqui depende
de formato proprietário de nenhuma ferramenta.

## Por onde começar

1. **`rules/README.md`** — regras absolutas e índice das regras (universal,
   sem dado de candidato).
2. **`profile/candidate.yaml`** — dados do candidato ativo. Se não existir,
   copie `profile/candidate.example.yaml` e preencha (nunca invente dado).
   Valide com:
   ```bash
   python3 scripts/validate_profile.py
   ```
3. **`rules/`** — regras de CV, avaliação de fit, verificação ATS, preparação
   de entrevista. Genérico pra qualquer trilha (web, mobile, IoT, dados...).
4. **`workflows/`** — passos operacionais:
   - `workflows/daily.md` — buscar vagas, ranquear por fit
   - `workflows/apply-batch.md` — gerar CVs pras vagas escolhidas
   - `workflows/compile.md` — compilar LaTeX → PDF, ATS check, arquivar
   - `workflows/confirm.md` — registrar candidatura confirmada no tracker
     (Notion, CSV, ou nenhum — configurável em `profile/candidate.yaml → tracker`)
5. **`templates/cv_template.tex`** — template LaTeX base.
6. **`scripts/`** — automação (`validate_profile.py`, `compile-all.sh`,
   `track_append.py`).

## Convenções do repositório

- `profile/` só contém abstração do candidato (dado), nunca regra/comportamento.
- `rules/` e `workflows/` só contêm regra universal, nunca dado de pessoa.
- `.claude/commands/`, `.claude/skills/`, `.opencode/commands/` são
  adaptadores finos — cada um só aponta pro conteúdo real em `workflows/` +
  `rules/` + `profile/`, adaptando à convenção de descoberta de cada agente.
- Requisito mínimo pra automação completa: agente com acesso a arquivo +
  shell (Python 3, Bun, pdflatex, poppler-utils). Ver `SETUP.md`.

## Se o seu agente não tem slash command

Não tem problema. Peça diretamente: "leia `AGENTS.md`, depois
`workflows/daily.md`, e execute os passos usando `profile/candidate.yaml`".
