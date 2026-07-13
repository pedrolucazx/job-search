# 🎯 Job Search — Workspace de Recolocação

Este repositório é seu centro de comando de guerra pra recolocação.
Claude Code (Opus) gera CVs com precisão cirúrgica; OpenCode faz compilação, ATS check e registro no tracker.

Arquitetura completa (agnóstica de agente/LLM): ver `AGENTS.md`.

## Regras Absolutas
1. NUNCA inventar dados, métricas, projetos ou tecnologias fora de `profile/candidate.yaml`
2. Seções Formação e Idiomas são TRAVADAS — copiar exatamente como estão
3. CV deve ter EXATAMENTE 1 página A4
4. Gap analysis sempre com tabela full/partial/absent
5. Soft skills sempre bilíngue "Português (English)", conforme `profile/candidate.yaml`
6. NUNCA usar duas colunas, tabelas, gráficos, ícones ou imagens no LaTeX

(Lista completa e comentada em `rules/README.md`.)

## Comandos Disponíveis
| Comando | O que faz | Executa |
|---|---|---|
| `/daily` | Scrape LinkedIn + freehire, rankeia vagas, apresenta tabela | Claude Code |
| `/apply-batch 1,2,3,8` | Gera CVs .tex para N vagas selecionadas (índice ou URL colada) | Claude Code |
| `/compile-today` | Compila .tex → .pdf → ATS check → arquiva (não toca no tracker) | OpenCode |
| `/confirm 1,2,3` | Único comando que registra "Aplicado" no tracker configurado (ver `profile/candidate.yaml → tracker`) | Claude Code |

## Onde estão as regras e os dados (leia antes de executar comandos)
- `profile/candidate.yaml` — dados canônicos do candidato ativo (gitignored; copiar de `profile/candidate.example.yaml`)
- `rules/` — regras universais de CV, avaliação de fit, ATS, entrevista
- `workflows/` — passos operacionais de cada comando acima

## Formato de Saída (bridge Claude Code → OpenCode)
Claude Code gera:
- `documents/cv/main_<empresa>.tex` — CV em LaTeX
- `daily/<data>/<empresa>.json` — Metadados da candidatura

OpenCode lê e processa.
