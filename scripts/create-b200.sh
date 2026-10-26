#!/usr/bin/env bash
set -Eeuo pipefail

# Compatibility wrapper for older documentation and automation.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export GPU_ID="${GPU_ID:-NVIDIA B200}"
export POD_NAME="${POD_NAME:-final-kurva-maker-b200}"
exec "$SCRIPT_DIR/create-gpu-pod.sh" "$@"
