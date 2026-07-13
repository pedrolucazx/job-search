# ats-verification.md — Verificação ATS (genérico)

Descreve o que o passo de compilação (`workflows/compile.md`) faz. É
mecânico — não depende de julgamento de LLM, roda via script/shell em
qualquer agente.

## Pipeline de Compilação

1. `pdflatex -interaction=nonstopmode` no `.tex` gerado.
2. Verificar página: exatamente 1 página A4. Diferente de 1 = falha, não
   arquivar — tratar igual erro de compilação.
3. `pdftotext -layout` no PDF → extrair text layer.
4. Verificar parseabilidade:
   - Email e telefone (`profile/candidate.yaml → personal.email/phone`)
     aparecem como texto literal, não como glifo de ícone.
   - Sem `(cid:*)` ou caracteres de substituição no texto extraído.
   - Ordem de leitura correta (sem contaminação de duas colunas).
5. Keyword coverage: comparar skills/stack da vaga (status `full`/`partial`)
   contra o text layer — devem aparecer. Skills marcadas `absent` na gap
   table **não podem aparecer no CV** — se aparecerem, é sinal de dado
   inventado, bloquear e corrigir antes de arquivar.
6. Erro de compilação: reportar o log, tentar 1 correção óbvia (caractere não
   escapado, overfull hbox) e recompilar uma vez; se falhar de novo, marcar
   como erro no relatório e não prosseguir pra essa vaga.

## Falso Positivo de Sinônimo

Se o ATS check acusar "skill ausente" mas o CV usou um sinônimo real (ex: a
vaga/JSON diz "CI/CD" mas o CV escreveu "GitHub Actions"), isso não é
bloqueante — usar julgamento antes de travar a compilação por causa disso.
Já "gap absent aparece no CV" é **sempre** bloqueante.
