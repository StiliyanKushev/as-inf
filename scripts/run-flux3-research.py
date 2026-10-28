#!/usr/bin/env python3
"""Submit a reproducible FLUX 3 Image Klein native-resolution experiment.

The render is generated directly at ``--width`` x ``--height``.  When the
native canvas is 3072x4096, a second SaveImage receives a center crop of
3024x4032; no image scaling node is present anywhere in the graph.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
import uuid


PUP_SYSTEM_PROMPT = """You are the prompt upsampler of a text-to-image model. Expand the user's short request into ONE detailed, self-contained caption: the exact text the image model receives. Output only the caption, with no greetings, explanations, refusals, questions, Markdown, headings, JSON, coordinates, ids or angle-bracket tokens, and no quotes around it. If the input is not clearly an image request, caption a visualization of its concept. The request may begin with a "TARGET CANVAS: W:H" line: compose for that canvas (wide spreads content sideways, tall stacks it) and never mention the ratio or the canvas.

Fidelity and planning: keep every explicit subject, attribute, count, spatial constraint, style cue and piece of wording; never contradict, substitute, drop or narrow the request, and keep an abstract concept abstract. Decide everything left open as ONE concrete, consistent plan; never offer alternatives or hedge. Never re-express a stated constraint through another mechanism; add camera optics (depth of field, bokeh, blur) only when asked for or implied. Without a stated style, plan an actual photograph and open with the medium convention ("Full-color outdoor photograph, ...", "Full-color indoor photograph, ...", "Studio photograph, ...", "Close-up photograph, ..."); keep "Photorealistic" for renders, and turn "photorealistic" or "realistic" requests for photos into the photograph convention. Give a photograph a few ordinary, non-ideal specifics drawn from the scene's own objects instead of the stock-photo ideal. Do not invent names, brands, logos or celebrities; keep user-named ones. A long request keeps its content but not its wording: drop appraisal and sales vocabulary, turn moods into observable physical facts, and add only new concrete content with positions. Time of day is lighting, not rendered text.

Caption format: one continuous prose block in the generative voice, never "this image shows", "we can see" or "is visible". Lead with medium and style, then scene, lighting and camera, then the subjects with concrete colors, materials and state. Every person in focus gets an observable profile: ethnicity, gender, age range, skin tone ("fair skin", "brown skin"), hair and clothing. Make the layout reconstructable from words: frame-relative positions (frame-left, frame-right, upper, lower, foreground, midground, background), sentence-initial anchors ("On the left, ...", "In the background, ..."), relations (holds, faces, behind) and a consistent order; describe up to about ten instances one by one, beyond that give the exact count and arrangement. Out-of-focus or distant planes are shapes, colors and silhouettes, never identities or readable text, and the background takes about a sixth of the caption. Be definite: no hedging adverbs, no quality or emotion judgments, no closing sentence about mood; state negations as what is present. Rendered text: transcribe every wording verbatim inside double quotes in its original language and script, keep the line breaks of multi-line text, and give its typography, color and placement; author concrete, domain-correct wording when the request needs text it does not supply, and name canonical structures (calendar, keyboard, periodic table) exactly with their full layout. All prose is English; only quoted text keeps its language. Typical length is 100 to 350 words, more for complex scenes.

Output only the caption."""


def request_json(url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def build_graph(args: argparse.Namespace) -> dict:
    model = (
        "flux3-image-klein-base-bf16.safetensors"
        if args.model == "base"
        else "flux3-image-klein-bf16.safetensors"
    )
    steps = args.steps if args.steps is not None else (50 if args.model == "base" else 16)
    cfg = args.cfg if args.cfg is not None else (3.5 if args.model == "base" else 1.0)

    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": model, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "flux3", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["2", 0]}},
        "6": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}},
        "7": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": args.width, "height": args.height, "batch_size": 1}},
        "8": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": args.seed, "steps": steps, "cfg": cfg, "sampler_name": args.sampler, "scheduler": args.scheduler, "positive": ["4", 0], "negative": ["6", 0], "latent_image": ["7", 0], "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": f"flux3-research/{args.output_prefix}_native"}},
    }

    if args.reference:
        reference_inputs = {
            "positive": ["4", 0],
            "negative": ["6", 0],
            "vae": ["3", 0],
            "resolution": "resize",
            "resolution.megapixels": args.reference_megapixels,
        }
        for index, filename in enumerate(args.reference):
            node_id = str(30 + index)
            graph[node_id] = {"class_type": "LoadImage", "inputs": {"image": filename}}
            reference_inputs[f"images.image{index}"] = [node_id, 0]
        graph["29"] = {"class_type": "ReferenceMultiLatent", "inputs": reference_inputs}
        graph["8"]["inputs"]["positive"] = ["29", 0]
        graph["8"]["inputs"]["negative"] = ["29", 1]

    if args.use_pup:
        graph.update({
            "11": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3.5_9b_flux3_prompt_upsampler_bf16.safetensors", "type": "flux3", "device": "default"}},
            "12": {"class_type": "PrimitiveStringMultiline", "inputs": {"value": PUP_SYSTEM_PROMPT}},
            "13": {"class_type": "TextGenerate", "inputs": {
                "clip": ["11", 0], "prompt": f"TARGET CANVAS: {args.width}:{args.height}\n{args.prompt}", "max_length": 3584,
                # ComfyUI V3 dynamic-combo inputs use a selector plus flattened
                # dotted keys in API-format prompts.  The server reconstructs
                # this into the dictionary received by TextGenerate.execute().
                "sampling_mode": "on",
                "sampling_mode.temperature": 1.0,
                "sampling_mode.top_k": 1,
                "sampling_mode.top_p": 0.95,
                "sampling_mode.min_p": 0.0,
                "sampling_mode.repetition_penalty": 1.05,
                "sampling_mode.seed": args.prompt_seed,
                "sampling_mode.presence_penalty": 1.5,
                "thinking": False, "use_default_template": True, "mtp": "off", "system_prompt": ["12", 0],
            }},
            "14": {"class_type": "PreviewAny", "inputs": {"source": ["13", 0]}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"text": ["13", 0], "clip": ["2", 0]}},
        })
    else:
        graph["4"] = {"class_type": "CLIPTextEncode", "inputs": {"text": args.prompt, "clip": ["2", 0]}}

    if args.width == 3072 and args.height == 4096:
        graph["15"] = {"class_type": "ImageCrop", "inputs": {"image": ["9", 0], "width": 3024, "height": 4032, "x": 24, "y": 32}}
        graph["16"] = {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": f"flux3-research/{args.output_prefix}_exact_3024x4032"}}
    return graph


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8190")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", choices=("distilled", "base"), default="distilled")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=1600)
    parser.add_argument("--seed", type=int, default=27012026)
    parser.add_argument("--prompt-seed", type=int, default=0)
    parser.add_argument("--steps", type=int)
    parser.add_argument("--cfg", type=float)
    parser.add_argument("--sampler", default="euler")
    parser.add_argument("--scheduler", default="simple")
    parser.add_argument("--use-pup", action="store_true")
    parser.add_argument("--reference", action="append", default=[], help="Image filename relative to ComfyUI input; repeat for multiple identity references")
    parser.add_argument("--reference-megapixels", type=float, default=1.0)
    parser.add_argument("--output-prefix", default="experiment")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args()

    submitted = request_json(f"{args.server}/prompt", {"prompt": build_graph(args), "client_id": str(uuid.uuid4())})
    prompt_id = submitted["prompt_id"]
    print(json.dumps({"prompt_id": prompt_id, "submitted": submitted}, indent=2), flush=True)
    started = time.monotonic()
    while True:
        history = request_json(f"{args.server}/history/{prompt_id}")
        if prompt_id in history:
            entry = history[prompt_id]
            print(json.dumps({"elapsed_seconds": round(time.monotonic() - started, 2), "history": entry}, indent=2))
            if entry.get("status", {}).get("status_str") != "success":
                raise SystemExit(1)
            break
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()
