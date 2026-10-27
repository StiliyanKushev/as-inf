# Workflows

Copy these JSON files to `/workspace/ComfyUI/user/default/workflows/`.

The production set contains two workflows:

- `final-kurva-maker-reference.json`
- `final-kurva-maker-reference-spatial-face-lora.json`

The `research/realism-native-4k` branch also contains:

- `research-realism-base-alex-reference-4k.json`

This is the measured realism candidate. It uses the checkpoint matched to the
Alex LoRA training (`FLUX.2 Klein Base 9B`), the BF16 Qwen3 encoder, a native
1200 x 1600 canvas, Euler with `Flux2Scheduler`, 30 steps, CFG 4, Alex at 0.55,
and a final 3024 x 4032 Lanczos delivery stage. Its scene reference is optional.
The control panel contains only the prompt, optional fixed-3:4 reference crop,
and final comparison viewer; model and sampler controls remain visible below.

The workflows contain model filenames and node settings but no model weights,
API credentials, or source/reference images. A `LoadImage` node may remember a
filename from the last machine; choose a valid image after opening the workflow.

`final-kurva-maker-reference-spatial-face-lora.json` is the isolated identity
variant. It first makes a scout render without the persona LoRA, detects the
face with ComfyUI's official MediaPipe model, and repeats the same seed from
noise with `alexsparks.safetensors` attached only to softly masked face
conditioning. Its embedded activation trigger is `vexa_person`.
It does not crop, repaint, or paste a separately rendered face. Both passes use
the shared seed and sampler controls in Advanced Settings, and the second slider
compares the face-local result against the no-identity scout.
