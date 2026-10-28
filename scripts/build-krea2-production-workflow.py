#!/usr/bin/env python3
"""Build the maintained Krea 2 production workflow from pinned UI templates.

The prompt/control nodes are copied from the largest maintained Kurva Maker
workflow. Krea-specific nodes are copied from the public workflow snapshots in
vendor/ so their serialized UI schema stays compatible with ComfyUI.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workflows/final-kurva-maker-reference-spatial-face-lora.json"
KREA_EDIT = ROOT / "vendor/krea2-edit/workflows/krea2_identity_edit.json"
KREA_CAROUSEL = ROOT / "vendor/krea2-carousel/example_workflows/Krea2_Carousel.json"
OUTPUT = ROOT / "workflows/final-kurva-maker-krea2.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


source = load(SOURCE)
edit = load(KREA_EDIT)
carousel = load(KREA_CAROUSEL)


def by_id(graph: dict, node_id: int) -> dict:
    return copy.deepcopy(next(node for node in graph["nodes"] if node["id"] == node_id))


def by_type(graph: dict, node_type: str) -> dict:
    return copy.deepcopy(next(node for node in graph["nodes"] if node["type"] == node_type))


def reset(node: dict, node_id: int, title: str, pos: tuple[float, float], size=None) -> dict:
    node["id"] = node_id
    node["title"] = title
    node["pos"] = list(pos)
    if size is not None:
        node["size"] = list(size)
    node["order"] = 0
    node["mode"] = 0
    for item in node.get("inputs", []):
        item["link"] = None
    for item in node.get("outputs", []):
        item["links"] = []
    return node


nodes: list[dict] = []
node_map: dict[int, dict] = {}


def add(node: dict) -> dict:
    if node["id"] in node_map:
        raise ValueError(f"duplicate node id {node['id']}")
    nodes.append(node)
    node_map[node["id"]] = node
    return node


def clone_source(old_id: int, new_id: int, title: str, pos, size=None) -> dict:
    return add(reset(by_id(source, old_id), new_id, title, pos, size))


def widget(node: dict, values: list, named: dict | None = None) -> None:
    node["widgets_values"] = values
    if named is not None:
        node["widgets_values_named"] = named


# ----------------------------- control panel -----------------------------
crop = clone_source(
    51,
    1,
    "OPTIONAL REFERENCE + FIXED 4:5 CROP · None = prompt-only",
    (-2200, -2260),
    (680, 760),
)
crop["type"] = "ASInfOptionalReferenceCrop4x5"
crop["properties"] = {"Node name for S&R": "ASInfOptionalReferenceCrop4x5", "cnr_id": "as-inf"}
widget(
    crop,
    ["[None — prompt-only mode]", 0.0, 0.0, 1.0, 1.0, "image"],
    {
        "image": "[None — prompt-only mode]",
        "crop_x": 0.0,
        "crop_y": 0.0,
        "crop_w": 1.0,
        "crop_h": 1.0,
        "upload": "image",
    },
)

request = clone_source(
    61,
    2,
    "REQUEST / PROMPT · full scene with None, changes with reference",
    (-1440, -2260),
    (620, 360),
)
widget(request, [""], {"value": ""})

compare = clone_source(
    57,
    3,
    "FINAL RESULT · generated / reference slider",
    (-740, -2260),
    (680, 760),
)

settings = clone_source(
    39,
    4,
    "KREA 2 SETTINGS · native render + batch",
    (-2200, -2800),
    (390, 250),
)
widget(
    settings,
    [10, 1.0, "euler", "simple", 1],
    {"steps": 10, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "batch_size": 1},
)

seed = clone_source(93, 5, "SEED · fixed / randomized", (-2200, -2520), (390, 120))
widget(seed, [27012026, "fixed"], {"value": 27012026})

# Three editable LoRA slots preserve the original Advanced Settings behavior.
lora1 = clone_source(7, 6, "LoRA 1 · Krea2 General Edit V2", (-1760, -2800), (400, 190))
widget(
    lora1,
    ["krea2_general_edit_v2.safetensors", 1.0, ""],
    {"lora_name": "krea2_general_edit_v2.safetensors", "strength_model": 1.0, "trigger_words": ""},
)
lora2 = clone_source(49, 7, "LoRA 2 · FameGrid", (-1310, -2800), (400, 190))
widget(
    lora2,
    ["famegrid_spicy.safetensors", 0.5, "famegrid"],
    {"lora_name": "famegrid_spicy.safetensors", "strength_model": 0.5, "trigger_words": "famegrid"},
)
lora3 = clone_source(7, 8, "LoRA 3 · Realism Engine", (-860, -2800), (400, 190))
widget(
    lora3,
    ["realism_engine_krea2_v3.1.safetensors", 0.5, ""],
    {"lora_name": "realism_engine_krea2_v3.1.safetensors", "strength_model": 0.5, "trigger_words": ""},
)

guide_text = """FINAL KURVA MAKER · KREA 2 TURBO

CONTROL PANEL
Choose an optional reference, write the request, inspect the final slider, and use Advanced Settings for seed, sampling, batch size, and three editable LoRA slots. Trigger text is added only while its LoRA strength is non-zero.

PROMPT-ONLY MODE
Choose [None — prompt-only mode] and describe the complete desired photograph. Krea2 generates a new generic fictional adult subject; the FLUX-trained Alex Sparks LoRA is deliberately not loaded because it is incompatible with Krea2.

REFERENCE MODE
Upload an image and move/zoom the permanently locked 4:5 crop. Describe only the desired changes. The selected pixels enter Qwen analysis, Krea2's VAE reference-token path, Krea2's grounded Qwen3-VL encoder, and the comparison viewer. General Edit V2 is active at the measured strength.

OUTPUT
The diffusion render is a true native 1280 × 1600 image. FameGrid Color Finish runs after decode. A separate 1080 × 1350 Instagram delivery copy is saved with Lanczos. This workflow does not claim a resized image is native 4K; Krea2 Edit's documented reliable range is at or below about two megapixels.

KNOWN LIMIT
Reference mode supplies identity and composition through Krea2 General Edit. A reusable Alex identity in prompt-only mode needs a Krea2-trained character LoRA; the existing alexsparks.safetensors is FLUX.2 Klein-specific."""
guide = clone_source(44, 9, "WORKFLOW GUIDE", (980, 1320), (900, 500))
widget(guide, [guide_text], {"text": guide_text})

# ------------------------------- model stack -----------------------------
unet = add(reset(by_type(carousel, "UNETLoader"), 10, "1 · Krea 2 Turbo FP8", (-2200, -980), (390, 100)))
widget(unet, ["krea2_turbo_fp8_scaled.safetensors", "default"], {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"})

clip = add(reset(by_type(carousel, "CLIPLoader"), 11, "Qwen3-VL 4B text encoder · Krea2", (-1750, -980), (430, 120)))
widget(clip, ["qwen3vl_4b_fp8_scaled.safetensors", "krea2", "default"], {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2", "device": "default"})

vae = add(reset(by_type(carousel, "VAELoader"), 12, "Krea 2 VAE", (-1260, -980), (390, 80)))
widget(vae, ["qwen_image_vae.safetensors"], {"vae_name": "qwen_image_vae.safetensors"})

# -------------------------- reference and latent -------------------------
normalize = clone_source(75, 13, "Normalize selected crop · 1280 × 1600", (-2200, -360), (400, 130))
widget(normalize, ["lanczos", 1280, 1600, "disabled"], {"upscale_method": "lanczos", "width": 1280, "height": 1600, "crop": "disabled"})

vae_encode = clone_source(53, 14, "Encode Krea2 reference tokens", (-1740, -360), (330, 90))

latent = add(reset(by_type(edit, "EmptySD3LatentImage"), 15, "Native canvas · 1280 × 1600", (-2200, -160), (390, 130)))
widget(latent, [1280, 1600, 1], {"width": 1280, "height": 1600, "batch_size": 1})
if not any(i["name"] == "batch_size" for i in latent["inputs"]):
    latent["inputs"].append({"name": "batch_size", "type": "INT", "widget": {"name": "batch_size"}, "link": None})

patch_node = add(reset(by_type(edit, "Krea2EditModelPatch"), 16, "Krea2 General Edit · source patch", (-1320, -390), (460, 280)))
widget(
    patch_node,
    [2.0, 1.0, "fit", "beside (right of target)", "aligned (trained)"],
    {"ref_boost": 2.0, "ref_boost_a": 1.0, "fit_mode": "fit", "ref_position": "beside (right of target)", "ref_position_a": "aligned (trained)"},
)

model_switch = clone_source(71, 17, "Model path · source patch optional", (-760, -390), (390, 130))
for inp in model_switch["inputs"][:2]:
    inp["type"] = "MODEL"
model_switch["outputs"][0]["type"] = "MODEL"

edit_lora_switch = clone_source(71, 43, "General Edit LoRA · reference only", (-820, -980), (390, 130))
for inp in edit_lora_switch["inputs"][:2]:
    inp["type"] = "MODEL"
edit_lora_switch["outputs"][0]["type"] = "MODEL"

reference_delivery = clone_source(56, 18, "Comparison reference · 1080 × 1350", (-1740, -160), (400, 130))
widget(reference_delivery, ["lanczos", 1080, 1350, "disabled"], {"upscale_method": "lanczos", "width": 1080, "height": 1350, "crop": "disabled"})

# ----------------------------- prompt compiler ---------------------------
analyzer = clone_source(58, 19, "1 · Analyze reference image · Qwen3-VL", (-2200, 740), (560, 650))
analysis_prompt = """Analyze the supplied reference photograph for a Krea 2 General Edit instruction. Output only a precise English source description, with no heading or commentary. Describe the exact camera position, 4:5 crop, rectilinear perspective, composition, subject count and placement, pose, proportions, hands, expression, hair, garments, lighting, focal plane, depth of field, background blur, white balance, exposure, contrast, saturation, major colors, objects, architecture, and spatial relationships. Treat visible pixels as authoritative defaults. Do not improve, mute, sharpen, recolor, or redesign them. The final canvas is a full-bleed vertical 4:5 photograph with straight boundaries and no fisheye, black corners, rounded mask, letterbox, or border. A later authoritative request may replace any named attribute; do not prohibit changes. End with safeguards against duplicate people, extra or missing limbs/digits, malformed anatomy, warped geometry, text, watermarks, and unrelated additions."""
analyzer["widgets_values"][6] = analysis_prompt
if "widgets_values_named" in analyzer:
    analyzer["widgets_values_named"]["custom_prompt"] = analysis_prompt

reference_rules = clone_source(60, 20, "Reference mode · Krea2 preservation rules", (-1570, 740), (560, 420))
reference_base = """REFERENCE MODE: use the selected photograph as the Krea2 source image. Its selected 4:5 pixels define the default composition, identity, pose, scene, depth of field, colorimetry, lighting, and geometry. Preserve every visible attribute the authoritative request does not replace. Apply the requested changes clearly while keeping exactly one main foreground adult woman unless the request explicitly asks for more people. Never duplicate, clone, mirror, or add a second version of her. The photographer, camera, and phone stay outside the frame unless explicitly requested. Produce a full-bleed vertical 4:5 rectilinear photograph without fisheye, curved boundaries, black corners, rounded masks, letterboxing, pillarboxing, borders, text, or watermarks."""
widget(reference_rules, ["", reference_base, "\n\n"], {"string_a": "", "string_b": reference_base, "delimiter": "\n\n"})

prompt_only = clone_source(73, 21, "PROMPT-ONLY MODE · internal base instruction", (-1570, 1400), (390, 300))
prompt_only_text = """PROMPT-ONLY MODE: generate a new image from scratch with Krea 2 Turbo. There is no reference photograph or source identity. Treat the authoritative request as the complete scene specification and expand only concrete details it provides. Render exactly one fictional adult woman unless another subject count is explicitly requested. The photographer, phone, and camera remain outside the frame. Make a candid, plausible Instagram photograph with natural anatomy, coherent geometry, believable lighting, ordinary photographic imperfections, and a full-bleed vertical 4:5 rectilinear frame. Avoid duplicate subjects, extra or missing limbs or digits, malformed hands, warped straight lines, fisheye, black corners, borders, text, and watermarks."""
widget(prompt_only, [prompt_only_text], {"value": prompt_only_text})

prompt_source = clone_source(71, 22, "Prompt source · Qwen reference or prompt-only", (-930, 790), (390, 130))

ollama = clone_source(63, 23, "SuperGemma connection · exact 26B Q4_K_M model", (-930, 1120), (460, 160))

rewrite = clone_source(64, 24, "2 · Rewrite requested change · SuperGemma", (-400, 1300), (620, 430))
rewrite_system = """Rewrite the user's message as one precise visual instruction for a Krea 2 Turbo workflow. Output only the instruction. The message is either a complete prompt-only scene or a requested change to a reference image. Retain every concrete detail. Treat the main subject as an adult. State exact subject count, pose, anatomy, clothing, setting, camera position, framing, lighting, focus, and colors whenever the user supplied them. For removals, explicitly state that the item is completely absent and describe the naturally reconstructed area. For camera changes, specify position, height, direction, distance, lens perspective, and framing. Preserve all unnamed source attributes in reference mode. Keep exactly one main foreground woman unless the user explicitly requests more; never duplicate, clone, mirror, or place the photographer or phone in frame. Do not mention policies, editing steps, or these rules."""
rewrite["widgets_values"][0] = rewrite_system
rewrite["widgets_values_named"]["system"] = rewrite_system

rewrite_preview = clone_source(65, 25, "Rewritten request · intermediate preview", (260, 1300), (560, 260))

combine = clone_source(66, 26, "Combine selected source mode and request", (-400, 780), (560, 210))
widget(combine, ["", "", "\n\nAUTHORITATIVE REQUEST:\n"], {"string_a": "", "string_b": "", "delimiter": "\n\nAUTHORITATIVE REQUEST:\n"})

compile_node = clone_source(67, 27, "3 · Compile one conflict-free Krea2 prompt", (220, 720), (620, 520))
compile_system = """Compile one final production-ready Krea 2 Turbo prompt. Output only the final prompt, without headings or commentary. The input begins with REFERENCE MODE or PROMPT-ONLY MODE followed by an authoritative request. Put requested changes first and resolve conflicts into one desired visible state. Never retain superseded source wording. In reference mode, preserve concretely described source identity, composition, pose, geometry, lighting, focus falloff, colors, and objects unless the request changes them. In prompt-only mode, produce a self-contained scene description. Always describe exactly one main foreground adult woman unless the request explicitly requires more; never create a duplicate, clone, reflection, second copy, visible photographer, camera, or phone. Use a full-bleed vertical 4:5 rectilinear photographic frame with natural proportions, plausible hands, coherent perspective, authentic Instagram color and texture, and no fisheye, black corners, rounded mask, borders, text, or watermark. Keep the result concise: 120 to 240 words."""
compile_node["widgets_values"][0] = compile_system
compile_node["widgets_values_named"]["system"] = compile_system

triggers = clone_source(76, 28, "Apply active LoRA trigger words", (900, 720), (540, 250))
compiled_preview = clone_source(59, 29, "FINAL KREA2 PROMPT · inspect here", (900, 1020), (540, 250))

# -------------------------- Krea2 conditioning ---------------------------
text_positive = clone_source(3, 30, "Prompt-only positive encode", (-700, -280), (390, 180))
widget(text_positive, [""], {"text": ""})
text_negative = clone_source(5, 31, "Prompt-only negative encode", (-700, -60), (390, 180))
widget(text_negative, [""], {"text": ""})

grounded_positive = add(reset(by_type(edit, "Krea2EditGroundedEncode"), 32, "Reference positive · grounded encode", (-240, -300), (430, 240)))
widget(grounded_positive, ["", 768, ""], {"prompt": "", "grounding_px": 768, "system_prompt": ""})
if not any(i["name"] == "prompt" for i in grounded_positive["inputs"]):
    grounded_positive["inputs"].insert(1, {"name": "prompt", "type": "STRING", "widget": {"name": "prompt"}, "link": None})

grounded_negative = add(reset(by_type(edit, "Krea2EditGroundedEncode"), 33, "Reference negative · grounded unconditional", (-240, 0), (430, 220)))
widget(grounded_negative, ["", 768, ""], {"prompt": "", "grounding_px": 768, "system_prompt": ""})
if not any(i["name"] == "prompt" for i in grounded_negative["inputs"]):
    grounded_negative["inputs"].insert(1, {"name": "prompt", "type": "STRING", "widget": {"name": "prompt"}, "link": None})

positive_switch = clone_source(71, 34, "Positive conditioning · reference optional", (260, -260), (390, 130))
negative_switch = clone_source(71, 35, "Negative conditioning · reference optional", (260, -60), (390, 130))
for switch in (positive_switch, negative_switch):
    for inp in switch["inputs"][:2]:
        inp["type"] = "CONDITIONING"
    switch["outputs"][0]["type"] = "CONDITIONING"

# ---------------------------- generation/output -------------------------
sampler = clone_source(91, 36, "Krea 2 Turbo sampler · native 1280 × 1600", (760, -320), (430, 300))
widget(
    sampler,
    [27012026, "fixed", 10, 1.0, "euler", "simple", 1.0],
    {"seed": 27012026, "control_after_generate": "fixed", "steps": 10, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0},
)

decode = clone_source(37, 37, "Decode native Krea2 render", (1260, -320), (320, 90))

finish = add(reset(by_type(carousel, "FameGridColorFinish"), 38, "FameGrid Color Finish · measured winner", (1640, -320), (390, 130)))
widget(finish, [0.6, 0.2], {"color_strength": 0.6, "sharpen_strength": 0.2})

save_native = clone_source(48, 39, "Save native render · 1280 × 1600", (2080, -360), (390, 120))
widget(save_native, ["FinalKurvaMakerKrea2/native_1280x1600"], {"filename_prefix": "FinalKurvaMakerKrea2/native_1280x1600"})

delivery = clone_source(47, 40, "Instagram delivery · 1080 × 1350", (1640, -100), (390, 130))
widget(delivery, ["lanczos", 1080, 1350, "disabled"], {"upscale_method": "lanczos", "width": 1080, "height": 1350, "crop": "disabled"})

save_delivery = clone_source(48, 41, "Save Instagram copy · 1080 × 1350", (2080, -120), (390, 120))
widget(save_delivery, ["FinalKurvaMakerKrea2/instagram_1080x1350"], {"filename_prefix": "FinalKurvaMakerKrea2/instagram_1080x1350"})

comparison_switch = clone_source(72, 42, "Comparison B · reference or generated fallback", (2080, 100), (400, 130))

# ------------------------------- wiring ---------------------------------
links: list[list] = []


def output_index(node: dict, name: str) -> int:
    for index, item in enumerate(node.get("outputs", [])):
        if item["name"] == name:
            return index
    raise KeyError(f"{node['id']}:{node['type']} missing output {name}")


def input_index(node: dict, name: str) -> int:
    for index, item in enumerate(node.get("inputs", [])):
        if item["name"] == name:
            return index
    raise KeyError(f"{node['id']}:{node['type']} missing input {name}")


def connect(src: int, src_out: str, dst: int, dst_in: str, link_type=None) -> None:
    source_node = node_map[src]
    target_node = node_map[dst]
    oi = output_index(source_node, src_out)
    ii = input_index(target_node, dst_in)
    typ = link_type or source_node["outputs"][oi]["type"]
    link_id = len(links) + 1
    links.append([link_id, src, oi, dst, ii, typ])
    source_node["outputs"][oi].setdefault("links", []).append(link_id)
    target_node["inputs"][ii]["link"] = link_id


# Model/LoRA stack.
connect(10, "MODEL", 6, "model")
connect(10, "MODEL", 43, "on_false")
connect(6, "model", 43, "on_true")
connect(1, "has_reference", 43, "switch")
connect(43, "output", 7, "model")
connect(7, "model", 8, "model")
connect(8, "model", 16, "model")
connect(8, "model", 17, "on_false")
connect(16, "MODEL", 17, "on_true")
connect(1, "has_reference", 17, "switch")

# Optional reference and Krea2 source patch.
connect(1, "image", 13, "image")
connect(13, "IMAGE", 14, "pixels")
connect(12, "VAE", 14, "vae")
connect(14, "LATENT", 16, "source_latent")
connect(12, "VAE", 16, "vae")
connect(13, "IMAGE", 16, "source_image")
connect(15, "LATENT", 16, "target_latent")
connect(13, "IMAGE", 18, "image")
connect(4, "BATCH_SIZE", 15, "batch_size")

# Prompt analysis and SuperGemma compiler.
connect(13, "IMAGE", 19, "image")
connect(19, "RESPONSE", 20, "string_a")
connect(21, "STRING", 22, "on_false")
connect(20, "STRING", 22, "on_true")
connect(1, "has_reference", 22, "switch")
connect(23, "connection", 24, "connectivity")
connect(2, "STRING", 24, "prompt")
connect(24, "result", 25, "source")
connect(22, "output", 26, "string_a")
connect(24, "result", 26, "string_b")
connect(23, "connection", 27, "connectivity")
connect(26, "STRING", 27, "prompt")
connect(6, "active_trigger_words", 28, "trigger_1")
connect(7, "active_trigger_words", 28, "trigger_2")
connect(8, "active_trigger_words", 28, "trigger_3")
connect(27, "result", 28, "prompt")
connect(28, "prompt", 29, "source")

# Text-only and reference-grounded Krea2 conditioning.
connect(11, "CLIP", 30, "clip")
connect(28, "prompt", 30, "text")
connect(11, "CLIP", 31, "clip")
connect(11, "CLIP", 32, "clip")
connect(28, "prompt", 32, "prompt")
connect(13, "IMAGE", 32, "image")
connect(11, "CLIP", 33, "clip")
connect(13, "IMAGE", 33, "image")
connect(30, "CONDITIONING", 34, "on_false")
connect(32, "CONDITIONING", 34, "on_true")
connect(1, "has_reference", 34, "switch")
connect(31, "CONDITIONING", 35, "on_false")
connect(33, "CONDITIONING", 35, "on_true")
connect(1, "has_reference", 35, "switch")

# Native generation and delivery.
connect(17, "output", 36, "model")
connect(34, "output", 36, "positive")
connect(35, "output", 36, "negative")
connect(15, "LATENT", 36, "latent_image")
connect(5, "INT", 36, "seed")
connect(4, "STEPS", 36, "steps")
connect(4, "CFG", 36, "cfg")
connect(4, "SAMPLER", 36, "sampler_name")
connect(4, "SCHEDULER", 36, "scheduler")
connect(36, "LATENT", 37, "samples")
connect(12, "VAE", 37, "vae")
connect(37, "IMAGE", 38, "image")
connect(38, "image", 39, "images")
connect(38, "image", 40, "image")
connect(40, "IMAGE", 41, "images")
connect(40, "IMAGE", 42, "on_false")
connect(18, "IMAGE", 42, "on_true")
connect(1, "has_reference", 42, "switch")
connect(40, "IMAGE", 3, "image_a")
connect(42, "output", 3, "image_b")

# Stable execution order helps Comfy's UI and prompt serializer.
for order, node in enumerate(nodes):
    node["order"] = order

groups = [
    {"id": 1, "title": "00 · CONTROL PANEL — START HERE", "bounding": [-2280, -2940, 2340, 1510], "color": "#2b607d", "font_size": 30, "flags": {}},
    {"id": 2, "title": "ADVANCED SETTINGS", "bounding": [-2240, -2870, 2200, 560], "color": "#4c3f73", "font_size": 24, "flags": {}},
    {"id": 3, "title": "01 · KREA 2 TURBO MODEL STACK", "bounding": [-2280, -1060, 1900, 250], "color": "#596247", "font_size": 24, "flags": {}},
    {"id": 4, "title": "02 · OPTIONAL 4:5 REFERENCE", "bounding": [-2280, -470, 2020, 680], "color": "#3c6875", "font_size": 24, "flags": {}},
    {"id": 5, "title": "03 · KREA 2 CONDITIONING", "bounding": [-760, -470, 1430, 760], "color": "#5d536e", "font_size": 24, "flags": {}},
    {"id": 6, "title": "04 · NATIVE GENERATION + INSTAGRAM DELIVERY", "bounding": [690, -470, 1830, 760], "color": "#48634e", "font_size": 24, "flags": {}},
    {"id": 7, "title": "05 · AUTOMATIC PROMPT BUILDER", "bounding": [-2280, 630, 4210, 1260], "color": "#66513d", "font_size": 24, "flags": {}},
]

workflow = {
    "id": "7a9e995d-ba78-4f17-8b7d-16978bd168df",
    "revision": 0,
    "last_node_id": max(node_map),
    "last_link_id": len(links),
    "nodes": nodes,
    "links": links,
    "groups": groups,
    "config": {},
    "extra": {"ds": {"scale": 0.55, "offset": [1420, 1790]}},
    "version": 0.4,
}


def validate(data: dict) -> None:
    seen_links = {link[0] for link in data["links"]}
    assert len(seen_links) == len(data["links"])
    for node in data["nodes"]:
        for inp in node.get("inputs", []):
            if inp.get("link") is not None:
                assert inp["link"] in seen_links, (node["id"], inp)
        for out in node.get("outputs", []):
            for link_id in out.get("links") or []:
                assert link_id in seen_links, (node["id"], out)
    for link_id, src, src_slot, dst, dst_slot, _ in data["links"]:
        assert node_map[src]["outputs"][src_slot]["links"].count(link_id) == 1
        assert node_map[dst]["inputs"][dst_slot]["link"] == link_id


validate(workflow)
OUTPUT.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUTPUT.relative_to(ROOT)}: {len(nodes)} nodes, {len(links)} links")
