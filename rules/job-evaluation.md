# job-evaluation.md — Framework de Avaliação de Fit (genérico)

## Critérios de Avaliação

Para cada requisito da vaga, classificar:
- **FULL**: atende completamente (skill presente no profile com nível
  adequado)
- **PARTIAL**: atende parcialmente (tem base, mas falta profundidade/anos)
- **ABSENT**: não atende (gap real — não está no profile)

## Cálculo do Score

```
Score = (FULL * 1.0 + PARTIAL * 0.5 + ABSENT * 0.0) / TOTAL * 100
```

## Regra dos 60%

Só apresentar na tabela do `/daily` vagas com score ≥ 60%. Abaixo disso o gap
é grande demais — gerar CV customizado não compensa o esforço.

## Dimensões de Análise (pesos sugeridos, ajustável por track)

1. Stack técnica (peso 40%) — comparar `skills` do profile vs requisitos
2. Experiência no domínio (peso 25%) — `professional_experience` /
   `personal_projects` relevantes ao setor da vaga
3. Nível da vaga vs `preferences.seniority_by_stack` (peso 15%)
4. Localização/flexibilidade (peso 10%) — só entra na conta se passou nos
   deal breakers abaixo
5. Alinhamento com `preferences.target_roles` / `target_industries` (peso 10%)

## Gap Table (formato obrigatório)

| Requisito | Status | Nota |
|---|---|---|
| <skill da vaga> | FULL / PARTIAL / ABSENT | contexto (anos, projeto onde apareceu, ou motivo do gap) |

## Deal Breakers

Excluir a vaga **da tabela inteira**, não só sinalizar — ver
`profile/candidate.yaml → preferences.deal_breakers`. Cada item ali é uma
condição de exclusão dura e específica do candidato (ex: modalidade de
trabalho, ausência de algo obrigatório pro candidato). Tratar cada
`deal_breaker` como regra literal: se a vaga bate nela, fora da tabela, sem
exceção — mesmo que o resto do fit seja excelente.

Se `preferences.deal_breakers` incluir algo sobre modalidade de trabalho
(remoto/híbrido/presencial), **sempre confirmar lendo a descrição completa da
vaga antes de aplicar a exclusão** — tags de busca (`--remote remote` etc.)
não são confiáveis, plataformas já marcaram vaga errado antes.

## Mismatch de Senioridade

Se `preferences.seniority_by_stack` existir e a vaga pedir nível diferente do
declarado pra aquela stack: não é deal breaker (não exclui sozinho), mas
sinalizar isso claramente na tabela/gap notes — quem decide se aplica mesmo
assim é o candidato.

## Dois Estágios de Avaliação

### 1. `/daily` — pré-triagem heurística (sem fetch completo)

Score aqui é estimado por título + tags da busca, sem ler a descrição
completa da vaga (evita gastar limite de scraping/tokens em vaga óbvia).
**Não é definitivo** — não aplicar deal breakers de forma definitiva aqui,
só como filtro grosseiro inicial.

### 2. `/apply-batch` — avaliação real (com descrição completa)

1. Fetch da descrição completa.
2. **Checar deal breakers primeiro**, com a descrição completa em mãos. Se
   bater em algum: parar aqui, não gerar CV, marcar como excluída no
   relatório com o motivo.
3. Extrair requisitos obrigatórios e desejáveis.
4. Comparar com `profile/candidate.yaml` (skills, professional_experience,
   personal_projects).
5. Produzir gap table completa + score real.
6. **Se score real < 60%**: parar aqui, não gerar CV — o score do `/daily`
   era só estimativa; o real decide se vale o esforço de escrever o CV.

## Fetch de Descrição Completa

- Padrão: WebFetch.
- Se um domínio específico bloquear WebFetch/curl (ex: SPA atrás de WAF/bot
  protection), usar um browser real via MCP (ex: Playwright) como fallback —
  documentar o domínio problemático numa nota de projeto pra não redescobrir
  o mesmo bloqueio depois.
