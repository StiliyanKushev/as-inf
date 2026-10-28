#!/usr/bin/env python3
"""Run a controlled Instagram-realism benchmark in ComfyUI.

The three branches reproduce the public inference cores from:

* Anuxq: Juggernaut XL v9 + PuLID v1.1.
* Ananya: Juggernaut XL v9 + ReActor, face restoration disabled.
* PixelAI Krea 2 Carousel: General Edit V2 + FameGrid + Realism Engine,
  with the source-reference geometry used by the Carousel node.

Private character LoRAs from the upstream projects are intentionally omitted.
Every branch receives the same fictional Alex Sparks reference, scene brief and
seed. Native outputs and 1080x1350 Instagram delivery files are both retained.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


CHECKPOINT = "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
REFERENCE = "persona_front_neutral.png"
SDXL_NEGATIVE = (
    "cgi, 3d render, illustration, painting, beauty filter, plastic skin, "
    "waxy skin, airbrushed skin, studio glamour, overprocessed, oversharpened, "
    "deformed hands, extra fingers, fused fingers, duplicate limbs, bad anatomy, "
    "text, watermark, logo"
)


@dataclass(frozen=True)
class Scene:
    name: str
    sdxl_prompt: str
    krea_instruction: str


SCENES = (
    Scene(
        "cafe",
        "A casual unposed iPhone photo of one 25-year-old woman with long "
        "center-parted dark-blonde hair seated at a small outdoor neighborhood "
        "cafe in late morning. She leans slightly toward the camera with a subtle "
        "closed-mouth smile. One hand loosely holds a plain ceramic coffee cup on "
        "the table and her other forearm rests naturally beside it. She wears a "
        "simple white linen sleeveless top and blue jeans. A few empty wicker "
        "chairs, small tables, and leafy plants sit behind her. Eye-level phone "
        "camera, ordinary 26 mm equivalent lens, slightly imperfect framing, "
        "believable daylight and highlight roll-off, natural pores and fine facial "
        "texture, restrained smartphone sharpening, no beauty filter, no staged "
        "fashion lighting, an authentic everyday Instagram post.",
        "Create a new casual unposed iPhone photograph of this same fictional "
        "woman seated at a small outdoor neighborhood cafe in late morning. "
        "Preserve her exact facial identity, eye color, facial proportions and "
        "long center-parted dark-blonde hair. She leans slightly toward the camera "
        "with a subtle closed-mouth smile. One hand loosely holds a plain ceramic "
        "coffee cup on the table and her other forearm rests naturally beside it. "
        "She wears a simple white linen sleeveless top and blue jeans. Include a "
        "few empty wicker chairs, small tables and leafy plants behind her. Use an "
        "eye-level ordinary iPhone camera, slightly imperfect framing, believable "
        "late-morning daylight, natural pores and fine skin texture, restrained "
        "phone sharpening, no beauty filter and no staged fashion lighting. The "
        "result is an authentic everyday Instagram post. famegrid",
    ),
    Scene(
        "street",
        "A candid full-body iPhone photograph of one 25-year-old woman with long "
        "center-parted dark-blonde hair walking along a quiet European side street "
        "in soft afternoon daylight. A friend photographs her from eye level as "
        "she takes an ordinary mid-step and glances toward the phone with a relaxed "
        "closed-mouth expression. She wears a plain charcoal T-shirt, straight-leg "
        "blue jeans, and worn white sneakers. One hand holds the strap of a small "
        "canvas shoulder bag and the other hangs naturally with five visible "
        "fingers. Parked bicycles, stucco walls, and two distant pedestrians form "
        "an unobtrusive background. Ordinary 26 mm equivalent phone lens, casual "
        "off-center composition, realistic body proportions, believable fabric "
        "folds, natural skin texture, restrained smartphone processing, no beauty "
        "filter, an authentic personal Instagram post.",
        "Create a new candid full-body iPhone photograph of this same fictional "
        "woman walking along a quiet European side street in soft afternoon "
        "daylight. Preserve her exact facial identity, eye color, facial "
        "proportions, and long center-parted dark-blonde hair. A friend photographs "
        "her from eye level during an ordinary mid-step while she glances toward "
        "the phone with a relaxed closed-mouth expression. She wears a plain "
        "charcoal T-shirt, straight-leg blue jeans and worn white sneakers. One "
        "hand holds a small canvas shoulder-bag strap; the other hangs naturally. "
        "Include parked bicycles, stucco walls and two distant pedestrians. Use an "
        "ordinary 26 mm equivalent phone lens, casual off-center composition, "
        "realistic body proportions and fabric folds, natural skin texture, "
        "restrained smartphone processing, no beauty filter. The result is an "
        "authentic personal Instagram post. famegrid",
    ),
)


def node(class_type: str, **inputs: Any) -> dict[str, Any]:
    return {"class_type": class_type, "inputs": inputs}


def add_delivery_nodes(graph: dict[str, Any], image: list[Any], prefix: str, start: int) -> None:
    graph[str(start)] = node(
        "ImageScale",
        image=image,
        upscale_method="lanczos",
        width=1080,
        height=1350,
        crop="disabled",
    )
    graph[str(start + 1)] = node(
        "SaveImage", images=[str(start), 0], filename_prefix=f"{prefix}/instagram_1080x1350"
    )


def build_anuxq(scene: Scene, seed: int, prefix: str, weight: float = 0.55) -> dict[str, Any]:
    graph = {
        "1": node("CheckpointLoaderSimple", ckpt_name=CHECKPOINT),
        "2": node("LoadImage", image=REFERENCE),
        "3": node("PulidModelLoader", pulid_file="pulid_v1.1.safetensors"),
        "4": node("PulidEvaClipLoader"),
        "5": node("PulidInsightFaceLoader", provider="CPU"),
        "6": node(
            "ApplyPulidAdvanced",
            model=["1", 0],
            pulid=["3", 0],
            eva_clip=["4", 0],
            face_analysis=["5", 0],
            image=["2", 0],
            weight=weight,
            projection="none",
            fidelity=12,
            noise=0.0,
            start_at=0.0,
            end_at=0.8,
        ),
        "7": node("CLIPTextEncode", text=scene.sdxl_prompt, clip=["1", 1]),
        "8": node("CLIPTextEncode", text=SDXL_NEGATIVE, clip=["1", 1]),
        "9": node("EmptyLatentImage", width=1024, height=1280, batch_size=1),
        "10": node(
            "KSampler",
            model=["6", 0],
            seed=seed,
            steps=25,
            cfg=4.0,
            sampler_name="dpmpp_2m",
            scheduler="karras",
            positive=["7", 0],
            negative=["8", 0],
            latent_image=["9", 0],
            denoise=1.0,
        ),
        "11": node("VAEDecode", samples=["10", 0], vae=["1", 2]),
        "12": node("SaveImage", images=["11", 0], filename_prefix=f"{prefix}/native_1024x1280"),
    }
    add_delivery_nodes(graph, ["11", 0], prefix, 13)
    return graph


def build_ananya(scene: Scene, seed: int, prefix: str, cfg: float = 8.0) -> dict[str, Any]:
    graph = {
        "1": node("CheckpointLoaderSimple", ckpt_name=CHECKPOINT),
        "2": node("LoadImage", image=REFERENCE),
        "3": node("CLIPTextEncode", text=scene.sdxl_prompt, clip=["1", 1]),
        "4": node("CLIPTextEncode", text=SDXL_NEGATIVE, clip=["1", 1]),
        "5": node("EmptyLatentImage", width=1024, height=1280, batch_size=1),
        "6": node(
            "KSampler",
            model=["1", 0],
            seed=seed,
            steps=30,
            cfg=cfg,
            sampler_name="dpmpp_2m",
            scheduler="karras",
            positive=["3", 0],
            negative=["4", 0],
            latent_image=["5", 0],
            denoise=1.0,
        ),
        "7": node("VAEDecode", samples=["6", 0], vae=["1", 2]),
        "8": node("SaveImage", images=["7", 0], filename_prefix=f"{prefix}/before_swap"),
        "9": node(
            "ReActorFaceSwap",
            enabled=True,
            input_image=["7", 0],
            source_image=["2", 0],
            swap_model="inswapper_128.onnx",
            facedetection="retinaface_resnet50",
            face_restore_model="none",
            face_restore_visibility=1.0,
            codeformer_weight=0.5,
            detect_gender_input="no",
            detect_gender_source="no",
            input_faces_index="0",
            source_faces_index="0",
            console_log_level=1,
        ),
        "10": node("SaveImage", images=["9", 0], filename_prefix=f"{prefix}/native_1024x1280"),
    }
    add_delivery_nodes(graph, ["9", 0], prefix, 11)
    return graph


def build_krea(scene: Scene, seed: int, prefix: str, finish: bool = True) -> dict[str, Any]:
    graph = {
        "1": node("UNETLoader", unet_name="krea2_turbo_fp8_scaled.safetensors", weight_dtype="default"),
        "2": node("LoraLoaderModelOnly", model=["1", 0], lora_name="krea2_general_edit_v2.safetensors", strength_model=1.0),
        "3": node("LoraLoaderModelOnly", model=["2", 0], lora_name="famegrid_spicy.safetensors", strength_model=0.5),
        "4": node("LoraLoaderModelOnly", model=["3", 0], lora_name="realism_engine_krea2_v3.1.safetensors", strength_model=0.5),
        "5": node("CLIPLoader", clip_name="qwen3vl_4b_fp8_scaled.safetensors", type="krea2", device="default"),
        "6": node("VAELoader", vae_name="qwen_image_vae.safetensors"),
        "7": node("LoadImage", image=REFERENCE),
        "8": node("VAEEncode", pixels=["7", 0], vae=["6", 0]),
        "9": node("EmptySD3LatentImage", width=1280, height=1600, batch_size=1),
        "10": node(
            "Krea2EditModelPatch",
            model=["4", 0],
            source_latent=["8", 0],
            ref_boost=2.0,
            fit_mode="fit",
            vae=["6", 0],
            source_image=["7", 0],
            target_latent=["9", 0],
            ref_position="beside (right of target)",
        ),
        "11": node(
            "Krea2EditGroundedEncode",
            clip=["5", 0],
            prompt=scene.krea_instruction,
            image=["7", 0],
            grounding_px=768,
            system_prompt="",
        ),
        "12": node(
            "Krea2EditGroundedEncode",
            clip=["5", 0],
            prompt="",
            image=["7", 0],
            grounding_px=768,
            system_prompt="",
        ),
        "13": node(
            "KSampler",
            model=["10", 0],
            seed=seed,
            steps=10,
            cfg=1.0,
            sampler_name="euler",
            scheduler="simple",
            positive=["11", 0],
            negative=["12", 0],
            latent_image=["9", 0],
            denoise=1.0,
        ),
        "14": node("VAEDecode", samples=["13", 0], vae=["6", 0]),
        "15": node("SaveImage", images=["14", 0], filename_prefix=f"{prefix}/before_finish"),
    }
    final = ["14", 0]
    if finish:
        graph["16"] = node(
            "FameGridColorFinish",
            image=["14", 0],
            color_strength=0.6,
            sharpen_strength=0.2,
        )
        graph["17"] = node("SaveImage", images=["16", 0], filename_prefix=f"{prefix}/native_1280x1600")
        final = ["16", 0]
        add_delivery_nodes(graph, final, prefix, 18)
    else:
        add_delivery_nodes(graph, final, prefix, 16)
    return graph


def request_json(url: str, payload: dict[str, Any] | None = None, timeout: float = 120) -> Any:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def submit_and_wait(server: str, graph: dict[str, Any]) -> tuple[str, dict[str, Any], float]:
    result = request_json(
        f"{server}/prompt", {"prompt": graph, "client_id": str(uuid.uuid4())}
    )
    if "error" in result:
        raise RuntimeError(json.dumps(result, indent=2))
    prompt_id = result["prompt_id"]
    started = time.monotonic()
    while True:
        history = request_json(f"{server}/history/{prompt_id}")
        if prompt_id in history:
            elapsed = time.monotonic() - started
            record = history[prompt_id]
            if record.get("status", {}).get("status_str") != "success":
                raise RuntimeError(json.dumps(record.get("status", record), indent=2))
            return prompt_id, record, elapsed
        if time.monotonic() - started > 3600:
            raise TimeoutError(f"ComfyUI prompt {prompt_id} exceeded one hour")
        time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--results", default="/workspace/as-inf/research-results/three-way-2026-10-28")
    parser.add_argument("--output-root", default="research-three-way")
    parser.add_argument("--methods", nargs="+", choices=("anuxq", "ananya", "krea"), default=("anuxq", "ananya", "krea"))
    parser.add_argument("--scenes", nargs="+", choices=tuple(s.name for s in SCENES), default=tuple(s.name for s in SCENES))
    parser.add_argument("--seeds", nargs="+", type=int, default=(27012026, 27012027))
    args = parser.parse_args()

    server = args.server.rstrip("/")
    results_dir = Path(args.results)
    graphs_dir = results_dir / "api-graphs"
    manifests_dir = results_dir / "manifests"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    builders: dict[str, Callable[[Scene, int, str], dict[str, Any]]] = {
        "anuxq": build_anuxq,
        "ananya": build_ananya,
        "krea": build_krea,
    }
    summary: list[dict[str, Any]] = []
    selected_scenes = [scene for scene in SCENES if scene.name in args.scenes]
    for method in args.methods:
        for scene in selected_scenes:
            for seed in args.seeds:
                run_name = f"{method}_{scene.name}_seed{seed}"
                prefix = f"{args.output_root}/{run_name}"
                graph = builders[method](scene, seed, prefix)
                (graphs_dir / f"{run_name}.json").write_text(json.dumps(graph, indent=2) + "\n")
                print(f"RUN {run_name}", flush=True)
                prompt_id, history, elapsed = submit_and_wait(server, graph)
                record = {
                    "run": run_name,
                    "method": method,
                    "scene": scene.name,
                    "seed": seed,
                    "prompt_id": prompt_id,
                    "elapsed_seconds": round(elapsed, 3),
                    "outputs": history.get("outputs", {}),
                    "status": history.get("status", {}),
                }
                (manifests_dir / f"{run_name}.json").write_text(json.dumps(record, indent=2) + "\n")
                summary.append(record)
                print(json.dumps({"run": run_name, "elapsed_seconds": record["elapsed_seconds"]}), flush=True)

    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"completed": len(summary), "results": str(results_dir)}, indent=2))


if __name__ == "__main__":
    main()
