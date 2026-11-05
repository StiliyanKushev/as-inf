# Krea 2 pre-Alex generation with restrained Alex identity finish (2026-11-05)

## Goal

Retain the unusually strong scene, pose, lighting, and phone-photo behavior of
`final-kurva-maker-krea2-pre-alex-backup.json`, then introduce Alex without
making the scene and identity references compete during the original render.

## Approach

The workflow has two independent diffusion passes:

1. The original pre-Alex workflow generates the complete 1280×1600 photograph.
   Its model stack, prompt builder, optional reference behavior, LoRAs, sampler,
   and reference preservation logic are unchanged.
2. A constrained Krea General Edit pass treats that decoded photograph as
   authoritative aligned reference A. One selected Alex portrait is reference
   B and supplies only face and hair identity. Color Finish runs once, after
   the optional identity pass.

The saved production defaults now use:

- sampler/scheduler: `LCM / Simple`
- steps / CFG: `10 / 1.0`
- first-pass reference strength: `2.0`
- identity-pass preservation strength: `2.0`
- Alex identity strength: `3.0`
- first-pass placement: `aligned (trained)`
- Alex placement: `beside (right of target)`
- fit mode: `fit`
- Krea 2 Turbo FP8, General Edit V2 1.0, FameGrid 0.5, Realism Engine 0.5
- native 1280×1600 target

`REFERENCE BEHAVIOR` has three first-pass modes:

- `Inspired — beside`: fresh latent at denoise 1.0 with detached reference
  coordinates, producing a related new photograph; this remains the default
- `Close — aligned`: fresh latent at denoise 1.0 with reference and target
  coordinates aligned, preserving composition and pose more closely
- `Pixel-preserving — aligned + low denoise`: starts from the VAE-encoded
  reference at denoise 0.25 and uses aligned coordinates for restrained edits

With no reference selected, all three settings safely fall back to ordinary
prompt-only generation from the empty latent at denoise 1.0.

The prompt explicitly limits the edit to underlying face and hair identity. It
defines the first pass as authoritative for expression, gaze, head angle,
eyewear, jewelry, clothing, pose, hands, lighting, skin texture, focus, camera,
crop, and every background element.

## Controlled test

The source was a pre-Alex output with a clearly brunette subject in a black
dress on a warm-lit staircase. Three 768×960 variants were tested:

- preserve 3.0 / identity 2.0
- preserve 2.0 / identity 2.5
- preserve 1.5 / identity 3.0

All three converged to a similar Alex identity. The conservative 3.0 / 2.0
variant was selected because it minimizes scene drift. It was then rerun at the
production 1280×1600 resolution. The full-resolution result retained the same
expression, black dress, pose, hands, framing, staircase geometry, depth of
field, and warm light while changing the brunette face and hair into Alex's
blonde, blue-eyed identity.

Proof files:

- `research-results/krea2-prealex-alex-finish/source-prealex-brunette.png`
- `research-results/krea2-prealex-alex-finish/alex-finish-preserve3-identity2-1280x1600.png`

## Workflow and reproducibility

- workflow: `workflows/final-kurva-maker-krea2-prealex-alex-finish.json`
- deterministic builder: `scripts/build-krea2-prealex-alex-finish-workflow.py`
- source backup remains untouched
- `APPLY ALEX IDENTITY FINISH` is enabled by default; disabling it returns the
  original first-pass output
- Advanced Settings exposes `FIRST-PASS REFERENCE STRENGTH`,
  `PRESERVATION STRENGTH`, and `ALEX IDENTITY STRENGTH`
- first-pass reference strength is an attention multiplier rather than a
  literal percentage: `1.0` is neutral, values above `1.0` pull harder toward
  the source image, and values below `1.0` allow more deviation
- select the Alex portrait closest to the desired head angle when needed

The installer already copies the versioned persona references from
`assets/persona_refs/` to the stable `alexsparks_*.png` ComfyUI input names.
