# Agent handoff: launch the Alex Sparks ComfyUI environment

Use this repository as the source of truth:

`https://github.com/StiliyanKushev/as-inf`

## Ready-to-use instruction for a new Codex session

> Clone or update `https://github.com/StiliyanKushev/as-inf`, read
> `docs/RECOVERY_AND_TRAINING_RUNBOOK.md` and `docs/PERSISTENCE_AUDIT.md`, then
> create one secure-cloud NVIDIA B200 RunPod attached to the existing network
> volume `3e71bw1e12` in `US-CA-2` at `/workspace`. It is already 300 GB; do not
> create, resize, or delete the network volume. Use `scripts/create-b200.sh`, discover the new pod's
> SSH address, run `scripts/recover-over-ssh.sh`, verify the persistent state,
> and give me the `https://POD_ID-8188.proxy.runpod.net` ComfyUI URL. Keep the
> pod running unless I explicitly ask you to stop it.

## Expected result

- ComfyUI starts from the pinned persistent installation.
- Only these two maintained workflows come from GitHub:
  - `final-kurva-maker-reference.json`
  - `final-kurva-maker-reference-spatial-face-lora.json`
- The spatial workflow selects `alexsparks.safetensors` at strength `0.70` and
  uses its trained trigger `vexa_person` only inside the detected face mask.
- Its shared Advanced settings include a true latent `Batch Size` control.
  Batch size 1 is the tested default; batch size 2 produces two independent
  face masks and two output files but does not materially improve B200
  per-image throughput at 2016×2688.
- Qwen3-VL, SuperGemma, custom nodes, public model weights, and all private
  workflow LoRAs are available.

## FLUX 3 native-4K research state

The research branch is `research/realism-native-4k`. Read these before spending
more GPU credit:

- `docs/INSTAGRAM_REALISM_MODEL_WORKFLOW_RESEARCH_2026-10-28.md`
- `docs/TRUE_4K_INSTAGRAM_RESEARCH_2026-10-27.md`
- `docs/FLUX3_EXPERIMENT_LOG_2026-10-28.md`
- `workflows/research-flux3-native-4k.json`
- `scripts/run-flux3-research.py`
- `scripts/install-flux3-research.sh`

The existing network volume also contains the isolated runtime at
`/workspace/ComfyUI-flux3`, downloaded FLUX 3 Base and Distilled BF16 weights,
Qwen text encoders, persona references, workflow, and original outputs. The
last H200 pod is gone, but network volume `3e71bw1e12` still exists.

The best clean test used FLUX 3 Base BF16, the official prompt upsampler, three
Alex references, 50 steps, CFG 3.5, Euler/simple, and a native 3072×4096 latent
cropped to 3024×4032. It took 513 seconds on an H200. Distilled was much faster
and sharper but produced sparse colored flecks at native 4K. The next controlled
test is the same Distilled seed, prompt, and references with ComfyUI started
using `--fp32-vae`; do not change another variable in that comparison.

The newer cross-model study changes the production recommendation. Before
renting another GPU, blind-test GPT Image 2.5 Sunburst, Nano Banana 2.1 at 4K,
and the existing FLUX 3 Klein Base workflow. Nano Banana 2.1 is the provisional
default for a recurring character at genuine 3:4 high resolution; Sunburst is
the raw-realism benchmark and localized editor; FLUX 3 Base remains the local,
fine-tunable fallback. The study contains the exact reference pack, prompting,
review rubric, and ten-scene benchmark needed to make that choice from evidence.

## Credentials that are deliberately outside Git

The machine running the automation must have:

1. `runpodctl` configured with the owner's RunPod API key.
2. An SSH private key whose public half is registered with the RunPod account.

These credentials must never be committed. If they are missing, ask only for
the user to configure them locally; do not request that secrets be pasted into
chat or added to the repository.
