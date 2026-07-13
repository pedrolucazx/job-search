# workflows/compile.md — Compilação e ATS Check

Pós-processamento das candidaturas geradas por `workflows/apply-batch.md`.
Mecânico — não toca no tracker (Notion/CSV/none). Recebe opcionalmente uma
data (`YYYY-MM-DD`); se omitida, usa hoje.

**Este passo não registra a candidatura em lugar nenhum.** O tracker só é
tocado em `workflows/confirm.md`, depois que o dev confirma que enviou de
verdade — evita gastar chamada de API (Notion) ou linha de CSV em candidatura
que pode nem virar envio real.

## 1. Compilar + ATS check (delegar ao script)

```bash
python3 scripts/validate_profile.py   # falha rápido se o profile estiver quebrado
bash scripts/compile-all.sh <data>
```

Compila cada `.tex` referenciado em `daily/<data>/*.json` (via `jq`, nunca
adivinhando o nome do arquivo), confere 1 página, roda ATS check via `grep`
(ver `rules/ats-verification.md`). Script mecânico — não deixa `.txt`
temporário pra trás, só o veredito.

Se um `.tex` falhar: ler o log, tentar corrigir a causa óbvia (caractere não
escapado, overfull hbox) e recompilar uma vez. Se falhar de novo, marcar como
erro no relatório final e não prosseguir pros passos 2-3 dessa vaga.

Se o ATS check vier com pendências: "gap absent aparece no CV" é sempre
bloqueante; "stack/gap full/partial ausente" pode ser falso positivo de
sinônimo — usar julgamento (ver `rules/ats-verification.md`).

## 2. Para cada vaga compilada com sucesso

Ler `daily/<data>/<empresa>.json` (schema em `workflows/apply-batch.md` §4).

### 2.1 Confirmar 1 página

`pdfinfo <pdf> | grep Pages`. Diferente de 1 = tratar como falha, não
arquivar, sinalizar pra intervenção manual (cortar conteúdo conforme
`rules/cv-rules.md`).

### 2.2 Arquivar

Mover pra `documents/applications/<empresa>_<cargo>/` (slugify ambos):
- `documents/cv/main_<empresa>.pdf` → `<pasta>/main_<empresa>.pdf`
- `documents/cv/main_<empresa>.tex` → `<pasta>/cv_draft.tex`
- Copiar (não mover) `daily/<data>/<empresa>.json` → `<pasta>/metadata.json`
  — é o que `workflows/confirm.md` lê depois.

Criar `<pasta>/outcome.md`:

```markdown
# Outcome: <Empresa> — <Cargo>

**URL:** <url do JSON> — submeter o CV manualmente aqui
**Status:** aguardando confirmação de envio (rode workflows/confirm.md)
**Data compilação:** <data do JSON>
**Data resolução:** —

## Interview stages reached
- [ ] Phone screen
- [ ] Technical interview
- [ ] System design
- [ ] Final round
- [ ] Offer received

## Notas
```

## 3. Relatório final

Incluir a URL de cada vaga compilada com sucesso:

```
✓ Empresa X → 1pg ✅ ATS OK ✅ arquivado → <url>
✗ Empresa Y → ERRO compilação (overfull) → intervir manualmente
8/10 CVs compilados e arquivados. Vá submeter nas URLs acima, depois rode
workflows/confirm.md — é o único passo que grava no tracker.
```
