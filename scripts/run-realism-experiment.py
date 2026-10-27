#!/usr/bin/env python3
"""Submit reproducible FLUX.2 Klein realism experiments to ComfyUI.

This script deliberately uses only the native ComfyUI FLUX.2 path:
Euler, Flux2Scheduler, SamplerCustomAdvanced, and a <=2 MP latent canvas.
It can add native FLUX.2 reference images or one model LoRA, and it saves a
native render plus two 3024x4032 delivery variants for comparison.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_PROMPT = (
    "A candid vertical 3:4 iPhone photograph of an adult brunette woman seated "
    "at an outdoor European cafe in clear morning light. She leans slightly "
    "toward the phone with one forearm visible and raises her other hand in a "
    "relaxed two-finger peace sign. Her hands and fingers have ordinary human "
    "anatomy. She wears a simple cotton summer dress. Coffee and eggs sit on the "
    "table, with cafe chairs and greenery receding naturally behind her. Natural "
    "skin texture, believable exposure and color, modest smartphone HDR, casual "
    "unretouched snapshot."
)


def node(class_type: str, **inputs: Any) -> dict[str, Any]:
    return {"class_type": class_type, "inputs": inputs}


def build_prompt(args: argparse.Namespace) -> dict[str, Any]:
    is_distilled = args.variant == "distilled"
    model_name = (
        "flux-2-klein-9b.safetensors"
        if is_distilled
        else "flux-2-klein-base-9b.safetensors"
    )
    steps = args.steps if args.steps is not None else (4 if is_distilled else 30)
    cfg = args.cfg if args.cfg is not None else (1.0 if is_distilled else 4.0)

    prompt_text = f"{args.trigger}, {args.prompt}" if args.trigger else args.prompt
    if args.reference and args.reference_role == "identity":
        prompt_text = (
            "The adult fictional woman must have the same facial identity as the "
            "woman shown in every reference image. Preserve that identity across "
            "the requested angle and expression. " + prompt_text
        )
    elif args.reference and args.reference_role == "scene":
        prompt_text = (
            "Use reference image 1 for the composition, pose, camera position, "
            "lighting, and scene layout. " + prompt_text
        )

    graph: dict[str, Any] = {
        "1": node("UNETLoader", unet_name=model_name, weight_dtype="default"),
        "2": node(
            "CLIPLoader",
            clip_name=args.encoder,
            type="flux2",
            device="default",
        ),
        "3": node("VAELoader", vae_name="flux2-vae.safetensors"),
        "4": node("CLIPTextEncode", text=prompt_text, clip=["2", 0]),
        "5": node("CLIPTextEncode", text="", clip=["2", 0]),
        "6": node(
            "EmptyFlux2LatentImage",
            width=args.width,
            height=args.height,
            batch_size=args.batch_size,
        ),
        "7": node("RandomNoise", noise_seed=args.seed),
        "8": node("KSamplerSelect", sampler_name="euler"),
        "10": node(
            "Flux2Scheduler",
            steps=steps,
            width=args.width,
            height=args.height,
        ),
    }

    model_output: list[Any] = ["1", 0]
    if args.lora:
        graph["20"] = node(
            "LoraLoaderModelOnly",
            model=model_output,
            lora_name=args.lora,
            strength_model=args.lora_strength,
        )
        model_output = ["20", 0]

    positive_output: list[Any] = ["4", 0]
    for index, image_name in enumerate(args.reference, start=1):
        base = 30 + index * 4
        load_id, scale_id, encode_id, ref_id = map(str, range(base, base + 4))
        graph[load_id] = node("LoadImage", image=image_name)
        graph[scale_id] = node(
            "ImageScaleToTotalPixels",
            image=[load_id, 0],
            upscale_method="lanczos",
            megapixels=args.reference_megapixels,
            resolution_steps=1,
        )
        graph[encode_id] = node("VAEEncode", pixels=[scale_id, 0], vae=["3", 0])
        graph[ref_id] = node(
            "ReferenceLatent", conditioning=positive_output, latent=[encode_id, 0]
        )
        positive_output = [ref_id, 0]

    graph["9"] = node(
        "CFGGuider",
        model=model_output,
        positive=positive_output,
        negative=["5", 0],
        cfg=cfg,
    )
    graph["11"] = node(
        "SamplerCustomAdvanced",
        noise=["7", 0],
        guider=["9", 0],
        sampler=["8", 0],
        sigmas=["10", 0],
        latent_image=["6", 0],
    )
    graph["12"] = node("VAEDecode", samples=["11", 0], vae=["3", 0])
    graph["13"] = node(
        "SaveImage", images=["12", 0], filename_prefix=f"{args.prefix}/native"
    )
    graph["14"] = node(
        "ImageScale",
        image=["12", 0],
        upscale_method="lanczos",
        width=3024,
        height=4032,
        crop="disabled",
    )
    graph["15"] = node(
        "SaveImage", images=["14", 0], filename_prefix=f"{args.prefix}/4k_lanczos"
    )

    if not args.skip_ai_upscale:
        graph["16"] = node("UpscaleModelLoader", model_name="RealESRGAN_x4plus.pth")
        graph["17"] = node(
            "ImageUpscaleWithModel", upscale_model=["16", 0], image=["12", 0]
        )
        graph["18"] = node(
            "ImageScale",
            image=["17", 0],
            upscale_method="lanczos",
            width=3024,
            height=4032,
            crop="disabled",
        )
        graph["19"] = node(
            "SaveImage", images=["18", 0], filename_prefix=f"{args.prefix}/4k_realesrgan"
        )
    return graph


def request_json(url: str, payload: dict[str, Any] | None = None) -> Any:
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def submit_and_wait(server: str, graph: dict[str, Any]) -> tuple[str, dict[str, Any], float]:
    queued = request_json(f"{server}/prompt", {"prompt": graph})
    prompt_id = queued["prompt_id"]
    started = time.monotonic()
    while True:
        history = request_json(f"{server}/history/{prompt_id}")
        if prompt_id in history:
            elapsed = time.monotonic() - started
            record = history[prompt_id]
            status = record.get("status", {})
            if status.get("status_str") == "error" or not status.get("completed", True):
                raise RuntimeError(json.dumps(status, indent=2))
            return prompt_id, record, elapsed
        if time.monotonic() - started > 3600:
            raise TimeoutError(f"ComfyUI prompt {prompt_id} exceeded one hour")
        time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--variant", choices=("distilled", "base"), default="distilled")
    parser.add_argument("--encoder", default="qwen_3_8b.safetensors")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--trigger", default="")
    parser.add_argument("--seed", type=int, default=27012026)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=1600)
    parser.add_argument("--steps", type=int)
    parser.add_argument("--cfg", type=float)
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument(
        "--reference-role", choices=("identity", "scene", "generic"), default="generic"
    )
    parser.add_argument("--reference-megapixels", type=float, default=1.0)
    parser.add_argument("--lora")
    parser.add_argument("--lora-strength", type=float, default=0.55)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--skip-ai-upscale", action="store_true")
    parser.add_argument("--manifest")
    args = parser.parse_args()

    graph = build_prompt(args)
    prompt_id, history, elapsed = submit_and_wait(args.server.rstrip("/"), graph)
    result = {
        "prompt_id": prompt_id,
        "elapsed_seconds": round(elapsed, 3),
        "settings": vars(args),
        "outputs": history.get("outputs", {}),
        "status": history.get("status", {}),
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.manifest:
        destination = Path(args.manifest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
