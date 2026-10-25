#!/usr/bin/env bash
set -Eeuo pipefail

if (( $# < 2 || $# > 3 )); then
  echo "Usage: $0 root@POD_IP SSH_PORT [SSH_PRIVATE_KEY]" >&2
  exit 2
fi

SSH_HOST="$1"
SSH_PORT="$2"
SSH_KEY="${3:-${RUNPOD_SSH_KEY:-$HOME/.runpod/ssh/runpodctl-ssh-key}}"

[[ -f "$SSH_KEY" ]] || {
  echo "SSH private key not found: $SSH_KEY" >&2
  exit 1
}

ssh -i "$SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new \
  -p "$SSH_PORT" "$SSH_HOST" 'set -e
if [[ -x /workspace/recover-final-kurva-maker.sh ]]; then
  exec /workspace/recover-final-kurva-maker.sh
fi
if [[ ! -d /workspace/as-inf/.git ]]; then
  command -v git >/dev/null 2>&1 || { apt-get update && apt-get install -y git; }
  git clone https://github.com/StiliyanKushev/as-inf.git /workspace/as-inf
fi
exec /workspace/as-inf/scripts/bootstrap-new-volume.sh'
