#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"

mkdir -p "$COMFY_DIR/user/default/workflows"
cp "$ROOT"/workflows/*.json "$COMFY_DIR/user/default/workflows/"

mkdir -p "$COMFY_DIR/input"
cp "$ROOT"/assets/persona_refs/*.png "$COMFY_DIR/input/"

mkdir -p "$COMFY_DIR/custom_nodes"
rm -rf "$COMFY_DIR/custom_nodes/as_inf_optional_reference"
mkdir -p "$COMFY_DIR/custom_nodes/as_inf_optional_reference"
cp "$ROOT/custom_nodes/as_inf_optional_reference/__init__.py" \
  "$COMFY_DIR/custom_nodes/as_inf_optional_reference/__init__.py"
cp "$ROOT/custom_nodes/as_inf_optional_reference/LICENSE.load-image-crop" \
  "$COMFY_DIR/custom_nodes/as_inf_optional_reference/LICENSE.load-image-crop"
mkdir -p "$COMFY_DIR/custom_nodes/as_inf_optional_reference/web/js"
cp "$ROOT/custom_nodes/as_inf_optional_reference/web/js/loadImageCrop3x4.js" \
  "$COMFY_DIR/custom_nodes/as_inf_optional_reference/web/js/loadImageCrop3x4.js"
# Remove the temporary compatibility image used before the optional loader was bundled.
rm -f "$COMFY_DIR/input/__NO_REFERENCE__.png"
install -m 755 "$ROOT/pod/start-ollama.sh" "$WORKSPACE/start-ollama.sh"
install -m 755 "$ROOT/pod/start-comfyui.sh" "$WORKSPACE/start-final-kurva-maker.sh"
install -m 755 "$ROOT/pod/recover-existing-volume.sh" "$WORKSPACE/recover-final-kurva-maker.sh"
install -m 755 "$ROOT/pod/verify-existing-volume.sh" "$WORKSPACE/verify-persistent-state.sh"

echo "Installed workflows and persistent runtime scripts under $WORKSPACE."
