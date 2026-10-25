#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"

download_and_check() {
  local url="$1" target="$2" expected="$3"
  mkdir -p "$(dirname "$target")"
  if [[ -f "$target" ]] && echo "$expected  $target" | sha256sum -c --status; then
    echo "Already verified: $(basename "$target")"
    return
  fi
  curl --fail --location --retry 5 --retry-all-errors --continue-at - \
    --output "$target" "$url"
  echo "$expected  $target" | sha256sum -c -
}

download_and_check \
  'https://huggingface.co/maksimkagams582/flux/resolve/main/flux-2-klein-9b.safetensors' \
  "$COMFY_DIR/models/diffusion_models/flux-2-klein-9b.safetensors" \
  '0975d6b77b5f510b99547d6724a208e36527df654e8f6134f59ece3f9f30da58'

download_and_check \
  'https://huggingface.co/Comfy-Org/Flux-2-Klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp4mixed.safetensors' \
  "$COMFY_DIR/models/text_encoders/qwen_3_8b_fp4mixed.safetensors" \
  'bbf16f981d98e16d080c566134814c4e9f6aadd0d0e1383c60bc44ba939d760d'

download_and_check \
  'https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors' \
  "$COMFY_DIR/models/vae/flux2-vae.safetensors" \
  'd64f3a68e1cc4f9f4e29b6e0da38a0204fe9a49f2d4053f0ec1fa1ca02f9c4b5'
