# Krea2 scene plus Alex identity workflow

The production topology uses Krea2 General Edit V2's trained two-reference
path:

1. Image 1 supplies the scene, camera, pose, clothing, lighting, and layout.
2. Image 2 supplies the identity of the only foreground woman.
3. The model patch places the scene in the trained aligned position and the
   person beside the target, with identity reference boost 1.5.
4. Grounded Qwen3-VL conditioning receives the same scene/identity ordering.

The control panel displays front, three-quarter-left, and
three-quarter-right Alex photographs. `ASInfSelectIdentityReference` forwards
exactly one. Choose the view closest to the scene subject's head angle.

## Measured failures that shaped the design

- The Raw-trained `alexsparks_krea2.safetensors` adapter changed the image but
  had weak identity transfer on the stacked Turbo workflow. Higher strength
  reduced texture quality.
- Four Krea Reference V11 cards (one scene and three equal identity cards)
  produced multiple copies of the woman.
- One scene card plus one identity card still produced twins because both
  reference images contained a person.
- General Edit V2 with scene first and identity second produced one subject,
  retained the cafe composition, and transferred Alex's blue eyes, freckles,
  facial proportions, and hair without the character LoRA.

The extra identity images therefore form a selectable angle bank rather than
simultaneous model inputs.

## Validation

The complete selector path was executed on 2026-11-03 with the front identity
view, a 1024 x 1280 target, 10 Euler/simple steps, and seed 27012026. ComfyUI
completed successfully and produced exactly one subject while retaining the
scene and transferring Alex's fair freckled skin, blue-green eyes, facial
geometry, and hair. The saved proof image is
`research-results/krea2_scene_identity/final_selector_validation_00001_.png`.
