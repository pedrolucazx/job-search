# Rules — Índice e Regras Absolutas

Instrução universal pra qualquer agente/LLM que for operar este repositório.
Não contém dado de nenhum candidato — isso vive em `profile/candidate.yaml`
(veja `AGENTS.md` na raiz pra saber por onde começar).

## Índice

| Arquivo | Conteúdo |
|---|---|
| `cv-rules.md` | Regras de geração do CV: seleção de conteúdo, verbos, formatação, soft skills |
| `job-evaluation.md` | Framework de fit score, gap table, deal breakers |
| `ats-verification.md` | Pipeline de compilação e verificação ATS |
| `interview-prep.md` | Preparação de entrevista a partir das aplicações registradas |

## Regras Absolutas (valem pra qualquer candidato)

1. **NUNCA inventar dado** — métrica, projeto, tecnologia ou experiência fora
   do que está em `profile/candidate.yaml`. Se faltar informação, perguntar ou
   deixar de fora — nunca preencher com algo plausível.
2. Seções **Formação** e **Idiomas** são TRAVADAS — copiar exatamente como
   estão em `profile/candidate.yaml → education / languages`, nunca reescrever
   ou resumir.
3. CV deve caber em **exatamente 1 página A4**.
4. Gap analysis sempre em tabela `full` / `partial` / `absent` (ver
   `job-evaluation.md`).
5. Soft skills sempre bilíngues, formato `"Português (English)"` — ver
   `profile/candidate.yaml → soft_skills`.
6. **NUNCA** usar duas colunas, tabelas, gráficos, ícones ou imagens no LaTeX
   do CV (ATS não parseia).
7. Todo dado de candidato vem de `profile/candidate.yaml` — nunca hardcoded
   aqui em `rules/` ou em `workflows/`.
8. Fit score e seleção de conteúdo do CV funcionam por **overlap de skills
   declaradas vs requisitos da vaga** — nunca por vocabulário fixo de nicho
   (o motor não assume "fintech" nem qualquer outro domínio; isso é
   `preferences.target_industries` do profile de cada dev).

## Robustez para modelos free/fracos

Se o agente executando isso for um modelo gratuito ou mais fraco:
- Prefira os **gates determinísticos** desta pasta (ex: regra de 100% remoto,
  regra de 60% de score) em vez de julgamento nuançado sempre que possível.
- Ao gerar saída estruturada (JSON de metadados, gap table), se o resultado
  não vier bem formado, tente novamente 1x antes de reportar erro.
- Requisito mínimo: o agente precisa ter acesso a arquivo + shell (ler
  `profile/`, rodar `scripts/validate_profile.py`, compilar LaTeX). Um chat
  raw sem tool-use só serve pro caminho manual (colar o YAML no prompt).
