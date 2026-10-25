#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"
VENV_DIR="${VENV_DIR:-$WORKSPACE/comfyui-venv}"
LOCK="$ROOT/manifests/plugins.lock.tsv"
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends git curl rsync zstd python3-venv

read -r _ comfy_repo comfy_commit < <(awk -F '\t' '$1=="ComfyUI" {print $1, $2, $3}' "$LOCK")
if [[ ! -d "$COMFY_DIR/.git" ]]; then
  git clone "$comfy_repo" "$COMFY_DIR"
fi
git -C "$COMFY_DIR" fetch --depth=1 origin "$comfy_commit"
git -C "$COMFY_DIR" checkout --detach "$comfy_commit"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv --system-site-packages "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -r "$COMFY_DIR/requirements.txt"

tail -n +3 "$LOCK" | while IFS=$'\t' read -r directory repository commit; do
  target="$COMFY_DIR/custom_nodes/$directory"
  if [[ ! -d "$target/.git" ]]; then
    git clone "$repository" "$target"
  fi
  git -C "$target" fetch --depth=1 origin "$commit"
  git -C "$target" checkout --detach "$commit"
  if [[ -f "$target/requirements.txt" ]]; then
    "$VENV_DIR/bin/python" -m pip install -r "$target/requirements.txt"
  fi
done

"$ROOT/scripts/install-runtime.sh"
"$ROOT/scripts/download-public-models.sh"

qwen_dir="$COMFY_DIR/models/LLM/Qwen/Qwen3-VL-8B-Instruct"
if [[ ! -f "$qwen_dir/config.json" ]]; then
  "$VENV_DIR/bin/python" - "$qwen_dir" <<'PY'
import sys
from huggingface_hub import snapshot_download
snapshot_download(repo_id="Qwen/Qwen3-VL-8B-Instruct", local_dir=sys.argv[1])
PY
fi

"$WORKSPACE/start-ollama.sh"
export OLLAMA_MODELS="$WORKSPACE/ollama/models"
ollama pull '0xIbra/supergemma4-26b-uncensored-gguf-v2:Q4_K_M'

echo
echo "Base installation complete. Upload the four LoRAs listed in"
echo "manifests/model-sha256.txt, then run:"
echo "  /workspace/recover-final-kurva-maker.sh"
