#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
REPO_DIR="${AS_INF_DIR:-$WORKSPACE/as-inf}"
TOOLKIT_DIR="${AI_TOOLKIT_DIR:-$WORKSPACE/ai-toolkit}"
VENV_DIR="${AI_TOOLKIT_VENV:-$WORKSPACE/ai-toolkit-venv}"
CONFIG="${KREA2_TRAIN_CONFIG:-$REPO_DIR/training/configs/alexsparks-krea2-b200.yaml}"
LOG_DIR="$WORKSPACE/training/logs"
DATASET="$WORKSPACE/training/datasets/alexsparks_krea2"
RAW_MODEL="$WORKSPACE/ComfyUI/models/diffusion_models/krea2_raw_bf16.safetensors"
RAW_SHA256="f99bb0ff8e362b77342bc4994e0c50906fe7ef7074864b181b7d48d2fa6d03d7"

export HF_HOME="${HF_HOME:-$WORKSPACE/huggingface}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-$HF_HOME/hub}"
export PYTHONUNBUFFERED=1

"$REPO_DIR/training/scripts/prepare-alexsparks-krea2-dataset.sh"

if [[ ! -x "$VENV_DIR/bin/python" || ! -f "$TOOLKIT_DIR/run.py" ]]; then
  echo "ERROR: persistent AI Toolkit environment is missing." >&2
  exit 1
fi
if [[ -z "${HF_TOKEN:-}" && ! -s "$HF_HOME/token" && ! -s "$HOME/.cache/huggingface/token" ]]; then
  echo "ERROR: Hugging Face authentication is missing." >&2
  exit 1
fi

if [[ ! -s "$RAW_MODEL" ]] || ! echo "$RAW_SHA256  $RAW_MODEL" | sha256sum -c --status; then
  mkdir -p "$(dirname "$RAW_MODEL")"
  echo "Downloading the public Krea2 Raw BF16 training checkpoint..."
  curl --fail --location --retry 5 --retry-all-errors --continue-at - \
    --output "$RAW_MODEL" \
    'https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_raw_bf16.safetensors'
  echo "$RAW_SHA256  $RAW_MODEL" | sha256sum -c -
fi

"$VENV_DIR/bin/python" - "$CONFIG" <<'PY'
import sys, torch, yaml
with open(sys.argv[1], encoding="utf-8") as f:
    cfg = yaml.safe_load(f)["config"]["process"][0]
assert cfg["model"]["arch"] == "krea2"
assert cfg["model"]["name_or_path"].endswith("krea2_raw_bf16.safetensors")
assert cfg["model"]["quantize"] is False
assert cfg["model"]["low_vram"] is False
assert cfg["network"]["linear"] == cfg["network"]["linear_alpha"] == 32
assert cfg["trigger_word"] == "alexsparks"
assert torch.cuda.is_available()
memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
if memory < 75:
    raise RuntimeError(f"Full-BF16 Krea2 training requires at least 75 GB VRAM; found {memory:.1f} GB")
print(f"Training on {torch.cuda.get_device_name(0)} with {memory:.1f} GB VRAM")
PY

mkdir -p "$LOG_DIR" "$WORKSPACE/training/output"
log="$LOG_DIR/alexsparks-krea2-$(date -u +%Y%m%dT%H%M%SZ).log"

echo "Starting Krea2 Raw Alex Sparks LoRA training. Log: $log"
cd "$TOOLKIT_DIR"
"$VENV_DIR/bin/python" run.py "$CONFIG" 2>&1 | tee "$log"
