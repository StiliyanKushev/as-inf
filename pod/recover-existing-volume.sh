#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="$WORKSPACE/ComfyUI"
VENV_DIR="$WORKSPACE/comfyui-venv"

if ! findmnt -T "$WORKSPACE" >/dev/null 2>&1; then
  echo "ERROR: $WORKSPACE is not mounted. Attach the RunPod network volume at /workspace." >&2
  exit 1
fi

for required in \
  "$COMFY_DIR/main.py" \
  "$COMFY_DIR/user/default/workflows/final-kurva-maker-reference-spatial-face-lora.json" \
  "$COMFY_DIR/user/default/workflows/final-kurva-maker-reference.json" \
  "$COMFY_DIR/models/diffusion_models/flux-2-klein-9b.safetensors" \
  "$COMFY_DIR/models/text_encoders/qwen_3_8b_fp4mixed.safetensors" \
  "$COMFY_DIR/models/vae/flux2-vae.safetensors" \
  "$COMFY_DIR/models/loras/alexsparks.safetensors" \
  "$VENV_DIR/bin/python" \
  "$WORKSPACE/start-ollama.sh" \
  "$WORKSPACE/start-final-kurva-maker.sh"
do
  if [[ ! -e "$required" ]]; then
    echo "ERROR: persistent asset is missing: $required" >&2
    exit 1
  fi
done

if ! "$VENV_DIR/bin/python" -c 'import torch, aiohttp, safetensors' >/dev/null 2>&1; then
  echo "ERROR: the persistent Python environment is incompatible with this image." >&2
  echo "Use runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0, or rebuild from the saved pip-freeze.txt." >&2
  exit 1
fi

chmod +x "$WORKSPACE/start-ollama.sh" "$WORKSPACE/start-final-kurva-maker.sh"
"$WORKSPACE/start-final-kurva-maker.sh"

for _ in {1..120}; do
  if curl -fsS http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
    echo "ComfyUI is ready on port 8188."
    echo "Open https://${RUNPOD_POD_ID:-POD_ID}-8188.proxy.runpod.net"
    exit 0
  fi
  sleep 1
done

echo "ERROR: ComfyUI did not become ready. See $WORKSPACE/comfyui.log" >&2
tail -n 100 "$WORKSPACE/comfyui.log" >&2 || true
exit 1
