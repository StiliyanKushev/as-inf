# Deployment architecture

## Persistent state

The network volume is mounted at `/workspace` and owns the whole runtime:

```text
/workspace/
├── ComfyUI/                    pinned application checkout
│   ├── custom_nodes/           pinned plugin checkouts
│   ├── models/                 diffusion, VAE, encoder, LoRA and Qwen-VL files
│   ├── input/                  uploaded references and masks
│   ├── output/                 generated images
│   └── user/default/workflows/ saved workflows
├── comfyui-venv/               Python 3.12 environment
├── ollama/models/              persistent SuperGemma blobs and manifest
├── as-inf/                     this repository
├── start-ollama.sh
├── start-final-kurva-maker.sh
└── recover-final-kurva-maker.sh
```

The pod container disk is disposable. On a replacement pod, the recovery script
reinstalls the small Ollama executable when necessary, then starts Ollama and
the persistent ComfyUI checkout.

## Prompt path

1. `ASInfOptionalReferenceImage` emits both the selected image and a Boolean
   indicating whether the selector is `None`.
2. With a reference, Qwen3-VL describes the photograph and FLUX.2 receives its
   encoded reference latent. With `None`, lazy switches skip both branches.
3. SuperGemma rewrites the user request as either a modification or a complete
   new-image description.
4. A second SuperGemma pass resolves the selected mode into one conflict-free
   FLUX.2 prompt.
5. FLUX.2 Klein renders at 2016 × 2688 and delivers 3024 × 4032.

## Files excluded from Git

Large base-model weights and private media are excluded because they are large
or can contain private material. The four required workflow LoRAs are stored in
Git LFS. `manifests/model-sha256.txt` records the exact expected filenames and
checksums. The repository never stores a RunPod API key, GitHub token, SSH
private key, reference photo, or generated image.
