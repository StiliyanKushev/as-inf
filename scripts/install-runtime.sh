#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"

mkdir -p "$COMFY_DIR/user/default/workflows"
cp "$ROOT"/workflows/*.json "$COMFY_DIR/user/default/workflows/"
python3 "$ROOT/scripts/create-placeholder-reference.py" \
  "$COMFY_DIR/input/__NO_REFERENCE__.png"
install -m 755 "$ROOT/pod/start-ollama.sh" "$WORKSPACE/start-ollama.sh"
install -m 755 "$ROOT/pod/start-comfyui.sh" "$WORKSPACE/start-final-kurva-maker.sh"
install -m 755 "$ROOT/pod/recover-existing-volume.sh" "$WORKSPACE/recover-final-kurva-maker.sh"
install -m 755 "$ROOT/pod/verify-existing-volume.sh" "$WORKSPACE/verify-persistent-state.sh"

echo "Installed workflows and persistent runtime scripts under $WORKSPACE."
