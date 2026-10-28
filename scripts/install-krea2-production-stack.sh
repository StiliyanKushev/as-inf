#!/usr/bin/env bash
# Install the pinned Krea 2 production dependencies into an existing ComfyUI.
# Run this after bootstrap-new-volume.sh on a new RunPod volume.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"
VENV_DIR="${VENV_DIR:-$WORKSPACE/comfyui-venv}"
COMFY_REV="4845e7a3ffc48a6961f15824239e9042cc7d4ad1"

if [[ ! -d "$COMFY_DIR/.git" ]]; then
  echo "ComfyUI is missing at $COMFY_DIR; run scripts/bootstrap-new-volume.sh first." >&2
  exit 1
fi
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "ComfyUI virtual environment is missing at $VENV_DIR." >&2
  exit 1
fi

install_node() {
  local directory="$1" repository="$2" revision="$3"
  local target="$COMFY_DIR/custom_nodes/$directory"
  if [[ ! -d "$target/.git" ]]; then
    git clone "$repository" "$target"
  fi
  git -C "$target" fetch --depth=1 origin "$revision"
  git -C "$target" checkout --detach "$revision"
  if [[ -f "$target/requirements.txt" ]]; then
    "$VENV_DIR/bin/python" -m pip install -r "$target/requirements.txt"
  fi
}

download_and_check() {
  local url="$1" target="$2" expected="$3"
  mkdir -p "$(dirname "$target")"
  if [[ -s "$target" ]] && echo "$expected  $target" | sha256sum -c --status; then
    echo "Already verified: $(basename "$target")"
    return
  fi
  curl --fail --location --retry 5 --retry-all-errors --continue-at - \
    --output "$target" "$url"
  echo "$expected  $target" | sha256sum -c -
}

# This is the exact ComfyUI revision used for the measured Krea2 runs. The
# existing checkout remains recoverable through Git, and all model data stays
# in the network volume.
git -C "$COMFY_DIR" fetch --depth=1 origin "$COMFY_REV"
git -C "$COMFY_DIR" checkout --detach "$COMFY_REV"
"$VENV_DIR/bin/python" -m pip install -r "$COMFY_DIR/requirements.txt"

install_node comfyui-krea2edit \
  https://github.com/lbouaraba/comfyui-krea2edit.git \
  13ef60f20828949becada815d3cbc371eb5ccaab
install_node ComfyUI-Krea2-Edit-Carousel \
  https://github.com/Pixelailabs/ComfyUI-Krea2-Edit-Carousel.git \
  a5c3eff64e9740e9ffc38ba0b7775961fa618614
install_node ComfyUI-FameGridColorFinish \
  https://github.com/Elevenheights/ComfyUI-FameGridColorFinish.git \
  944c14e53fffee3e9e6dbedad36ab95b0e1629f7

# The workflow retains the established control panel, prompt compiler, and
# comparison UI. These plugins are already present after the base bootstrap;
# install their pinned revisions here as well so this script is idempotent.
install_node ComfyUI-QwenVL \
  https://github.com/1038lab/ComfyUI-QwenVL.git \
  1b67b443918801f571714bab636edc1845b7002a
install_node comfyui-ollama \
  https://github.com/stavsap/comfyui-ollama.git \
  6db7560576e5a59488708e6be13e07b5aba2432a
install_node rgthree-comfy \
  https://github.com/rgthree/rgthree-comfy.git \
  d7297b42f0fa78bec1c0411478f887423c249502

rsync -a --delete \
  "$ROOT/custom_nodes/as_inf_optional_reference/" \
  "$COMFY_DIR/custom_nodes/as_inf_optional_reference/"

download_and_check \
  'https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_fp8_scaled.safetensors' \
  "$COMFY_DIR/models/diffusion_models/krea2_turbo_fp8_scaled.safetensors" \
  'eb4dd8c612cfd10f64f25b057e6e6bbcb5737c94a7372177e456dbf7579502f1'
download_and_check \
  'https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors' \
  "$COMFY_DIR/models/text_encoders/qwen3vl_4b_fp8_scaled.safetensors" \
  '54bd5144df0bbc25dd6ccadfcb826b521445a1b06ae5a42570bdd2974ca87094'
download_and_check \
  'https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors' \
  "$COMFY_DIR/models/vae/qwen_image_vae.safetensors" \
  'a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f'
download_and_check \
  'https://huggingface.co/conradlocke/krea2-identity-edit/resolve/main/krea2_general_edit_v2.safetensors' \
  "$COMFY_DIR/models/loras/krea2_general_edit_v2.safetensors" \
  'fb5315477444c8df6dea2ad347a852bd90e97ab0f9109f4100a39714a7a09356'
download_and_check \
  'https://huggingface.co/darken144/krea2assets/resolve/main/famegrid_spicy.safetensors' \
  "$COMFY_DIR/models/loras/famegrid_spicy.safetensors" \
  '7b4a37a9b9ec3885bf39242f2d4f691f186d959cbaaa30b0630e4631767b425e'
download_and_check \
  'https://huggingface.co/RazzzHF/realism_engine_krea2/resolve/main/realism_engine_krea2_v3.1.safetensors' \
  "$COMFY_DIR/models/loras/realism_engine_krea2_v3.1.safetensors" \
  'a6712629445a2e91a616568e82befa8c8c7518e891a0f7c9918138634b5b54a5'

mkdir -p "$COMFY_DIR/user/default/workflows"
cp -f "$ROOT/workflows/final-kurva-maker-krea2.json" \
  "$COMFY_DIR/user/default/workflows/final-kurva-maker-krea2.json"

cat <<EOF
Krea 2 production stack is installed.
Restart ComfyUI, then open final-kurva-maker-krea2.json.
Native output: 1280 x 1600
Instagram copy: 1080 x 1350
EOF
