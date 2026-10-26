# Agent handoff: launch the Alex Sparks ComfyUI environment

Use this repository as the source of truth:

`https://github.com/StiliyanKushev/as-inf`

## Ready-to-use instruction for a new Codex session

> Clone or update `https://github.com/StiliyanKushev/as-inf`, read
> `docs/RECOVERY_AND_TRAINING_RUNBOOK.md` and `docs/PERSISTENCE_AUDIT.md`, then
> create one secure-cloud NVIDIA B200 RunPod attached to the existing network
> volume `3e71bw1e12` in `US-CA-2` at `/workspace`. Do not create, resize, or
> delete the network volume. Use `scripts/create-b200.sh`, discover the new pod's
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
- Qwen3-VL, SuperGemma, custom nodes, public model weights, and all private
  workflow LoRAs are available.

## Credentials that are deliberately outside Git

The machine running the automation must have:

1. `runpodctl` configured with the owner's RunPod API key.
2. An SSH private key whose public half is registered with the RunPod account.

These credentials must never be committed. If they are missing, ask only for
the user to configure them locally; do not request that secrets be pasted into
chat or added to the repository.
