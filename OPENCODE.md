# OpenCode — Sequência do Dia e Modelos Grátis

Guia de uso do OpenCode (IA grátis, via OpenCode Zen) como segundo ator do pipeline.
Objetivo: Claude Code (pago) faz o trabalho que exige julgamento fino; OpenCode (grátis)
faz o trabalho mecânico. Poupa token do Claude Code Pro mesmo com RTK.

---

## 1. Sequência completa do dia

### Passo 1 — Claude Code (`claude` na raiz do repo)

```
/daily
```
Scrape (LinkedIn + freehire) → dedup no Notion → gap score → tabela rankeada.
Você escolhe os números.

```
/apply-batch 1,2,3,8
```
Gera `documents/cv/main_<empresa>.tex` + `daily/<data>/<empresa>.json` pra cada vaga escolhida.
Aceita índice da tabela ou URL colada direto (vaga achada fora do `/daily`).

Sair do Claude Code (`exit` / Ctrl+D) quando os `.tex` estiverem prontos.

### Passo 2 — OpenCode (`opencode` na raiz do repo)

```
/compile-today
```
Lê `daily/<data>/*.json` → `pdflatex` cada `.tex` (via `scripts/compile-all.sh`) →
ATS check → registra no Notion via MCP → arquiva em `documents/applications/`.

Implementado em `.opencode/commands/compile-today.md`, já com `north-mini-code-free`
fixado no frontmatter — não precisa escolher modelo na mão.

> ⚠️ **Pendência de setup**: `pdflatex` não está instalado neste ambiente
> (`sudo apt install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended`,
> ver `SETUP.md`). Sem isso o Passo 1 do `/compile-today` não roda. Ainda não testei
> a compilação ponta a ponta — só validei que a leitura do `cv_tex` do JSON está
> correta.

---

## 2. Modelos grátis disponíveis (OpenCode Zen)

| Modelo | O que se sabe |
|---|---|
| `opencode/big-pickle` | Modelo "stealth" (nome código, provedor não revela qual é). Sem sinal de tamanho/velocidade no nome. |
| `opencode/deepseek-v4-flash-free` | Linha DeepSeek, variante "flash" (otimizada pra velocidade/custo). **Seu padrão atual no OpenCode.** |
| `opencode/mimo-v2.5-free` | Linha MiMo (Xiaomi) — historicamente essa linha foca em raciocínio/matemática relativo ao tamanho. |
| `opencode/north-mini-code-free` | "mini" + "code" no nome — sinaliza modelo pequeno/rápido tunado pra código e tool-calling. Contexto de 256K segundo agregadores de terceiros. |

⚠️ **Isso é heurística de nome, não benchmark**: a documentação oficial do OpenCode Zen
não publica comparação de capacidade entre esses 4 — só confirma que são grátis por
tempo limitado (dados de uso podem ser retidos pra melhorar o modelo, evite colar
informação sensível). Ajuste a tabela abaixo conforme observar na prática.

---

## 3. Qual modelo usar em qual tarefa

| Tarefa (dentro de `/compile-today`) | Modelo sugerido | Por quê |
|---|---|---|
| Rodar `pdflatex`, `pdftotext`, parsear JSON, chamar Notion MCP | `north-mini-code-free` | Tool-calling/bash mecânico, pouco julgamento — o "code" no nome é o sinal mais forte que temos. |
| Interpretar erro de compilação LaTeX (overfull hbox, pacote faltando) e propor fix | `mimo-v2.5-free` | Precisa de raciocínio real sobre a causa do erro, não só seguir passo a passo. |
| Relatório final do dia / `/status` | `deepseek-v4-flash-free` | Seu padrão atual — resumir texto é tarefa leve, não precisa trocar. |
| Fallback — se os três acima travarem ou derem resposta ruim numa vaga difícil | `big-pickle` | Reserva sem sinal claro no nome; grátis, então custa zero testar antes de recorrer ao Claude. |

Trocar de modelo no meio da sessão do OpenCode: `/models` na TUI, ou fixar por
comando (Seção 4).

---

## 4. Fixando o modelo por comando (evita escolher manualmente toda vez)

Comandos custom do OpenCode ficam em `.opencode/commands/*.md`, igual ao
`.claude/commands/`. O frontmatter aceita `model:`:

```markdown
---
description: Compila os CVs do dia, roda ATS check e registra no Notion
agent: build
model: opencode/north-mini-code-free
---

Leia daily/<data>/*.json e para cada um: compile o .tex com pdflatex,
rode pdftotext -layout pro ATS check, e registre a candidatura no Notion via MCP.
```

Assim `/compile-today` sempre abre com `north-mini-code-free` sem você precisar
selecionar na hora. Comandos menores (`/ats-check`, `/register-notion`,
`/status`, `/compile-last`) ficam pra quando forem realmente usados — mesmo
raciocínio do `/interview`: não construir antes de precisar.
