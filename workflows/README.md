# Workflows

Copy these JSON files to `/workspace/ComfyUI/user/default/workflows/`.

The repository intentionally maintains exactly two workflows:

- `final-kurva-maker-reference.json`
- `final-kurva-maker-reference-spatial-face-lora.json`

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
