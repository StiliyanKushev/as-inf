#!/usr/bin/env bash
set -Eeuo pipefail

if (( $# < 2 || $# > 4 )); then
  echo "Usage: $0 root@POD_IP SSH_PORT [LOCAL_LORA_DIR] [SSH_PRIVATE_KEY]" >&2
  exit 2
fi

SSH_HOST="$1"
SSH_PORT="$2"
LORA_DIR="${3:-$PWD}"
SSH_KEY="${4:-${RUNPOD_SSH_KEY:-$HOME/.runpod/ssh/runpodctl-ssh-key}}"
names=(
  FLUX2_KLEIN_UNLOCKED_V2.safetensors
  klein_instagramreality_v2.safetensors
  HighDetail.safetensors
  alexsparks.safetensors
)

for name in "${names[@]}"; do
  [[ -f "$LORA_DIR/$name" ]] || {
    echo "Missing $LORA_DIR/$name" >&2
    exit 1
  }
done

ssh -i "$SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new \
  -p "$SSH_PORT" "$SSH_HOST" 'mkdir -p /workspace/ComfyUI/models/loras'

for name in "${names[@]}"; do
  rsync -a --no-owner --no-group --partial --append-verify --info=progress2 \
    -e "ssh -i $SSH_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -p $SSH_PORT" \
    "$LORA_DIR/$name" "$SSH_HOST:/workspace/ComfyUI/models/loras/$name"
done
