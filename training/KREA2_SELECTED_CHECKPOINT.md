# Selected Alex Sparks Krea2 identity checkpoint

- Persona: Alex Sparks (fictional)
- Training project: `alexsparks_krea2_v1`
- Training base: Krea2 Raw BF16
- Inference target: Krea2 Turbo
- Embedded trigger: `alexsparks`
- Selected training step: 1000 (final)
- Original persistent path: `/workspace/training/output/alexsparks_krea2_v1/alexsparks_krea2_v1.safetensors`
- ComfyUI and Git LFS filename: `alexsparks_krea2.safetensors`
- Size: `228587400` bytes
- SHA-256: `0e32c5d0535cb778859c25ffd4bbdc6af944709d20bbcaaca1ad0d54149061d9`
- Initial workflow strength: `0.65`

## Production validation status

The checkpoint is reproducible and technically valid, but it is **not the
recommended production identity path**. A same-seed Turbo comparison at
strengths 0, 0.6, 0.8, and 1.0 showed weak Alex resemblance and progressively
softer, more artificial texture. The Raw-model training previews learned the
identity, but the adapter did not transfer cleanly into the final stacked Turbo
workflow. The file is retained for research and rollback with a default
strength of zero. Use `final-kurva-maker-krea2-scene-identity.json` instead.

The fixed-seed previews at steps 200, 400, 600, 800, and 1000 were compared.
Step 1000 gave the strongest consistent identity while still following varied
portrait, full-body, lighting, clothing, and expression prompts. The selected
artifact is stored in Git LFS; all intermediate checkpoints and previews remain
on the persistent RunPod volume.
