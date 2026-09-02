#!/usr/bin/env bash
# Regenera todo o pacote v3.0: STL, .blend, prévia, relatórios e referência de corte.
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
blender_bin="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
if ! [ -x "$blender_bin" ]; then
  blender_bin="$(command -v blender || true)"
fi
if [ -z "$blender_bin" ]; then
  echo "Blender 5.x não encontrado. Instale com: brew install --cask blender" >&2
  exit 1
fi

cd "$project_dir"
"$blender_bin" -b --python "$project_dir/CAD/generate.py" -- --output-dir "$project_dir/exports" "$@"
python3 "$project_dir/scripts/validate_stl.py" "$project_dir/exports/stl" --output "$project_dir/reports/stl_validation.json"
python3 "$project_dir/scripts/plate_cut_reference.py"
"$blender_bin" -b --python "$project_dir/scripts/render_views.py" -- --output-dir "$project_dir/exports/preview"
