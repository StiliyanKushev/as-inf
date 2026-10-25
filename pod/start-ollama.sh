#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
OLLAMA_DIR="$WORKSPACE/ollama"
export OLLAMA_MODELS="$OLLAMA_DIR/models"
export OLLAMA_HOST="127.0.0.1:11434"
mkdir -p "$OLLAMA_MODELS"
if ! command -v ollama >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y zstd curl
  curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh
  sh /tmp/ollama-install.sh
fi
if curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
  echo "Ollama is already running."
  exit 0
fi
nohup ollama serve >"$OLLAMA_DIR/ollama.log" 2>&1 &
for _ in {1..60}; do
  if curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
    echo "Started Ollama with persistent models at $OLLAMA_MODELS"
    exit 0
  fi
  sleep 1
done
echo "Ollama failed to start; see $OLLAMA_DIR/ollama.log" >&2
exit 1
