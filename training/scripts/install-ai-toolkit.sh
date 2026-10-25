#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
TOOLKIT_DIR="${AI_TOOLKIT_DIR:-$WORKSPACE/ai-toolkit}"
VENV_DIR="${AI_TOOLKIT_VENV:-$WORKSPACE/ai-toolkit-venv}"
TOOLKIT_COMMIT="73ebae13a468942ded8b47991b5d56eeeea25c36"
MIN_FREE_GIB="${MIN_FREE_GIB:-50}"

available_kib="$(df -Pk "$WORKSPACE" | awk 'NR==2 {print $4}')"
required_kib="$((MIN_FREE_GIB * 1024 * 1024))"
if (( available_kib < required_kib )); then
  available_gib="$((available_kib / 1024 / 1024))"
  echo "ERROR: only about ${available_gib} GiB is free on $WORKSPACE." >&2
  echo "FLUX.2 Klein 9B training needs at least ${MIN_FREE_GIB} GiB free for model components, the environment, caches, samples, and checkpoints." >&2
  exit 1
fi

if [[ ! -d "$TOOLKIT_DIR/.git" ]]; then
  git clone https://github.com/ostris/ai-toolkit.git "$TOOLKIT_DIR"
fi
git -C "$TOOLKIT_DIR" fetch --depth=1 origin "$TOOLKIT_COMMIT"
git -C "$TOOLKIT_DIR" checkout --detach "$TOOLKIT_COMMIT"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install --no-cache-dir \
  torch==2.13.0 torchvision==0.28.0 torchaudio==2.11.0 \
  --index-url https://download.pytorch.org/whl/cu130
"$VENV_DIR/bin/python" -m pip install -r "$TOOLKIT_DIR/requirements.txt"

mkdir -p "$WORKSPACE/huggingface" "$WORKSPACE/training/output" "$WORKSPACE/training/logs"

echo "AI Toolkit installed at $TOOLKIT_DIR ($TOOLKIT_COMMIT)."
echo "Training environment: $VENV_DIR"
