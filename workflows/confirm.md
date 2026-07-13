# workflows/confirm.md — Confirmar Candidaturas Enviadas

**Único passo que escreve no tracker.** Nem `apply-batch.md` nem
`compile.md` tocam nele — só depois que o dev confirma que enviou de
verdade é que existe um registro (API call ou linha de CSV gasta).

O backend real é lido de `profile/candidate.yaml → tracker.backend`:

```bash
python3 scripts/validate_profile.py --get tracker.backend
```

## Input

Lista de índices da tabela apresentada por `workflows/daily.md` nesta sessão
(ex: `2,5,7`), ou nomes de empresa direto se a sessão não tiver mais a
tabela em contexto.

## Fluxo por vaga

### Se a vaga tinha `CV? = Sim` (passou por `apply-batch.md`)

1. Checar localmente se `documents/applications/<empresa>_<cargo>/metadata.json`
   existe — prova que `compile.md` já rodou e arquivou.
2. Se não existir: avisar, não registrar nada — pedir pra rodar
   `workflows/compile.md` primeiro.
3. Se existir: ler `metadata.json` e registrar com **status = "Aplicado"**
   (nunca um estado intermediário).

### Se a vaga tinha `CV? = Não` (candidatura por perfil já cadastrado)

1. Usar os dados já coletados no `/daily` desta sessão (sem CV, sem arquivo
   local).
2. Checar duplicata no tracker antes de registrar.
3. Se não existir: registrar direto com status = "Aplicado".

## Registrar — por backend

### `tracker.backend: csv` (padrão, zero dependência)

```bash
CSV_PATH="$(python3 scripts/validate_profile.py --get tracker.csv.path)"
python3 scripts/track_append.py --check-duplicate --path "$CSV_PATH" --empresa "<empresa>" --cargo "" --data ""
# se saiu com código 0 (não existe), registrar de fato:
python3 scripts/track_append.py \
  --path "$CSV_PATH" \
  --empresa "<empresa>" --cargo "<cargo>" --url "<url>" \
  --status "Aplicado" --data "$(date +%Y-%m-%d)" --fonte "<fonte>" \
  --nivel "<nivel>" --stack "<stack, separado por vírgula>" \
  --gaps "<skills com status != full, separado por vírgula>" \
  --versao-cv "<nome do .tex usado, vazio se não teve CV>" \
  --feedback "<notas dos gaps>"
```

### `tracker.backend: notion` (config pessoal — MCP do dono do profile)

Requer que o agente tenha o MCP do Notion configurado (não existe em todo
ambiente — por isso não é o padrão). Ler
`profile/candidate.yaml → tracker.notion.*`:

- `data_source_id` = `tracker.notion.data_source_id`
- Campos: Empresa, Cargo, Link = url, Status = "Aplicado", Fonte, Nível,
  Data = hoje.
- **Stack/Tecnologias**: só os itens de `stack` que baterem com
  `tracker.notion.stack_tags` (vocabulário fixo daquele workspace) — o que
  sobrar vai no texto do Feedback, nunca tentar escrever fora do vocabulário.
- **Gaps identificados**: mesma regra, filtrando por
  `tracker.notion.gap_tags`.
- Antes de criar, buscar (`notion-search` ou equivalente) por empresa pra
  não duplicar.

### `tracker.backend: none`

Não registrar nada — só compilar e arquivar local
(`documents/applications/`). Útil pra quem não quer tracker nenhum.

## Relatório

```
✓ Empresa X → CV compilado, registrado → Aplicado (csv/notion)
✓ Empresa Y → sem CV, registrado → Aplicado
✗ Empresa Z → documents/applications/.../ não existe, rode workflows/compile.md primeiro
2 confirmadas, 1 pendente.
```
