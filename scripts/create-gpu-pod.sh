#!/usr/bin/env bash
set -Eeuo pipefail

RUNPODCTL_BIN="${RUNPODCTL_BIN:-runpodctl}"
NETWORK_VOLUME_ID="${NETWORK_VOLUME_ID:-3e71bw1e12}"
DATA_CENTER_ID="${DATA_CENTER_ID:-US-CA-2}"
GPU_ID="${GPU_ID:-NVIDIA H100 80GB HBM3}"
GPU_COUNT="${GPU_COUNT:-1}"
POD_NAME="${POD_NAME:-final-kurva-maker-gpu}"
IMAGE="${IMAGE:-runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0}"
CONTAINER_DISK_GB="${CONTAINER_DISK_GB:-20}"
VOLUME_MOUNT_PATH="${VOLUME_MOUNT_PATH:-/workspace}"
PORTS="${PORTS:-8188/http,22/tcp}"
CLOUD_TYPE="${CLOUD_TYPE:-SECURE}"

usage() {
  cat <<'EOF'
Create a RunPod GPU pod attached to the persistent AS-INF network volume.

Usage:
  ./scripts/create-gpu-pod.sh

Configuration is supplied through environment variables. Common examples:

  GPU_ID='NVIDIA H100 80GB HBM3' \
  POD_NAME='final-kurva-maker-h100' \
    ./scripts/create-gpu-pod.sh

  GPU_ID='NVIDIA B200' \
  POD_NAME='final-kurva-maker-b200' \
    ./scripts/create-gpu-pod.sh

Variables:
  GPU_ID                RunPod GPU identifier (default: NVIDIA H100 80GB HBM3)
  GPU_COUNT             Number of GPUs (default: 1)
  POD_NAME              Pod name (default: final-kurva-maker-gpu)
  NETWORK_VOLUME_ID     Persistent volume ID (default: 3e71bw1e12)
  DATA_CENTER_ID        Volume data center (default: US-CA-2)
  IMAGE                 Container image
  CONTAINER_DISK_GB     Ephemeral container disk size (default: 20)
  VOLUME_MOUNT_PATH     Network-volume mount (default: /workspace)
  PORTS                 Published ports (default: 8188/http,22/tcp)
  CLOUD_TYPE            SECURE or COMMUNITY (default: SECURE)
  RUNPODCTL_BIN         runpodctl executable (default: runpodctl)
EOF
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  "") ;;
  *)
    echo "Unknown argument: $1" >&2
    usage >&2
    exit 2
    ;;
esac

command -v "$RUNPODCTL_BIN" >/dev/null 2>&1 || {
  echo "runpodctl is required. Install it and configure your API key first." >&2
  exit 1
}

echo "Creating ${GPU_COUNT}x ${GPU_ID} pod '${POD_NAME}' in ${DATA_CENTER_ID}." >&2
echo "Attaching network volume ${NETWORK_VOLUME_ID} at ${VOLUME_MOUNT_PATH}." >&2

exec "$RUNPODCTL_BIN" pod create \
  --name "$POD_NAME" \
  --image "$IMAGE" \
  --gpu-id "$GPU_ID" \
  --gpu-count "$GPU_COUNT" \
  --container-disk-in-gb "$CONTAINER_DISK_GB" \
  --ports "$PORTS" \
  --network-volume-id "$NETWORK_VOLUME_ID" \
  --volume-mount-path "$VOLUME_MOUNT_PATH" \
  --data-center-ids "$DATA_CENTER_ID" \
  --cloud-type "$CLOUD_TYPE" \
  --ssh
