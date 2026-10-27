#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI-flux3}"
SHARED_MODELS_DIR="${SHARED_MODELS_DIR:-$WORKSPACE/ComfyUI/models}"
HF_HOME="${HF_HOME:-$WORKSPACE/huggingface}"
COMFY_REPOSITORY="${COMFY_REPOSITORY:-https://github.com/Comfy-Org/ComfyUI.git}"
COMFY_COMMIT="${COMFY_COMMIT:-426f5eea52a7ece1dd599fff4cb6cd1f352ddd24}"
MODEL_REPOSITORY="black-forest-labs/flux-3-image-klein-comfy"

export HF_HOME

command -v git >/dev/null
command -v hf >/dev/null

if ! HF_HOME="$HF_HOME" hf auth whoami >/dev/null 2>&1; then
  echo "No Hugging Face login was found under HF_HOME=$HF_HOME." >&2
  echo "Log in with a read token, then accept the FLUX 3 Image Klein license:" >&2
  echo "https://huggingface.co/black-forest-labs/flux-3-image-klein-comfy" >&2
  exit 1
fi

if [[ ! -d "$COMFY_DIR/.git" ]]; then
  git clone "$COMFY_REPOSITORY" "$COMFY_DIR"
fi
git -C "$COMFY_DIR" fetch --depth=1 origin "$COMFY_COMMIT"
git -C "$COMFY_DIR" checkout --detach "$COMFY_COMMIT"

mkdir -p \
  "$SHARED_MODELS_DIR/diffusion_models" \
  "$SHARED_MODELS_DIR/text_encoders" \
  "$SHARED_MODELS_DIR/vae" \
  "$COMFY_DIR/user/default/workflows" \
  "$COMFY_DIR/input" \
  "$COMFY_DIR/output"

download_model() {
  local remote_path="$1"
  local destination_dir="$2"
  local filename="${remote_path##*/}"

  if [[ -s "$destination_dir/$filename" ]]; then
    echo "Already present: $destination_dir/$filename"
    return
  fi

  HF_HOME="$HF_HOME" hf download "$MODEL_REPOSITORY" "$remote_path" \
    --local-dir "$WORKSPACE/flux3-model-download"
  mv "$WORKSPACE/flux3-model-download/$remote_path" "$destination_dir/$filename"
  chmod 0644 "$destination_dir/$filename"
}

# Quality-first BF16 image model and encoder. The official BF16 prompt
# upsampler is preferred; W4A8 can be substituted through PUP_FILE when disk or
# memory is constrained.
PUP_FILE="${PUP_FILE:-text_encoders/qwen3.5_9b_flux3_prompt_upsampler_bf16.safetensors}"

download_model \
  "diffusion_models/flux3-image-klein-bf16.safetensors" \
  "$SHARED_MODELS_DIR/diffusion_models"
download_model \
  "diffusion_models/flux3-image-klein-base-bf16.safetensors" \
  "$SHARED_MODELS_DIR/diffusion_models"
download_model \
  "text_encoders/qwen3vl_4b_bf16.safetensors" \
  "$SHARED_MODELS_DIR/text_encoders"
download_model "$PUP_FILE" "$SHARED_MODELS_DIR/text_encoders"

# FLUX 3 uses the same autoencoder file already used by the FLUX.2 runtime.
if [[ ! -s "$SHARED_MODELS_DIR/vae/flux2-vae.safetensors" ]]; then
  download_model "vae/flux2-vae.safetensors" "$SHARED_MODELS_DIR/vae"
fi

cat >"$COMFY_DIR/extra_model_paths.yaml" <<YAML
as_inf_shared:
  base_path: $SHARED_MODELS_DIR
  diffusion_models: diffusion_models
  text_encoders: text_encoders
  vae: vae
  loras: loras
  upscale_models: upscale_models
YAML

cp "$ROOT/workflows/research-flux3-native-4k.json" \
  "$COMFY_DIR/user/default/workflows/" 2>/dev/null || true

echo "FLUX 3 research assets are installed under $WORKSPACE."
