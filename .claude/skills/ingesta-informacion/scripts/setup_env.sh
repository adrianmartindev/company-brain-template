#!/usr/bin/env bash
# Crea (una sola vez) el entorno Python con el conversor de PDF y devuelve la ruta del interprete.
# pymupdf4llm se fija a 0.2.9: la version 2.0 publicada en PyPI es un paquete vacio sin modulo.
set -euo pipefail
VENV="${INGESTA_VENV:-$HOME/.cache/ingesta-informacion/venv}"
if ! "$VENV/bin/python" -c "import pymupdf4llm, pymupdf" >/dev/null 2>&1; then
  mkdir -p "$(dirname "$VENV")"
  uv venv -q "$VENV"
  uv pip install -q --link-mode=copy --python "$VENV/bin/python" "pymupdf4llm==0.2.9"
fi
echo "$VENV/bin/python"
