# 002: Vaga encerrada, fact-check do CV e follow-up

Continuação da 001, com o resto da análise do career-ops que cabe aqui.
Risco: **médio** (gates locais; `followup.py --apply` escreve Status no Notion,
só com flag explícita).

## Escopo (o que veio do career-ops)

| Item | Origem no career-ops | Aqui |
|---|---|---|
| Vaga encerrada antes do CV | `liveness-core.mjs` (frases de encerramento) | `scripts/check_liveness.py` + passo 1 do `apply-batch.md`. Somou os sinais medidos nas nossas fontes: LinkedIn redireciona para `trk=expired_jd_redirect`; Gupy embute `"status":"closed"` |
| Fato inventado no CV | `cv-payload-facts` (gate antes do PDF) | `scripts/fact_check.py` + bloqueio no `compile-all.sh`. Compara **número + unidade** (anos, %, pessoas, linhas...) PT/EN contra o perfil, ignorando comentários do YAML |
| Follow-up e vaga fria | `followup-cadence.mjs` (7 dias, máx. 2, depois cold; "retire" sem contato) | `scripts/followup.py`: follow-up só onde há e-mail; 30+ dias sem resposta vira candidata a "Sumiu" (`--apply`) |

## Fora de escopo (e por quê)

- `detect-reposts.mjs`: o problema que tivemos (Joblet-AI) foi spam de muitas
  vagas diferentes no mesmo dia, não a mesma vaga repostada; e o próprio
  career-ops documenta 3 armadilhas que geravam falso positivo.
- `triage` com `_brief.md`, batch paralelo, scanner de portais, avaliação A–H,
  TUI, PDF via HTML: ver a thread.

## Critérios de aceite

1. `check_liveness.py`: LinkedIn expirado e Gupy fechado → `closed`; vaga
   aberta das duas fontes → `live`; `mailto:` → `uncertain` (conferido em
   URLs reais em 2026-11-13).
2. `fact_check.py`: 0 falsos positivos nos CVs arquivados; pega "5 years",
   "95%", "12 developers" inventados; aceita "4+ years", "1,000 lines", "100%".
3. `followup.py`: lista follow-up só com canal de e-mail e ≥ 7 dias; frias com
   ≥ 30 dias; `--apply` só com Notion.
4. Testes novos passam; nenhuma falha nova além das 5 de `test_check_roteiro`.
