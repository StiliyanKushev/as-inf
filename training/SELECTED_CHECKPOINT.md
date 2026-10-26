# Selected Alex Sparks identity checkpoint

- Persona: Alex Sparks (fictional)
- Training project: `vexa_person_klein9b_v1`
- Embedded trigger: `vexa_person`
- Selected training step: 1500
- Original persistent path: `/workspace/training/output/vexa_person_klein9b_v1/vexa_person_klein9b_v1_000001500.safetensors`
- ComfyUI and Git LFS filename: `alexsparks.safetensors`
- Size: `165704328` bytes
- SHA-256: `072f0184a52cc00de330e7f863951d44120a2412a9369d8ba0c76118d2e345ad`
- Initial workflow strength: `0.70`

The filename was changed for clarity. The trigger remains `vexa_person`
because it was learned during training. The other saved checkpoints on the
RunPod volume are experiments; this step-1500 artifact is the selected,
deployment-critical result and is stored in Git LFS.
