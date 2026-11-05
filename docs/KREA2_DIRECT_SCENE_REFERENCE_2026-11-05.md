# Krea 2 direct scene + Alex identity route (2026-11-05)

## Problem

The scene-text workflow reduced an uploaded reference to a 32×40 color map and used a Qwen caption to recreate its content. This prevented source-person identity leakage, but it also discarded exact pose, clothing color, framing, crowd density, and spatial layout.

## Tested solution

Use two visual references through `Krea2EditModelPatch` and `Krea2EditGroundedEncode`:

- reference A: the full cropped scene, `aligned (trained)`, neutral `ref_boost_a = 1.0`
- reference B: the selected Alex portrait, `beside (right of target)`, `ref_boost = 2.5`
- Krea2 General Edit V2 LoRA at `1.0`
- Krea 2 Turbo FP8, 10 steps, CFG 1, Euler/Simple
- native 1280×1600 render

The prompt defines image A as the authority for composition, foreground pose, clothing, camera, lighting, palette, crowd density, materials, and layout. Image B is the sole authority for the main foreground identity. Background people are regenerated as anonymous adults and must not inherit Alex's identity.

## Result

`research-results/krea2_scene_identity/direct_full_scene_alex_1280x1600.png` preserved the reference's sage-green ruched dress, hand-on-hip pose, camera distance, lively beach-club crowd, palm/thatch/timber layout, and warm sunlight while rendering Alex as the foreground subject.

## Workflow

`workflows/final-kurva-maker-krea2-alex-direct-scene.json`

The workflow automatically selects the direct two-reference route when a scene is uploaded. With `None`, it retains the Alex-only prompt generation route. Optional tweaks may remain blank in reference mode.
