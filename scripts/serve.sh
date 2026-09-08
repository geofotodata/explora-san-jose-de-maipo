#!/usr/bin/env sh
set -eu

PORT="${1:-8080}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "No se encontró python3. Instálalo o usa GitHub Codespaces." >&2
  exit 1
fi

echo "Servidor disponible en http://localhost:${PORT}"
python3 -m http.server "$PORT"
