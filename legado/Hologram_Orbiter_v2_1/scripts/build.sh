#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(cd "$project_dir/.." && pwd)"

cd "$workspace_dir"
blender -b --python "$project_dir/CAD/generate.py" -- --output-dir "$project_dir/exports"
python3 "$project_dir/scripts/validate_stl.py" \
  "$project_dir/exports/stl" \
  --output "$project_dir/reports/stl_validation.json"
