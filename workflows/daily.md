# workflows/daily.md — Rotina Matinal

Inicia o dia de aplicações: scrape → gap score → tabela → escolha do dev.
Genérico — as queries de busca vêm do profile ativo, nunca hardcoded aqui.

## 0. Carregar o profile

```bash
python3 scripts/validate_profile.py
```

Se der erro, parar e pedir pro dev corrigir `profile/candidate.yaml` antes de
continuar. Ler `preferences.target_roles`, `track` e `skills` do profile —
são a base das queries de busca do passo 1.

## 1. Scrape (fontes configuráveis)

As CLIs de busca disponíveis hoje neste repo: `.agents/skills/linkedin-search/`
e `.agents/skills/freehire-search/` (ambas bun, zero custo de API). Monte as
queries a partir de `preferences.target_roles` e das skills de maior nível em
`skills.<categoria>` do profile ativo — não usar lista fixa de queries.

```bash
for q in "${QUERIES[@]}"; do
  bun run .agents/skills/linkedin-search/cli/src/cli.ts search \
    -q "$q" -l "Brazil" --remote remote --jobage 7 --format json
  bun run .agents/skills/freehire-search/cli/src/cli.ts search \
    -q "$q" --country BR --remote remote --jobage 7 --format json
done
```

⚠️ Isso filtra pela tag de busca, não é garantia — reconfirmar modelo de
trabalho real no passo 2.5 do `apply-batch.md` (ver `rules/job-evaluation.md`
→ Deal Breakers). Nunca confiar só na tag daqui pra aplicar
`preferences.deal_breakers` de forma definitiva.

Deduplicar por empresa + cargo entre as fontes. Guardar a fonte de cada vaga
(`linkedin`/`freehire`/outra) pra usar depois no tracker, se o backend for
Notion (`tracker.notion.stack_tags` etc.).

**Detectar vaga sem CV**: se a plataforma de destino usa perfil já cadastrado
em vez de PDF (ex: Gupy, Solides — mas isso varia por mercado/país, ajustar
conforme o profile), marcar a vaga como "sem CV" — gerar `.tex` pra essas é
esforço jogado fora.

## 2. Verificar duplicatas

Depende do `tracker.backend` do profile ativo:

- **notion**: buscar por empresa via MCP do Notion (`tracker.notion.database_id`).
  Remover vagas cuja empresa já está cadastrada, qualquer status.
- **csv**: ler `tracker.csv.path` (ex: `documents/applications.csv`) e remover
  vagas cuja empresa já aparece lá.
- **none**: só checar local (`documents/applications/*/` e `daily/*/*.json`
  dos últimos dias) — sem tracker externo pra consultar.

Em qualquer backend, também checar local (`documents/applications/*/` e
`daily/*/*.json`) — cobre candidatura em andamento que ainda não foi
confirmada no tracker.

## 3. Calcular fit score

Usar `rules/job-evaluation.md` (pré-triagem heurística, sem fetch completo)
comparando título + skills da vaga com `profile/candidate.yaml`.

## 4. Apresentar tabela rankeada

Incluir sempre a URL (é o link que o dev vai usar pra submeter manualmente
depois — este sistema nunca aplica sozinho). Só vagas com score ≥ 60%:

```
#  │ Empresa   │ Cargo           │ URL              │ Score │ Gaps    │ CV?
───┼───────────┼─────────────────┼──────────────────┼───────┼─────────┼──────
1  │ Empresa X │ Backend Pleno   │ ...              │ 82%   │ AWS     │ Sim
```

## 5. Perguntar

> "Quais números quer aplicar hoje? (ex: 1,2,3,4,8,10,20) ou 'pular'."

## 6. Encaminhar por tipo

- **`CV? = Sim`** → `workflows/apply-batch.md` com esses índices.
- **`CV? = Não`** → aplicar manualmente na plataforma; depois
  `workflows/confirm.md` com esses índices pra registrar no tracker.
