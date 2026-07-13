---
name: career-command-center
version: 2.0.0
description: >
  Ponteiro fino pro motor genérico de recolocação. Dado do candidato vive em
  profile/candidate.yaml, regras universais em rules/, workflows em
  workflows/. Use esta skill em TODOS os comandos de aplicação.
context: fork
allowed-tools:
  - Bash(bun run .agents/skills/linkedin-search/*)
  - Bash(bun run .agents/skills/freehire-search/*)
  - Bash(python3 scripts/*)
  - WebFetch
  - WebSearch
  - Read
  - Write
  - Edit
  - mcp__claude_ai_Notion__notion-search
  - mcp__claude_ai_Notion__notion-create-pages
  - mcp__claude_ai_Notion__notion-update-page
---

# Career Command Center

Skill central que orquestra a busca de emprego. Não contém dado de candidato
nem regra de comportamento — é só o gatilho pro Claude Code carregar:

1. `profile/candidate.yaml` — dados do candidato ativo
2. `rules/README.md` (e os demais arquivos de `rules/`) — regras universais
3. `workflows/` — passos operacionais de cada comando

Ver `AGENTS.md` na raiz do repo pra descrição completa da arquitetura.
