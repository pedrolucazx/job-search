# 001: Funil de conversão e status canônico

Origem: análise do career-ops (thread "Aproveitar Career Ops no projeto"),
itens 1 (stats/analyze-patterns) e 6 (states.yml) adaptados ao nosso caso.
Risco: **médio** (scripts locais + leitura do Notion; nenhuma escrita externa).

## Objetivo

Responder com dados, a partir das ~430 candidaturas já registradas:

1. O score de fit prevê resposta? (conversão por faixa de score)
2. Qual fonte converte melhor? (LinkedIn, Gupy, e-mail, site da empresa...)
3. Quais gaps aparecem mais nas rejeitadas do que nas que avançaram?

Hoje o score é calculado na entrada e o resultado nunca volta para validá-lo.

## Problema de base: status sem vocabulário

A verdade dos status está no Notion (144 rejeitadas lá, quase nenhuma no
`outcome.md` local). O dashboard deriva estado por substring ("contém
Applied"), então `Applied, Rejected` conta como ativa. Os `outcome.md` têm
`Applied`, `Rejected`, `Rejeitado`, `Posição fechada`, `Desisti`,
`Not applied — ...` misturados.

## Escopo

- **`scripts/outcome.py`**: vocabulário canônico único (`STATES`, em ordem de
  ciclo de vida) + `normalize(texto) -> estado` com aliases PT/EN, cobrindo os
  status do Notion e os textos livres dos `outcome.md`.
- **`scripts/build_dashboard.py`**: `derive_state` usa `normalize`; candidatura
  rejeitada/fechada/sumida/desistida deixa de aparecer como ativa (nova raia
  "Encerrada"). Dashboard mostra o resumo do funil quando houver
  `documents/funnel.json`.
- **`scripts/analyze_outcomes.py`** (novo, stdlib): lê o data source do Notion
  pela API (`NOTION_TOKEN` no `.env`, `data_source_id` do
  `profile/candidate.yaml`), cruza cada linha com o `metadata.json` local por
  slug de empresa+cargo (score, fonte, gaps), e imprime:
  - funil por estado canônico;
  - taxa de resposta e de avanço por faixa de score (<60, 60-69, 70-79, 80+,
    sem score), por fonte e por mês;
  - gaps mais frequentes entre rejeitadas vs. avançadas.
  Grava `documents/funnel.json` (gitignored) para o dashboard.
  `--from-json <arquivo>` lê linhas de um arquivo em vez da API (testes e uso
  offline).

## Fora de escopo

- Escrever no Notion (é a parte 2, junto com o job-status-bot).
- Envelhecimento automático, follow-up, fact-check do CV, detector de repost.
- Corrigir as 5 falhas pré-existentes em `tests/test_check_roteiro.py`.

## Definições

- **Enviada**: qualquer estado exceto `compiled`, `discarded`, `withdrew`
  (decisão do candidato) e `unknown` (listado à parte no relatório).
- **Respondida**: decisão vinda da empresa: `screening`, `technical`,
  `offer`, `hired`, `rejected` ou `closed`. `frozen` não é veredito e
  `withdrew` não vem da empresa (corrigido após o review independente, A1).
- **Avançou**: estado `screening`, `technical`, `offer` ou `hired`, OU
  `outcome.md` local com etapa marcada quando o Notion já mostra resposta
  (evita que uma reaplicação herde etapas de outro processo). Limitação
  conhecida: o Notion guarda só o estado atual, então uma rejeição depois da
  técnica só conta como avanço se o `outcome.md` tiver a etapa marcada.
- **Score**: o do `metadata.json` local; sem pasta local, o "Score NN%" /
  "Fit NN%" do Feedback (nunca score de ATS).

## Critérios de aceite

1. `normalize` mapeia todos os 10 status do Notion e todos os textos de
   `Status:` hoje presentes em `documents/applications/*/outcome.md`
   (nenhum cai em `unknown`).
2. Dashboard: `Rejected` e `Applied, Rejected` não aparecem na raia
   "Aplicada"; `--check` passa.
3. `analyze_outcomes.py --from-json` com fixture produz as tabelas corretas
   (teste unitário, sem rede).
4. Rodado contra o Notion real, as contagens por estado batem com a contagem
   do Notion (Aplicado 223+, Rejeitado 144+, ...).
5. Sem `NOTION_TOKEN`, o script sai com mensagem clara, não stack trace.
6. Suite de testes: nenhuma falha nova além das 5 pré-existentes.

## Tarefas

- T1 `outcome.py`: `STATES`, `ALIASES`, `normalize` + testes.
- T2 `build_dashboard.py`: `derive_state` via `normalize`, raia Encerrada,
  resumo do funil + self-check atualizado.
- T3 `analyze_outcomes.py`: fetch Notion (paginado), join local, agregações,
  `funnel.json`, `--from-json` + testes.
- T4 Token: integração interna no Notion compartilhada com o banco
  "Aplicações"; `NOTION_TOKEN` no `.env`.
- T5 Rodar contra o Notion real, conferir critério 4, review independente.
