# AS-INF ComfyUI / RunPod environment

Portable deployment files for the current FLUX.2 Klein reference workflow.
The repository contains workflows, pinned plugin revisions, integrity manifests,
and scripts for recovering the existing RunPod network volume or provisioning a
new one.

The four LoRAs required by the saved workflows are stored with Git LFS. Large
base-model weights, reference photos, generated images, API keys, and SSH
private keys are intentionally excluded from Git.

## Current deployment

| Setting | Value |
|---|---|
| GPU | NVIDIA B200 180 GB |
| Container image | `runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0` |
| Region | `US-CA-2` |
| Network volume | `final-kurva-maker-storage` (`3e71bw1e12`) |
| Network-volume mount | `/workspace` |
| Ports | `8188/http,22/tcp` |
| Main workflow | `final-kurva-maker-reference.json` |
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

Create a B200 attached to the existing volume:

```bash
./scripts/create-b200.sh
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

- `final-kurva-maker-reference.json` — main 4K portrait flow with one optional
  reference selector. Choosing an image enables Qwen3-VL analysis and image
  conditioning; choosing `None` skips both. Both modes use two-pass SuperGemma
  prompt compilation, FLUX.2 Klein generation, DyPE, and comparison review.
  The bundled `ASInfOptionalReferenceImage` node provides the single-control
  behavior without requiring a placeholder photo. A built-in interactive crop
  lets you frame an arbitrary source image at 3:4 before it enters Qwen,
  reference conditioning, and the final comparison; crop-to-fill normalization
  prevents aspect-ratio stretching and resize padding. The installer enables
  ComfyUI Nodes 2.0 because the visual crop editor requires that renderer.
- `final-kurva-maker.json` — prompt-only predecessor.
- `4k-local-repair-flux2-v2.json` — masked FLUX.2 repair flow.
- `4k-masked-editor.json` — crop-and-stitch masked editor.
- `4k-hand-repair-v2.json` — Angelo-based local hand repair.

## Persistence and cost control

Everything expensive or stateful belongs under `/workspace`. Stopping or
terminating a GPU pod does not remove an attached RunPod network volume. Never
delete the network volume unless the data has been copied elsewhere. Stop the
pod when it is idle; GPU billing continues while it is running.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the file layout and exact
recovery behavior.
