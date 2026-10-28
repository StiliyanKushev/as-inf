# FLUX 3 native-4K experiment log

Run date: 2026-10-27 to 2026-10-28

Hardware: RunPod NVIDIA H200

ComfyUI: `0.43.0` at commit `426f5eea52a7ece1dd599fff4cb6cd1f352ddd24`

All 3024 × 4032 files below were generated at 3072 × 4096 and then center-cropped by 24 pixels per side and 32 pixels at the top and bottom. No scaling or upscaler was used.

## Results

| File | Configuration | Runtime | Finding |
|---|---|---:|---|
| `distilled_direct_1200x1600_native_00001_.png` | Distilled BF16, direct prompt, no identity refs | 36.9 s cold | Correct hand and clean face, but composed like a polished portrait instead of an ordinary phone selfie. |
| `distilled_pup_phone_1200x1600_native_00001_.png` | Distilled BF16, official prompt upsampler, no refs | 32.4 s | Much stronger selfie perspective and natural skin variation. |
| `distilled_pup_phone_3072x4096_exact_3024x4032_00001_.png` | Same, native 12.6 MP | 70.2 s | Genuine 3024 × 4032 generated detail, but sparse colored flecks appear at full-size inspection. |
| `distilled_pup_alex_refs_1200x1600_native_00001_.png` | Distilled BF16 plus three Alex references | 24.0 s warm | Strong identity transfer with integrated lighting and texture; reference conditioning works better than a post-generation face swap. |
| `distilled_pup_alex_refs_3072x4096_exact_3024x4032_00001_.png` | Same, native 12.6 MP | 96.2 s | Alex identity remains recognizable, but colored confetti pixels and an unwanted top-edge selfie arm make this run a rejection. |
| `base_pup_alex_refs_1200x1600_native_00001_.png` | Base BF16, 50 steps, CFG 3.5, three refs | 92.2 s | Cleaner and more natural than distilled, with correct hand and selfie-arm geometry. |
| `base_pup_alex_refs_3072x4096_exact_3024x4032_00001_.png` | Base BF16, 50 steps, CFG 3.5, native 12.6 MP | 513.0 s | Best clean true-4K result from this run: strong Alex identity, correct hand, no obvious colored confetti. It is visibly softer than the distilled result and still needs blind multi-seed validation. |

The local copies are intentionally excluded from Git because the seven PNG files total roughly 48 MB. They live at:

```text
/var/home/kushev/src/as-inf/research-results/flux3/
```

The same RunPod outputs were written under:

```text
/workspace/ComfyUI-flux3/output/flux3-research/
```

## What the tests established

1. FLUX 3 can execute a real 3072 × 4096 diffusion pass on the H200. The final 3024 × 4032 output is a crop, not an enlargement.
2. The official Qwen3.5 prompt upsampler materially improves phone-selfie composition, but its expanded text must remain visible because it can invent clothing or place the selfie arm incorrectly.
3. Three FLUX 3 reference latents preserve Alex more cleanly than post-generation face replacement. The face shares the scene's light, focus, skin texture, and color treatment.
4. Distilled is approximately five to eight times faster at native 4K, but both native distilled tests showed sparse colored flecks. Base eliminated the obvious flecks on this seed.
5. Base at 50 steps is the current quality default. Its cost is about 8.5 minutes per native 4K image on this H200 and the result is softer, so one seed is not enough to declare the model solved.
6. More steps did not merely sharpen the result. Switching from the distilled checkpoint to the Base checkpoint changed texture, cleanliness, composition, and runtime together.
7. The exact selfie-arm instruction mattered: the arm must enter only from the lower-left edge, with the phone outside the frame, while the separate peace-sign hand stays fully visible.

## Unfinished controlled tests

The RunPod credit reached zero before these could run:

- Distilled native 4K with `--fp32-vae` or `--bf16-vae`, to determine whether the colored flecks come from FP16 VAE decoding.
- Base native 4K at CFG 4.0.
- Five-seed usable-image-rate comparison for distilled versus Base.
- A selected 1 MP draft used as a separate composition reference alongside the three Alex identity references.
- Full FLUX 3 API and Nano Banana 2.1 native-4K controls.

The next test should be distilled BF16 with the same fixed prompt, seed, and three references while starting ComfyUI with `--fp32-vae`. If that removes the colored flecks without losing distilled sharpness, it may beat the slower Base path. Otherwise keep Base as the quality default.

## Reproduction artifacts

- Workflow: `workflows/research-flux3-native-4k.json`
- API experiment runner: `scripts/run-flux3-research.py`
- Model/runtime installer: `scripts/install-flux3-research.sh`
- Research and sources: `docs/TRUE_4K_INSTAGRAM_RESEARCH_2026-10-27.md`

