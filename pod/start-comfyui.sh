#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE/ComfyUI}"
VENV_DIR="${VENV_DIR:-$WORKSPACE/comfyui-venv}"
LOG="$WORKSPACE/comfyui.log"
PIDFILE="$WORKSPACE/comfyui.pid"

if [[ -x "$WORKSPACE/start-ollama.sh" ]]; then
  "$WORKSPACE/start-ollama.sh"
fi

# A PID file survives with the network volume. Only trust it when the PID is
# alive and its command is actually this persistent ComfyUI installation.
if [[ -f "$PIDFILE" ]]; then
  old_pid="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
    old_cmd="$(tr '\0' ' ' <"/proc/$old_pid/cmdline" 2>/dev/null || true)"
    if [[ "$old_cmd" == *"main.py"*"--port 8188"* ]]; then
      echo "ComfyUI is already running with PID $old_pid"
      exit 0
    fi
  fi
  rm -f "$PIDFILE"
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "ERROR: missing persistent Python environment: $VENV_DIR" >&2
  exit 1
fi

# Stop the template's bundled ComfyUI before launching the pinned copy stored
# on the network volume.
mapfile -t conflicting_pids < <(pgrep -f 'python(3)? main.py.*--port 8188' || true)
if (( ${#conflicting_pids[@]} )); then
  echo "Stopping template ComfyUI process(es): ${conflicting_pids[*]}"
  kill -TERM "${conflicting_pids[@]}" 2>/dev/null || true
  for _ in {1..20}; do
    pgrep -f 'python(3)? main.py.*--port 8188' >/dev/null || break
    sleep 0.5
  done
fi

cd "$COMFY_DIR"
nohup "$VENV_DIR/bin/python" main.py --listen 0.0.0.0 --port 8188 \
  >"$LOG" 2>&1 &
echo $! >"$PIDFILE"
echo "Started persistent ComfyUI with PID $(cat "$PIDFILE"). Log: $LOG"
