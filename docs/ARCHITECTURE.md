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

1. Qwen3-VL describes the reference photograph.
2. SuperGemma rewrites the optional user modification.
3. A second SuperGemma pass resolves both texts into one conflict-free FLUX.2
   prompt and removes superseded source attributes.
4. The compiled prompt is encoded and paired with the reference latent.
5. FLUX.2 Klein renders at 2016 × 2688 and delivers 3024 × 4032.

## Files excluded from Git

Weights and media are excluded because they are large, may have separate model
licenses, and can contain private material. `manifests/model-sha256.txt` records
the exact expected filenames and checksums. The repository never stores a
RunPod API key, GitHub token, SSH private key, reference photo, or generated
image.
