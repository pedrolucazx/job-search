#!/bin/bash
# compile-all.sh — Compila todos os .tex do dia em lote (mecânico, sem julgamento)
# Uso: ./scripts/compile-all.sh [data]
# Se data for omitida, usa a data atual
# Lê o campo "cv_tex" de cada daily/<data>/<empresa>.json — não adivinha o nome do arquivo.
# ATS check é feito aqui via grep (mecânico, sem gastar token de LLM): confirma
# email/telefone literais, cobertura de keyword de stack/gaps full+partial, e
# ausência de keyword de gaps absent (sinal de dado inventado no CV). O texto
# extraído é apagado no final — só o resultado PASS/FAIL importa pra quem chama.

set -euo pipefail

DATA_DIR="${1:-$(date +%Y-%m-%d)}"
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CV_DIR="$BASE_DIR/documents/cv"

# Email/telefone vêm do profile ativo, nunca hardcoded aqui (ver profile/idea.md)
EMAIL="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.email)"
PHONE="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.phone)"
DAILY_DIR="$BASE_DIR/daily/$DATA_DIR"
COMPILED=0
ERRORS=0

echo "╔══════════════════════════════════════════╗"
echo "║     Compilação em Lote — $DATA_DIR"
echo "╚══════════════════════════════════════════╝"

if [ ! -d "$DAILY_DIR" ]; then
  echo "❌ Nenhum metadado encontrado para $DATA_DIR"
  exit 1
fi

for json_file in "$DAILY_DIR"/*.json; do
  [ -f "$json_file" ] || continue

  empresa=$(basename "$json_file" .json)
  tex_rel=$(jq -r '.cv_tex' "$json_file")
  tex_file="$BASE_DIR/$tex_rel"
  pdf_file="${tex_file%.tex}.pdf"

  if [ ! -f "$tex_file" ]; then
    echo "⚠  $empresa — .tex não encontrado em $tex_rel (cv_tex do JSON)"
    continue
  fi

  echo ""
  echo "── $empresa ──"

  # Compilar
  if pdflatex -interaction=nonstopmode -output-directory="$CV_DIR" "$tex_file" > /tmp/latex_log.txt 2>&1; then
    echo "  ✅ PDF gerado: ${pdf_file}"

    # Verificar número de páginas
    PAGES=$(pdfinfo "$pdf_file" 2>/dev/null | grep Pages | awk '{print $2}')
    if [ "$PAGES" = "1" ]; then
      echo "  ✅ Páginas: $PAGES (1 = OK)"
    else
      echo "  ⚠  Páginas: $PAGES (esperado: 1)"
    fi

    # ATS check mecânico via grep — não deixa .txt pra trás, só o veredito
    if command -v pdftotext &> /dev/null; then
      txt_file="$CV_DIR/${empresa}_ats.txt"
      pdftotext -layout "$pdf_file" "$txt_file" 2>/dev/null

      ATS_FAILS=()
      grep -qF "$EMAIL" "$txt_file" || ATS_FAILS+=("email ausente/não-literal")
      grep -qF "$PHONE" "$txt_file" || ATS_FAILS+=("telefone ausente/não-literal")

      while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        grep -qi -- "$skill" "$txt_file" || ATS_FAILS+=("stack ausente: $skill")
      done < <(jq -r '.stack[]?' "$json_file")

      while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        grep -qi -- "$skill" "$txt_file" || ATS_FAILS+=("gap full/partial ausente: $skill")
      done < <(jq -r '.gaps[]? | select(.status != "absent") | .skill' "$json_file")

      while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        grep -qi -- "$skill" "$txt_file" && ATS_FAILS+=("gap absent APARECE no CV (dado inventado?): $skill")
      done < <(jq -r '.gaps[]? | select(.status == "absent") | .skill' "$json_file")

      rm -f "$txt_file"

      if [ ${#ATS_FAILS[@]} -eq 0 ]; then
        echo "  ✅ ATS check OK (email, telefone, stack e gaps conferidos)"
      else
        echo "  ⚠  ATS check com pendências:"
        printf '     - %s\n' "${ATS_FAILS[@]}"
      fi
    else
      echo "  ⚠  pdftotext não instalado — pulando ATS check"
    fi

    COMPILED=$((COMPILED + 1))
  else
    echo "  ❌ ERRO de compilação"
    head -20 /tmp/latex_log.txt | tail -10
    ERRORS=$((ERRORS + 1))
  fi

  # Limpar artifacts de build (não o _ats.txt, esse fica)
  rm -f "$CV_DIR/$(basename "${tex_file%.tex}").aux" "$CV_DIR/$(basename "${tex_file%.tex}").log" "$CV_DIR/$(basename "${tex_file%.tex}").out"
done

echo ""
echo "══════════════════════════════════════════"
echo "  Compilados: $COMPILED | Erros: $ERRORS"
echo "══════════════════════════════════════════"
