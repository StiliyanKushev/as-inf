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

`REFERENCE BEHAVIOR` has six first-pass modes when the experimental workflow is
installed:

- `Inspired — beside`: fresh latent at denoise 1.0 with detached reference
  coordinates, producing a related new photograph
- `Balanced — partial alignment`: fresh latent at denoise 1.0 with the
  reference shifted by half a target width, retaining partial spatial overlap;
  this is the saved default between Inspired and Close
- `Balanced 75% — stronger alignment`: shifts the reference by one quarter of
  the target width, retaining about 75% spatial overlap; it is closer to
  Aligned while still allowing more scene variation
- `Balanced 75% — feathered` (experimental workflow): applies that same
  quarter-width displacement gradually. For local reference coordinate `x`,
  target width `W`, and blend fraction `b`, it uses
  `x' = x + (W/4) * smoothstep(clamp(x/(W*b), 0, 1))`. This removes the one
  abrupt positional boundary without turning the mode into aligned copying.
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
- feathered experiment:
  `workflows/final-kurva-maker-krea2-prealex-alex-finish-feathered.json`
- deterministic builder: `scripts/build-krea2-prealex-alex-finish-workflow.py`
- feathered builder: `scripts/build-krea2-feathered-workflow.py`
- source backup remains untouched
- `APPLY ALEX IDENTITY FINISH` is enabled by default; disabling it returns the
  original first-pass output
- Advanced Settings exposes `FIRST-PASS REFERENCE STRENGTH`,
  `PRESERVATION STRENGTH`, and `ALEX IDENTITY STRENGTH`
- first-pass reference strength is an attention multiplier rather than a
  literal percentage: `1.0` is neutral, values above `1.0` pull harder toward
  the source image, and values below `1.0` allow more deviation
- `FEATHER BLEND WIDTH` is a fraction of target width and affects only the
  feathered mode. The saved default is `0.25`; `0` deliberately reproduces the
  original hard 75% shift for controlled comparisons.
- background focus is pixel-controlled rather than generated from Qwen's prose.
  The reference analyzer is forbidden from turning ordinary distance softness
  into shallow-depth-of-field or bokeh language, and the compiler removes such
  language unless it appears in the authoritative user request. The reference
  pixels can still carry real optical softness into Krea without a text prompt
  that amplifies it. Prompt-only mode defaults to phone-camera deep focus; an
  explicit user request for blur, bokeh, portrait mode, or deep focus wins.
- the feathered workflow optionally matches the finished image's global color
  statistics to the selected scene reference after FameGrid Color Finish. The
  `REFERENCE COLOR MATCH` control uses ComfyUI's core Reinhard Lab transfer at
  `0.35` by default. It adjusts broad hue, saturation, luminance, and contrast
  without changing geometry or adding detail. `0` disables it; `0.2` to `0.5`
  is the recommended range. The node is bypassed automatically in prompt-only
  mode, so an absent reference cannot affect the result.
- a separate final saturation control runs after reference color matching.
  `APPLY SATURATION ADJUSTMENT` is an exact bypass toggle. With it enabled,
  `SATURATION` uses `1.0` as neutral, `0.0` as grayscale, values below `1.0`
  to mute color, and values above `1.0` to strengthen color. This adjustment
  works in both reference and prompt-only modes and does not alter geometry.
- select the Alex portrait closest to the desired head angle when needed

The installer already copies the versioned persona references from
`assets/persona_refs/` to the stable `alexsparks_*.png` ComfyUI input names.

## Inspired-mode phone-focus diagnostic (2026-11-06)

The beach-club reference was tested with a blank user request after automatic
blur language had been removed from the prompt compiler. Close/aligned produced
a resolved background, but Inspired/beside still generated pronounced portrait
bokeh even though the compiled prompt explicitly requested deep focus and no
artificial background blur.

A save directly from the first-pass VAE decode proved that the blur already
exists before the optional Alex identity finish. The identity pass is therefore
not its source. A second first-pass test strengthened the instruction to an
ordinary iPhone rear 1x Photo-mode snapshot, portrait mode off, 24mm-equivalent
wide perspective, no computational depth map, no DSLR portrait look, and
legible background people and materials. This reduced the portrait character
only slightly and did not remove the blur.

The remaining controlled variables are the Inspired placement and the style
stack. Inspired starts from an empty latent and places the reference outside the
target coordinates, giving Krea freedom to fall back to its subject-isolating
portrait prior. FameGrid 0.5 and Realism Engine 0.5 are likely amplifiers; KNP
1.0 may also contribute. The queued no-style-LoRA ablation was interrupted when
the RunPod credit balance reached zero and the H200 pod was automatically
terminated. If it completed before termination, its persistent output is under
`output/FocusDiagnosis/inspired_iphone_no_style_loras_00001_.png`.

Proof outputs retained on the network volume:

- `output/FocusDiagnosis/inspired_first_pass_00001_.png`
- `output/FocusDiagnosis/inspired_iphone_prompt_00001_.png`
- `output/FocusFixTest/native_1280x1600_00001_.png` (resolved Close/aligned control)

The next experiment should keep General Edit and KNP active while bypassing
FameGrid and Realism Engine only for the Inspired first pass. If that resolves
the background, expose an `iPhone Photo mode` switch that selects this model
path and appends the tested phone-camera instruction. Until that ablation is
complete, Balanced or Close is the proven choice for a resolved environment.
