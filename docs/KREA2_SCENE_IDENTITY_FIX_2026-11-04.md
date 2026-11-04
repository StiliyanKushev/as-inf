# Krea2 scene and Alex identity fix — 2026-11-04

## Failure reproduced

The earlier two-reference graph sent the uploaded scene as Krea image A and an
Alex portrait as image B. The scene subject leaked into the result: a brunette
source could override Alex's blonde hair and blue eyes. The compiled prompt also
allowed invented anonymous bystanders, so secondary women appeared and could
inherit Alex-like features.

## Production graph change

- The selected Alex angle is now the only visual input to
  `Krea2EditModelPatch` and `Krea2EditGroundedEncode`.
- The optional scene reaches generation only as a Qwen-produced environment and
  photographic-style brief. Its foreground person and bystanders are ignored.
- General Edit V2 remains active with or without a scene reference.
- Alex uses `ref_boost = 2.5` and `ref_position = beside (right of target)`.
- The compiler reinforces pale blue eyes, fair lightly freckled skin, her face
  geometry, and long straight light golden-blonde center-parted hair.
- Exactly one visible human is the default. Other people are allowed only when
  the optional user request explicitly asks for them.

## Phone-lighting and pose follow-up

Identity-only conditioning prevented source-person leakage, but a text-only
scene brief lost some of the reference's palette and illumination. The revised
graph creates a 32 x 40 scene color/light map and scales it back to the canvas
before Krea encoding. At that resolution, no usable face, hair, clothing or
body detail remains. The map is applied at `ref_boost_a = 0.2`; Alex remains the
second reference at `ref_boost = 2.5`.

Qwen now extracts the source pose explicitly: seated/standing state, torso and
head direction, gaze, shoulder/hip rotation, arm angles, hand placement, leg
position and weight distribution. It also records imperfect phone behavior:
flash appearance, uneven exposure, white-balance cast, clipped highlights,
crushed shadows, HDR halos, noise, sharpening and compression. The compiler
preserves those traits unless the optional user request replaces them.

An ablation showed that FameGrid 0.5, Realism Engine 0.5 and Color Finish
0.6/0.2 retained a polished editorial look even with a phone-photo prompt. The
closest result to the source's direct-flash snapshot used all three at zero.
They are therefore off by default in the Alex scene workflow and remain
available in Advanced Settings. The separate pre-Alex backup preserves the old
polished defaults.

This matches the identity-first wiring used by PixelAI's Krea2 Carousel node:
the original person photograph is the primary reference, while new places are
described in the prompt.

## Native validation

Two 1280 × 1600 runs used the full production stack: Krea 2 Turbo FP8, General
Edit V2 1.0, FameGrid 0.5, Realism Engine 0.5, Euler/simple, 10 steps, CFG 1,
Alex reference boost 2.5, and FameGrid Color Finish 0.6/0.2.

- `identity_only_red_validation.png`: one blonde, blue-eyed Alex; no background
  people; newly invented red floral corridor.
- `identity_only_beach_validation.png`: one blonde, blue-eyed Alex; no background
  people; newly invented Mediterranean beach-club terrace.

The source scene images were not passed to the Krea model in either run.
