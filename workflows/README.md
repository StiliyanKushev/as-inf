# Workflows

Copy these JSON files to `/workspace/ComfyUI/user/default/workflows/`.

The production set contains two workflows:

- `final-kurva-maker-reference.json`
- `final-kurva-maker-reference-spatial-face-lora.json`

The `research/realism-native-4k` branch also contains:

- `research-realism-base-alex-reference-4k.json`
- `final-kurva-maker-krea2.json`
- `final-kurva-maker-krea2-pre-alex-backup.json`
- `final-kurva-maker-krea2-prealex-alex-finish.json`
- `final-kurva-maker-krea2-scene-identity.json`
- `final-kurva-maker-krea2-alex-scene-text.json`
- `final-kurva-maker-krea2-alex-direct-scene.json`

`final-kurva-maker-krea2-prealex-alex-finish.json` keeps the pre-Alex backup's
entire first pass unchanged. Its decoded photograph becomes aligned reference A
in a second Krea edit, while one selected Alex portrait is reference B. The
measured conservative settings are preservation 3.0 and Alex identity 2.0.
This separated a successful scene generation from identity replacement and, in
a 1280×1600 brunette test, retained expression, clothes, pose, hands, lighting,
camera, depth of field, and environment while changing the subject to Alex.
`APPLY ALEX IDENTITY FINISH` is enabled by default and can be disabled to return
the untouched backup output. Both preservation and Alex identity strengths are
exposed beside this toggle in Advanced Settings; their tested defaults remain
3.0 and 2.0. See
`docs/KREA2_PREALEX_ALEX_FINISH_2026-11-05.md`.

The feathered variant additionally exposes `REFERENCE COLOR MATCH` in Advanced
Settings. With a scene reference selected, the default `0.35` applies a mild
Reinhard Lab color transfer after FameGrid Color Finish so the generated photo
inherits the source's broad hue, saturation, luminance, and contrast. Set it to
`0` to disable the transfer. Prompt-only runs bypass it automatically.
Its independent `APPLY SATURATION ADJUSTMENT` toggle and `SATURATION` value run
after color matching. `1.0` is neutral, `0.0` is grayscale, and values above
`1.0` increase saturation. Disabling the toggle returns the input unchanged.

`final-kurva-maker-krea2-alex-direct-scene.json` is the preferred close-match workflow when the uploaded image should control the visible scene. It sends the full cropped source beside the target at neutral strength 1.0 and the selected Alex portrait as identity reference B at strength 2.5. This produces a newly arranged nearby viewpoint while retaining the source's scene family, approximate pose, garment design/color, camera character, lighting, crowd density, and materials. A default-on second pass transfers the source expression and face-adjacent styling such as glasses, makeup, jewelry, and headwear onto the generated Alex image; it can be disabled in Advanced Settings. When the selector is `None`, the workflow automatically falls back to the Alex-only prompt route and skips the finish. The optional request may be blank. The validated beach-club results and exact settings are documented in `docs/KREA2_DIRECT_SCENE_REFERENCE_2026-11-05.md`.

`final-kurva-maker-krea2-alex-scene-text.json` is the simplified direct hybrid validated on 2026-11-04. The uploaded scene is analyzed into text only and its pixels never reach Krea. One selected Alex portrait is Krea's sole visual reference; the model and conditioning switches are locked to that identity-only route. Keep the Alex angle selector on `front` to reproduce the measured setup. This avoided source-person leakage while following two unrelated scene/pose briefs. See `research-results/pixelai_alex_scene_2026-11-04/` for outputs and exact settings.

`final-kurva-maker-krea2-scene-identity.json` is the recommended Alex workflow.
The selected Alex photograph is General Edit V2's only visual conditioning
identity image. The optional scene is analyzed into an environment, pose,
camera, imperfect-lighting and color brief. A 32 x 40 abstract color/light map
also reaches Krea at low strength; the downsample destroys usable person detail
while retaining broad palette and illumination. This prevents a scene subject's
hair, eyes, eyewear, and face from leaking into Alex. Three
identity angles remain visible in the control panel, while an angle selector
forwards only one to Krea2. Sending several identity photographs as equal
subjects produced twins and collages in live tests. Select the face angle
closest to the desired head angle. The default prompt contains exactly one
visible person and reinforces Alex's blonde hair, blue eyes, freckles, and face
geometry. It also asks Krea to reproduce the source pose approximately and
retain observed phone-camera defects instead of upgrading them to studio light.
FameGrid, Realism Engine, and Color Finish are disabled by default in this
workflow to avoid a polished advertising finish. This workflow does not load
the experimental Alex Krea2 character LoRA.

`final-kurva-maker-krea2-pre-alex-backup.json` is the exact production graph
from commit `dab80ad`, before Alex identity experiments began. Use it for a
clean comparison with the earlier single-reference behavior. Its original
style strengths and reference-preservation logic are unchanged. One usability
fix was added: in reference mode the request field may be empty. A blank value
is converted to `No additional user modifications.` so the prompt compiler
preserves the selected reference rather than sending an empty Ollama request.

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
from the selected source image. For reusable Alex identity, use
`final-kurva-maker-krea2-scene-identity.json` and its separate identity bank.

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
