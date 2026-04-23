#!/usr/bin/env bash
# Use a real OS Python from /usr/bin (3.11–3.13). Python 3.14 is NOT supported yet:
# pydantic-core / PyO3 cannot build on 3.14. If pacman has no python3.13 package, use ./run-uv.sh
set -euo pipefail
cd "$(dirname "$0")"

pick_python() {
  local c
  for c in /usr/bin/python3.13 /usr/bin/python3.12 /usr/bin/python3.11 /usr/bin/python3.10; do
    if [[ -x "$c" ]] && "$c" -c 'import sys; raise SystemExit(0 if sys.version_info < (3, 14) else 1)' 2>/dev/null; then
      echo "$c"
      return 0
    fi
  done
  if [[ -x /usr/bin/python3 ]]; then
    if /usr/bin/python3 -c 'import sys; raise SystemExit(0 if sys.version_info < (3, 14) else 1)' 2>/dev/null; then
      echo /usr/bin/python3
      return 0
    fi
  fi
  return 1
}

if ! SYS_PY=$(pick_python); then
  echo "error: need Python 3.10–3.13 for this project (3.14 breaks pydantic-core/PyO3)." >&2
  echo "  Option A — download Python with uv:  ./run-uv.sh   (see script header for uv install)" >&2
  echo "  Option B — search repos:  pacman -Ss python | grep -E '3\\.12|3\\.13'" >&2
  echo "  Then: rm -rf .venv && ./run.sh" >&2
  exit 1
fi
echo "using: $SYS_PY ($($SYS_PY -c 'import sys; print(sys.version)'))"

# Broken venv (Cursor shim) or wrong Python major/minor → recreate
recreate=
if [[ -L .venv/bin/python ]]; then
  real=$(readlink -f .venv/bin/python 2>/dev/null || true)
  if echo "$real" | grep -qiE 'cursor|AppImage|electron'; then
    recreate=1
  fi
fi
if [[ -d .venv ]] && [[ -n "$recreate" ]]; then
  echo "removing broken .venv..."
  rm -rf .venv
fi
if [[ -d .venv ]]; then
  cur=$(
    .venv/bin/python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null || echo ""
  )
  if [[ "$cur" == "3.14" ]] || ! .venv/bin/python -c 'import sys; raise SystemExit(0 if sys.version_info < (3, 14) else 1)' 2>/dev/null; then
    echo "removing .venv (need Python <3.14, was $cur)..."
    rm -rf .venv
  fi
fi

if [[ ! -d .venv ]]; then
  echo "creating venv with: $SYS_PY"
  "$SYS_PY" -m venv .venv
fi

.venv/bin/python -m ensurepip --upgrade 2>/dev/null || true
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
exec .venv/bin/python -m uvicorn app.main:app --reload
