#!/usr/bin/env bash
set -Eeuo pipefail

RUNPODCTL_BIN="${RUNPODCTL_BIN:-runpodctl}"
NETWORK_VOLUME_ID="${NETWORK_VOLUME_ID:-3e71bw1e12}"
DATA_CENTER_ID="${DATA_CENTER_ID:-US-CA-2}"
POD_NAME="${POD_NAME:-final-kurva-maker-b200}"
GPU_ID="${GPU_ID:-NVIDIA B200}"
IMAGE="${IMAGE:-runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0}"

command -v "$RUNPODCTL_BIN" >/dev/null 2>&1 || {
  echo "runpodctl is required. Install it and configure your API key first." >&2
  exit 1
}

exec "$RUNPODCTL_BIN" pod create \
  --name "$POD_NAME" \
  --image "$IMAGE" \
  --gpu-id "$GPU_ID" \
  --gpu-count 1 \
  --container-disk-in-gb 20 \
  --ports '8188/http,22/tcp' \
  --network-volume-id "$NETWORK_VOLUME_ID" \
  --volume-mount-path /workspace \
  --data-center-ids "$DATA_CENTER_ID" \
  --cloud-type SECURE \
  --ssh
