#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/workspace
COMFY="$ROOT/ComfyUI"
VENV="$ROOT/comfy-venv"
COMFY_REV=4845e7a3ffc48a6961f15824239e9042cc7d4ad1

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends git git-lfs aria2 curl unzip ffmpeg libgl1 libglib2.0-0 python3-venv build-essential

if [[ ! -d "$COMFY/.git" ]]; then
  git clone https://github.com/Comfy-Org/ComfyUI.git "$COMFY"
fi
git -C "$COMFY" fetch --depth=1 origin "$COMFY_REV"
git -C "$COMFY" checkout --detach "$COMFY_REV"

if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv --system-site-packages "$VENV"
fi
"$VENV/bin/python" -m pip install -U pip setuptools wheel
# The RunPod image ships a matched CUDA 12.8 Torch/Torchaudio 2.9.1 pair.
# Installing ComfyUI's unpinned `torchvision` currently pulls a newer Torch
# build and leaves Torchaudio on an incompatible ABI, which prevents ReActor
# from importing. Keep the image's Torch, add its matching Torchvision, and
# install the remaining ComfyUI requirements without those two unpinned lines.
"$VENV/bin/python" -m pip install --no-deps torchvision==0.24.1
grep -v -E '^(torch|torchvision)([<=> ].*)?$' "$COMFY/requirements.txt" \
  > "$ROOT/comfy-requirements-without-torch.txt"
"$VENV/bin/python" -m pip install \
  -r "$ROOT/comfy-requirements-without-torch.txt" huggingface_hub hf_xet

clone_node() {
  local url="$1" dir="$2" rev="$3"
  if [[ ! -d "$COMFY/custom_nodes/$dir/.git" ]]; then
    git clone "$url" "$COMFY/custom_nodes/$dir"
  fi
  git -C "$COMFY/custom_nodes/$dir" fetch --depth=1 origin "$rev"
  git -C "$COMFY/custom_nodes/$dir" checkout --detach "$rev"
  if [[ -f "$COMFY/custom_nodes/$dir/requirements.txt" ]]; then
    "$VENV/bin/python" -m pip install -r "$COMFY/custom_nodes/$dir/requirements.txt"
  fi
}

clone_node https://github.com/lbouaraba/comfyui-krea2edit.git comfyui-krea2edit 13ef60f20828949becada815d3cbc371eb5ccaab
clone_node https://github.com/Pixelailabs/ComfyUI-Krea2-Edit-Carousel.git ComfyUI-Krea2-Edit-Carousel a5c3eff64e9740e9ffc38ba0b7775961fa618614
clone_node https://github.com/Elevenheights/ComfyUI-FameGridColorFinish.git ComfyUI-FameGridColorFinish 944c14e53fffee3e9e6dbedad36ab95b0e1629f7
# This maintained fork retains cubiq's node API and adds native PuLID v1.1
# checkpoint support, matching the published Anuxq graph.
clone_node https://github.com/yashikawa3/ComfyUI-PuLID.git PuLID_ComfyUI c672e2a88580afe59773bde1576ce1838abd1a0f
clone_node https://github.com/Gourieff/ComfyUI-ReActor.git ComfyUI-ReActor 0763f707e3f791323f2e7450d100a25860df546c

# ReActor's installer selects the correct Linux runtime packages and downloads
# its core models on first use. It is kept separate from face restoration,
# which this benchmark intentionally disables.
(cd "$COMFY/custom_nodes/ComfyUI-ReActor" && "$VENV/bin/python" install.py) || true

mkdir -p \
  "$COMFY/models/checkpoints" \
  "$COMFY/models/diffusion_models" \
  "$COMFY/models/text_encoders" \
  "$COMFY/models/vae" \
  "$COMFY/models/loras" \
  "$COMFY/models/pulid" \
  "$COMFY/models/insightface/models/antelopev2" \
  "$COMFY/input" \
  "$COMFY/output/research-three-way"

REFERENCE="$ROOT/as-inf/assets/persona_refs/persona_front_neutral.png"
if [[ ! -f "$REFERENCE" ]]; then
  echo "Missing benchmark reference: $REFERENCE" >&2
  exit 1
fi
cp -f "$REFERENCE" "$COMFY/input/persona_front_neutral.png"

cat > "$ROOT/start-research-comfy.sh" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace/ComfyUI
exec /workspace/comfy-venv/bin/python main.py --listen 0.0.0.0 --port 8188 --preview-method auto
EOF
chmod +x "$ROOT/start-research-comfy.sh"

echo "Remote runtime installed."
