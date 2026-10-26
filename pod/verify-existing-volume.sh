#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="$WORKSPACE/ComfyUI"

required=(
  "$COMFY_DIR/main.py"
  "$COMFY_DIR/user/default/workflows/final-kurva-maker-reference-spatial-face-lora.json"
  "$COMFY_DIR/user/default/workflows/final-kurva-maker-reference.json"
  "$COMFY_DIR/user/default/workflows/final-kurva-maker.json"
  "$COMFY_DIR/models/diffusion_models/flux-2-klein-9b.safetensors"
  "$COMFY_DIR/models/text_encoders/qwen_3_8b_fp4mixed.safetensors"
  "$COMFY_DIR/models/vae/flux2-vae.safetensors"
  "$COMFY_DIR/models/loras/FLUX2_KLEIN_UNLOCKED_V2.safetensors"
  "$COMFY_DIR/models/loras/klein_instagramreality_v2.safetensors"
  "$COMFY_DIR/models/loras/HighDetail.safetensors"
  "$COMFY_DIR/models/loras/alexsparks.safetensors"
  "$COMFY_DIR/models/LLM/Qwen/Qwen3-VL-8B-Instruct/config.json"
  "$COMFY_DIR/custom_nodes/ComfyUI-QwenVL"
  "$COMFY_DIR/custom_nodes/comfyui-ollama"
  "$COMFY_DIR/custom_nodes/RES4LYF"
  "$COMFY_DIR/custom_nodes/ComfyUI-Angelo"
  "$COMFY_DIR/custom_nodes/as_inf_optional_reference/__init__.py"
  "$WORKSPACE/ollama/models"
  "$WORKSPACE/comfyui-venv/bin/python"
)

failed=0
for path in "${required[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "MISSING  $path"
    failed=1
  fi
done
(( failed == 0 )) || exit 1

python3 - "$COMFY_DIR/user/default/workflows" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
files = sorted(root.glob('*.json'))
for path in files:
    json.loads(path.read_text())
print(f"Validated {len(files)} workflow JSON files.")
PY

expected_alexsparks=165704328
actual_alexsparks="$(stat -c %s "$COMFY_DIR/models/loras/alexsparks.safetensors")"
[[ "$actual_alexsparks" == "$expected_alexsparks" ]] || {
  echo "ERROR: alexsparks.safetensors has unexpected size $actual_alexsparks" >&2
  exit 1
}

expected_alexsparks_sha256=072f0184a52cc00de330e7f863951d44120a2412a9369d8ba0c76118d2e345ad
actual_alexsparks_sha256="$(sha256sum "$COMFY_DIR/models/loras/alexsparks.safetensors" | cut -d' ' -f1)"
[[ "$actual_alexsparks_sha256" == "$expected_alexsparks_sha256" ]] || {
  echo "ERROR: alexsparks.safetensors checksum mismatch" >&2
  exit 1
}

"$WORKSPACE/comfyui-venv/bin/python" -c 'import torch, aiohttp, safetensors; print("Python environment OK; torch", torch.__version__)'
echo "Persistent state OK."
du -sh "$COMFY_DIR" "$WORKSPACE/comfyui-venv" "$WORKSPACE/ollama"
