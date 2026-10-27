# Realism optimization research

Date: 2026-10-27  
Target workflow: `workflows/final-kurva-maker-reference-spatial-face-lora.json` at commit `d9f0987`

## Executive finding

The current workflow is not failing because it lacks more sampler steps. Its main
generation path combines several settings that conflict with the native operating
point of FLUX.2 Klein 9B Distilled:

- it samples a step-distilled, guidance-distilled checkpoint at 12 steps and CFG
  1.1-1.3 instead of its fixed 4 steps and guidance 1;
- it uses a generic `simple` schedule instead of ComfyUI's resolution-aware
  `Flux2Scheduler`;
- it generates 2016 x 2688 (5.419 MP), above BFL's 4 MP limit and well above its
  <=2 MP quality recommendation;
- it applies an experimental DyPE patch and then overwrites model sampling again
  with `ModelSamplingFlux`;
- it stacks a strong realism LoRA with an identity LoRA trained on the undistilled
  Base checkpoint, while inference uses the distilled checkpoint;
- it asks a four-step model to resolve a 200-340 word prompt containing repeated
  preservation clauses and negative constraints;
- it performs a second full diffusion pass for face identity, rather than using
  FLUX.2's native multi-reference identity capability.

The first optimization should therefore be a clean native baseline, not another
sampler, more steps, a higher CFG, or a larger canvas.

## Evidence from the exact graph

The maintained workflow currently has:

| Component | Current value | Concern |
|---|---:|---|
| Distilled model | `flux-2-klein-9b.safetensors`, BF16 | Good model file, but driven outside its native schedule |
| Text encoder | `qwen_3_8b_fp4mixed.safetensors` | Aggressive quantization is unnecessary on B200 and is an avoidable prompt-adherence variable |
| Native canvas | 2016 x 2688 = 5.419 MP | Exceeds BFL's 4 MP maximum and <=2 MP quality recommendation |
| Delivered image | 3024 x 4032 = 12.192 MP | Lanczos enlargement changes dimensions, not generative detail |
| Sampling | 12 steps, CFG 1.3, `res_2s`/`simple` in repository; recent live tests used `lcm`/`simple` | All differ from the official distilled recipe |
| Schedule patches | DyPE, then `ModelSamplingFlux` at shift 2.35 | Two overlapping non-native schedule interventions |
| Style LoRA | Instagram Reality v2 at 0.70 | Strong enough to alter anatomy, color, skin and lens rendering; no isolated validation yet |
| Identity LoRA | Alex at 0.70, face-local hook | Trained on Base 9B, deployed on Distilled 9B; hook node is experimental |
| Identity pass | scout render -> detected face mask -> second full render | Doubles generation and can change global attention even with local conditioning |
| Negative prompt | long anatomy/artifact list | At CFG 1, standard CFG reduces to conditional output, so the negative branch has effectively no leverage |
| Final prompt | 200-340 words | High chance of redundant or competing constraints in a four-step model |

The graph does normalize the reference to an exact 1008 x 1344 3:4 crop before
encoding, so the earlier stretch issue is no longer caused by the crop node.
Fisheye corners, muted colors and body distortion that remain are generated
content or conditioning effects.

## What the official implementations require

Black Forest Labs' model registry fixes FLUX.2 Klein 9B Distilled to guidance 1
and 4 steps because it is both guidance- and timestep-distilled. The official
ComfyUI distilled template uses `euler`, `Flux2Scheduler(4, width, height)`,
`CFGGuider(1)` and `SamplerCustomAdvanced`. It does not use LCM, RES, a generic
`simple` schedule, DyPE, or `ModelSamplingFlux`.

The official undistilled Base 9B model uses guidance 4 and 50 steps in BFL's
reference implementation. ComfyUI's current Base example uses Euler,
`Flux2Scheduler`, 20 steps and CFG 5, which is a faster preview recipe. Because
the Alex LoRA was trained on Base 9B, Base is the technically matched inference
checkpoint for it.

BFL supports outputs up to 4 MP, with dimensions divisible by 16, but recommends
staying at or below 2 MP for optimal quality and speed. Suitable native 3:4
canvases are:

| Canvas | Megapixels | Role |
|---|---:|---|
| 1008 x 1344 | 1.355 | Fast baseline and exact current reference size |
| 1152 x 1536 | 1.769 | Balanced native render |
| 1200 x 1600 | 1.920 | Recommended high-quality upper baseline |
| 1536 x 2048 | 3.146 | Later stress test; supported but above optimal range |

2016 x 2688 should be removed from the primary generation path.

Sources:

- [BFL model defaults and fixed distilled parameters](https://github.com/black-forest-labs/flux2/blob/main/src/flux2/util.py)
- [BFL model selection and distilled/Base distinction](https://github.com/black-forest-labs/flux2)
- [Official ComfyUI Distilled 9B workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_flux2_klein_image_edit_9b_distilled.json)
- [Official ComfyUI Base 9B workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_flux2_klein_image_edit_9b_base.json)
- [BFL resolution limits](https://help.bfl.ai/articles/8531149640-what-are-the-resolution-limits)
- [ComfyUI Flux2Scheduler implementation](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_flux.py)

## Highest-priority experiments

### 1. Establish an official Distilled baseline

Create a research copy of the workflow with:

- BF16 `flux-2-klein-9b.safetensors`;
- `qwen_3_8b.safetensors` in BF16 on B200; use FP8 mixed if startup or memory
  cost becomes material, but stop using FP4 for the quality baseline;
- full `flux2-vae.safetensors`;
- 1200 x 1600 canvas;
- Euler + `Flux2Scheduler`, exactly 4 steps, CFG 1;
- no DyPE and no `ModelSamplingFlux`;
- no LoRAs;
- empty negative conditioning;
- one concise positive narrative prompt.

This is the control. If it still produces colored speckles, the cause is below
the workflow layer: checkpoint/runtime/precision. If it does not, reintroducing
one component at a time identifies the offender.

The full BF16 Qwen3 8B encoder is an official ComfyUI artifact (16.4 GB). The
official templates use FP8 mixed as a memory-conscious default. There is no
reason to accept FP4 as an uncontrolled variable on a 180 GB B200.

- [Official ComfyUI Qwen3 8B BF16 artifact](https://huggingface.co/Comfy-Org/Flux-2-Klein-9B/blob/main/split_files/text_encoders/qwen_3_8b.safetensors)
- [Official ComfyUI Qwen3 8B FP8 mixed artifact](https://huggingface.co/Comfy-Org/Flux-2-Klein-9B/blob/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors)

### 2. Test native multi-reference identity before the identity LoRA

FLUX.2 Klein supports up to four references. Use:

- image 1: scene/pose reference, when present;
- image 2: Alex front or three-quarter face;
- image 3: Alex opposite three-quarter face;
- image 4: Alex profile or smile, chosen for the target angle.

The prompt should identify their roles directly, for example: "Keep the
composition, pose, clothing and lighting from image 1. Give the foreground adult
woman the same fictional identity as the woman in images 2 and 3."

For prompt-only generation, use two or three Alex references without a scene
reference. This removes the cross-variant LoRA, face detector, mask, and second
diffusion pass from the experiment. BFL specifically lists consistent characters
as a multi-reference use case.

- [BFL Klein multi-reference capability](https://help.bfl.ai/articles/7592221790-how-do-i-generate-quickly-with-flux-2-klein)
- [BFL multi-reference editing guidance](https://help.bfl.ai/articles/6546682167-what-is-multi-reference-editing)

### 3. Run the Alex LoRA on its matched Base checkpoint

The training configuration names
`black-forest-labs/FLUX.2-klein-base-9B`, rank/alpha 32, 1e-4 learning rate and
up to 2,000 updates. The chosen 1,500-step checkpoint was previewed with 30
steps/CFG 4 and then deployed on Distilled 9B. BFL says Base variants are the
right starting point for fine-tuning; cross-variant LoRA deployment is not an
officially defined equivalence.

Test Base 9B at 1200 x 1600 with:

- Euler + `Flux2Scheduler`;
- CFG 4;
- 30 steps for the first quality/cost comparison, then 50 for the best seeds;
- Alex LoRA at 0.40, 0.55 and 0.70;
- Instagram Reality disabled;
- no DyPE;
- no face-local second pass for the first test.

If Base + Alex is clean globally, test face-local conditioning afterward. If it
is already waxy or speckled, masking cannot cure the learned texture.

- [BFL Base 9B model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9B)
- [BFL fine-tuning guidance](https://help.bfl.ai/articles/7108141705-can-i-run-or-fine-tune-flux-2-klein-locally)

### 4. Isolate every LoRA

Never evaluate both realism and identity LoRAs for the first time in the same
render. With a fixed eight-seed set, compare:

1. no LoRA;
2. Instagram Reality at 0.25;
3. Instagram Reality at 0.45;
4. Instagram Reality at 0.70;
5. Alex alone at 0.40/0.55/0.70 on Base;
6. only after those pass, the best pair at reduced strengths.

The creator's Instagram Reality description says trigger words such as
"Instagram photo", "iPhone photo" and "amateur photo" may help, not that they
are mandatory. Repeating all three in every prompt can bias the output toward a
processed social-media look. Test one phrase at a time.

### 5. Simplify the final prompt

The current pipeline performs a 180-300 word visual analysis, a 60-140 word
rewrite, then forces a 200-340 word final prompt. That is useful as an internal
scene inventory, but the final model input repeatedly states preservation,
anatomy, borders, color, focus and removal rules.

Keep the detailed Qwen analysis internally, then compile a single positive
description of the final visible state:

- roughly 80-140 words for reference edits;
- roughly 60-120 words for prompt-only scenes;
- first sentence: subject, action and requested change;
- second: composition and camera;
- third: lighting, exposure and color;
- fourth: clothing and important scene objects;
- one short final preservation sentence for reference mode.

Avoid keyword piles such as "8K, hyperreal, perfect skin, extreme detail" and
avoid contradictory optics such as "0.5x ultra-wide fisheye" together with
"normal rectilinear perspective". Use BFL's recommended narrative style.

- [BFL Klein prompting guide](https://help.bfl.ai/articles/7592221790-how-do-i-generate-quickly-with-flux-2-klein)

## Identity LoRA diagnosis and retraining path

The 30-image Alex dataset is identity-consistent, but visually homogeneous:

- every image is a clean 1024 x 1024 synthetic portrait;
- most are head-and-shoulders with centered composition;
- hair, skin texture, depth of field and daylight rendering are very similar;
- only two images are full body;
- there are no genuinely noisy phone snapshots, hard flash photos, difficult
  mixed light, partial occlusions, or varied camera pipelines;
- the selected checkpoint represents about 50 passes over the 30-image set;
- there are no regularization images.

This makes style leakage likely. The model can learn "Alex" together with smooth
skin, centered portrait framing, soft daylight and shallow background blur.

Before retraining, compare any retained checkpoints at steps 750, 1000, 1250
and 1500. An earlier checkpoint may keep enough identity with less texture bleed.
If retraining is necessary:

- keep Base 9B as the training and inference checkpoint;
- add varied high-quality images across phone daylight, indoor mixed light,
  direct flash, low light, wide/normal lenses, close/waist/full-body framing;
- raise full-body representation so the face is learned at small scale;
- vary hairstyle, clothing, background and camera treatment while keeping the
  facial identity stable;
- add regularization images to preserve the base model's general rendering;
- test rank 16 as well as 32;
- test a lower learning rate such as 5e-5;
- save and score checkpoints earlier rather than assuming the last one wins.

SimpleTuner's Flux guidance notes that image artifacts are readily absorbed by
Flux LoRAs and that regularization data can help preserve the base model.

- [SimpleTuner Flux training guidance](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX.md)

## Face-local conditioning

The current spatial hook is a valid ComfyUI mechanism, but
`CreateHookLoraModelOnly` is explicitly marked experimental in ComfyUI core. It
attaches the LoRA hook to masked conditioning; it is not pixel compositing. The
second sampler still performs a complete diffusion trajectory, so attention can
change pose, head size, lighting and background outside the visible mask.

If the LoRA remains necessary:

- reduce the 1200 x 1600 face-mask growth from 48 px to about 24-32 px;
- reduce blur to roughly 17-23 px with sigma 6-8;
- include enough forehead/jaw transition to avoid a face-shaped seam, but avoid
  hair, ears and background where possible;
- test hook keyframes that fade identity strength during the final denoising
  quarter, allowing the base model to finish skin and lighting;
- compare the final render against the scout, not only against the source.

With a four-step distilled model, hook scheduling is coarse. It is more useful on
Base with 20-50 steps.

- [ComfyUI hook implementation](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_hooks.py)
- [ConditioningSetProperties documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetProperties/en.md)

## Hands and anatomy

Extra digits are not evidence that the sampler needs 50 steps when the checkpoint
is distilled for four. Twelve or fifty off-schedule steps cannot add information
the distilled trajectory was not trained to use. The efficient strategy is:

1. generate several candidates at native settings;
2. reject failures before upscaling;
3. repair a selected image with a hand-sized inpaint mask and enough wrist/arm
   context;
4. keep inpaint denoise low enough to preserve scene lighting;
5. upscale only the accepted final.

OpenPose or depth conditioning helps global pose and scene geometry. It does not
guarantee five correctly articulated fingers. Negative prompts also cannot do
that at CFG 1.

## Resolution and 4K delivery

The diffusion model should solve composition and anatomy at 1200 x 1600. The
delivery branch should then enlarge the accepted image to 3024 x 4032.

Test these in order:

1. Lanczos only: perfect fidelity, no invented detail;
2. Real-ESRGAN/RealESRNet x4, then downsample to 3024 x 4032: sharper, but inspect
   hair, eyes, jewelry and repeated architecture for invented texture;
3. a generative restoration model only if the first two are insufficient.

Real-ESRGAN is a blind restoration model and can introduce tile inconsistencies;
its own repository documents this caveat. SUPIR and SeedVR2 can invent plausible
detail, but that also means they can alter identity, skin and small anatomy. The
main pipeline should therefore keep a deterministic upscale option and never use
face enhancement by default.

- [Real-ESRGAN official repository and paper](https://github.com/xinntao/Real-ESRGAN)
- [SUPIR official repository and paper](https://github.com/Fanghua-Yu/SUPIR)
- [Official SeedVR2 ComfyUI implementation](https://github.com/comfyorg/comfyui_seedvr2)

For an Instagram feed, the published asset is commonly displayed well below
3024 x 4032. Downsampling a clean 1200 x 1600 or 1536 x 2048 master can look more
photographic than filling a 12.2 MP file with generated microtexture.

## Color and photographic finish

Do not train a color LoRA to fix reference color drift. A style LoRA changes the
whole image distribution and can worsen anatomy. For reference mode, add an
optional post-generation color-match branch instead:

- match output luminance/chroma statistics to the cropped reference in Lab;
- expose strength from 0 to 1 and begin around 0.25-0.40;
- protect skin with a soft mask if global matching produces an unwanted cast;
- compare this against no color matching using the slider.

For prompt-only images, describe one coherent camera treatment. Slight luminance
noise and restrained compression can reduce the sterile synthetic finish, but
should be applied after anatomy and lighting pass. Grain cannot rescue malformed
geometry or plastic skin.

## DyPE and AnyFlow

DyPE is a research method for resolution extrapolation, and the installed Flux2
node is a third-party port. It is not part of BFL's native Klein recipe. Because
FLUX.2 already supports up to 4 MP and the quality target should start below 2
MP, DyPE adds risk without a demonstrated need. Revisit it only after the native
baseline is stable, as an isolated experiment at 1536 x 2048 or above.

Prodia's recent AnyFlow work does not apply to this workflow. It is a distillation
LoRA for FLUX.3 Klein Base, trained at large scale to permit arbitrary step
counts. It is neither a high-resolution fix nor a drop-in sampler for FLUX.2
Klein 9B.

- [DyPE paper](https://arxiv.org/abs/2510.20766)
- [Installed FlowMatching Upscaler repository](https://github.com/ttulttul/ComfyUI-FlowMatching-Upscaler)
- [Prodia AnyFlow research](https://prodia.com/research/anyflow)

## Controlled test matrix

Use the same eight seeds for every row. Generate in two batches of four. Save the
compiled prompt and all settings into PNG metadata. Rate images blind before
revealing the row name.

| ID | Model / sampling | Identity | Style | Resolution | Purpose |
|---|---|---|---|---:|---|
| D0 | Distilled, Euler, Flux2Scheduler, 4, CFG 1 | none | none | 1200 x 1600 | Official control |
| D1 | D0 + scene reference | none | none | 1200 x 1600 | Native reference quality |
| D2 | D1 + 2-3 Alex reference images | native multi-ref | none | 1200 x 1600 | Identity without LoRA |
| D3 | D2 | native multi-ref | Instagram 0.25/0.45 | 1200 x 1600 | Lowest useful style strength |
| B0 | Base, Euler, Flux2Scheduler, 30, CFG 4 | none | none | 1200 x 1600 | Base quality control |
| B1 | B0 | Alex LoRA 0.40/0.55/0.70 | none | 1200 x 1600 | Matched LoRA test |
| B2 | B0 | native multi-ref | none | 1200 x 1600 | Base multi-ref comparison |
| B3 | best Base row, 50 steps | best identity route | best isolated style | 1200 x 1600 | Quality ceiling within Klein |
| R0 | best generation row | unchanged | unchanged | upscale to 3024 x 4032 | Lanczos vs RealESRNet/Real-ESRGAN |

For each image, score 0-2 on:

- natural anatomy and fingers;
- Alex identity;
- skin and hair texture;
- lighting consistency across face/body/scene;
- reference composition and color fidelity;
- absence of speckles, lines, halos and repeated micro-patterns;
- camera plausibility;
- prompt compliance.

Reject a configuration based on the eight-seed distribution, not one favorable
fixed seed. The winning row should improve the median and reduce catastrophic
failures.

## Recommended implementation order

1. Add a separate `realism-native-distilled` research workflow. Do not overwrite
   the maintained workflow yet.
2. Implement D0 and verify the official sampling graph exactly.
3. Add D1 and D2 native multi-reference identity.
4. Add the Base 9B branch and B0/B1 tests.
5. Shorten the final compiled prompt and repeat only the winning branches.
6. Select the identity route: native multi-ref or matched Base LoRA.
7. Add deterministic 4K delivery and optional color matching.
8. Keep hand repair as a separate post-selection workflow.
9. Only then consider DyPE, generative upscaling, another style LoRA, or LoRA
   retraining.

## Reproducibility checks before testing

The repository-selected Alex checkpoint is 165,704,328 bytes with SHA-256
`072f0184a52cc00de330e7f863951d44120a2412a9369d8ba0c76118d2e345ad`.
The current local desktop ComfyUI file is 332,548,896 bytes with SHA-256
`c5a4682e7055e640dec98bb3e2946bcd8068b6e5a9ce18629431db5f02398244`.
They are not the same file. RunPod and local comparisons are invalid until every
test environment verifies the repository manifest.

The BF16 model checkpoint currently downloaded by the project matches SHA-256
`0975d6b77b5f510b99547d6724a208e36527df654e8f6134f59ece3f9f30da58`,
the same BF16 single-file artifact mirrored across Hugging Face repositories.

## Model ceiling

If D0/B0 are clean but still fail the desired realism rate, the remaining limit
is primarily the model rather than ComfyUI. BFL positions Klein for real-time
iteration, Base for customization, and FLUX.2 Dev for maximum open-weight
quality. On a B200, a Dev multi-reference benchmark is technically feasible and
should be run before spending more time stacking patches onto Klein. A small API
comparison with FLUX.2 Pro or Max can also establish the current production
quality ceiling.

- [BFL model chooser](https://help.bfl.ai/articles/6122710168-which-flux-2-model-should-i-choose)

One operational issue is separate from image quality: BFL states that local
FLUX.2 Klein 9B uses the FLUX Non-Commercial License, and commercial local use
requires a license; the hosted API includes commercial rights. This matters for
a monetized publishing pipeline and should be resolved before production.
