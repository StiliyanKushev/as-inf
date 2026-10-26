# AS-INF ComfyUI / RunPod environment

Portable deployment files for the current FLUX.2 Klein reference workflow.
The repository contains workflows, pinned plugin revisions, integrity manifests,
and scripts for recovering the existing RunPod network volume or provisioning a
new one.

The four private/custom LoRAs required by the saved workflows are stored with
Git LFS. The public BFS task LoRA is downloaded from its official Hugging Face
repository and verified by SHA-256. Six canonical synthetic persona head views
are stored with Git LFS. Large base-model weights, generated images, API keys,
and SSH private keys are intentionally excluded from Git.

The repository also contains a reproducible FLUX.2 Klein 9B persona-LoRA
training package under [`training/`](training/README.md), including the 30-image
synthetic dataset in Git LFS, its captions, a high-memory-GPU AI Toolkit config,
and persistent RunPod install/run scripts. The selected step-1500 identity
checkpoint for the fictional Alex Sparks persona is stored through Git LFS as
`models/loras/alexsparks.safetensors`; its trained trigger is `vexa_person`.

## Current deployment

| Setting | Value |
|---|---|
| GPU | Selected per session; H100 80 GB is the economical test default |
| Container image | `runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0` |
| Region | `US-CA-2` |
| Network volume | `final-kurva-maker-storage` (`3e71bw1e12`) |
| Network-volume mount | `/workspace` |
| Ports | `8188/http,22/tcp` |
| Main persona workflow | `final-kurva-maker-reference-spatial-face-lora.json` |
| ComfyUI | `0.35.0`, commit `1d48d9cf7bcecb6022a87b3cb13e0fb435bf9b8a` |
| Prompt model | `0xIbra/supergemma4-26b-uncensored-gguf-v2:Q4_K_M` |

## Fast path: use the existing network volume

Install and configure `runpodctl` on the machine you are using. Keep the API key
out of the repository and shell history:

```bash
read -rsp "RunPod API key: " key; echo
runpodctl config --apiKey "$key"
unset key
```

Create an H100 attached to the existing volume (the economical testing
default):

```bash
./scripts/create-gpu-pod.sh
```

Select another GPU without changing the script:

```bash
GPU_ID='NVIDIA B200' POD_NAME='final-kurva-maker-b200' \
  ./scripts/create-gpu-pod.sh
```

When `runpodctl pod get POD_ID` reports an SSH host and port, recover the saved
environment:

```bash
./scripts/recover-over-ssh.sh root@POD_IP SSH_PORT ~/.runpod/ssh/runpodctl-ssh-key
```

The recovery command uses the complete ComfyUI installation, models, plugins,
Ollama model, workflows, settings, inputs, and outputs already stored under
`/workspace`. Open `https://POD_ID-8188.proxy.runpod.net` after it finishes.

## New empty network volume

For a new volume, clone this repository inside `/workspace`, then run:

```bash
git clone https://github.com/StiliyanKushev/as-inf.git /workspace/as-inf
/workspace/as-inf/scripts/bootstrap-new-volume.sh
```

The bootstrap pins ComfyUI and every custom node, installs the Python packages,
downloads the public FLUX.2/Qwen/VAE files, downloads Qwen3-VL, installs Ollama,
pulls the exact SuperGemma model, and restores the four workflow LoRAs from Git
LFS.

## Workflows

- `final-kurva-maker-reference-spatial-face-lora.json` — Alex Sparks persona
  workflow. It performs a no-identity scout pass, detects the face, then repeats
  the full-canvas render from the same seed with `alexsparks.safetensors`
  spatially conditioned inside the softened face mask. This avoids a separately
  rendered crop being pasted back with mismatched lighting or texture.

- `final-kurva-maker-reference.json` — main 4K portrait flow with one optional
  reference selector. Choosing an image enables Qwen3-VL analysis and image
  conditioning; choosing `None` skips both. Both modes use two-pass SuperGemma
  prompt compilation, FLUX.2 Klein generation, DyPE, and comparison review.
  The bundled `ASInfOptionalReferenceCrop3x4` node combines the optional image
  picker with a fixed 3:4 WYSIWYG crop. Move the crop rectangle directly or
  zoom it with the mouse wheel; its ratio and coordinate widgets stay hidden.
  The same crop enters Qwen, reference conditioning, and comparison, while
  crop-to-fill normalization prevents stretching and padding.

The fixed crop interaction is adapted from
[ComfyUI-LoadImageCrop](https://github.com/domg73/ComfyUI-LoadImageCrop)
under its MIT license.
- `final-kurva-maker.json` — prompt-only predecessor.
- `4k-local-repair-flux2-v2.json` — masked FLUX.2 repair flow.
- `4k-masked-editor.json` — crop-and-stitch masked editor.
- `4k-hand-repair-v2.json` — Angelo-based local hand repair.
- `persona-face-finish.json` — optional second-pass BFS head/face finish for a
  completed 4K image. Paint the replaceable face or head in MaskEditor, select
  the closest bundled persona angle, and run the official FLUX.2 Klein 9B BFS
  target-first/persona-second, four-step LCM path. Only the generated crop is
  blended back; unmasked full-resolution pixels remain untouched.

The persona references installed under `input/persona_refs` are selected from
the existing fictional `face_dataset/03_dataset_candidates` set: neutral front,
smiling front, left/right three-quarter, and left/right profile.

## Persistence and cost control

Everything expensive or stateful belongs under `/workspace`. Stopping or
terminating a GPU pod does not remove an attached RunPod network volume. Never
delete the network volume unless the data has been copied elsewhere. Stop the
pod when it is idle; GPU billing continues while it is running.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the file layout and exact
recovery behavior.

See [docs/PERSISTENCE_AUDIT.md](docs/PERSISTENCE_AUDIT.md) for the exact
boundary between Git-backed deployment state, reproducible public downloads,
and private runtime data retained only on the network volume.

For a complete new-computer procedure covering pod creation, state validation,
Hugging Face login, Klein 9B LoRA training, checkpoint selection, and cost-safe
shutdown, see
[docs/RECOVERY_AND_TRAINING_RUNBOOK.md](docs/RECOVERY_AND_TRAINING_RUNBOOK.md).
