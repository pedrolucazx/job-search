# Setup do Workspace

## Dependências de Sistema
```bash
# LaTeX (texlive-latex-extra é obrigatório — o template usa titlesec, que não vem no recommended)
sudo apt install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra

# pdftotext + pdfinfo (ATS check e contagem de página)
sudo apt install poppler-utils

# jq (compile-all.sh lê os campos do metadata JSON com isso)
sudo apt install jq

# Bun (LinkedIn CLI)
curl -fsSL https://bun.sh/install | bash
```

## Instalação do LinkedIn CLI
```bash
cd .agents/skills/linkedin-search/cli
bun install
cd ../../../..
```

## Verificação
```bash
python3 scripts/check_setup.py
```
Roda todas as checagens de uma vez (bun, pdflatex, pdftotext, pdfinfo, jq,
PyYAML) e diz exatamente o que falta instalar. Verificação manual, se
preferir:
```bash
pdflatex --version
pdftotext -v
pdfinfo -v
jq --version
bun --version
python3 -c "import yaml; print('pyyaml ok')"  # pip install pyyaml se faltar
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -l "Brazil" --jobage 7 --limit 3 --format table
```

## Seu Profile
```bash
cp profile/candidate.example.yaml profile/candidate.yaml
# preencha com seus dados reais (nunca invente o que não sabe)
python3 scripts/validate_profile.py
```

## Uso Diário
1. Claude Code: `claude` → `/daily`
2. Escolher vagas → `/apply-batch 1,2,3,8`
3. OpenCode: `/compile-today`
4. Claude Code: `/confirm 1,2,3` (registra no tracker configurado em `profile/candidate.yaml`)
