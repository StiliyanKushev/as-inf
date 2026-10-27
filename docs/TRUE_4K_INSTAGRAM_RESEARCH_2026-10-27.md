# True 4K Instagram-style image generation research

Research date: 2026-10-27

## Objective

Build a reproducible ComfyUI workflow that produces portrait photographs which look like ordinary high-quality phone/Instagram photos, preserve the fictional Alex Sparks identity, and contain genuinely generated detail at a final 3024 × 4032 output.

For this project, **true 4K** means the final diffusion canvas is approximately 12–16 megapixels. A small center crop is acceptable; enlarging a 1–4 MP image with Lanczos, Real-ESRGAN, or another resizer is not.

No model can guarantee that every image will be indistinguishable from a real photograph. The workflow must therefore expose failures instead of hiding them, generate several drafts, and use a measured selection and repair process.

## Main conclusion

The current FLUX.2 Klein 9B workflow is no longer the best base. The first **local, reproducible ComfyUI implementation** should use **FLUX 3 Image Klein distilled in BF16**, with its official Qwen3.5 prompt upsampler and Qwen3-VL-4B encoder. It supports text-to-image, editing, up to ten reference images, bounding-box layout, and native generation up to 4K in one model.

For absolute output quality, local Klein must be compared with two hosted native-4K models: **Nano Banana 2.1** and **full FLUX 3 Image**. Nano Banana 2.1 currently ranks above Klein in general blind preference and supports more references; full FLUX 3 is the higher-capacity version of the same family. Hosted moderation, lack of a portable LoRA, and separate API billing may make either unsuitable for the final system, but excluding them without a controlled comparison would not satisfy the “best possible” requirement.

The exact portrait canvas should be **3072 × 4096**. This is a standard 3:4, 12 MP (where 1 MP is 1024² pixels) generation canvas. A center crop of 24 pixels from each side and 32 pixels from the top and bottom produces 3024 × 4032 without resampling. Every retained output pixel was therefore synthesized on the high-resolution diffusion canvas.

The strongest practical pipeline is:

1. Generate eight 1 MP drafts for composition, anatomy, and expression.
2. Select one draft.
3. Generate the final image directly at 3072 × 4096, using the selected draft for composition and two or three curated Alex references for identity.
4. Crop to 3024 × 4032 without scaling.
5. If required, perform one bounded local edit for a hand, face, or object while preserving the rest of the pixels.

This is not an upscale workflow. The draft only guides the final full-resolution diffusion pass.

## Model assessment

| Model | Local/open | Native output | Identity/editing | Best use here | Decision |
|---|---:|---:|---|---|---|
| FLUX 3 Image Klein distilled | Yes | Up to 4K | Up to 10 references; boxes | Main local generator | Test first |
| FLUX 3 Image Klein Base | Yes | Up to 4K | Up to 10 references; boxes; trainable | Quality control and Alex LoRA training | Test against distilled |
| Full FLUX 3 Image API | No | Native 4K tier, about 16 MP | Up to 10 references; pixel-preserving edits | Likely highest-quality FLUX result | Test later with API credentials |
| Nano Banana 2.1 | No | Native 4K; 3584 × 4800 at 3:4 | Up to 14 references | Strong hosted quality/identity control | Valuable external control |
| Krea 3 | No | Native 2K | Up to 6 references; editing-first | Fast identity-preserving edits | Repair/control only |
| Qwen-Image 3.0 Pro | No | Up to 4 MP / native 2K class | Unified generation and editing | Strong hosted prompt adherence | Not a direct-4K final |
| Qwen-Image 2.1 | Yes | Native 2K | Up to 10 references and masks | Strong open model, but not a direct-4K final | Secondary control |
| Krea 2 Turbo | Yes | Up to 2K | LoRA ecosystem | Strong aesthetics and skin rendering | Secondary 2K control |
| Z-Image Turbo | Yes | Recommended up to about 2K area | Text-to-image; identity needs LoRA | Strong pure-photorealism control | Secondary realism control |
| Existing FLUX.2 Klein 9B | Yes | Existing workflow uses staged enlargement | Existing Alex LoRA | Baseline only | Retire as primary |

The current Artificial Analysis blind-preference leaderboard places Nano Banana 2.1 at 1176 ± 12, full FLUX 3 Image around 1117, FLUX 3 Image Klein at 1043 ± 12, and Qwen-Image 2.1 at 1042 ± 12. FLUX.2 Klein 9B is 929 ± 10. These scores measure general preference rather than Instagram realism, but the gap is large enough that more tuning of FLUX.2 is a poor first investment.

RealBench V1 is useful but older: Z-Image Turbo was judged real 46% of the time, tied with GPT Image 2 and ahead of FLUX.2 Max at 41%. It does not yet include FLUX 3 or Qwen-Image 2.1, so it cannot choose the final model for us. It justifies keeping Z-Image as a realism control.

## Exact FLUX 3 configurations to test

### Distilled generation baseline

- Diffusion model: `flux3-image-klein-bf16.safetensors`
- Text encoder: `qwen3vl_4b_bf16.safetensors`
- VAE: `flux2-vae.safetensors`
- Prompt upsampler: official Qwen3.5-9B FLUX 3 prompt upsampler; use BF16 where storage permits, W4A8 only as an efficiency fallback
- Steps: 16
- CFG: 1 / no classifier-free guidance
- Sampler: Euler
- Scheduler: Simple
- Weight precision: BF16
- Draft canvas: 896 × 1200 or the closest official 3:4 1 MP output
- Final canvas: 3072 × 4096
- Batch: eight drafts; one final image at a time

### Base quality control

- Diffusion model: `flux3-image-klein-base-bf16.safetensors`
- Same encoder, VAE, and prompt upsampler
- Steps: 50
- CFG: 3.5 initially; 4.0 is the reference-code recommendation and should be one controlled comparison
- Sampler: Euler
- Scheduler: Simple
- Canvas: 3072 × 4096

The official ComfyUI templates ship quantized weights for broad hardware compatibility but explicitly recommend BF16 above 24 GB VRAM. Our H200/B200 target has enough memory, so quality testing should not begin with INT8, FP8, or NVFP4.

More steps are not a general quality knob. Distilled Klein is trained for 16 steps and no CFG. Base is trained for roughly 50 steps with CFG. Running distilled at 50 steps or raising its CFG is not equivalent to using Base and can make the result worse.

## Prompting for photographs instead of synthetic renders

The official FLUX 3 prompt-upscaler instructions reveal several high-impact rules:

- Start a real scene as `Full-color outdoor photograph`, `Full-color indoor photograph`, `Studio photograph`, or `Close-up photograph`.
- Do not call an actual photo `photorealistic`, `ultra-realistic`, or `hyper-realistic`. The official instructions say this wording indexes a synthetic-render cluster.
- Remove appraisal words such as `stunning`, `flawless`, `premium`, `cinematic`, `highly detailed`, and `8K`.
- Describe observable facts rather than claiming an image is candid, natural, authentic, or imperfect.
- Describe out-of-focus background regions only as masses, colors, silhouettes, or blurred figures. Naming tiny details forces the model to resolve every plane, which the official instructions identify as a recognizable AI signature.
- Keep the background around one sixth of the caption. Spend most of the prompt on the subject and immediate surroundings.
- Give explicit frame-relative placement and a physically consistent camera viewpoint.

For an arm's-length selfie, use a plausible front-facing phone camera description such as `front-facing phone camera, roughly 23–26 mm equivalent, held at arm's length`. An iPhone `0.5×` camera is normally the rear ultrawide camera, so combining `0.5×`, `front camera`, and an invisible phone creates contradictory geometry.

A useful short input for the prompt upsampler is concrete and restrained:

> Full-color outdoor phone photograph of Alex Sparks seated at a small European café table, taken with a front-facing phone camera held at arm's length. Her face and upper torso occupy the center of the 3:4 frame. Morning daylight comes from frame-left. Her raised hand is completely visible and makes a two-finger peace sign. The café behind her falls out of focus into green foliage, tan walls, and several indistinct chairs. Moderate phone sharpening and compression, with no beauty filter.

The prompt upsampler should write the long caption. Our workflow should expose its output in a preview node so we can diagnose unwanted additions.

## Identity strategy

### First choice: reference conditioning

Use two or three different Alex images from the existing dataset:

- one neutral frontal view;
- one three-quarter view with the desired expression range;
- one profile or wider view if the pose needs it.

The composition draft or scene reference is a separate reference. The expanded instruction must state which references supply Alex's face and which supplies composition. Multiple nearly identical identity references add little information and can overconstrain expression.

This should be tested before loading any identity LoRA. Reference conditioning is local to the request, while a LoRA modifies the model globally and can leak its training background, lighting, color, skin treatment, or portrait crop into every scene.

### If a LoRA is still required

The existing FLUX.2 Alex LoRA is not the correct adapter for FLUX 3. Retrain on **FLUX 3 Image Klein Base** and validate it on distilled Klein.

Starting recipe, based on current official/community-supported FLUX 3 trainers:

- Trainer: AI Toolkit, SimpleTuner, or the official Diffusers DreamBooth/LoRA scripts
- Base: `black-forest-labs/flux-3-image-klein-base`
- Resolution buckets: 768 and 1024; preserve aspect ratio
- Rank/alpha: 32/32 starting point
- Learning rate: `1e-4` starting point
- Caption dropout: about 5%
- Cache VAE latents and text embeddings
- Use regularization images and REPA where supported
- Save checkpoints frequently and compare identity versus style leakage rather than choosing the last checkpoint

The current 30-image Alex dataset is visually consistent but too homogeneous. Before retraining, reject near-duplicates and add varied focal lengths, expressions, head turns, indoor/outdoor illumination, hair arrangements, and some upper-body views. Captions should name variable properties such as clothing, lighting, and background so the LoRA does not bind them to the trigger token. Training at 4K is unnecessary; identity is learned at lower resolution, while the base model supplies final high-frequency detail.

Do not stack an Instagram/realism LoRA during the baseline. If one is later evaluated, test it at low strength against identical seeds and inspect skin, hair, fabric, hands, and background separately. A LoRA that improves the face while creating colored speckles or waxy texture fails the acceptance test.

## Resolution and high-frequency detail

At 3:4, ComfyUI's built-in `ResolutionSelector` computes:

- 1 MP: approximately 896 × 1200
- 4 MP: approximately 1792 × 2400
- 8 MP: approximately 2512 × 3344
- 12 MP: exactly 3072 × 4096
- 16 MP: approximately 3552 × 4736

The first true-4K target is 12 MP. It minimizes the distance from 3024 × 4032 and avoids asking the model to solve a larger 16 MP canvas before we know 12 MP is stable.

The output path must not contain `ImageScale`, Lanczos, Real-ESRGAN, Ultimate SD Upscale, DyPE, FlowMatching Progressive Upscaler, or any hidden resize before the final save. The only allowed geometry operation is a center crop from 3072 × 4096 to 3024 × 4032.

Native 4K may still produce incoherent tiny background faces because the model must coordinate roughly 49,000 image tokens at 3072 × 4096. The prompt should keep background people blurred and nonspecific. The main subject should be large enough that face and hands receive sufficient pixels.

Tiled diffusion is a fallback, not the baseline. Tile methods can introduce seams, duplicated objects, mismatched lighting, and style changes because each tile is partially regenerated. The older DyPE/FlowMatching stack also conflicts with the current ComfyUI model patcher in our installation (`attribute 'sigmas' already exists`). FLUX 3 makes that workaround unnecessary unless native 4K fails.

## Anatomy and repair

Six fingers are a semantic generation failure, not a lack of pixels. More steps alone will not reliably repair them.

The workflow should reduce the failure rate by:

- using a clear pose with hands separated from hair and patterned backgrounds;
- keeping every important hand fully inside the frame;
- selecting from multiple 1 MP drafts before the expensive 4K pass;
- using a selected draft as composition guidance for the final pass;
- avoiding complex crossed fingers unless the gesture is essential.

For the remaining failures, use a bounded FLUX 3 edit at native resolution. Give the hand a source and target box, ask for the exact end state, and preserve every unedited region. A hard-mask inpaint remains available, but reference-aware bounded editing should be tried first because it can match light and perspective without repainting the entire face or body.

## Color, lens, and “Instagram” appearance

The earlier muted colors and squeezed bodies were workflow problems rather than proof that a realism LoRA was missing:

- stretching an arbitrary reference directly to 3:4 changes body geometry;
- fisheye wording encourages curved borders and black corners;
- describing the entire background at equal precision destroys plausible depth of field;
- style LoRAs can impose their own grading and skin texture.

Reference images must be center/interactive cropped to 3:4 before conditioning; never stretched. The generated canvas must also be 3:4 from the start.

The baseline should ask for observable phone processing: restrained local contrast, moderate sharpening, ordinary highlight roll-off, and mild compression. Avoid `HDR`, `vivid`, `cinematic color grade`, `perfect skin`, and blanket film grain. If a small final phone-like finish helps in blind tests, add it after generation as a reversible branch and keep the untouched output.

## Hosted alternatives worth measuring

Two hosted models are serious controls, even if the final workflow remains local:

1. **Full FLUX 3 Image API** generates directly in a 4K tier of about 16 MP, accepts references, and advertises pixel-preserving edits. BFL shows a 5456 × 3072 image generated entirely by the model. Current list price is $0.607 per 4K image.
2. **Gemini Nano Banana 2.1** generates 3:4 at 3584 × 4800 in its 4K tier and accepts up to fourteen reference images. Current standard API cost is about $0.113 per 4K image.

Their moderation and service terms may restrict some content. They also do not provide an identity LoRA path. They remain valuable because a small blinded comparison will tell us whether more RunPod optimization is actually competitive with the best hosted result.

## Controlled experiment matrix

Use one restrained café selfie prompt and one full-body outdoor prompt. For each configuration, keep the prompt, references, crop, and a five-seed set fixed.

| Test | Model and method | Purpose |
|---|---|---|
| A | FLUX 3 distilled BF16, 1 MP, PUP, no refs | Prompt/style baseline |
| B | Same, three Alex refs | Identity effect and style leakage |
| C | Same, draft/composition ref + three Alex refs | Composition and identity together |
| D | FLUX 3 distilled BF16, direct 3072 × 4096 | Native-4K stability |
| E | D with selected 1 MP draft + Alex refs | Proposed production path |
| F | FLUX 3 Base BF16, 50 steps, CFG 3.5 | Base-versus-distilled quality |
| G | F at CFG 4.0 | Official-reference CFG check |
| H | Z-Image Turbo at native recommended size | Pure-realism control, not final 4K |
| I | Qwen-Image 2.1 at native 1792 × 2400 | Open-model identity/detail control |
| J | Full FLUX 3 API 4K | Hosted true-4K control, credentials required |
| K | Nano Banana 2.1 4K | Hosted true-4K control, credentials required |

Do not add LoRAs, face restoration, cleanup nodes, or sharpening until A–G identify a stable base. Each additional component then gets an isolated same-seed A/B test.

## Acceptance criteria

Every candidate must be inspected at full resolution and at 200% crops.

- File dimensions are 3024 × 4032 after crop, with no resampling in provenance.
- The face matches Alex across seeds without inheriting a fixed background, makeup, lighting, or crop.
- Five fingers where visible; coherent wrists, elbows, teeth, ears, jewelry, fabric seams, chair legs, and railings.
- Skin contains scale-consistent pores and fine variation without colored confetti, repeated pore grids, waxy patches, or face-restoration halos.
- Hair strands do not merge into jewelry, clothing, or architecture.
- Background resolution matches optical depth of field; distant people are indistinct rather than malformed miniature portraits.
- Highlight clipping, shadows, lens perspective, and depth of field are physically compatible.
- No squeezed anatomy, fisheye black corners, tile seams, doubled objects, or obvious upscale texture.
- In a shuffled comparison, the result should beat the current FLUX.2 workflow on realism, identity, anatomy, and detail independently.

The best workflow is the one with the highest usable-image rate, not the most impressive single seed.

## Sources

- [FLUX 3 Image Klein official repository](https://github.com/black-forest-labs/flux-3-image-klein)
- [FLUX 3 Image Klein ComfyUI weights](https://huggingface.co/black-forest-labs/flux-3-image-klein-comfy)
- [FLUX 3 Image Klein Base model card](https://huggingface.co/black-forest-labs/flux-3-image-klein-base)
- [Official FLUX 3 prompt-upscaler instructions](https://github.com/black-forest-labs/flux-3-image-klein/blob/main/src/flux3/pup_prompts_external_vlm.json)
- [Full FLUX 3 Image model and native-4K example](https://bfl.ai/models/flux-3-image)
- [BFL pricing and resolution tiers](https://bfl.ai/pricing)
- [ComfyUI ResolutionSelector implementation](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_resolution.py)
- [Hugging Face FLUX 3 Diffusers integration](https://github.com/huggingface/blog/blob/main/flux-3.md)
- [Official Diffusers FLUX 3 LoRA guide](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/README_flux3_klein.md)
- [AI Toolkit model support](https://github.com/ostris/ai-toolkit)
- [SimpleTuner FLUX 3 LoRA guide](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX3_IMAGE.md)
- [Qwen-Image 2.1 official repository](https://github.com/QwenLM/Qwen-Image-2.1)
- [Krea 2 official prompting guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md)
- [Krea 3 release and native-2K limits](https://www.krea.ai/blog/introducing-krea-3)
- [Z-Image official repository](https://github.com/Tongyi-MAI/Z-Image)
- [Gemini Nano Banana 2.1 image generation documentation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Qwen Image API resolution documentation](https://help.aliyun.com/en/model-studio/qwen-image-generation-and-editing-api-reference)
- [Artificial Analysis image leaderboard](https://artificialanalysis.ai/embed/text-to-image-leaderboard/leaderboard/text-to-image)
- [ImageBench RealBench V1](https://imagebench.ai/realbench-v1)
