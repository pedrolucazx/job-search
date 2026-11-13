# 003: Volume (~10 CVs/dia) e consistência dos formulários

Risco: **médio** (fontes e gates locais; nenhuma escrita externa).

## Objetivo

Chegar a ~10 CVs por dia sem baixar o corte de qualidade. Medido em
2026-11-13: os dias com 20-30 CVs foram os que rodaram o `/daily` completo com
Gupy/freehire; os dias fracos usaram só o LinkedIn. O Gupy é a fonte que mais
converte (72% resposta, 4% avanço em 78 envios; LinkedIn 34% / 0% em 225), mas
só entrava pelo freehire.

## Escopo (o que veio do career-ops, e o que é nosso)

| Item | Origem | Aqui |
|---|---|---|
| Gupy como fonte fixa | nosso (dado do funil) | `scripts/gupy_search.py`, API pública do portal: descrição completa e `workplaceType` estruturado, filtro remoto/14 dias/teto no título. Passo 1 do `/daily`. Medido: 503 varridas, 52 remotas sem Sênior em 14 dias |
| InHire como fonte | nosso | `scripts/inhire_search.py`: sem portal central, API pública por empresa com header `X-Tenant`; lista de empresas em `documents/inhire_tenants.txt` que cresce com o histórico. Medido: 25 empresas, 1204 vagas varridas, 13 remotas dentro do teto em 14 dias |
| Java Pleno | decisão do usuário | teto do Java passou de Júnior para Júnior/Pleno (perfil declara 4 anos) |
| Anos exigidos na JD | `jd-years.mjs` | `scripts/jd_years.py` + passo 2.5 do apply-batch: `above` no Gupy exclui (pergunta eliminatória), fora do Gupy vira `partial` |
| Banco de respostas | `application-answers` | `profile.application_answers` + `rules/application-answers.md` + passo 4.5 do apply-batch |
| Voz do CV | `cv-voice.mjs` | `scripts/cv_voice.py` bloqueia arquivamento no `compile-all.sh` (travessão, 3ª pessoa) |
| O que estudar | `upskill.mjs` | seção no `analyze_outcomes.py`, gap ponderado por (100 − score) |

## Fora de escopo

`filter-audit`/`discard-analytics` e resumo semanal (descartados pelo usuário:
o foco é trazer mais vaga, não saber das descartadas).

## Critérios de aceite

1. `gupy_search.py` no formato do linkedin-search, com filtros testados offline.
2. `jd_years.py` acerta as frases de teste e ignora "anos de mercado".
3. `cv_voice.py`: 0 falso positivo nos 77 CVs feitos após a regra (1 violação
   real: CV do iFood com travessão).
4. Suíte sem falha nova além das 5 de `test_check_roteiro`.
