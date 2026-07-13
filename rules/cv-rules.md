# cv-rules.md — Regras de Geração de CV (genérico, qualquer track)

Ver `README.md` pras Regras Absolutas. Este arquivo cobre a lógica de seleção
e formatação do conteúdo do CV. Nunca contém dado de candidato — tudo aqui lê
`profile/candidate.yaml`.

## Seleção de Conteúdo por Overlap de Stack

Não existe tabela fixa de "qual projeto destacar pra qual stack" — isso seria
regra de nicho, e o objetivo é funcionar igual pra backend, frontend, mobile,
IoT, dados etc. Em vez disso:

1. Extrair a stack requerida da vaga (obrigatórios + desejáveis).
2. Para cada item de `professional_experience[].projects[]` e cada item de
   `personal_projects[]`, calcular overlap entre `stack` do item e a stack da
   vaga.
3. Ordenar por overlap decrescente. Escolher os projetos/experiências com
   maior overlap pra destacar primeiro no CV — os de baixo overlap ficam de
   fora se o espaço de 1 página apertar.
4. Item com `include_only_if` só entra se a condição textual bater com a vaga
   (ex: um projeto Ruby só aparece se a vaga menciona Ruby).
5. Item de `personal_projects` sem `link` preenchido: citar sem hyperlink,
   nunca inventar uma URL de repositório.

## Seleção por Nível da Vaga

Tom e verbos mudam conforme o nível declarado na vaga vs a senioridade do
candidato (`preferences.seniority_by_stack`, se preenchido):

| Nível da vaga | Tom | Verbos preferidos |
|---|---|---|
| Sênior/Staff/Especialista | Autonomia, ownership, decisão arquitetural | Conduzi, Defini, Garanti, Arquitetei |
| Pleno | Autonomia técnica, condução | Conduzi, Defini, Garanti, Implementei |
| Júnior | Fundamentos, entrega, aprendizado | Desenvolvi, Implementei, Colaborei |

Se `preferences.seniority_by_stack` sinalizar mismatch (vaga pede nível acima
do que o candidato declarou pra aquela stack), reportar isso na avaliação —
não impede geração do CV sozinho, mas o agente deve avisar no relatório.

## Soft Skills

Sempre bilíngue, formato `"Português (English)"`. Usar exatamente as 6 (ou
quantas houver) de `profile/candidate.yaml → soft_skills`. Se a vaga usar um
termo equivalente a alguma delas, pode trocar o rótulo mantendo o par
bilíngue — nunca adicionar uma sétima.

## Bullets de Experiência

Formato: **VERBO DE AÇÃO + CONTEXTO TÉCNICO + RESULTADO/ESCOPO**.

- 4 a 6 bullets por experiência, começando pelo mais relevante pra vaga.
- Variar o verbo — nunca repetir o mesmo verbo em bullets consecutivos.
- Basear os bullets em `professional_experience[].responsibilities` — não
  inventar responsabilidade que não está listada lá.
- Se o profile distinguir ferramentas por contexto (ex: um ORM usado no
  trabalho e outro em projetos pessoais), respeitar essa distinção — não
  transplantar ferramenta de projeto pessoal pro bullet de experiência
  profissional ou vice-versa.

**Exemplo de bullet correto**: verbo específico + tecnologia real do profile
+ escopo/resultado concreto. Nunca genérico tipo "Construção de APIs robustas
e seguras" (isso não diz nada verificável).

## Duração de Experiência

Nunca arredondar tempo de experiência além de 1 ano (ex: se
`duration_note` diz "4+ anos", escrever "4 anos" ou "4+ anos", nunca "5 anos").

## Template e Formatação

- Article class LaTeX, A4, 1 página, fonte sans-serif (Helvetica ou
  equivalente), cor de destaque única pra títulos de seção.
- Ver `templates/cv_template.tex` como base — ele já tem os placeholders.
- Título de seção em UPPERCASE, sem duas colunas/tabelas/ícones/imagens
  (Regra Absoluta #6).

## Checklist Obrigatório Antes de Entregar

1. Nenhum dado inventado — todo bullet/projeto/skill rastreável até
   `profile/candidate.yaml`.
2. Nomes de instituições/projetos/tecnologias grafados exatamente como no
   profile (checar erro de digitação).
3. Links de repositório como hyperlink de verdade, só os que têm `link`
   preenchido no profile.
4. Formação e Idiomas idênticos ao profile, sem paráfrase.
5. Documento cabe em 1 página A4.
6. Email e telefone aparecem como texto literal no PDF final (não como glifo
   de ícone — verificado no `ats-verification.md`).
