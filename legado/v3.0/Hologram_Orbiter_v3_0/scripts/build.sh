#!/usr/bin/env bash
# Regenera e valida em staging; publica os artefatos somente após o aceite.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$script_dir/build.py" "$@"
