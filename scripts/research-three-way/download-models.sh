#!/usr/bin/env bash
set -Eeuo pipefail

COMFY=/workspace/ComfyUI
PY=/workspace/comfy-venv/bin/python
export HF_XET_HIGH_PERFORMANCE=1

fetch() {
  local repo="$1"
  local file="$2"
  local dir="$3"
  local name="${4:-$(basename "$file")}" 
  mkdir -p "$dir"
  if [[ -s "$dir/$name" ]]; then
    echo "Present: $dir/$name"
    return
  fi
  /workspace/comfy-venv/bin/hf download "$repo" "$file" --local-dir /workspace/hf-stage
  mv "/workspace/hf-stage/$file" "$dir/$name"
}

fetch RunDiffusion/Juggernaut-XL-v9 \
  Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors \
  "$COMFY/models/checkpoints"

fetch Comfy-Org/Krea-2 diffusion_models/krea2_turbo_fp8_scaled.safetensors \
  "$COMFY/models/diffusion_models" krea2_turbo_fp8_scaled.safetensors
fetch Comfy-Org/Krea-2 text_encoders/qwen3vl_4b_fp8_scaled.safetensors \
  "$COMFY/models/text_encoders" qwen3vl_4b_fp8_scaled.safetensors
fetch Comfy-Org/Krea-2 vae/qwen_image_vae.safetensors \
  "$COMFY/models/vae" qwen_image_vae.safetensors
fetch conradlocke/krea2-identity-edit krea2_general_edit_v2.safetensors \
  "$COMFY/models/loras"
fetch darken144/krea2assets famegrid_spicy.safetensors \
  "$COMFY/models/loras"
fetch RazzzHF/realism_engine_krea2 realism_engine_krea2_v3.1.safetensors \
  "$COMFY/models/loras"

# Keep the exact v1.1 weights used by the published Anuxq workflow as well as
# the older converted checkpoint. The benchmark selects v1.1 when the loader
# accepts it and records the converted checkpoint only as a compatibility
# fallback.
fetch guozinan/PuLID pulid_v1.1.safetensors \
  "$COMFY/models/pulid"
fetch huchenlei/ipadapter_pulid ip-adapter_pulid_sdxl_fp16.safetensors \
  "$COMFY/models/pulid"

# AntelopeV2 is distributed as one archive and is used by PuLID.
if [[ ! -s "$COMFY/models/insightface/models/antelopev2/glintr100.onnx" ]]; then
  fetch MonsterMMORPG/tools antelopev2.zip /workspace/download-cache antelopev2.zip
  unzip -o /workspace/download-cache/antelopev2.zip -d /workspace/antelope-unpack
  find /workspace/antelope-unpack -type f -name '*.onnx' \
    -exec cp -f {} "$COMFY/models/insightface/models/antelopev2/" \;
fi

# ReActor's installer normally fetches this file. Keep it explicit so a fresh
# benchmark volume is reproducible even if the install hook is interrupted.
fetch Gourieff/ReActor models/inswapper_128.onnx \
  "$COMFY/models/insightface" inswapper_128.onnx

HASH_MANIFEST=/workspace/as-inf/manifests/research-three-way-models.sha256
if [[ -f "$HASH_MANIFEST" ]]; then
  echo "Verifying benchmark model bytes..."
  (cd "$COMFY" && sha256sum --check "$HASH_MANIFEST")
else
  echo "Missing model hash manifest: $HASH_MANIFEST" >&2
  exit 1
fi

echo "Benchmark models downloaded and verified."
