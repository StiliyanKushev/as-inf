# Anuxq vs Ananya vs Krea2 Instagram benchmark — 2026-10-28

## Result

For the Alex Sparks persona, **Krea2 Turbo + General Edit V2 is the strongest
starting point**. It preserved the supplied face far better than the two SDXL
paths, produced clean skin and anatomy, and rendered directly at 1280×1600.
The public FameGrid and Realism Engine LoRAs add only a small visual change; the
important correction was an explicit single-subject prompt.

**Anuxq's Juggernaut XL + PuLID core produced the most casual phone-like
photographs**, ran in about 10 seconds after warm-up, and kept one subject in all
four trials. Its face was recognizably guided by the reference but was not a
close enough Alex identity match for a production persona.

**The tested Ananya SDXL + ReActor path is not recommended.** Its base images
were plausible, but the final face swap did not recover Alex reliably and could
soften close facial detail. The current upstream project is a larger FLUX,
refinement, hand-repair, ReActor, and color-lock system; this test reproduced
the project's published SDXL realism-ablation core, not that entire private
character pipeline.

The complete visual comparison is in
[`contact-sheet-instagram.jpg`](../research-results/three-way-2026-10-28/contact-sheet-instagram.jpg).

## Controlled test

Every branch received the same synthetic Alex reference, two scene briefs, and
seeds `27012026` and `27012027`. No real person's identity was used. The two
scenes were a seated outdoor-cafe portrait and a full-body European-street
photo. The benchmark retained native files and made 1080×1350 delivery files.

| Branch | Inference core | Native size | Settings | Warm runtime on A40 |
|---|---|---:|---|---:|
| Anuxq | Juggernaut XL v9 + PuLID v1.1 | 1024×1280 | 25 steps, CFG 4, DPM++ 2M/Karras, PuLID 0.55 | ~10.0 s |
| Ananya | Juggernaut XL v9 + ReActor | 1024×1280 | 30 steps, CFG 8, DPM++ 2M/Karras, no face restoration | ~16.1 s |
| Krea2 | Krea2 Turbo FP8 + General Edit V2 + FameGrid 0.5 + Realism Engine 0.5 | 1280×1600 | 10 steps, CFG 1, Euler/Simple, reference boost 2 | ~76.2 s |

The first Anuxq and Krea2 calls took 76.4 and 138.3 seconds because their model
families had to load. Subsequent calls are the meaningful interactive timings.
The exact 12 API graphs and execution records are under
[`api-graphs/`](../research-results/three-way-2026-10-28/api-graphs/) and
[`manifests/`](../research-results/three-way-2026-10-28/manifests/).

The upstream Anuxq project reports its best result from a trained character LoRA
combined with PuLID. That private character LoRA cannot represent Alex and was
not available. The same rule applies to Ananya's private identity assets. This
benchmark compares the reusable public inference mechanisms with one shared
reference rather than pretending to reproduce someone else's character.

The public workflow sources inspected at fixed commits were
[Anuxq](https://github.com/Poshhha/anuxq-consistent-character-generation),
[Ananya](https://github.com/kavyabarnadhya/ai-influencer),
[PixelAI Krea2 Edit Carousel](https://github.com/Pixelailabs/ComfyUI-Krea2-Edit-Carousel),
[Krea2 Edit nodes](https://github.com/lbouaraba/comfyui-krea2edit),
[PuLID v1.1 nodes](https://github.com/yashikawa3/ComfyUI-PuLID), and
[ReActor](https://github.com/Gourieff/ComfyUI-ReActor). The lock file records
the exact revisions rather than relying on each repository's moving default
branch.

## What the images show

### Anuxq

- Both cafe seeds look like ordinary social photographs rather than polished
  campaign photography.
- Both street seeds contain one subject and coherent body geometry.
- Identity is too generic: eye shape, jaw, hair, and age drift from the Alex
  source. The street bag/hand interaction is also less convincing than Krea2.
- This is the best fallback when a casual phone look matters more than strict
  identity, or if a future Alex SDXL LoRA is trained and combined with PuLID.

### Ananya

- Scene generation is stable and often convincingly photographic.
- The before/after sheet shows that ReActor alters the face only slightly at
  full-body scale and can smooth the face in close portraits:
  [`contact-sheet-ananya-swap.jpg`](../research-results/three-way-2026-10-28/contact-sheet-ananya-swap.jpg).
- The swapped result is still not a dependable Alex match. A pasted-face
  identity system also remains a style/lighting seam risk, matching earlier
  project experience with face-swap finishing.

### Krea2

- Cafe results have the closest face, strongest pores/freckles, cleanest hands,
  and best fabric/object detail.
- The original street wording produced two copies of the subject in both seeds.
  It said a friend was photographing her and also requested distant people;
  identity-conditioned edit models can repeat the reference when people are
  semantically ambiguous.
- An ablation added: “exactly one foreground woman; never duplicate her; the
  photographer and phone remain outside frame.” Both seeds then produced one
  correct subject. See
  [`contact-sheet-krea-ablation.jpg`](../research-results/three-way-2026-10-28/contact-sheet-krea-ablation.jpg).
- Removing FameGrid and Realism Engine did not materially change composition.
  The full stack is marginally crisper; the core stack is simpler and nearly as
  good. The color-finish pass itself is subtle:
  [`contact-sheet-krea-finish.jpg`](../research-results/three-way-2026-10-28/contact-sheet-krea-finish.jpg).
- A final prompt-only test explicitly requested deep phone focus, sensor grain,
  no portrait mode, and no bokeh. Krea2 still produced shallow depth of field
  and became more centered/staged. Prompt wording alone cannot turn this model's
  learned editorial camera prior into a convincing phone snapshot.

## Production recommendation

Use Krea2 Turbo FP8 with General Edit V2 at **1280×1600**, then export to
**1080×1350** for Instagram. Keep the public style LoRAs available as a toggle;
start with FameGrid `0.5` and Realism Engine `0.5`, because their cost is small
and the full-stack faces were marginally stronger. Use the corrected constraints
for every prompt:

> Exactly one foreground woman: the same fictional woman shown in the
> reference. Never duplicate, clone, mirror, or repeat her. The photographer
> and phone remain outside the frame.

Treat 1080×1350 as the product file. The Krea branch generates 1280×1600 pixels
through diffusion and downsamples once; it does not pretend a resized image is
native 4K. Instagram does not require 4K for a portrait feed post, and the
extra native pixels provide a modest clean margin for crop and delivery.

Krea2's remaining weakness is its polished shallow-depth camera prior. If a
more casual phone look becomes mandatory, the next experiment should change
the generation model or use a real-phone style training set. Repeating phrases
such as “iPhone,” “deep focus,” and “no bokeh” is not supported by this test.

## Reproduction

On a fresh Ubuntu RunPod with a matching CUDA 12.8 Torch base:

```bash
scripts/research-three-way/install-remote.sh
scripts/research-three-way/download-models.sh
nohup /workspace/start-research-comfy.sh >/workspace/research-comfy.log 2>&1 &
python scripts/research-three-way/run-benchmark.py
python scripts/research-three-way/run-krea-ablation.py
python scripts/research-three-way/run-krea-phone-ablation.py
```

The exact ComfyUI/custom-node revisions are pinned in
[`manifests/research-three-way.lock.tsv`](../manifests/research-three-way.lock.tsv).
Model byte hashes are pinned and checked by
[`research-three-way-models.sha256`](../manifests/research-three-way-models.sha256);
the measured sizes and hashes are also preserved in
[`runtime-models.sha256`](../research-results/three-way-2026-10-28/runtime-models.sha256).
The runtime was ComfyUI 0.43.0, Torch/Torchvision/Torchaudio 2.9.1/0.24.1/2.9.1
with CUDA 12.8 on an NVIDIA A40 48 GB.

This is an 18-run directional benchmark, including six follow-up Krea2
ablations. Two scenes and two primary seeds are enough to reject the duplicate
subject prompt and the tested face-swap finish, but they are not a population
level quality estimate.
