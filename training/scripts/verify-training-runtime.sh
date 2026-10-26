#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
REPO_DIR="${AS_INF_DIR:-$WORKSPACE/as-inf}"
TOOLKIT_DIR="${AI_TOOLKIT_DIR:-$WORKSPACE/ai-toolkit}"
VENV_DIR="${AI_TOOLKIT_VENV:-$WORKSPACE/ai-toolkit-venv}"
EXPECTED_COMMIT="73ebae13a468942ded8b47991b5d56eeeea25c36"

export HF_HOME="${HF_HOME:-$WORKSPACE/huggingface}"

"$REPO_DIR/training/scripts/validate-dataset.sh"
(cd "$REPO_DIR" && sha256sum -c training/dataset-manifest.sha256 >/dev/null)
echo "Dataset checksums OK."

actual_commit="$(git -C "$TOOLKIT_DIR" rev-parse HEAD)"
if [[ "$actual_commit" != "$EXPECTED_COMMIT" ]]; then
  echo "ERROR: AI Toolkit commit is $actual_commit, expected $EXPECTED_COMMIT" >&2
  exit 1
fi
echo "AI Toolkit commit OK: $actual_commit"

"$VENV_DIR/bin/python" - "$REPO_DIR/training/configs/vexa-person-klein9b-b200.yaml" <<'PY'
import sys
import accelerate
import bitsandbytes
import diffusers
import torch
import transformers
import yaml

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    cfg = yaml.safe_load(handle)
process = cfg["config"]["process"][0]
assert process["model"]["arch"] == "flux2_klein_9b"
assert process["model"]["name_or_path"] == "black-forest-labs/FLUX.2-klein-base-9B"
assert process["trigger_word"] == "vexa_person"
assert process["train"]["steps"] == 2000
assert torch.cuda.is_available()
gpu = torch.cuda.get_device_name(0)
if "B200" not in gpu:
    raise RuntimeError(f"Expected an NVIDIA B200, found {gpu}")
print(f"PyTorch {torch.__version__}; CUDA {torch.version.cuda}; GPU {gpu}")
print(f"diffusers {diffusers.__version__}; transformers {transformers.__version__}; accelerate {accelerate.__version__}")
print("Klein 9B training config OK.")
PY

if "$VENV_DIR/bin/hf" auth whoami >/dev/null 2>&1; then
  echo "Hugging Face authentication OK."
else
  echo "Hugging Face authentication pending."
fi

df -h "$WORKSPACE"
