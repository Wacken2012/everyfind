#!/usr/bin/env bash
# Small wrapper to activate a venv (if present) and run the GUI helper script.
# Usage: ./scripts/run_gui.sh [venv-path] [--index /path] [--size 1280x720]

set -euo pipefail

VENV_DIR="${1:-.venv}"
shift || true

if [ -d "${VENV_DIR}" ] && [ -f "${VENV_DIR}/bin/activate" ]; then
  echo "Activating venv: ${VENV_DIR}"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
else
  echo "Warning: virtualenv not found at ${VENV_DIR}. Proceeding with system Python."
fi

python3 scripts/run_gui.py "$@"
