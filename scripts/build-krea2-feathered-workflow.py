#!/usr/bin/env python3
"""Build the feathered 75% Krea reference experiment from production workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workflows/final-kurva-maker-krea2-prealex-alex-finish.json"
OUTPUT = ROOT / "workflows/final-kurva-maker-krea2-prealex-alex-finish-feathered.json"

POSITIONS = [
    "aligned (trained)",
    "balanced (75% overlap)",
    "feathered (75% shift)",
    "balanced (half overlap)",
    "beside (right of target)",
    "bag of features",
]

REFERENCE_ANALYSIS = (
    "Analyze the supplied reference photograph for a Krea 2 General Edit "
    "instruction. Output only a precise English source description, with no "
    "heading or commentary. Describe the exact camera position, 4:5 crop, "
    "rectilinear perspective, composition, subject count and placement, pose, "
    "proportions, hands, expression, hair, garments, lighting, focal plane, "
    "depth of field, background focus, white balance, exposure, contrast, "
    "saturation, major colors, objects, architecture, and spatial relationships. "
    "Classify background focus strictly from visible pixels as deep/sharp, mildly "
    "soft, or shallow/bokeh. If it is sharp, explicitly state deep focus with no "
    "portrait-mode blur or bokeh. Never infer background blur merely because a "
    "person is in the foreground, and never exaggerate the amount visible. Treat "
    "visible pixels as authoritative defaults. Do not improve, mute, sharpen, "
    "recolor, or redesign them. The final canvas is a full-bleed vertical 4:5 "
    "photograph with straight boundaries and no fisheye, black corners, rounded "
    "mask, letterbox, or border. A later authoritative request may replace any "
    "named attribute; do not prohibit changes. End with safeguards against "
    "duplicate people, extra or missing limbs/digits, malformed anatomy, warped "
    "geometry, text, watermarks, and unrelated additions."
)

REFERENCE_RULES = (
    "REFERENCE MODE: use the selected photograph as the Krea2 source image. Its "
    "selected 4:5 pixels define the default composition, identity, pose, scene, "
    "depth of field, colorimetry, lighting, and geometry. Preserve every visible "
    "attribute the authoritative request does not replace. Reproduce the source's "
    "observed background focus exactly: a sharp source must remain sharp, a mildly "
    "soft source must remain only mildly soft, and genuine source bokeh may be "
    "preserved. Never add or increase background blur, shallow depth of field, "
    "portrait mode, or bokeh unless the authoritative request explicitly asks for "
    "it. Apply the requested changes clearly while keeping exactly one main "
    "foreground adult woman unless the request explicitly asks for more people. "
    "Never duplicate, clone, mirror, or add a second version of her. The "
    "photographer, camera, and phone stay outside the frame unless explicitly "
    "requested. Produce a full-bleed vertical 4:5 rectilinear photograph without "
    "fisheye, curved boundaries, black corners, rounded masks, letterboxing, "
    "pillarboxing, borders, text, or watermarks."
)

PROMPT_ONLY_RULES = (
    "PROMPT-ONLY MODE: generate a new image from scratch with Krea 2 Turbo. There "
    "is no reference photograph or source identity. Treat the authoritative "
    "request as the complete scene specification and expand only concrete details "
    "it provides. Unless the request explicitly asks for shallow depth of field, "
    "portrait mode, bokeh, or background blur, use ordinary phone-camera deep focus "
    "with the environment naturally resolved and no artificial background blur. "
    "Render exactly one fictional adult woman unless another subject count is "
    "explicitly requested. The photographer, phone, and camera remain outside the "
    "frame. Make a candid, plausible Instagram photograph with natural anatomy, "
    "coherent geometry, believable lighting, ordinary photographic imperfections, "
    "and a full-bleed vertical 4:5 rectilinear frame. Avoid duplicate subjects, "
    "extra or missing limbs or digits, malformed hands, warped straight lines, "
    "fisheye, black corners, borders, text, and watermarks."
)

REQUEST_REWRITER = (
    "Rewrite the user's message as one precise visual instruction for a Krea 2 "
    "Turbo workflow. Output only the instruction. If the message is exactly “No "
    "additional user modifications.”, output exactly that sentence and nothing "
    "else. Otherwise, the message is either a complete prompt-only scene or a "
    "requested change to a reference image. Retain every concrete detail. Treat "
    "the main subject as an adult. State exact subject count, pose, anatomy, "
    "clothing, setting, camera position, framing, lighting, focus and colors "
    "whenever supplied. Preserve an explicit request for background blur, shallow "
    "depth of field, portrait mode, bokeh, deep focus, or a sharp background "
    "verbatim in meaning. Do not invent any focus or blur change the user did not "
    "request. For removals, explicitly state that the item is completely absent "
    "and describe the naturally reconstructed area. For camera changes, specify "
    "position, height, direction, distance, lens perspective and framing. Preserve "
    "all unnamed source attributes in reference mode. Keep exactly one main "
    "foreground woman unless explicitly requested otherwise; never duplicate, "
    "clone, mirror, or place the photographer or phone in frame. Do not mention "
    "policies, editing steps or these rules."
)

PROMPT_COMPILER = (
    "Compile one final production-ready Krea 2 Turbo prompt. Output only the final "
    "prompt, without headings or commentary. The input begins with REFERENCE MODE "
    "or PROMPT-ONLY MODE followed by an authoritative request. The sentence “No "
    "additional user modifications.” means preserve the analyzed reference exactly "
    "and add no new requested changes. Put actual requested changes first and "
    "resolve conflicts into one desired visible state. Never retain superseded "
    "source wording. In reference mode, preserve concretely described source "
    "identity, composition, pose, geometry, lighting, colors and objects unless the "
    "request changes them. Preserve the analyzed amount of background focus exactly "
    "and never amplify mild softness into bokeh. In prompt-only mode, default to "
    "ordinary phone-camera deep focus. In either mode, use shallow depth of field, "
    "portrait mode, bokeh, or background blur only when the authoritative request "
    "explicitly asks for it or the reference analysis clearly reports it as visible. "
    "Otherwise state that the environment is naturally resolved with no artificial "
    "background blur. Always describe exactly one main foreground adult woman unless "
    "the request explicitly requires more; never create a duplicate, clone, "
    "reflection, second copy, visible photographer, camera or phone. Use a full-bleed "
    "vertical 4:5 rectilinear photographic frame with natural proportions, plausible "
    "hands, coherent perspective, authentic Instagram color and texture, and no "
    "fisheye, black corners, rounded mask, borders, text or watermark. Keep the "
    "result concise: 120 to 240 words."
)


def node(workflow: dict, node_id: int) -> dict:
    return next(item for item in workflow["nodes"] if item["id"] == node_id)


def build() -> dict:
    workflow = json.loads(SOURCE.read_text())
    workflow = copy.deepcopy(workflow)

    patch = node(workflow, 16)
    behavior = node(workflow, 61)

    analyzer = node(workflow, 19)
    analyzer["widgets_values"][6] = REFERENCE_ANALYSIS
    analyzer.setdefault("widgets_values_named", {})["custom_prompt"] = REFERENCE_ANALYSIS

    reference_rules = node(workflow, 20)
    reference_rules["widgets_values"][1] = REFERENCE_RULES
    reference_rules.setdefault("widgets_values_named", {})["string_b"] = REFERENCE_RULES

    prompt_only = node(workflow, 21)
    prompt_only["widgets_values"][0] = PROMPT_ONLY_RULES
    prompt_only.setdefault("widgets_values_named", {})["value"] = PROMPT_ONLY_RULES

    rewriter = node(workflow, 24)
    rewriter["widgets_values"][0] = REQUEST_REWRITER
    rewriter.setdefault("widgets_values_named", {})["system"] = REQUEST_REWRITER

    compiler = node(workflow, 27)
    compiler["widgets_values"][0] = PROMPT_COMPILER
    compiler.setdefault("widgets_values_named", {})["system"] = PROMPT_COMPILER

    behavior["widgets_values"] = ["Balanced 75% — feathered"]
    behavior["widgets_values_named"] = {"mode": "Balanced 75% — feathered"}
    behavior["title"] = (
        "REFERENCE BEHAVIOR · Inspired / Balanced 50% / Balanced 75% / "
        "Feathered 75% / Close / Pixel-preserving"
    )
    behavior["outputs"][1]["type"] = POSITIONS

    # ref_blend_width was appended by the backend so all existing socket indices
    # remain stable. Zero exactly reproduces the original hard quarter-width shift.
    patch["inputs"].append(
        {
            "name": "ref_blend_width",
            "type": "FLOAT",
            "widget": {"name": "ref_blend_width"},
            "link": 120,
        }
    )
    patch["widgets_values"].append(0.25)
    patch.setdefault("widgets_values_named", {})["ref_blend_width"] = 0.25
    patch["size"][1] = max(patch["size"][1], 310)

    control = {
        "id": 63,
        "type": "PrimitiveFloat",
        "pos": [-410, -2520],
        "size": [350, 110],
        "flags": {},
        "order": 63,
        "mode": 0,
        "inputs": [
            {
                "name": "value",
                "type": "FLOAT",
                "link": None,
                "widget": {"name": "value"},
            }
        ],
        "outputs": [{"name": "FLOAT", "type": "FLOAT", "links": [120]}],
        "title": "FEATHER BLEND WIDTH · 0 = hard edge, 0.25 = default",
        "properties": {
            "Node name for S&R": "PrimitiveFloat",
            "cnr_id": "comfy-core",
        },
        "widgets_values": [0.25],
        "widgets_values_named": {"value": 0.25},
        "color": "#493c5b",
        "bgcolor": "#31293e",
    }
    workflow["nodes"].append(control)
    workflow["links"].append([120, 63, 0, 16, 10, "FLOAT"])

    color_strength = {
        "id": 64,
        "type": "PrimitiveFloat",
        "pos": [-410, -2370],
        "size": [350, 110],
        "flags": {},
        "order": 64,
        "mode": 0,
        "inputs": [
            {
                "name": "value",
                "type": "FLOAT",
                "link": None,
                "widget": {"name": "value"},
            }
        ],
        "outputs": [{"name": "FLOAT", "type": "FLOAT", "links": [123]}],
        "title": "REFERENCE COLOR MATCH · 0 = off, 0.35 = default",
        "properties": {
            "Node name for S&R": "PrimitiveFloat",
            "cnr_id": "comfy-core",
        },
        "widgets_values": [0.35],
        "widgets_values_named": {"value": 0.35},
        "color": "#493c5b",
        "bgcolor": "#31293e",
    }
    color_transfer = {
        "id": 65,
        "type": "ColorTransfer",
        "pos": [2080, -480],
        "size": [420, 210],
        "flags": {},
        "order": 65,
        "mode": 0,
        "inputs": [
            {"name": "image_target", "type": "IMAGE", "link": 121},
            {"name": "image_ref", "type": "IMAGE", "link": 122},
            {
                "name": "method",
                "type": "COMBO",
                "widget": {"name": "method"},
                "link": None,
            },
            {
                "name": "source_stats",
                "type": "COMFY_DYNAMICCOMBO_V3",
                "widget": {"name": "source_stats"},
                "link": None,
            },
            {
                "name": "strength",
                "type": "FLOAT",
                "widget": {"name": "strength"},
                "link": 123,
            },
        ],
        "outputs": [{"name": "image", "type": "IMAGE", "links": [125]}],
        "title": "Match generated color to selected reference · Reinhard Lab",
        "properties": {
            "Node name for S&R": "ColorTransfer",
            "cnr_id": "comfy-core",
            "ver": "0.43.0",
        },
        "widgets_values": ["reinhard_lab", "per_frame", 0.35],
        "widgets_values_named": {
            "method": "reinhard_lab",
            "source_stats": "per_frame",
            "strength": 0.35,
        },
    }
    color_switch = {
        "id": 66,
        "type": "ComfySwitchNode",
        "pos": [2080, -220],
        "size": [420, 140],
        "flags": {},
        "order": 66,
        "mode": 0,
        "inputs": [
            {
                "name": "on_false",
                "shape": 7,
                "type": "IMAGE",
                "link": 124,
            },
            {
                "name": "on_true",
                "shape": 7,
                "type": "IMAGE",
                "link": 125,
            },
            {
                "name": "switch",
                "type": "BOOLEAN",
                "widget": {"name": "switch"},
                "link": 126,
            },
        ],
        "outputs": [{"name": "output", "type": "IMAGE", "links": [127]}],
        "title": "Reference selected? · apply color match / bypass",
        "properties": {
            "Node name for S&R": "ComfySwitchNode",
            "cnr_id": "comfy-core",
            "ver": "0.43.0",
        },
        "widgets_values": [True],
        "widgets_values_named": {"switch": True},
    }
    saturation_enabled = {
        "id": 67,
        "type": "PrimitiveBoolean",
        "pos": [-410, -2220],
        "size": [350, 110],
        "flags": {},
        "order": 67,
        "mode": 0,
        "inputs": [
            {
                "name": "value",
                "type": "BOOLEAN",
                "link": None,
                "widget": {"name": "value"},
            }
        ],
        "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": [128]}],
        "title": "APPLY SATURATION ADJUSTMENT",
        "properties": {
            "Node name for S&R": "PrimitiveBoolean",
            "cnr_id": "comfy-core",
        },
        "widgets_values": [True],
        "widgets_values_named": {"value": True},
        "color": "#493c5b",
        "bgcolor": "#31293e",
    }
    saturation_amount = {
        "id": 68,
        "type": "PrimitiveFloat",
        "pos": [-410, -2080],
        "size": [350, 110],
        "flags": {},
        "order": 68,
        "mode": 0,
        "inputs": [
            {
                "name": "value",
                "type": "FLOAT",
                "link": None,
                "widget": {"name": "value"},
            }
        ],
        "outputs": [{"name": "FLOAT", "type": "FLOAT", "links": [129]}],
        "title": "SATURATION · 1.0 = neutral, 0 = grayscale",
        "properties": {
            "Node name for S&R": "PrimitiveFloat",
            "cnr_id": "comfy-core",
        },
        "widgets_values": [1.0],
        "widgets_values_named": {"value": 1.0},
        "color": "#493c5b",
        "bgcolor": "#31293e",
    }
    saturation_adjust = {
        "id": 69,
        "type": "ASInfSaturationAdjust",
        "pos": [2540, -360],
        "size": [420, 180],
        "flags": {},
        "order": 69,
        "mode": 0,
        "inputs": [
            {"name": "image", "type": "IMAGE", "link": 127},
            {
                "name": "enabled",
                "type": "BOOLEAN",
                "widget": {"name": "enabled"},
                "link": 128,
            },
            {
                "name": "saturation",
                "type": "FLOAT",
                "widget": {"name": "saturation"},
                "link": 129,
            },
        ],
        "outputs": [{"name": "image", "type": "IMAGE", "links": [63, 64]}],
        "title": "Final global saturation adjustment",
        "properties": {
            "Node name for S&R": "ASInfSaturationAdjust",
        },
        "widgets_values": [True, 1.0],
        "widgets_values_named": {"enabled": True, "saturation": 1.0},
    }
    workflow["nodes"].extend(
        [
            color_strength,
            color_transfer,
            color_switch,
            saturation_enabled,
            saturation_amount,
            saturation_adjust,
        ]
    )

    # Insert color matching and saturation after FameGrid Color Finish so no
    # later image-processing node can undo either adjustment.
    node(workflow, 38)["outputs"][0]["links"] = [121, 124]
    node(workflow, 13)["outputs"][0]["links"].append(122)
    node(workflow, 1)["outputs"][2]["links"].append(126)
    for link in workflow["links"]:
        if link[0] in (63, 64):
            link[1] = 69
    workflow["links"].extend(
        [
            [121, 38, 0, 65, 0, "IMAGE"],
            [122, 13, 0, 65, 1, "IMAGE"],
            [123, 64, 0, 65, 4, "FLOAT"],
            [124, 38, 0, 66, 0, "IMAGE"],
            [125, 65, 0, 66, 1, "IMAGE"],
            [126, 1, 2, 66, 2, "BOOLEAN"],
            [127, 66, 0, 69, 0, "IMAGE"],
            [128, 67, 0, 69, 1, "BOOLEAN"],
            [129, 68, 0, 69, 2, "FLOAT"],
        ]
    )

    node(workflow, 39)["pos"] = [3000, -360]
    node(workflow, 41)["pos"] = [3000, -120]
    node(workflow, 42)["pos"] = [3000, 100]
    for group in workflow.get("groups", []):
        if group["id"] == 6:
            group["bounding"][2] = 2750

    for link in workflow["links"]:
        if link[0] == 114:
            link[5] = POSITIONS

    workflow["last_node_id"] = 69
    workflow["last_link_id"] = 129
    return workflow


def validate(workflow: dict) -> None:
    ids = [item["id"] for item in workflow["nodes"]]
    assert len(ids) == len(set(ids))
    assert max(ids) == workflow["last_node_id"]
    link_ids = [item[0] for item in workflow["links"]]
    assert len(link_ids) == len(set(link_ids))
    assert max(link_ids) == workflow["last_link_id"]
    assert node(workflow, 61)["widgets_values"][0] == "Balanced 75% — feathered"
    assert node(workflow, 16)["inputs"][-1]["name"] == "ref_blend_width"
    assert node(workflow, 65)["widgets_values"][0] == "reinhard_lab"
    assert node(workflow, 66)["outputs"][0]["links"] == [127]
    assert node(workflow, 69)["outputs"][0]["links"] == [63, 64]
    assert node(workflow, 68)["widgets_values"][0] == 1.0


if __name__ == "__main__":
    result = build()
    validate(result)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT)
