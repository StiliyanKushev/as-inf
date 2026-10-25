# Fresh-machine recovery and persona-LoRA training

This runbook reconstructs the AS-INF ComfyUI environment and continues the
`vexa_person` FLUX.2 Klein 9B LoRA project from a new computer. Pod IDs, public
proxy URLs, SSH ports, and IP addresses are temporary and must be discovered on
each run. The GitHub repository and RunPod network-volume ID are durable.

## Durable resources

| Resource | Value |
|---|---|
| GitHub repository | `https://github.com/StiliyanKushev/as-inf` |
| RunPod network volume | `final-kurva-maker-storage` (`3e71bw1e12`) |
| Volume region and mount | `US-CA-2`, `/workspace` |
| Volume size | 150 GB |
| GPU | One secure-cloud NVIDIA B200 180 GB |
| Container | `runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0` |
| Main workflow | `final-kurva-maker-reference.json` |
| Training config | `training/configs/vexa-person-klein9b-b200.yaml` |
| Identity trigger | `vexa_person` |

Never commit RunPod API keys, SSH private keys, Hugging Face tokens, or other
credentials. Generated checkpoints stay on `/workspace` unless deliberately
backed up elsewhere.

## Prepare a new computer

Install `git`, Git LFS, and `runpodctl`, then clone the repository:

```bash
git clone https://github.com/StiliyanKushev/as-inf.git
cd as-inf
git lfs install
git lfs pull
```

Configure RunPod without putting the API key in shell history:

```bash
read -rsp "RunPod API key: " key; echo
runpodctl config --apiKey "$key"
unset key
```

## Create and recover a B200 pod

The creation script attaches network volume `3e71bw1e12` at `/workspace`:

```bash
./scripts/create-b200.sh
runpodctl pod list -o json
```

Wait until `runtimeStatus` is `running`, then obtain current SSH details:

```bash
runpodctl pod get POD_ID --include-machine --include-network-volume -o yaml
```

Restore the persistent ComfyUI and Ollama services using the reported IP and
SSH port:

```bash
./scripts/recover-over-ssh.sh root@POD_IP SSH_PORT \
  ~/.runpod/ssh/runpodctl-ssh-key
```

Open `https://POD_ID-8188.proxy.runpod.net`. The recovery script launches the
pinned ComfyUI copy, plugins, models, workflows, settings, inputs, outputs, and
Ollama model stored on the network volume.

## Verify persistent state

On the pod:

```bash
/workspace/verify-persistent-state.sh
cd /workspace/as-inf
./training/scripts/validate-dataset.sh
sha256sum -c training/dataset-manifest.sha256
df -h /workspace
```

The dataset check must report 30 images and 30 matching captions. The checksum
command must report every file as `OK`.

## One-time Hugging Face access

While signed into Hugging Face, accept the license at:

<https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9B>

After installing AI Toolkit, authenticate through the browser device flow. The
token is stored on the persistent volume and is never committed:

```bash
HF_HOME=/workspace/huggingface \
  /workspace/ai-toolkit-venv/bin/hf auth login

HF_HOME=/workspace/huggingface \
  /workspace/ai-toolkit-venv/bin/hf auth whoami
```

FLUX.2 Klein 9B Base has a non-commercial license. Commercial use requires the
appropriate BFL license or changing the training target to Apache-2.0 Klein 4B.

## Install AI Toolkit and train

AI Toolkit is pinned by the install script. Its environment, model cache,
logs, samples, and checkpoints all stay under `/workspace`:

```bash
cd /workspace/as-inf
./training/scripts/install-ai-toolkit.sh
./training/scripts/train-vexa-klein9b.sh
```

The job trains rank 32 for 2,000 steps and saves fixed-seed previews and LoRA
checkpoints every 250 steps. Compare checkpoints from roughly step 750 through
1,500 before choosing one; identity quality may peak before step 2,000.

## Install the selected LoRA into ComfyUI

List the produced weights, then install the selected checkpoint:

```bash
find /workspace/training/output/vexa_person_klein9b_v1 \
  -type f -name '*.safetensors' -print

/workspace/as-inf/training/scripts/install-selected-lora.sh \
  /workspace/training/output/vexa_person_klein9b_v1/CHOSEN_CHECKPOINT.safetensors
```

Refresh ComfyUI's model list, select
`vexa_person_klein9b_v1.safetensors`, use trigger `vexa_person`, and begin near
LoRA strength `0.70`. Compare approximately `0.55` through `0.90`.

## Stop spending without losing state

Stop or delete the GPU pod when it is idle. Do **not** delete network volume
`3e71bw1e12`. Pod deletion removes the temporary container, but `/workspace`
persists independently. A future pod can attach the same volume and use the
recovery procedure above.
