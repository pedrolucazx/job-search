# 🎯 Job Search — Leia Isso Toda Manhã

<p align="center">
  <img src="https://img.shields.io/badge/agent--agnostic-Claude%20%7C%20Codex%20%7C%20OpenCode-1F497D?style=flat-square" alt="Agent-agnostic">
  <img src="https://img.shields.io/badge/CV-LaTeX%201%20p%C3%A1gina%20A4-1F497D?style=flat-square" alt="CV LaTeX 1 página">
  <img src="https://img.shields.io/badge/tracker-Notion%20%7C%20CSV%20%7C%20none-1F497D?style=flat-square" alt="Tracker plugável">
  <img src="https://img.shields.io/badge/license-MIT-1F497D?style=flat-square" alt="MIT license">
</p>

Central de comando da recolocação. Duas ferramentas, uma sequência fixa.
Dados do candidato (incluindo metas pessoais de volume/match/foco) vivem em
`profile/candidate.yaml` — veja `AGENTS.md` pra arquitetura completa
(funciona com qualquer agente de código, não só Claude).

---

## A rotina do dia

### 1. Claude Code
```
claude
```
Dentro do repo, na raiz.

```
/daily
```
Busca vagas (LinkedIn + freehire), tira duplicata do que já foi aplicado, rankeia
por fit score. Aparece uma tabela numerada **com a URL de cada vaga** e uma coluna
`CV?`:
- **`CV? = Sim`** → vaga normal, precisa de CV customizado.
- **`CV? = Não`** → Gupy ou Solides, candidatura usa o perfil que já tá cadastrado
  lá. Não gera CV nenhum.

Você não precisa da URL agora pra rodar `/apply-batch` (ele já resolve o número
pra URL sozinho) — ela reaparece no relatório do `/apply-batch` e de novo no do
`/compile-today`, que é a hora que você realmente vai usar pra submeter.

```
/apply-batch 1,2,3,8
```
Só pros números com `CV? = Sim`. Gera um CV por vaga.

Vaga achada fora do `/daily` (LinkedIn CLI quebrou, ou você foi atrás de uma
específica)? Cola a URL direto no `/apply-batch` em vez de um índice.

Termina, sai do Claude Code.

### 2. OpenCode
```
opencode
```
Também na raiz do repo.

```
/compile-today
```
Compila os PDFs, confere se ficaram em 1 página, checa se as keywords da vaga
aparecem no texto extraído, e arquiva tudo em `documents/applications/`. **Não
toca no Notion** — nada é registrado ainda nesse ponto.

### 3. Aplique de verdade, depois volte pro Claude Code

Envie os CVs (upload no site, e-mail, etc.) e aplique manualmente nas vagas
`CV? = Não` direto na Gupy/Solides com seu perfil. Depois:

```
claude
```
```
/confirm 1,2,3
```
Números das vagas que você **realmente enviou** hoje — com CV ou sem CV
(Gupy/Solides). **Esse é o único comando que grava no Notion**, sempre direto como
"Aplicado" — não existe registro antes disso, então não se gasta chamada de API
em candidatura que ainda pode não ter saído do papel.

Fim do dia.

---

## Se algo quebrar

| Sintoma | Onde olhar |
|---|---|
| `/daily` não acha vaga nenhuma | LinkedIn pode ter bloqueado — tenta só com freehire, ou cola a URL direto no `/apply-batch` |
| CV saiu com mais de 1 página | `/compile-today` já barra isso sozinho (não registra, não arquiva, aparece no relatório) — corte conteúdo seguindo `rules/cv-rules.md` e rode `/compile-today` de novo |
| `/compile-today` deu erro de compilação | Log do pdflatex aparece no relatório — geralmente é caractere especial não escapado |
| Vaga já apareceu antes | `/daily` filtra pelo Notion (Aplicado/Congelado/Rejeitado) **e** pelos arquivos locais (`documents/applications/`, `daily/*/*.json`) pra pegar candidatura em andamento que ainda não foi confirmada |
| Esqueci de rodar `/confirm` | Sem problema — o CV já tá compilado e arquivado localmente, o Notion só fica desatualizado até você rodar `/confirm <número>`, não precisa ser no mesmo dia |

---

## Cavando mais fundo (não precisa ler todo dia)

- `AGENTS.md` — arquitetura atual (profile/rules/workflows, agnóstica de agente/LLM)
- `SETUP.md` — instalar dependências (LaTeX, bun, poppler, Python)
- `OPENCODE.md` — os modelos grátis do OpenCode e qual usar em cada tarefa
- `documents/README.md` — como fica organizada a pasta de candidaturas

## Créditos

As CLIs de busca (`.agents/skills/linkedin-search/`, `.agents/skills/freehire-search/`)
foram adaptadas a partir de trechos de [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (não é um fork).
