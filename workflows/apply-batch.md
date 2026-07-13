# workflows/apply-batch.md — Aplicação em Massa

Gera CVs `.tex` para N vagas selecionadas na tabela do `workflows/daily.md`.
Genérico — lê `profile/candidate.yaml` + `rules/`, nunca dado hardcoded.

## Input

- Lista de índices numéricos (ex: `1,2,3,4,8,10,20`) da tabela do `/daily`
  desta sessão, OU uma URL colada direto (fluxo manual).

## Fluxo por vaga

### 1. Fetch da postagem

Se já coletada no scrape com descrição completa, usar direto. Senão,
WebFetch da URL (ver `rules/job-evaluation.md` → Fetch de Descrição Completa
pro fallback de domínios problemáticos).

### 2. Extrair requisitos

Listar obrigatórios e desejáveis da vaga.

### 2.5 Gate — deal breakers e score real

Usar `rules/job-evaluation.md`, com a descrição completa em mãos:

1. Checar `profile/candidate.yaml → preferences.deal_breakers` contra a
   descrição completa (não a tag de busca). Se bater em algum: **não gerar
   CV**, marcar como excluída no relatório com o motivo.
2. Calcular o score real (gap table completa). Se < 60%: **não gerar CV**,
   marcar como excluída com o score e o principal motivo da queda.
3. Só prosseguir pro passo 3 se passou nos dois.

### 3. Gerar CV

Ler `rules/cv-rules.md` + `profile/candidate.yaml` + `templates/cv_template.tex`.

Produzir `documents/cv/main_<empresa_sanitizada>.tex` com:
- [ ] Resumo personalizado alinhado à vaga
- [ ] Habilidades ordenadas por overlap com a stack da vaga
- [ ] 4-6 bullets de experiência, mais relevante primeiro
- [ ] Projetos selecionados por overlap de stack (ver `rules/cv-rules.md`)
- [ ] Formação e Idiomas — copiados exatamente de `profile/candidate.yaml`
- [ ] Soft skills — exatamente as do profile, formato bilíngue
- [ ] Exatamente 1 página A4
- [ ] Nenhum dado fora do profile

### 4. Salvar metadados

Criar `daily/<data>/<empresa_sanitizada>.json` — schema canônico, os nomes de
campo não podem mudar (`workflows/compile.md` depende deles):

```json
{
  "empresa": "Nome da Empresa",
  "cargo": "Cargo da vaga",
  "url": "https://...",
  "data": "YYYY-MM-DD",
  "cv_tex": "documents/cv/main_empresa.tex",
  "score": 82,
  "gaps": [
    {"skill": "AWS", "status": "absent", "nota": "Gap identificado"},
    {"skill": "Kafka", "status": "partial", "nota": "Conceitos, sem prática"}
  ],
  "stack": ["Node.js", "TypeScript", "PostgreSQL"],
  "nivel": "Pleno",
  "fonte": "LinkedIn",
  "requisitos_full": 7,
  "requisitos_partial": 2,
  "requisitos_absent": 1,
  "total_requisitos": 10
}
```

### 5. Relatório parcial

- Passou no gate: `✓ Empresa — CV gerado — <url>`
- Excluída no gate: `✗ Empresa — excluída, score real 33% (motivo)` — sem
  gerar `.tex`, sem gastar esforço em CV que não deveria chegar aqui.

Ao final: "X CVs gerados, Y excluídas. Rode `workflows/compile.md` pras
geradas."
