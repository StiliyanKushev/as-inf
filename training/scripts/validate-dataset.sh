#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATASET="${1:-$ROOT/training/datasets/vexa_person}"

if [[ ! -d "$DATASET" ]]; then
  echo "ERROR: dataset directory does not exist: $DATASET" >&2
  exit 1
fi

mapfile -t images < <(find "$DATASET" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) -printf '%f\n' | sort)
mapfile -t captions < <(find "$DATASET" -maxdepth 1 -type f -iname '*.txt' -printf '%f\n' | sort)

if (( ${#images[@]} < 15 )); then
  echo "ERROR: expected at least 15 images, found ${#images[@]}." >&2
  exit 1
fi

for image in "${images[@]}"; do
  stem="${image%.*}"
  caption="$DATASET/$stem.txt"
  if [[ ! -s "$caption" ]]; then
    echo "ERROR: missing or empty caption for $image" >&2
    exit 1
  fi
  if ! grep -q '^vexa_person\([,. ]\|$\)' "$caption"; then
    echo "ERROR: caption does not start with vexa_person: $caption" >&2
    exit 1
  fi
  if head -c 80 "$DATASET/$image" | grep -q 'git-lfs.github.com/spec'; then
    echo "ERROR: $image is still a Git LFS pointer. Run: git lfs pull" >&2
    exit 1
  fi
done

if (( ${#images[@]} != ${#captions[@]} )); then
  echo "ERROR: found ${#images[@]} images and ${#captions[@]} captions." >&2
  exit 1
fi

echo "Dataset OK: ${#images[@]} images, ${#captions[@]} matching captions, trigger vexa_person."
