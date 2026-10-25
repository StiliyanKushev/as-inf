# Vexa persona LoRA training

This is a separate training pipeline for the fictional `vexa_person` identity.
It is not a ComfyUI generation workflow. It trains a LoRA once; ComfyUI then
loads the selected `.safetensors` checkpoint during normal image generation.

## Training target

- Base: `black-forest-labs/FLUX.2-klein-base-9B`
- Inference target: the distilled FLUX.2 Klein 9B checkpoint already used by
  `final-kurva-maker-reference.json`
- Trainer: AI Toolkit, pinned to commit
  `73ebae13a468942ded8b47991b5d56eeeea25c36`
- Trigger: `vexa_person`
- Dataset: 30 synthetic 1024 x 1024 images with matching captions
- LoRA: rank/alpha 32, 2,000 steps, checkpoints and previews every 250 steps

The config keeps all eight checkpoints. Compare the fixed-seed preview grids,
especially steps 750 through 1,500. Choose the checkpoint with the strongest
identity that still follows pose, clothing, expression, and scene prompts.
The final 2,000-step checkpoint may be overfit.

## Persistent RunPod layout

All state is placed on the network volume:

```text
/workspace/as-inf/training/       config, scripts, and dataset
/workspace/ai-toolkit/            pinned trainer source
/workspace/ai-toolkit-venv/       dedicated Python environment
/workspace/huggingface/           model download cache and login token
/workspace/training/output/       LoRA checkpoints and preview images
/workspace/training/logs/         terminal logs
```

The FLUX.2 Klein 9B components total about 35 GB before the trainer, caches,
and checkpoints. Keep at least 50 GiB free on `/workspace` before installing.

## One-time prerequisites

1. Accept the gated model license at
   <https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9B>.
2. Make an account token with read access. Add it to RunPod as the `HF_TOKEN`
   secret/environment variable. Do not commit it or paste it into chat.
3. Expand the network volume if `/workspace` has less than 50 GiB free.

FLUX.2 Klein 9B Base uses the FLUX non-commercial license. For commercial
publishing, obtain the appropriate license or retrain this package against the
Apache-2.0 Klein 4B base instead.

## Install and train

From the RunPod terminal:

```bash
cd /workspace/as-inf
git pull --ff-only
git lfs pull
./training/scripts/install-ai-toolkit.sh
./training/scripts/train-vexa-klein9b.sh
```

The download remains in `/workspace/huggingface`, so replacing or stopping a
GPU pod does not discard it.

## Install the chosen checkpoint into ComfyUI

Inspect the preview images under
`/workspace/training/output/vexa_person_klein9b_v1/`, then run:

```bash
/workspace/as-inf/training/scripts/install-selected-lora.sh \
  /workspace/training/output/vexa_person_klein9b_v1/CHOSEN_CHECKPOINT.safetensors
```

Refresh the ComfyUI model list. Put the LoRA in an available LoRA slot, enter
`vexa_person` as its trigger, and begin around strength `0.70`. Test roughly
`0.55` through `0.90`; higher strength can improve resemblance while reducing
prompt flexibility or importing dataset composition.
