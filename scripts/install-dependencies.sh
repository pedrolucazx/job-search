#!/usr/bin/env bash
# Installs the external dependencies required by the job-search pipeline.
# Safe to rerun: already-installed tools are skipped.

set -euo pipefail

has() {
  command -v "$1" >/dev/null 2>&1
}

run_as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@"
  elif has sudo; then
    sudo "$@"
  else
    echo "❌ This installation needs root access, but sudo is not available." >&2
    exit 1
  fi
}

repair_dpkg_state() {
  if ! has dpkg; then
    return
  fi

  # `dpkg --audit` can be empty even when apt reports an interrupted dpkg
  # transaction. `dpkg --configure -a` is idempotent, so run it as a
  # preflight whenever this installer is about to change apt packages.
  echo "Checking for interrupted dpkg configuration..."
  run_as_root dpkg --configure -a
}

install_apt_dependencies() {
  local packages=()

  if ! has pdflatex; then
    packages+=(
      texlive-latex-base
      texlive-latex-recommended
      texlive-latex-extra
      texlive-fonts-recommended
      texlive-fonts-extra
    )
  fi

  if ! has pdftotext || ! has pdfinfo; then
    packages+=(poppler-utils)
  fi

  if ! has jq; then
    packages+=(jq)
  fi

  if ! has bun && [ ! -x "${HOME}/.bun/bin/bun" ] && ! has curl; then
    packages+=(curl)
  fi

  if ! python3 -c "import yaml" >/dev/null 2>&1; then
    packages+=(python3-yaml)
  fi

  if [ "${#packages[@]}" -gt 0 ]; then
    repair_dpkg_state
    echo "Installing system packages with apt..."
    run_as_root apt-get update
    run_as_root apt-get install -y "${packages[@]}"
  else
    echo "✅ System packages already installed."
  fi
}

install_bun() {
  if has bun || [ -x "${HOME}/.bun/bin/bun" ]; then
    echo "✅ Bun already installed."
    return
  fi

  if ! has curl; then
    echo "❌ curl is required to install Bun." >&2
    exit 1
  fi

  echo "Installing Bun from the official installer..."
  curl -fsSL https://bun.sh/install | bash
}

main() {
  echo "Job Search dependency installer"
  echo

  if ! has python3; then
    echo "❌ Python 3 is required to bootstrap this installer." >&2
    exit 1
  fi

  if has apt-get; then
    install_apt_dependencies
  else
    echo "❌ Automatic system-package installation currently supports Debian/Ubuntu (apt) only." >&2
    echo "   Follow SETUP.md for manual installation on this operating system." >&2
    exit 1
  fi

  install_bun

  echo
  echo "✅ Dependency installation finished."
  echo "   Open a new terminal if the bun command is not available in your current shell."
}

main "$@"
