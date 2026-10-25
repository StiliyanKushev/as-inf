#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
REPO_DIR="${AS_INF_DIR:-$WORKSPACE/as-inf}"
TOOLKIT_DIR="${AI_TOOLKIT_DIR:-$WORKSPACE/ai-toolkit}"
VENV_DIR="${AI_TOOLKIT_VENV:-$WORKSPACE/ai-toolkit-venv}"
CONFIG="$REPO_DIR/training/configs/vexa-person-klein9b-b200.yaml"
LOG_DIR="$WORKSPACE/training/logs"

export HF_HOME="${HF_HOME:-$WORKSPACE/huggingface}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-$HF_HOME/hub}"
export PYTHONUNBUFFERED=1

"$REPO_DIR/training/scripts/validate-dataset.sh"

if [[ ! -x "$VENV_DIR/bin/python" || ! -f "$TOOLKIT_DIR/run.py" ]]; then
  echo "ERROR: AI Toolkit is not installed. Run training/scripts/install-ai-toolkit.sh first." >&2
  exit 1
fi

if [[ -z "${HF_TOKEN:-}" && ! -f "$HF_HOME/token" && ! -f "$HOME/.cache/huggingface/token" ]]; then
  echo "ERROR: Hugging Face authentication is missing." >&2
  echo "Accept the FLUX.2 Klein 9B Base license, then set the RunPod secret HF_TOKEN or log in with: hf auth login" >&2
  exit 1
fi

mkdir -p "$LOG_DIR" "$WORKSPACE/training/output"
log="$LOG_DIR/vexa-person-klein9b-$(date -u +%Y%m%dT%H%M%SZ).log"

echo "Starting FLUX.2 Klein 9B persona LoRA training. Log: $log"
cd "$TOOLKIT_DIR"
"$VENV_DIR/bin/python" run.py "$CONFIG" 2>&1 | tee "$log"
