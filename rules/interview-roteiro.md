# interview-roteiro.md — Interview Presentation Script (generic)

## Scope

This file governs a single-shot generator: the **HR/behavioral interview
script** ("Roteiro de Entrevista") produced by `workflows/interview-prep.md`
for one specific job the candidate already applied to. It is a template
contract + style rules, not a knowledge base.

**Non-goal**: technical-round preparation. Every company tests differently
(live coding, a take-home assignment, no technical test at all) — there's no
way to generalize that into a fixed script. For STAR examples, domain
topics, and system-design prep, see `rules/interview-prep.md` instead.

## Template Contract (mandatory structure)

Output is Markdown, exactly these 6 sections, in this order, for the target
company:

```markdown
# Roteiro de Apresentação — [EMPRESA] ([STACK/CARGO])

## 1. Roteiro PT-BR (~[X] segundos)

**PRESENTE (~[X]s)**
"[TEXTO CONVERSACIONAL — TOM DE FALA, NÃO DE LEITURA]"

**PASSADO (~[X]s)**
"[TEXTO CONVERSACIONAL]"

**FUTURO (~[X]s)**
"[TEXTO CONVERSACIONAL]"

## 2. Roteiro EN (~[X] seconds)

**PRESENT (~[X]s)**
"[VOCABULÁRIO B1-B2, FRASES CURTAS]"

**PAST (~[X]s)**
"[TEXTO EM INGLÊS]"

**FUTURE (~[X]s)**
"[TEXTO EM INGLÊS]"

## 3. Pontos-chave para anotar no papel
- [PONTO 1] — [justificativa de relevância para a vaga]
- ... (5 no total)

## 4. Perguntas para fazer ao recrutador
- Sobre [TEMA]: "[PERGUNTA ESPECÍFICA À VAGA/EMPRESA]"
- ... (mínimo 4)

## 5. Checklist de preparação
- [ ] Cronometrar a apresentação (deve ficar entre 60–90s)
- [ ] Gravar áudio/vídeo de si mesmo apresentando
- [ ] Se for apresentar em inglês: usar Google Tradutor (modo áudio) para validar pronúncia
- [ ] Usar o app "Interview Warmup" do Google para praticar
- [ ] Anotar em papel os 3 pontos-chave ANTES da entrevista
- [ ] Pesquisar a [EMPRESA]: site, LinkedIn, Glassdoor, produto principal
- [ ] [ITENS ESPECÍFICOS DA VAGA]
- [ ] Ter [PROJETO MAIS RELEVANTE] rodando localmente para demonstrar se pedirem

## 6. Análise crítica de compatibilidade

**Requisitos obrigatórios atendidos**
- [REQUISITO] — [evidência do CV]

**Diferenciais atendidos**
- [DIFERENCIAL] — [evidência do CV]

**Atende parcialmente**
- [TECNOLOGIA/REQUISITO] — [gap honesto + risco: baixo/médio/alto + ação concreta]

**Não atende**
- [TECNOLOGIA/REQUISITO] — [gap honesto + ação: estudar X / ser transparente na entrevista]

**Veredicto honesto**
Compatibilidade ~[X]%. [Parágrafo direto sobre o que é forte, o que é gap, e
se vale a pena seguir.]
```

## Present → Past → Future Rule

Guideline timing: PRESENTE ~25s, PASSADO ~30s, FUTURO ~20s (total 60–90s).

- **PRESENTE**: name + role + years of experience + stack aligned to the
  job + 1 motivation sentence.
- **PASSADO**: 1-2 mini-STAR achievements (situation in 1 sentence → result
  in 1 sentence), pulled from the projects/responsibilities the CV
  (`cv_draft.tex`) actually highlighted for this job.
- **FUTURO**: why this company/role + what the candidate wants to develop +
  mention in-progress or completed higher education from
  `profile/candidate.yaml → education` (only if actually present there).

## Tone Rule

Conversational, as if spoken — never a shopping list of technologies.

- **Errado**: "Trabalho com Node, NestJS, TypeScript, PostgreSQL, Docker, Jest..."
- **Correto**: "Meu foco é backend com NestJS e TypeScript, especialmente para APIs que precisam de segurança e testes robustos."

## English Section Rule

B1-B2 vocabulary, short sentences, naturally rewritten — never a literal
translation of the Portuguese section. Frame spoken-English confidence based
on the candidate's own declared `languages[].level` for English (a
candidate-agnostic lookup, not specific to any one candidate):

| `languages[].level` for English | Framing |
|---|---|
| Básico / Basic | Cautious: keep the EN script shorter/simpler, and note the level honestly in section 6's critical analysis rather than overselling it |
| Intermediário / Intermediate | "Conversational, comfortable with technical topics" — matches the B1-B2 vocabulary rule directly |
| Avançado / Advanced, Fluente / Fluent, Nativo / Native | Full script, no hedging needed |

Never invent a spoken-proficiency nuance that isn't derivable from the
profile's literal `level` (and `description`, if present) — if the profile
only has a CV-style tag, use only that tag to pick the row above.

## Honesty Rule (Critical Compatibility Analysis)

Never soften a gap. Every requirement that is `partial` or `absent` in the
job's gap table (see `rules/job-evaluation.md` and the job's
`metadata.json → gaps[]`) must appear in section 6 **using the same literal
skill term as `metadata.json`** (a natural-language paraphrase in Portuguese
is fine alongside it, but the literal term must also be present — e.g. write
"Microservices (arquitetura de microsserviços)", not just the Portuguese
translation on its own). This keeps the gap traceable/mechanically checkable
(see `scripts/check_roteiro.py`), the same way the CV's ATS check greps for
literal stack/gap keywords. Each gap needs:
1. An explicit risk level: baixo / médio / alto.
2. One concrete action (study X, be transparent about it in the interview,
   point to an adjacent skill that partially covers it).

If the job's contract type is PJ (`Modelo de contrato` on the job, or
inferred from the posting), add a reminder in the honest verdict paragraph:
calculate a minimum rate 40–60% above the CLT-equivalent salary, to account
for the candidate's own tax/benefits burden under PJ.

## Recruiter Questions Rule

Minimum 4 questions, each tailored to the specific job/company (never
generic filler), and at least one must clarify a real gap or ambiguity —
something genuinely unclear from the job posting or the fit analysis, not a
softball.

## "Verify-Before-Use" Rule (company facts)

Any claim about the company itself (culture, product, mission, tech
direction) used in the FUTURO/FUTURE section or in a recruiter question
must trace back to something actually fetched/researched in this session
(the job posting text, or a WebSearch of the company's site/LinkedIn) — never
a generic, unverified assumption ("I'm passionate about your mission"
without a specific, citable overlap). This mirrors Absolute Rule 1
(`rules/README.md`) applied to facts about the employer, not just the
candidate.

## Data-Sourcing Sub-Rules (never invent)

1. **Years of experience** (PRESENTE): use
   `professional_experience[0].duration_note` verbatim if present — it's
   already phrased to respect the "never round beyond 1 year" rule. If a
   candidate's profile has no `duration_note`, compute from `period`'s
   start/end, rounding down, never up.
2. **Motivation sentence** (FUTURO): never pre-written or stored — synthesize
   at generation time by cross-referencing
   `preferences.target_industries` / `preferences.target_roles` against
   something concretely true about this specific job/company (its stack,
   domain, or role scope). It must be a claim the candidate could defend if
   asked "why" — never a generic sentiment with no real overlap behind it.
3. **Most relevant project** (checklist item "ter X rodando localmente"):
   reuse `rules/cv-rules.md` → "Content Selection by Stack Overlap" verbatim
   — rank the job's stack against `professional_experience[].projects[]` and
   `personal_projects[]` by overlap, take the #1 result, respect
   `include_only_if` and the rule against inventing a repository link. This
   keeps the roteiro's featured project consistent with whatever
   `cv_draft.tex` itself already highlighted for that job.
