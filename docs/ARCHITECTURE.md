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

1. `ASInfOptionalReferenceCrop3x4` combines the optional reference picker with
   a draggable crop overlay. The crop is permanently locked to 3:4; its saved
   normalized coordinates remain hidden, and the backend enforces an exact
   integer 3:4 rectangle again during execution.
2. The crop is normalized to 1008 × 1344 with crop-to-fill, so arbitrary source
   aspect ratios are neither stretched nor padded.
3. With a reference, the same cropped pixels reach Qwen3-VL, the encoded
   FLUX.2 reference latent, and the comparison viewer. With `None`, lazy
   switches skip the reference branches.
4. SuperGemma rewrites the user request as either a modification or a complete
   new-image description.
5. A second SuperGemma pass resolves the selected mode into one conflict-free
   FLUX.2 prompt.
6. FLUX.2 Klein renders at 2016 × 2688 and delivers 3024 × 4032.

## Files excluded from Git

Large base-model weights and private media are excluded because they are large
or can contain private material. The four required workflow LoRAs are stored in
Git LFS. `manifests/model-sha256.txt` records the exact expected filenames and
checksums. The repository never stores a RunPod API key, GitHub token, SSH
private key, reference photo, or generated image.

The fictional Alex Sparks identity LoRA is the selected step-1500 training
checkpoint, committed as `models/loras/alexsparks.safetensors`. The original
training codename and activation token `vexa_person` remain in the training
configuration because changing a filename cannot change a token learned by the
weights.
