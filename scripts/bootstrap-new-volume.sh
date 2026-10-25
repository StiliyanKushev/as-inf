#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"
VENV_DIR="${VENV_DIR:-$WORKSPACE/comfyui-venv}"
LOCK="$ROOT/manifests/plugins.lock.tsv"
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends git git-lfs curl rsync zstd python3-venv

git -C "$ROOT" lfs install --local
git -C "$ROOT" lfs pull

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

mkdir -p "$COMFY_DIR/models/loras"
for name in \
  FLUX2_KLEIN_UNLOCKED_V2.safetensors \
  klein_instagramreality_v2.safetensors \
  HighDetail.safetensors \
  alexsparks.safetensors; do
  source_file="$ROOT/models/loras/$name"
  if [[ ! -s "$source_file" ]] || head -c 64 "$source_file" | grep -q 'git-lfs.github.com/spec'; then
    echo "Git LFS object is unavailable: $source_file" >&2
    exit 1
  fi
  cp -f "$source_file" "$COMFY_DIR/models/loras/$name"
done

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
echo "Base installation and LoRA restoration complete. Now run:"
echo "  /workspace/recover-final-kurva-maker.sh"
