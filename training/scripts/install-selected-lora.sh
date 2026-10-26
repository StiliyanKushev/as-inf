#!/usr/bin/env bash
set -Eeuo pipefail

if (( $# != 1 )); then
  echo "Usage: $0 /workspace/training/output/.../checkpoint.safetensors" >&2
  exit 2
fi

WORKSPACE="${WORKSPACE:-/workspace}"
SOURCE="$1"
DEST="$WORKSPACE/ComfyUI/models/loras/alexsparks.safetensors"

if [[ ! -s "$SOURCE" || "$SOURCE" != *.safetensors ]]; then
  echo "ERROR: checkpoint is not a non-empty .safetensors file: $SOURCE" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST")"
cp -f "$SOURCE" "$DEST"
sha256sum "$DEST"
echo "Installed selected checkpoint as $DEST"
echo "Refresh ComfyUI's model list, select alexsparks.safetensors, and use trigger: vexa_person"
