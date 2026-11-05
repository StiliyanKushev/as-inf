# Krea 2 close scene inspiration + Alex identity route (2026-11-05)

## Goal

Generate a photograph with a very close resemblance to the uploaded scene without reproducing its exact pixels or layout. The result should look like another photograph taken moments later from a slightly different nearby viewpoint.

## Tested solution

Use two visual references through `Krea2EditModelPatch` and `Krea2EditGroundedEncode`:

- reference A: full cropped scene, `beside (right of target)`, neutral `ref_boost_a = 1.0`
- reference B: selected Alex portrait, `beside (right of target)`, `ref_boost = 2.5`
- Krea2 General Edit V2 LoRA at `1.0`
- Krea 2 Turbo FP8, 10 steps, CFG 1, Euler/Simple
- native 1280×1600 render

Placing the scene `aligned (trained)` reproduced the source layout too literally even when scene strength was reduced to 0.35. `bag of features` drifted too far and changed important pose and garment details. Placing the scene `beside` retained the scene family, clothing, approximate pose, lighting, palette, materials, and crowd energy while allowing a new viewpoint and layout.

The prompt defines image A as close inspiration rather than an edit plate. Image B remains the sole authority for Alex's foreground identity. Background people are regenerated as anonymous adults and must never inherit Alex's identity.

## Result

`research-results/krea2_scene_identity/close_not_copy_alex_1280x1600.png` retains the sage-green ruched dress, hand-on-hip pose category, warm beach-club light, palm/thatch/timber materials, crowd density, and casual phone-photo character, but uses a different camera position and newly arranged bar area.

## Workflow

`workflows/final-kurva-maker-krea2-alex-direct-scene.json`

The workflow automatically selects this two-reference route when a scene is uploaded. With `None`, it retains the Alex-only prompt generation route. Optional tweaks may remain blank in reference mode.
