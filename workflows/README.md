# Workflows

Copy these JSON files to `/workspace/ComfyUI/user/default/workflows/`.

The production set contains two workflows:

- `final-kurva-maker-reference.json`
- `final-kurva-maker-reference-spatial-face-lora.json`

The `research/realism-native-4k` branch also contains:

- `research-realism-base-alex-reference-4k.json`
- `final-kurva-maker-krea2.json`

`final-kurva-maker-krea2.json` is the production-style Krea 2 Turbo version of
the largest Kurva Maker control panel. It retains the optional WYSIWYG
reference crop, request field, Qwen/SuperGemma prompt compiler, seed and batch
controls, three editable LoRA slots with conditional trigger text, comparison
slider, and separate native/delivery saves. Its measured defaults are Krea 2
Turbo FP8, General Edit V2 at 1.0 in reference mode, FameGrid at 0.5, Realism
Engine at 0.5, Euler/simple, 10 steps, CFG 1, reference boost 2, and FameGrid
Color Finish at 0.6/0.2. It generates a true native 1280 x 1600 image and a
separate 1080 x 1350 Instagram copy.

The optional crop is locked to 4:5 for this workflow. General Edit V2 and its
Krea2 source patch are bypassed automatically in prompt-only mode. The existing
`alexsparks.safetensors` is intentionally absent because it was trained for
FLUX.2 Klein and is not compatible with Krea 2. Reference mode gets identity
from the selected source image; prompt-only mode needs a future Krea2-trained
Alex character LoRA for persistent identity.

On a bootstrapped volume, install the pinned Krea2 nodes and public weights:

```bash
/workspace/as-inf/scripts/install-krea2-production-stack.sh
```

`research-realism-base-alex-reference-4k.json` is the measured FLUX realism
candidate. It uses the checkpoint matched to the Alex LoRA training (`FLUX.2
Klein Base 9B`), the BF16 Qwen3 encoder, a native 1200 x 1600 canvas, Euler with
`Flux2Scheduler`, 30 steps, CFG 4, Alex at 0.55, and a final 3024 x 4032 Lanczos
delivery stage. Its scene reference is optional. The control panel contains
only the prompt, optional fixed-3:4 reference crop, and final comparison viewer;
model and sampler controls remain visible below.

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
