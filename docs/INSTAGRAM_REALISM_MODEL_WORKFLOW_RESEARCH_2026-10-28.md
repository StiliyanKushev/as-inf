# Research: highest-realism Instagram-style persona images

Research date: 2026-10-28

This report answers a narrower question than the earlier native-4K study: which
current model and workflow is most likely to produce casual photographs of the
fictional Alex Sparks persona that look like ordinary real Instagram photos?
The priorities are human-perceived realism, recurring identity, anatomy,
camera coherence, and genuine high-resolution output. Speed and compute cost
are secondary.

## Decision

There is no single winner across every constraint.

1. **Highest raw generation and editing quality:** GPT Image 2.5 Sunburst at
   `max` quality. It is currently first on Arena's overall, photorealistic, and
   portrait leaderboards, and first for photorealistic image editing. It is the
   strongest control for judging whether a local workflow is actually
   competitive. Its output ceiling is 8,294,400 pixels with a 3,840-pixel edge,
   so it cannot directly produce a 3024×4032 12.2 MP portrait. An exact 3:4
   request near its limit is 2448×3264.

2. **Best fit for a true high-resolution recurring persona:** Gemini Nano
   Banana 2.1 at `4K`, `3:4`, with high thinking and four carefully selected
   Alex references. It outputs 3584×4800 (17.2 MP), explicitly supports
   character consistency, and accepts up to four character references within a
   fourteen-image request. It can be reduced to 3024×4032 by downsampling; no
   enlargement is involved. It ranks fourth in the current photorealistic
   Arena and fifth for portraits, behind GPT Image 2.5 but far ahead of the old
   FLUX.2 Klein setup.

3. **Best self-hosted and fine-tunable choice:** FLUX 3 Image Klein Base BF16
   with its official prompt upsampler, three identity references, 50 steps,
   Euler/simple, and CFG 3.5–4.0. Artificial Analysis currently places FLUX 3
   Klein, Qwen-Image-2.1, and Fibo 2.0 in a statistical tie at the top of its
   open-weight leaderboard. Our own first Base run produced the most believable
   local result. It remains much weaker than the best hosted models in general
   preference rankings, but it supports native 4K, local references, LoRA
   training, unrestricted infrastructure, and reproducible seeds.

The recommended production design is therefore a **three-backend ComfyUI
workflow**, not a commitment to one model before blind testing:

- Nano Banana 2.1 is the provisional final-render default.
- GPT Image 2.5 Sunburst is the absolute-quality benchmark and precision editor.
- FLUX 3 Klein Base is the private/local fallback and LoRA research branch.

## Evidence

### Current independent rankings

Arena's 26 October 2026 photorealistic category is based on more than three
million pairwise votes. Its leading models are:

| Rank | Model | Photorealistic score |
|---:|---|---:|
| 1 | GPT Image 2.5 Sunburst | 1433 ± 8 |
| 2 | GPT Image 2.5 Flare | 1415 ± 8 |
| 3 | GPT Image 2 | 1378 ± 6 |
| 4 | Gemini Nano Banana 2.1 | 1337 ± 14 |
| 5 | MAI-Image-2.6 | 1330 ± 7 |
| 6 | Grok Imagine Image 2.0 | 1311 ± 10 |
| 11 | Seedream 5.0 Pro | 1274 ± 6 |
| 13 | Qwen-Image-3.0-Pro | 1261 ± 10 |

The portrait category has the same top three, with Sunburst first at 1461 ± 10
and Nano Banana 2.1 in the 4–8 confidence band. These are preference rankings,
not a guarantee of identity accuracy or high-resolution stability, but their
scale makes them more useful than promotional sample galleries.

ImageBench RealBench asks whether humans mistake model outputs for real
photographs. Its latest published snapshot predates the newest models, so it
cannot rank GPT Image 2.5 or Nano Banana 2.1. It is still useful methodologically:
Nano Banana Pro reached 53% “real” votes, while GPT Image 2 reached 46%.

The earlier CHI photorealism study collected 749,828 observations from 50,444
participants. It found that scene complexity, visible artifacts, viewing time,
prompt choice, and human curation all materially affect whether an image is
recognized as synthetic. Portraits were harder to detect than full-body or
group scenes. The artifact taxonomy matches our failures: anatomical errors,
plastic or overly cinematic styling, broken object function, inconsistent
shadows/reflections/perspective, and implausible social context.

Sources:

- [Arena photorealistic leaderboard](https://arena.ai/leaderboard/image/text-to-image/photorealistic)
- [Arena portrait leaderboard](https://arena.ai/leaderboard/image/text-to-image/portraits)
- [ImageBench RealBench V1](https://imagebench.ai/realbench-v1)
- [Characterizing Photorealism and Artifacts in Diffusion Model-Generated Images](https://arxiv.org/abs/2502.11989)
- [Artificial Analysis open-weight leaderboard](https://artificialanalysis.ai/image/leaderboard/text-to-image/open-weights)

### Model comparison for this project

| Model | Human realism evidence | Native output | Identity/reference path | Fine-tune | Main limitation |
|---|---|---|---|---|---|
| GPT Image 2.5 Sunburst | #1 photorealism and portraits | Up to 8.29 MP, 3840 max edge | Multiple image inputs; improved subject preservation | No | Cannot make exact 3024×4032; API moderation; expensive at `max` |
| Nano Banana 2.1 | #4 photorealism, #4–8 portraits | 3584×4800 at 3:4 | Up to 4 character refs, 14 total; multi-turn | No | Hosted only; SynthID; identity must be validated across seeds |
| MAI-Image-2.6 | #5 photorealism | Up to roughly 1.5K | Multi-reference editing | No public local weights | Too small for final true 4K |
| Grok Imagine 2.0 | #6 photorealism | Up to 2K | Up to 5 edit refs | No | Too small for final true 4K |
| Seedream 5 Pro | #11 photorealism | Service-dependent | Multi-image fusion and editing | No | Weaker portrait evidence and less reproducible integration |
| Full FLUX 3 Image API | #13 overall on Artificial Analysis | About 16 MP; demonstrated 5456×3072 | Up to 10 references; precise edits | No | Lower general ranking; $0.607 per 4K output |
| FLUX 3 Klein Base | Top statistical group among open weights | Native 4K | Up to 10 refs; LoRA training | Yes | Local 4K is slow; first test was soft; needs more seeds |
| Qwen-Image-2.1 | Top statistical group among open weights | Native 2K | Up to 16 reference slots in ComfyUI | Yes | Above-trained-size 4K loses prompt adherence; not the final 4K choice |
| SDXL / SD 3.5 | Mature ControlNet/LoRA ecosystem | About 1K native | Excellent legacy tooling | Yes | Current generation quality is far behind frontier models |

MAI, Grok, and Seedream deserve a small benchmark sample, but their resolution
ceilings or weaker project fit prevent them from being the default. SDXL is
still useful when a specific ControlNet or community LoRA is indispensable; it
is not the route to the highest current realism.

Sources:

- [GPT Image 2.5 prompting and resolution limits](https://developers.openai.com/api/docs/guides/image-prompting)
- [GPT Image 2.5 launch and reference preservation](https://openai.com/index/introducing-chatgpt-images-2-5/)
- [Nano Banana 2.1 model page](https://ai.google.dev/gemini-api/docs/models/gemini-nano-banana-2.1)
- [Gemini image generation, references and exact dimensions](https://ai.google.dev/gemini-api/docs/image-generation)
- [MAI-Image-2.6 announcement](https://microsoft.ai/news/pushing-the-quality-cost-frontier-with-mai-image-2-6/)
- [Grok Imagine Image 2.0 documentation](https://docs.x.ai/developers/models/grok-imagine-image-2.0)
- [Seedream 5 Pro announcement](https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro)
- [FLUX 3 Image native-4K and multi-reference capabilities](https://bfl.ai/models/flux-3-image)
- [FLUX 3 Klein official repository](https://github.com/black-forest-labs/flux-3-image-klein)
- [Qwen-Image-2.1 ComfyUI guide](https://github.com/Comfy-Org/docs/blob/main/tutorials/image/qwen/qwen-image-2-1.mdx)

## Recommended workflow

### 1. Create one controlled identity pack

Use four images for hosted-model tests:

1. neutral front head-and-shoulders view;
2. left three-quarter view;
3. right three-quarter or clean side profile;
4. waist-up or full-body reference showing stable body proportions.

Each image should contain only Alex, without sunglasses, hands covering the
face, extreme makeup, colored stage light, heavy depth-of-field blur, or a
repeated background. Crop the face large enough to be useful while retaining
hairline, ears, jaw, neck, and shoulders. Keep the selected pack immutable
during the benchmark. Adding many near-duplicate faces can overconstrain pose
and style; four diverse views are more informative than fourteen repetitions.

For FLUX 3, begin with the same first three views through
`ReferenceMultiLatent`. Do not apply the old FLUX.2 Alex LoRA to FLUX 3. A new
FLUX 3 Base LoRA should be trained only if references fail a five-seed identity
test.

### 2. Separate scene intent from identity

The generation request should contain five explicit blocks:

1. **Identity:** the woman in the identity references, preserving facial
   structure, hairline, eye spacing, jaw, nose, and body proportions.
2. **Scene:** location, activity, nearby objects, and social context.
3. **Camera:** phone held at arm's length or another named viewpoint, sensible
   equivalent focal length, camera height, subject distance, and orientation.
4. **Capture behavior:** ordinary automatic exposure, plausible highlight
   clipping, local tone mapping, natural focus falloff, mild compression, and
   consistent lighting.
5. **Constraints:** exact visible hands, object interactions, wardrobe, and what
   must remain outside the frame.

Avoid the common realism-killing vocabulary: `masterpiece`, `8K detail`,
`perfect skin`, `flawless`, `cinematic lighting`, `epic`, `hyper-detailed
pores`, `HDR`, generic film grain, and long lists of negative anatomy words.
Those terms push the output toward advertising or synthetic portrait styling.
Describe the intended physical state positively. Google's own guide recommends
semantic positive constraints rather than relying on a conventional negative
prompt.

An appropriate camera paragraph is:

> Casual handheld phone photograph taken at arm's length. The phone is outside
> the frame. Rectilinear wide camera with normal lens correction, not a fisheye
> view. Slightly imperfect off-center framing, ordinary automatic exposure,
> restrained local contrast, realistic highlight roll-off, natural skin color,
> and mild focus falloff into the background. It looks like an unedited personal
> photo rather than a fashion campaign or studio portrait.

Camera terminology should enforce physical relationships rather than act as a
style spell. Apple describes ordinary phone photography as a processed,
multi-frame fused pipeline with local dynamic-range and detail processing. A
convincing result therefore needs coherent computational-camera behavior, not
random noise or extreme sharpness everywhere.

Sources:

- [Google image prompting strategies](https://ai.google.dev/gemini-api/docs/image-generation)
- [Apple high-resolution computational photography](https://developer.apple.com/videos/play/wwdc2026/304/)

### 3. Use a draft/final process without assuming seed equivalence

Hosted image models do not promise that a 1K and 4K request with the same seed
will have identical composition. The safe process is:

1. Generate four to eight 1K or 2K drafts with the four identity references.
2. Select a draft for anatomy, identity, framing, and physical logic.
3. Send that selected draft as the first edit/reference image, followed by the
   four identity images.
4. Request a 4K 3:4 rerender that preserves composition, pose, expression,
   wardrobe, lighting direction, and background layout while resolving native
   detail.
5. Compare the final against the draft. Reject it if the rerender changes body
   proportions or facial identity.

For Nano Banana 2.1, use:

- model: `gemini-nano-banana-2.1`
- aspect ratio: `3:4`
- resolution: `4K` (3584×4800)
- thinking: `high` for final, `medium` for drafts
- input images: selected draft first, then four identity views
- output: lossless master before any publishing conversion

At current official prices, Nano Banana 2.1 costs about $0.0336 for 1K,
$0.0504 for 2K, and $0.113 for 4K in standard processing. Batch processing is
half those output prices, with up to a 24-hour turnaround. This is materially
cheaper than renting a high-end GPU for long native-4K FLUX 3 Base searches.

Source: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

### 4. Keep GPT Image 2.5 as the realism and repair branch

Use GPT Image 2.5 Sunburst for two purposes:

- Generate a direct comparison at 2448×3264, `max`, using the same prompt and
  references.
- Perform localized repairs when the scene is excellent but one hand, object,
  garment, or expression is wrong.

The edit prompt should name one change and explicitly freeze identity,
background, composition, lighting, camera angle, focus, and image quality. Do
not pass a successful image through a global “enhancement” prompt. GPT Image
2.5 is first on the current photorealistic edit leaderboard, which makes it a
more defensible repair tool than a face-swap or generic inpainting checkpoint.

OpenAI's ComfyUI partner node already exposes GPT Image 2.5 Flare and Sunburst,
multiple references, custom dimensions, and `max` quality. The official OpenAI
API also supports masks, although masks guide the edit rather than guaranteeing
an exact hard boundary.

GPT Image outputs include provenance signals. Preserve the original master and
do not design the workflow around removing provenance.

Sources:

- [Arena photorealistic editing leaderboard](https://arena.ai/leaderboard/image/image-edit/single-image-photorealistic)
- [OpenAI image generation and editing guide](https://developers.openai.com/api/docs/guides/image-generation)
- [ComfyUI GPT Image 2.5 node implementation](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_api_nodes/nodes_openai.py)
- [OpenAI image provenance](https://help.openai.com/en/articles/8912793-c2pa-in-chatgpt-images)

### 5. Preserve the local FLUX 3 path

The local quality branch should use:

- `flux-3-image-klein-base-bf16.safetensors`
- official Qwen3.5 prompt upsampler enabled and its output visible
- Qwen3-VL BF16 text encoder
- three Alex reference images
- 50 steps
- Euler/simple
- CFG 3.5 and 4.0 as the only initial A/B
- native 3072×4096 latent
- center crop to 3024×4032, without resizing
- FP32 VAE decode as the next controlled artifact test

Do not use AnyFlow for the quality baseline. AnyFlow is a speed/distillation
method. Its authors report automatic metrics only, no human study, and a
few-step stage that sacrifices some diversity and color fidelity. It is useful
after the best Base workflow is established, not for discovering the realism
ceiling.

If references cannot maintain Alex, train a new subject LoRA against FLUX 3
Klein Base. SimpleTuner now has an official-style Base recipe. Train on varied
angles, expressions, distances, clothing, and lighting; use a distinctive token
and captions that describe non-identity content so the LoRA does not absorb one
background or photographic treatment. Validate checkpoints against prompts
excluded from training. Keep LoRA strength low enough that identity improves
without changing the entire image's frequency response.

Sources:

- [FLUX 3 Klein official settings](https://github.com/black-forest-labs/flux-3-image-klein)
- [SimpleTuner FLUX 3 training guide](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX3_IMAGE.md)
- [Prodia AnyFlow experiment and limitations](https://prodia.com/research/anyflow)

### 6. Review before repair

Human curation is part of the generation method. Evaluate every candidate at
fit-to-screen and at 100–200%. A candidate fails immediately for:

- wrong finger count, merged fingers, impossible wrists, or discontinuous arms;
- incompatible reflection, shadow, perspective, or depth of field;
- hair merging into jewelry, clothing, or architecture;
- unreadable functional objects, straps, seams, chair legs, railings, or food;
- face/hand/background rendered at visibly different sharpness;
- colored speckles, repeated pore grids, waxy skin, face-restoration halos;
- an advertising, studio, or cinematic look when the request is a casual post;
- repeated backgrounds or pose leakage from the identity references.

Score surviving images on identity, anatomy, camera coherence, physical logic,
texture consistency, and ordinary social plausibility. The production metric is
the percentage of usable images across fixed prompts and seeds, not the best
single image.

Small errors should receive one localized edit. If that edit changes identity,
light, or texture, discard it and regenerate. Global face swap, face restore,
unsharp masking, artificial grain, and universal cleanup nodes should remain
off in the baseline.

### 7. Export two files

Retain the native lossless master. Create a separate publishing derivative at
the platform's delivery size and JPEG quality. Do not judge model realism from
the compressed upload alone. Downsampling a 3584×4800 source to 3024×4032 or a
smaller social-media derivative can improve sampling cleanliness; enlarging a
1K file does not create native detail.

## ComfyUI architecture

The next workflow should expose a small control panel:

- scene/request text;
- four fixed Alex identity image inputs;
- optional scene/composition reference;
- backend selector: Nano Banana 2.1 / GPT Image 2.5 / local FLUX 3 Base;
- draft count and draft/final mode;
- resolution and aspect ratio;
- generated/reference comparison;
- accept/reject/save controls.

Backend details should stay inside grouped subgraphs. All three branches should
write a JSON sidecar recording model ID, resolution, prompt, input hashes,
settings, runtime, and review outcome. ComfyUI now includes native partner nodes
for Nano Banana 2.1 and GPT Image 2.5, so the workflow does not require an
unmaintained third-party proxy node.

Source: [ComfyUI partner-node changelog](https://github.com/Comfy-Org/docs/blob/main/changelog/index.mdx)

## Controlled benchmark before choosing the production backend

Use ten prompts representative of the intended account:

- three close/waist-up selfies;
- three full-body travel or café photos;
- two indoor low-light photos;
- one mirror photo;
- one photo with a difficult hand/object interaction.

For each prompt, generate three candidates from:

1. GPT Image 2.5 Sunburst, max, 2448×3264;
2. Nano Banana 2.1, high thinking, 3584×4800;
3. FLUX 3 Klein Base BF16, 50 steps, CFG 3.5;
4. MAI-Image-2.6 or Seedream 5 Pro as one rotating challenger.

Hide filenames and metadata during review. Score identity, anatomy, camera
realism, fine-detail plausibility, and overall “could this be an ordinary
Instagram photo?” Record hard-failure rate separately. The winner should be the
backend with the highest usable-image rate. If GPT wins realism but Nano wins
resolution and identity, keep both branches rather than degrading GPT output
through an automatic second model.

## What this changes from the earlier plan

- FLUX 3 Base remains useful, but it is no longer assumed to be the best model
  merely because it runs locally and produces native 4K.
- Nano Banana 2.1 becomes the provisional final-render default because it is the
  only top-ranked model that combines explicit recurring-character references
  with a native 17 MP 3:4 output at low per-image cost.
- GPT Image 2.5 Sunburst becomes the realism ceiling and preferred localized
  editor.
- Qwen-Image-2.1, SDXL, face swap, DyPE, generic upscalers, cleanup nodes, and
  style LoRAs stay outside the baseline until a controlled test proves value.
- The workflow optimizes curation and rejection rate as seriously as sampler
  settings. Human research shows that prompt choice, visible artifacts, scene
  complexity, and curation dominate perceived realism.

No paid experiment was run during this research pass because the RunPod balance
is zero and no hosted API credentials were supplied. The recommendations above
are grounded in current independent rankings, official model specifications,
the published photorealism study, and the seven FLUX 3 images already generated
for this repository. They should be validated with the blind benchmark before
we replace the existing production workflow.
