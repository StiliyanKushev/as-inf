# Research: highest-realism Instagram-style persona images

Research date: 2026-10-28

This report answers a narrower question than the earlier native-4K study: which
current model and workflow is most likely to produce casual photographs of the
fictional Alex Sparks persona that look like ordinary real Instagram photos?
The priorities are human-perceived realism, recurring identity, anatomy,
camera coherence, and genuine high-resolution output. Speed and compute cost
are secondary.

## Decision

There is no single winner across every constraint. A follow-up audit of public
creator pipelines materially changes the order in which this project should be
tested:

1. **Most relevant public workflow already producing this kind of content:**
   PixelAI Labs' Krea 2 Edit Carousel. It ships a real ComfyUI JSON, example
   output sheets, and exact model settings for turning one original character
   photo into two, four, or eight smartphone-style lifestyle photographs. The
   checked-in graph uses Krea 2 Turbo FP8, Krea 2 General Edit V2 at 1.0,
   FameGrid at 0.5, Realism Engine Krea 2 v3.1 at 0.5, an optional Krea 2
   character LoRA at 0.8, Qwen3-VL 4B, a 2 MP 3:4 canvas, and Euler/simple at
   ten steps and CFG 1. Its examples are substantially closer to ordinary
   Instagram photos than most generic text-to-image showcases.

2. **Most credible public identity-restaging component:** Krea 2 Identity Edit
   V2. Its public node pack, workflow, weights, training code, and geometry are
   available. It conditions on the original photograph through both VAE tokens
   and Qwen3-VL grounded encoding. The author recommends Krea 2 Turbo, 8–10
   steps, CFG 1, `ref_boost` around 4, `grounding_px` 768, and no more than 2 MP.
   For this project, Identity Edit V2 should be A/B tested against the Carousel's
   General Edit V2 while keeping every other node fixed.

3. **Highest raw generation and editing quality:** GPT Image 2.5 Sunburst at
   `max` quality. It is currently first on Arena's overall, photorealistic, and
   portrait leaderboards, and first for photorealistic image editing. It is the
   strongest control for judging whether a local workflow is actually
   competitive. Its output ceiling is 8,294,400 pixels with a 3,840-pixel edge,
   so it cannot directly produce a 3024×4032 12.2 MP portrait. An exact 3:4
   request near its limit is 2448×3264.

4. **Best fit for a native high-resolution recurring persona:** Gemini Nano
   Banana 2.1 at `4K`, `3:4`, with high thinking and four carefully selected
   Alex references. It outputs 3584×4800 (17.2 MP), explicitly supports
   character consistency, and accepts up to four character references within a
   fourteen-image request. It can be reduced to 3024×4032 by downsampling; no
   enlargement is involved. It ranks fourth in the current photorealistic
   Arena and in the leading portrait confidence band.

5. **Best native-4K self-hosted and fine-tunable choice:** FLUX 3 Image Klein
   Base BF16 with its official prompt upsampler, three identity references, 50
   steps, Euler/simple, and CFG 3.5–4.0. It remains the local native-resolution
   research branch.

The recommended production design is now an **authenticity-first Krea 2
workflow plus three benchmark branches**, not a commitment to one model before
blind testing:

- Krea 2 Edit Carousel is the first public pipeline to reproduce exactly.
- Krea 2 Identity Edit V2 plus a Krea-trained Alex LoRA is the first controlled
  improvement to it.
- Nano Banana 2.1 is the native-high-resolution challenger.
- GPT Image 2.5 Sunburst is the absolute-quality benchmark and precision editor.
- FLUX 3 Klein Base is the private/local fallback and LoRA research branch.

## Practitioner workflow audit

The first version of this report emphasized model rankings and official
capabilities. That was incomplete. A realistic production recommendation also
needs evidence from creators who have already attempted recurring virtual
people. The following projects were inspected directly, including their JSON,
sample outputs, experiment logs, and settings where public.

### Krea 2 Edit Carousel: closest reproducible match

PixelAI Labs publishes the complete `Krea2_Carousel.json` workflow and example
contact sheets for lifestyle, fashion, uniform, product, and character-LoRA
scenarios. This audit inspected Carousel commit
`a5c3eff64e9740e9ffc38ba0b7775961fa618614` and Krea2Edit commit
`13ef60f20828949becada815d3cbc371eb5ccaab`. Its important production
choices are:

- every output is conditioned directly from the same original character photo;
  generated outputs are never chained as the next reference;
- a vision model writes a coherent story and a distinct prompt per slide;
- the intended camera mode is explicitly `smartphone` for lifestyle posts;
- expressions are subtle because large laughs and extreme expressions drift;
- 1 MP is used to find a plan/seed, and 2 MP is used for the final render;
- Krea 2 Edit carries identity, scene, outfit, and photographic appearance;
- a character LoRA trained on Krea 2 Raw can be added at about 0.8;
- low-strength realism/style LoRAs and a restrained color finish are applied;
- one drifting image in an eight-image batch is rerolled or rejected.

This is much closer to the requested product than a generic FLUX sampler graph.
It also exposes a constraint the previous report underweighted: the strongest
public examples are made at 1–2 MP, then delivered at social-media resolution.
They are not native 12 MP generations.

Sources:

- [PixelAI Labs Krea 2 Edit Carousel repository](https://github.com/Pixelailabs/ComfyUI-Krea2-Edit-Carousel)
- [Krea 2 Edit V2 node pack and example workflow](https://github.com/lbouaraba/comfyui-krea2edit)
- [Krea 2 Identity Edit V2 model card](https://huggingface.co/conradlocke/krea2-identity-edit)

### Public character-LoRA experiments

The Anuxq project publishes three result images, SDXL workflows, experiment
notes, and training settings. Its final choice was Juggernaut XL plus a curated
38-image rank-32 character LoRA at epoch 8 plus PuLID. LoRA alone drifted,
IP-Adapter FaceID produced artificial facial exaggeration at stronger weights,
and ReActor softened facial texture. PuLID was the best compromise in that
project. The outputs are coherent and reproducible, although they still have a
more obvious generated portrait look than the Krea 2 Carousel examples.

This audit inspected Anuxq commit
`5ba7965e6abb48a412292d185f0b5d4421dbaa7c` and Ananya commit
`effb3de1f933061ca0041e0f55c8e84859a964ba`.

The Ananya repository goes further by preserving an actual ablation grid. Its
SDXL/Juggernaut pipeline uses a character LoRA, then ReActor, then skin-tone
matching. Its experiment found CodeFormer made clean faces smoother and more
plastic; the winning configuration disabled face restoration. The repository
also documents proportion and framing failures, and shows that the workflow
needed continued manual review despite its identity stack.

These projects support four practical conclusions:

1. A character LoRA remains the most durable identity mechanism across many
   posts, but it does not by itself guarantee the same face.
2. Strong face injection or restoration can make the face less photographic
   than the unswapped generation.
3. Dataset curation and choosing the correct training epoch matter more than
   simply adding rank or training steps.
4. A successful pipeline expects failures and rejects them; it does not assume
   every batch member is publishable.

Sources:

- [Anuxq identity-consistency project](https://github.com/Poshhha/anuxq-consistent-character-generation)
- [Ananya AI influencer pipeline and ablations](https://github.com/kavyabarnadhya/ai-influencer)

### What a commercially successful account actually does

The Aitana López operation is useful evidence because it is a verified,
successful virtual-influencer account rather than a workflow advertisement.
Its team does not rely on a single text-to-image graph. Public reporting says
they photograph a human stand-in at the real location with the intended light,
replace the stand-in with Aitana, and complete the image in Photoshop. They
also trained their system on Aitana's own accumulated images and use a human
team for art direction, selection, retouching, story planning, and publishing.

That is the strongest known route to physical realism because the lens,
perspective, shadows, reflections, background, clothing interaction, and social
context begin as a real photograph. The synthetic step has a narrower job:
replace identity while preserving the photographic plate. For Alex, the safe
and reproducible equivalent is to use self-shot or properly licensed scene/body
plates, then apply identity-preserving restaging and manual localized cleanup.

Sources:

- [Bloomberg Línea report describing the stand-in replacement workflow](https://www.bloomberglinea.com/estilo-de-vida/asi-es-aitana-lopez-la-ia-influencer-mas-seguida-del-mundo-que-gana-miles-de-dolares/)
- [RTVE report describing AI generation followed by Photoshop retouching](https://www.rtve.es/play/noticias/20231221/aitana-model-ia-existeix/2468875.shtml)
- [Fast Company profile of the eleven-person Aitana team](https://www.fastcompany.com/91546466/she-has-400000-instagram-followers-and-major-brand-deals-shes-also-ai)

### Resolution is a real tradeoff

The practitioner evidence does not support native 3024×4032 as a requirement
for creating a believable Instagram post. Krea 2's authors recommend at most
2 MP for identity edits; above that, references can bleed or duplicate. The
Carousel workflow uses 2 MP finals. Anuxq uses 1024-class SDXL. The Ananya
ablation uses 768×1360. Instagram's published delivery guidance is only 1080
pixels wide for feed photos.

Therefore two separate deliverables should be defined:

- **Instagram master:** generate around 2 MP, reject defects, and export a clean
  1080×1440 3:4 publishing file. This is the realism-first target.
- **Archival 3024×4032 file:** upscale the accepted 2 MP image conservatively,
  or render a separate Nano Banana/FLUX 3 native-high-resolution version. It is
  not evidence that the social post itself will look more real.

Requiring one model to solve identity, physical realism, editing, and native
12 MP simultaneously led this project away from the workflows that creators
are actually using successfully.

Licensing also matters: Krea 2 open weights allow commercial use below the
base model's stated revenue threshold, but the Krea 2 Identity/General Edit V2
weights require a separate written commercial license from their author. They
can be evaluated now, but commercial deployment must satisfy both licenses.

Sources:

- [Krea 2 Community License](https://github.com/krea-ai/krea-2/blob/main/docs/KREA-2-COMMUNITY-LICENSE)
- [Krea 2 Identity Edit V2 license](https://huggingface.co/conradlocke/krea2-identity-edit/blob/main/LICENSE_V2.md)

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

### 0. Reproduce the working Krea 2 workflow before redesigning it

Install and run the public Krea 2 Edit Carousel unchanged with its included
example image and exact model versions. Preserve the author's 2 MP 3:4 final,
ten steps, CFG 1, Euler/simple, and LoRA strengths. This is the control. Only
after reproducing its example quality should Alex replace the example subject.

Run three controlled Alex variants:

1. original Alex hero image plus General Edit V2, matching the published graph;
2. original Alex hero image plus Identity Edit V2, `ref_boost=4`,
   `grounding_px=768`;
3. variant 2 plus a new Alex LoRA trained on Krea 2 Raw and loaded on Turbo at
   0.8.

The existing `alexsparks.safetensors` is tied to another model family and
cannot be reused as a Krea 2 LoRA. Use the existing curated images to train a
new Krea-compatible LoRA. Follow Krea's intended pairing: train on Raw, infer
on Turbo.

For the highest-realism branch, add an optional real-photo plate input. This
must be self-shot or properly licensed. Keep the plate's camera, background,
pose, light, shadows, and object contact; replace only the fictional identity.
This is the public technique closest to the successful Aitana production
method.

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
- original Alex hero photograph;
- four fixed Alex identity image inputs;
- optional scene/composition reference;
- optional self-shot or licensed photographic plate;
- backend selector: Krea 2 Carousel / Nano Banana 2.1 / GPT Image 2.5 /
  local FLUX 3 Base;
- draft count and draft/final mode;
- resolution and aspect ratio;
- generated/reference comparison;
- accept/reject/save controls.

Backend details should stay inside grouped subgraphs. All branches should
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

1. Krea 2 Turbo plus Identity Edit V2, 2 MP, with the Krea Alex LoRA;
2. Krea 2 Turbo using a licensed real-photo plate, where available;
3. GPT Image 2.5 Sunburst, max, 2448×3264;
4. Nano Banana 2.1, high thinking, 3584×4800;
5. FLUX 3 Klein Base BF16, 50 steps, CFG 3.5.

Hide filenames and metadata during review. Score identity, anatomy, camera
realism, fine-detail plausibility, and overall “could this be an ordinary
Instagram photo?” Record hard-failure rate separately. The winner should be the
backend with the highest usable-image rate. If GPT wins realism but Nano wins
resolution and identity, keep both branches rather than degrading GPT output
through an automatic second model.

## What this changes from the earlier plan

- FLUX 3 Base remains useful, but it is no longer assumed to be the best model
  merely because it runs locally and produces native 4K.
- The published Krea 2 Carousel becomes the first implementation target because
  it already solves the requested product and exposes its graph and examples.
- Krea 2 Identity Edit plus a Krea-trained Alex LoRA becomes the provisional
  local production path for social-resolution output.
- Nano Banana 2.1 remains the native-high-resolution challenger.
- GPT Image 2.5 Sunburst becomes the realism ceiling and preferred localized
  editor.
- SDXL/PuLID and SDXL/ReActor remain documented alternatives, but their public
  examples show more texture and identity compromises than the Krea path.
- DyPE, generic cleanup nodes, and aggressive face restoration stay outside the
  baseline until a controlled test proves value.
- The workflow optimizes curation and rejection rate as seriously as sampler
  settings. Human research shows that prompt choice, visible artifacts, scene
  complexity, and curation dominate perceived realism.

No paid experiment was run during this research pass because the RunPod balance
is zero and no hosted API credentials were supplied. The recommendations above
are grounded in current independent rankings, official model specifications,
the published photorealism study, and the seven FLUX 3 images already generated
for this repository. They should be validated with the blind benchmark before
we replace the existing production workflow.
