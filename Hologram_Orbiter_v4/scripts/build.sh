#!/usr/bin/env bash
# Regenera e valida em staging; publica os artefatos somente após o aceite.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "${PYTHON:-}" ]; then
  py="$PYTHON"
elif python3 -c "import numpy" >/dev/null 2>&1; then
  py="python3"
elif command -v python3.14 >/dev/null 2>&1 && python3.14 -c "import numpy" >/dev/null 2>&1; then
  py="$(command -v python3.14)"
elif [ -x /opt/homebrew/bin/python3.14 ]; then
  py="/opt/homebrew/bin/python3.14"
else
  py="python3"
fi
exec "$py" "$script_dir/build.py" "$@"
