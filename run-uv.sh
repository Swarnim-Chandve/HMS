#!/usr/bin/env bash
# Uses Astral "uv" to download Python 3.13 and create a venv — no pacman python313 package needed.
# Install uv once:  curl -LsSf https://astral.sh/uv/install.sh | sh
# Then add ~/.local/bin to PATH (or restart the shell) and run:  ./run-uv.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed." >&2
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  echo "Then open a new terminal or: export PATH=\"\$HOME/.local/bin:\$PATH\"" >&2
  exit 1
fi

if [[ ! -d .venv ]] || ! .venv/bin/python -c 'import sys; raise SystemExit(0 if sys.version_info < (3, 14) else 1)' 2>/dev/null; then
  echo "recreating .venv with Python 3.13 (via uv)..."
  rm -rf .venv
fi

if [[ ! -d .venv ]]; then
  # Downloads CPython 3.13 if needed (no system python313 package required)
  uv venv --python 3.13 .venv
fi

uv pip install -r requirements.txt --python .venv/bin/python
echo "starting server → http://127.0.0.1:8000/docs"
exec .venv/bin/python -m uvicorn app.main:app --reload
