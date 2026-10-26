# Persistence and reproducibility audit

Audit date: 2026-10-26

## Deployment-critical state stored in GitHub

- All maintained ComfyUI workflows, including the spatial Alex Sparks workflow.
- The AS-INF optional-reference, crop, trigger, and sampler custom node source.
- Exact ComfyUI and third-party custom-node revisions.
- Installation, recovery, verification, pod-creation, and model-download scripts.
- Python package manifests and SHA-256 checksums for downloaded model files.
- The 30-image fictional-person training dataset, captions, configuration, and
  training scripts.
- Four private workflow LoRAs through Git LFS. `alexsparks.safetensors` is the
  chosen step-1500 identity checkpoint, size `165704328`, SHA-256
  `072f0184a52cc00de330e7f863951d44120a2412a9369d8ba0c76118d2e345ad`.
- The selected checkpoint decision and hashes of every retained training
  checkpoint.

## Persistent-volume state intentionally reconstructed instead of committed

- FLUX.2 Klein 9B, Qwen text encoder, FLUX VAE, MediaPipe, and BFS public model
  files are fetched by `scripts/download-public-models.sh` and checked against
  `manifests/model-sha256.txt`.
- Qwen3-VL is fetched by `scripts/bootstrap-new-volume.sh` from
  `Qwen/Qwen3-VL-8B-Instruct`.
- Ollama pulls the exact prompt model tag
  `0xIbra/supergemma4-26b-uncensored-gguf-v2:Q4_K_M`.
- ComfyUI, AI Toolkit, and custom-node sources are pinned by repository commit.
- Python environments are rebuilt from the checked-in install scripts and
  package manifests.

## Files kept only on the persistent volume by design

- Generated images, uploaded reference images, temporary masks, previews, and
  application caches. These can contain private media and are not required to
  reconstruct the generator.
- Hugging Face tokens, RunPod credentials, and other secrets. They must never
  enter Git.
- Intermediate LoRA checkpoints at steps 250–1750. Their hashes are recorded in
  `training/checkpoint-sha256.txt`; the deployment-selected step 1500 weights
  are backed up in Git LFS as `models/loras/alexsparks.safetensors`.
- Old `*.before-*.json` workflow snapshots and legacy bootstrap directories.
  The maintained workflows and their history are in Git.

The repository therefore contains all unique configuration, code, training
data, decisions, and selected private weights needed to recreate the current
pipeline. It deliberately does not mirror private/generated media, secrets,
caches, downloadable public weights, or unselected experimental checkpoints.
