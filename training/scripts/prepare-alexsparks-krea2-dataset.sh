#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
REPO_DIR="${AS_INF_DIR:-$WORKSPACE/as-inf}"
SOURCE="${SOURCE_DATASET:-$REPO_DIR/training/datasets/vexa_person}"
TARGET="${TARGET_DATASET:-$WORKSPACE/training/datasets/alexsparks_krea2}"

mkdir -p "$TARGET"

count=0
for image in "$SOURCE"/*.png; do
  [[ -f "$image" ]] || continue
  stem="$(basename "${image%.png}")"
  caption="$SOURCE/$stem.txt"
  [[ -s "$caption" ]] || {
    echo "ERROR: missing caption for $image" >&2
    exit 1
  }
  cp -f "$image" "$TARGET/$stem.png"
  description="$(sed -E 's/^vexa_person,[[:space:]]*//' "$caption")"
  printf 'A realistic photograph of alexsparks, an adult woman. The image shows %s\n' \
    "$description" > "$TARGET/$stem.txt"
  count=$((count + 1))
done

if (( count < 15 )); then
  echo "ERROR: expected at least 15 training images, prepared $count." >&2
  exit 1
fi

images="$(find "$TARGET" -maxdepth 1 -type f -name '*.png' | wc -l)"
captions="$(find "$TARGET" -maxdepth 1 -type f -name '*.txt' | wc -l)"
[[ "$images" == "$captions" ]] || {
  echo "ERROR: prepared $images images and $captions captions." >&2
  exit 1
}

if grep -L '^A realistic photograph of alexsparks' "$TARGET"/*.txt | grep -q .; then
  echo "ERROR: one or more captions are missing the alexsparks trigger." >&2
  exit 1
fi

echo "Prepared $count Krea2 image/caption pairs at $TARGET."
