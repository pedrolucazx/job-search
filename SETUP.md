# Setup do Workspace

## Dependências de Sistema
```bash
# LaTeX (texlive-latex-extra é obrigatório — o template usa titlesec, que não vem no recommended)
sudo apt install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra

# pdftotext (ATS check)
sudo apt install poppler-utils

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
pdflatex --version
pdftotext -v
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
