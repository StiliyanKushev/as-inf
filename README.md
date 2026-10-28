# AS-INF ComfyUI / RunPod environment

Portable deployment files for the current FLUX.2 Klein reference workflow.
The repository contains workflows, pinned plugin revisions, integrity manifests,
and scripts for recovering the existing RunPod network volume or provisioning a
new one.

The four private/custom LoRAs required by the saved workflows are stored with
Git LFS. The public BFS task LoRA is downloaded from its official Hugging Face
repository and verified by SHA-256. Six canonical synthetic persona head views
are stored with Git LFS. Large base-model weights, routine generated images,
API keys, and SSH private keys are intentionally excluded from Git. Curated
research benchmark outputs are retained under `research-results/` through Git
LFS so claims can be checked visually.

The repository also contains a reproducible FLUX.2 Klein 9B persona-LoRA
training package under [`training/`](training/README.md), including the 30-image
synthetic dataset in Git LFS, its captions, a high-memory-GPU AI Toolkit config,
and persistent RunPod install/run scripts. The selected step-1500 identity
checkpoint for the fictional Alex Sparks persona is stored through Git LFS as
`models/loras/alexsparks.safetensors`; its trained trigger is `vexa_person`.

The `research/realism-native-4k` branch also contains a reproducible FLUX 3
native-4K candidate. It generates at 3072×4096 and center-crops to 3024×4032;
there is no resize or upscale stage. See
[`docs/FLUX3_EXPERIMENT_LOG_2026-10-28.md`](docs/FLUX3_EXPERIMENT_LOG_2026-10-28.md)
for measured H200 results and the remaining controlled tests.

The current cross-model recommendation is documented in
[`docs/INSTAGRAM_REALISM_MODEL_WORKFLOW_RESEARCH_2026-10-28.md`](docs/INSTAGRAM_REALISM_MODEL_WORKFLOW_RESEARCH_2026-10-28.md).
It compares the October 2026 frontier models and specifies a blind benchmark for
GPT Image 2.5 Sunburst, Nano Banana 2.1, FLUX 3 Klein Base, and one challenger.

The first public-workflow benchmark is complete. See
[`docs/THREE_WAY_INSTAGRAM_BENCHMARK_2026-10-28.md`](docs/THREE_WAY_INSTAGRAM_BENCHMARK_2026-10-28.md)
for 18 measured Anuxq, Ananya, and Krea2 runs. Krea2 General Edit is the current
identity-first recommendation at a true 1280×1600 native render; Anuxq remains
the better casual-phone baseline.

The measured Krea2 winner is now available as a full Kurva Maker-style workflow:
[`workflows/final-kurva-maker-krea2.json`](workflows/final-kurva-maker-krea2.json).
It preserves the large workflow's control panel and prompt automation while
replacing the FLUX backend with Krea 2 Turbo, General Edit V2, FameGrid, Realism
Engine, and FameGrid Color Finish. Install its pinned runtime and public model
files with `scripts/install-krea2-production-stack.sh` after the normal volume
bootstrap. The native render is 1280×1600; the 1080×1350 file is a separate
Instagram delivery resize.

## Current deployment

| Setting | Value |
|---|---|
| GPU | Selected per session; H100 80 GB is the economical test default |
| Container image | `runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0` |
| Region | `US-CA-2` |
| Network volume | `final-kurva-maker-storage` (`3e71bw1e12`, 300 GB) |
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

- `final-kurva-maker-krea2.json` — Krea 2 Turbo production candidate with the
  same optional-reference control panel, SuperGemma/Qwen prompt pipeline,
  advanced seed/sampler/batch controls, three LoRA slots, and before/after
  slider as the largest FLUX workflow. Reference mode uses the measured Krea2
  General Edit stack; prompt-only mode bypasses the edit patch. It does not load
  the FLUX-trained Alex LoRA.

- `research-flux3-native-4k.json` — research candidate using FLUX 3 Klein Base
  BF16, the official Qwen3.5 prompt upsampler, Qwen3-VL, and three Alex identity
  references. Its current quality preset is 50 steps, CFG 3.5, Euler/simple. It
  performs a real 3072×4096 diffusion pass and crops to exact 3024×4032 without
  resampling. The Base result was the cleanest native-4K test, although it was
  softer and took about 8.5 minutes on an H200.

- `final-kurva-maker-reference-spatial-face-lora.json` — Alex Sparks persona
  workflow. It performs a no-identity scout pass, detects the face, then repeats
  the full-canvas render from the same seed with `alexsparks.safetensors`
  spatially conditioned inside the softened face mask. This avoids a separately
  rendered crop being pasted back with mismatched lighting or texture. Its
  Advanced settings expose a true latent `Batch Size`; MediaPipe creates a
  separate face mask and the save node writes a separate 3024×4032 file for
  every batch item. Batch size 1 remains the default because a B200 test at
  batch size 2 showed essentially unchanged per-image throughput.

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

The two FLUX.2 files remain the maintained production workflows. The FLUX 3
file is a reproducible research candidate. Earlier repair, face-finish, and
prompt-only experiments remain available through Git history.

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

For a short instruction that can be pasted into a future Codex session, see
[docs/AGENT_HANDOFF.md](docs/AGENT_HANDOFF.md).

For a complete new-computer procedure covering pod creation, state validation,
Hugging Face login, Klein 9B LoRA training, checkpoint selection, and cost-safe
shutdown, see
[docs/RECOVERY_AND_TRAINING_RUNBOOK.md](docs/RECOVERY_AND_TRAINING_RUNBOOK.md).
