# Realism workflow test results

Date: 2026-10-27  
Branch: `research/realism-native-4k`  
Test host: RunPod NVIDIA H200, 141 GB VRAM  
Final delivery target: **3024 x 4032**

## Result

The strongest practical setup from this pass is:

- FLUX.2 Klein **Base** 9B in BF16;
- Qwen3 8B text encoder in BF16;
- full `flux2-vae.safetensors` VAE;
- native generation at 1200 x 1600 (1.92 MP);
- Euler plus `Flux2Scheduler`;
- 30 steps and CFG 4;
- `alexsparks.safetensors` at 0.40-0.55, with 0.55 as the workflow default;
- the `vexa_person` trigger at the start of the prompt;
- optional native FLUX.2 reference conditioning;
- Lanczos delivery at exactly 3024 x 4032.

The resulting workflow is
`workflows/research-realism-base-alex-reference-4k.json`. It leaves the current
production workflows unchanged.

## Measured runs

Times are end-to-end ComfyUI execution times reported by the test runner. They
include saves and resizing. First loads include model/encoder transfer; warm
runs reuse cached components.

| Test | Images | Time | Observation |
|---|---:|---:|---|
| Distilled BF16 clean control, cold | 1 | 36.25 s | Clean texture; no confetti, black corners, or aspect distortion |
| Distilled BF16 clean control, warm batch | 4 | 22.06 s | Strong realism; 3/4 obeyed the requested two-finger gesture |
| Distilled, two native identity references | 1 | 10.02 s | Strong Alex identity; same seed changed the hand to four raised fingers |
| Base BF16, no LoRA, first Base load | 1 | 44.07 s | Correct hand and clean global rendering |
| Base + Alex 0.40, 30 steps | 1 | 24.20 s | Best restraint and realistic texture |
| Base + Alex 0.55, 30 steps | 1 | 26.07 s | Stronger identity; still clean; selected default |
| Base + Alex 0.70, 30 steps | 1 | 24.23 s | Strong identity but more polished/synthetic |
| Base + Alex 0.55, 50 steps | 1 | 38.06 s | Small visual change for about 58% more sampling time |
| Base + Alex 0.55, trigger enabled | 1 | 24.04 s | Strong, recognizable identity and correct hand |
| Distilled + Instagram Reality 0.25 | 1 | 8.01 s | Nearly redundant against the clean control |
| Distilled + Instagram Reality 0.45 | 1 | 8.02 s | Sharper/polished eyes and edges; looked more generated |
| Distilled + scene reference | 1 | 8.02 s | Preserved composition and flash; fixed 3:4 canvas avoided stretching |
| Base + Alex 0.55 + scene reference | 1 | 30.05 s | Preserved layout and applied identity; viable combined path |
| Cached 4K Lanczos/RealESRGAN comparison | 1 | 14.03 s | Both files verified at 3024 x 4032 |

These are deliberately small diagnostic samples rather than statistical proof.
They are enough to reject settings that visibly worsen the same seed and to set
a safer default for continued manual testing.

## What the tests established

The native official schedule fixed the earlier speckles and geometry problems.
The old graph's 2016 x 2688 diffusion canvas, non-native sampler/schedule,
overlapping DyPE/model-sampling patches, FP4 encoder, and stacked LoRAs were
confounded variables. The clean 1200 x 1600 baseline did not show those defects.

More steps did not repair anatomy. The distilled model is designed for exactly
four steps; the Base model showed little benefit from 50 versus 30 steps on the
controlled seed. Finger count remains stochastic. Batch generation and manual
selection are still necessary for hand-heavy poses.

Native multi-reference identity was visually convincing but altered global
composition and hand anatomy on the controlled seed. It remains useful when an
identity LoRA is unavailable, but it is not a localized face-only operation.

Alex works cleanly on the Base checkpoint it was trained against. Strength 0.40
retains the most base-model texture; 0.55 gives the better identity/realism
balance. Strength 0.70 increases the smooth, curated portrait look.

Instagram Reality was not useful in this controlled scene. It is disabled in the
research workflow. It may still be tested manually at 0.25 for a specific prompt,
but it should not be part of the default stack.

RealESRGAN x4 generated harder hair edges and smoother, more processed skin when
reduced back to 3024 x 4032. Plain Lanczos preserved the native photograph's
texture better, so it is the default 4K delivery path. The 4K file has the exact
requested dimensions, but enlargement cannot create true scene detail that was
absent from the 1200 x 1600 diffusion render.

Reference conditioning reproduced source UI artifacts such as carousel dots and
an arrow when those were present in the screenshot. Crop or clean the reference
before generation when those elements should not appear.

## Reproduction

`scripts/run-realism-experiment.py` submits the same native graph through the
ComfyUI API and records settings, output filenames, status, and runtime in a JSON
manifest. Example:

```bash
/workspace/comfyui-venv/bin/python /workspace/run-realism-experiment.py \
  --variant base \
  --seed 27012026 \
  --lora alexsparks.safetensors \
  --lora-strength 0.55 \
  --trigger vexa_person \
  --reference staircase_reference.png \
  --reference-role scene \
  --prefix research/base-alex-reference \
  --manifest /workspace/research-results/base-alex-reference.json
```

The script saves a native 1200 x 1600 render, a 3024 x 4032 Lanczos version, and
optionally a 3024 x 4032 RealESRGAN comparison.
