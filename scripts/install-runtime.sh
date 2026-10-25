#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"

mkdir -p "$COMFY_DIR/user/default/workflows"
cp "$ROOT"/workflows/*.json "$COMFY_DIR/user/default/workflows/"

# The built-in ImageCropV2 visual editor is a Nodes 2.0 component. Preserve
# all existing user settings while enabling the renderer it requires.
SETTINGS_FILE="$COMFY_DIR/user/default/comfy.settings.json"
python3 - "$SETTINGS_FILE" <<'PY'
import json
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
try:
    settings = json.loads(path.read_text()) if path.exists() else {}
except (OSError, json.JSONDecodeError):
    settings = {}
settings["Comfy.VueNodes.Enabled"] = True
temporary = path.with_suffix(path.suffix + ".tmp")
temporary.write_text(json.dumps(settings, indent=4) + "\n")
os.replace(temporary, path)
PY

mkdir -p "$COMFY_DIR/custom_nodes"
rm -rf "$COMFY_DIR/custom_nodes/as_inf_optional_reference"
mkdir -p "$COMFY_DIR/custom_nodes/as_inf_optional_reference"
cp "$ROOT/custom_nodes/as_inf_optional_reference/__init__.py" \
  "$COMFY_DIR/custom_nodes/as_inf_optional_reference/__init__.py"
# Remove the temporary compatibility image used before the optional loader was bundled.
rm -f "$COMFY_DIR/input/__NO_REFERENCE__.png"
install -m 755 "$ROOT/pod/start-ollama.sh" "$WORKSPACE/start-ollama.sh"
install -m 755 "$ROOT/pod/start-comfyui.sh" "$WORKSPACE/start-final-kurva-maker.sh"
install -m 755 "$ROOT/pod/recover-existing-volume.sh" "$WORKSPACE/recover-final-kurva-maker.sh"
install -m 755 "$ROOT/pod/verify-existing-volume.sh" "$WORKSPACE/verify-persistent-state.sh"

echo "Installed workflows and persistent runtime scripts under $WORKSPACE."
