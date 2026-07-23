# Workspace Setup

## System Dependencies
```bash
# LaTeX (texlive-latex-extra is required — the template uses titlesec, which isn't in "recommended")
sudo apt install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra

# pdftotext + pdfinfo (ATS check and page count)
sudo apt install poppler-utils

# jq (compile-all.sh reads the metadata JSON fields with this)
sudo apt install jq

# Bun (LinkedIn CLI)
curl -fsSL https://bun.sh/install | bash
```

## Installing the LinkedIn CLI
```bash
cd .agents/skills/linkedin-search/cli
bun install
cd ../../../..
```

## Verification
```bash
python3 scripts/check_setup.py
```
Runs all checks at once (bun, pdflatex, pdftotext, pdfinfo, jq, PyYAML) and
tells you exactly what's missing. When run in an interactive terminal, it
offers to install all missing dependencies immediately.

To start the installer directly, without waiting for the prompt:
```bash
python3 scripts/check_setup.py --install
```

The underlying installer can also be run on its own:
```bash
./scripts/install-dependencies.sh
```

The automatic installer currently supports Debian/Ubuntu systems that use
`apt`. It only installs missing dependencies and is safe to run again. On a
different operating system, follow the manual commands in this document.

For diagnostics in scripts or CI, without an interactive question:
```bash
python3 scripts/check_setup.py --no-prompt
```

Manual verification, if you prefer:
```bash
pdflatex --version
pdftotext -v
pdfinfo -v
jq --version
bun --version
python3 -c "import yaml; print('pyyaml ok')"  # pip install pyyaml if missing
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -l "Brazil" --jobage 7 --limit 3 --format table
```

## Your Profile
```bash
cp profile/candidate.example.yaml profile/candidate.yaml
# fill in your real data (never invent what you don't know)
python3 scripts/validate_profile.py
```

## Daily Usage
1. Claude Code: `claude` → `/daily`
2. Pick jobs → `/apply-batch 1,2,3,8`
3. OpenCode: `/compile-today`
4. Claude Code: `/confirm 1,2,3` (registers in the tracker configured in `profile/candidate.yaml`)
