# Workflow LoRAs

The four `.safetensors` files in this directory are stored with Git LFS and are
the exact LoRAs referenced by the checked-in ComfyUI workflows. Run
`git lfs pull` after cloning if the files appear as small text pointers.

The base FLUX.2, text encoder, VAE, Qwen3-VL, and Ollama weights remain external
and are restored by `scripts/download-public-models.sh` and
`scripts/bootstrap-new-volume.sh`.
