#!/usr/bin/env python3
"""Build the backup-first Krea 2 workflow with a restrained Alex identity finish."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "workflows/final-kurva-maker-krea2-pre-alex-backup.json"
TEMPLATE_PATH = ROOT / "workflows/final-kurva-maker-krea2-alex-direct-scene.json"
OUTPUT_PATH = ROOT / "workflows/final-kurva-maker-krea2-prealex-alex-finish.json"


def node_by_id(workflow: dict, node_id: int) -> dict:
    return next(node for node in workflow["nodes"] if node["id"] == node_id)


def reset_links(node: dict) -> None:
    for item in node.get("inputs", []):
        if "link" in item:
            item["link"] = None
    for item in node.get("outputs", []):
        item["links"] = None


def main() -> None:
    workflow = json.loads(BASE_PATH.read_text())
    template = json.loads(TEMPLATE_PATH.read_text())

    # The original workflow remains untouched.  Only its first-pass decode is
    # rerouted through a new, optional identity-edit pass before color finish.
    workflow["nodes"] = copy.deepcopy(workflow["nodes"])
    workflow["links"] = [
        link
        for link in workflow["links"]
        if link[0] != 62
        and not (link[1] == 15 and link[3] in {16, 36})
    ]

    # Reuse known-good node schemas from the deployed direct-scene workflow.
    source_ids = [45, 46, 47, 48, 49, 59, 60, 61, 62, 63, 64, 66, 65]
    new_ids = list(range(45, 58))
    nodes = []
    for source_id, new_id in zip(source_ids, new_ids):
        node = copy.deepcopy(node_by_id(template, source_id))
        node["id"] = new_id
        node["order"] = new_id
        reset_links(node)
        nodes.append(node)

    by_id = {node["id"]: node for node in nodes}

    # Preset Alex references.  The installer copies the versioned repository
    # assets to these stable ComfyUI input names.
    for node_id, title, filename, x in [
        (45, "ALEX IDENTITY 1 · front", "alexsparks_front.png", -2200),
        (46, "ALEX IDENTITY 2 · three-quarter left", "alexsparks_three_quarter_left.png", -1900),
        (47, "ALEX IDENTITY 3 · three-quarter right", "alexsparks_three_quarter_right.png", -1600),
    ]:
        by_id[node_id]["title"] = title
        by_id[node_id]["widgets_values"] = [filename, "image"]
        by_id[node_id]["pos"] = [x, 2100]
        by_id[node_id]["size"] = [270, 330]

    by_id[48]["title"] = "ALEX VIEW · choose the closest head angle"
    by_id[48]["pos"] = [-2200, 2480]
    by_id[48]["size"] = [870, 130]
    by_id[48]["widgets_values"] = ["front"]

    by_id[49]["title"] = "Encode selected Alex identity"
    by_id[49]["pos"] = [-1260, 2480]

    by_id[50]["title"] = "Encode untouched first-pass photograph"
    by_id[50]["pos"] = [-1260, 2100]

    by_id[51]["title"] = "Restrained identity substitution · preserve 2.0 / Alex 3.0"
    by_id[51]["pos"] = [-800, 2100]
    by_id[51]["widgets_values"] = [
        3.0,
        2.0,
        "fit",
        "beside (right of target)",
        "aligned (trained)",
    ]
    by_id[51]["widgets_values_named"] = {
        "ref_boost": 3.0,
        "ref_boost_a": 2.0,
        "fit_mode": "fit",
        "ref_position": "beside (right of target)",
        "ref_position_a": "aligned (trained)",
    }

    identity_prompt = (
        "Perform one constrained identity substitution on the main foreground woman. "
        "Replace only her underlying facial and hair identity with Alex from image 2. "
        "Preserve image 1's exact facial expression, mouth shape, gaze, head turn and tilt, "
        "eyewear, jewelry, body pose, hand placement, clothing, lighting, shadows, skin texture, "
        "focal depth, camera, crop, and every environmental detail. Alex has a softly angular "
        "oval face, straight medium brows, a narrow straight nose, naturally shaped pink lips, "
        "fair lightly freckled skin, pale clear blue eyes, and long light golden-blonde "
        "center-parted hair. Do not beautify, relight, restage, change expression, alter anatomy, "
        "remove accessories, or modify clothing or background. Keep exactly one main woman."
    )
    identity_system = (
        "Image 1 is authoritative for composition, expression, pose, accessories, lighting, "
        "texture, clothes and scene. Image 2 supplies the main woman's stable underlying face "
        "and hair identity only. Preserve every non-identity attribute from image 1. This is a "
        "restrained identity substitution, not a new scene generation."
    )

    by_id[52]["title"] = "Alex identity finish · grounded positive"
    by_id[52]["pos"] = [-240, 2070]
    by_id[52]["widgets_values"] = [identity_prompt, 768, identity_system]
    by_id[52]["widgets_values_named"] = {
        "prompt": identity_prompt,
        "grounding_px": 768,
        "system_prompt": identity_system,
    }

    by_id[53]["title"] = "Alex identity finish · unconditional"
    by_id[53]["pos"] = [-240, 2390]
    by_id[53]["widgets_values"] = ["", 768, ""]
    by_id[53]["widgets_values_named"] = {
        "prompt": "",
        "grounding_px": 768,
        "system_prompt": "",
    }

    by_id[54]["title"] = "Alex identity finish sampler · same production settings"
    by_id[54]["pos"] = [300, 2100]

    by_id[55]["title"] = "Decode Alex identity finish"
    by_id[55]["pos"] = [800, 2100]

    by_id[56]["title"] = "APPLY ALEX IDENTITY FINISH · tested conservative pass"
    by_id[56]["pos"] = [-410, -2800]
    by_id[56]["size"] = [350, 100]
    by_id[56]["widgets_values"] = [True]
    by_id[56]["widgets_values_named"] = {"value": True}

    by_id[57]["title"] = "FINAL IMAGE · original backup result / Alex finish"
    by_id[57]["pos"] = [1200, 2100]
    by_id[57]["widgets_values"] = [True]
    by_id[57]["widgets_values_named"] = {"switch": True}

    # Three user-facing floats drive formerly embedded Krea reference-patch
    # values. They live beside the identity toggle in Advanced Settings.
    primitive_template = copy.deepcopy(node_by_id(workflow, 5))
    strength_nodes = []
    for node_id, title, value, y in [
        (58, "PRESERVATION STRENGTH · default 2.0", 2.0, -2660),
        (59, "ALEX IDENTITY STRENGTH · default 3.0", 3.0, -2500),
        (60, "FIRST-PASS REFERENCE STRENGTH · default 2.0", 2.0, -2340),
    ]:
        node = copy.deepcopy(primitive_template)
        node["id"] = node_id
        node["type"] = "PrimitiveFloat"
        node["pos"] = [-410, y]
        node["size"] = [350, 110]
        node["order"] = node_id
        node["title"] = title
        node["inputs"][0]["type"] = "FLOAT"
        node["outputs"][0]["name"] = "FLOAT"
        node["outputs"][0]["type"] = "FLOAT"
        node["properties"] = {
            "Node name for S&R": "PrimitiveFloat",
            "cnr_id": "comfy-core",
        }
        node["widgets_values"] = [value]
        node["widgets_values_named"] = {"value": value}
        reset_links(node)
        strength_nodes.append(node)

    # Convert the two Krea patch widgets to externally connected widget inputs.
    patch_inputs = by_id[51]["inputs"]
    patch_inputs[3:3] = [
        {
            "name": "ref_boost",
            "type": "FLOAT",
            "widget": {"name": "ref_boost"},
            "link": None,
        },
        {
            "name": "ref_boost_a",
            "type": "FLOAT",
            "widget": {"name": "ref_boost_a"},
            "link": None,
        },
    ]

    # Expose the single-reference boost used by the original first Krea pass.
    # This is the actual target->reference attention multiplier: 1.0 is neutral,
    # >1.0 pulls harder toward the source, and <1.0 allows more change.
    first_patch = node_by_id(workflow, 16)
    first_patch["title"] = "Krea2 General Edit · adjustable reference strength"
    first_patch["inputs"].insert(
        3,
        {
            "name": "ref_boost",
            "type": "FLOAT",
            "widget": {"name": "ref_boost"},
            "link": None,
        },
    )
    first_patch["inputs"].append(
        {
            "name": "ref_position",
            "type": "COMBO",
            "widget": {"name": "ref_position"},
            "link": None,
        }
    )

    # The inserted socket shifts the existing optional sockets and therefore
    # their canonical target slot numbers in the link table.
    for link in workflow["links"]:
        if link[3] == 16 and link[4] >= 3:
            link[4] += 1

    # Save the empirically preferred sampler defaults from the control panel.
    sampler_settings = node_by_id(workflow, 4)
    sampler_settings["widgets_values"] = [10, 1.0, "lcm", "simple", 1]
    sampler_settings["widgets_values_named"] = {
        "steps": 10,
        "cfg": 1.0,
        "sampler_name": "lcm",
        "scheduler": "simple",
        "batch_size": 1,
    }
    next(group for group in workflow["groups"] if group["id"] == 2)["bounding"][3] = 880

    reference_mode = {
        "id": 61,
        "type": "ASInfReferenceBehavior",
        "pos": [-410, -2180],
        "size": [350, 150],
        "flags": {},
        "order": 61,
        "mode": 0,
        "inputs": [
            {"name": "empty_latent", "type": "LATENT", "link": None},
            {"name": "reference_latent", "type": "LATENT", "link": None},
            {"name": "has_reference", "type": "BOOLEAN", "link": None},
            {"name": "mode", "type": "COMBO", "widget": {"name": "mode"}, "link": None},
        ],
        "outputs": [
            {"name": "latent_image", "type": "LATENT", "links": None},
            {
                "name": "ref_position",
                "type": [
                    "aligned (trained)",
                    "beside (right of target)",
                    "bag of features",
                ],
                "links": None,
            },
            {"name": "denoise", "type": "FLOAT", "links": None},
        ],
        "properties": {
            "Node name for S&R": "ASInfReferenceBehavior",
            "cnr_id": "as-inf",
        },
        "widgets_values": ["Inspired — beside"],
        "widgets_values_named": {"mode": "Inspired — beside"},
        "title": "REFERENCE BEHAVIOR · Inspired / Close / Pixel-preserving",
    }

    workflow["nodes"].extend(nodes + strength_nodes + [reference_mode])

    node_by_id(workflow, 9)["widgets_values"] = [
        "FINAL KURVA MAKER · KREA 2 TURBO · BACKUP-FIRST ALEX FINISH\n\n"
        "The proven pre-Alex workflow generates the complete photograph first. A second, "
        "restrained Krea edit then substitutes Alex's face and hair identity while treating the "
        "first render as authoritative for expression, eyewear, pose, clothing, lighting, texture, "
        "camera and background. Disable APPLY ALEX IDENTITY FINISH to recover the untouched backup "
        "result. Advanced Settings exposes REFERENCE BEHAVIOR, FIRST-PASS REFERENCE STRENGTH (2.0), PRESERVATION "
        "STRENGTH (2.0), and ALEX IDENTITY STRENGTH (3.0). LCM / Simple at 10 steps and CFG 1 "
        "is the saved production default. Select the Alex view closest to the intended head angle."
    ]
    node_by_id(workflow, 39)["title"] = "Save native Alex-finished render · 1280 × 1600"
    node_by_id(workflow, 39)["widgets_values"] = [
        "FinalKurvaMakerKrea2AlexFinish/native_1280x1600"
    ]
    node_by_id(workflow, 41)["title"] = "Save Instagram Alex-finished copy · 1080 × 1350"
    node_by_id(workflow, 41)["widgets_values"] = [
        "FinalKurvaMakerKrea2AlexFinish/instagram_1080x1350"
    ]

    workflow.setdefault("groups", []).append(
        {
            "id": 8,
            "title": "06 · OPTIONAL RESTRAINED ALEX IDENTITY FINISH",
            "bounding": [-2280, 1980, 3900, 760],
            "color": "#65506f",
            "font_size": 24,
            "flags": {},
        }
    )

    # Links are listed as [id, origin node, origin slot, target node, target slot, type].
    links = workflow["links"]
    next_link = max(link[0] for link in links) + 1

    def add(origin: int, origin_slot: int, target: int, target_slot: int, link_type) -> None:
        nonlocal next_link
        links.append([next_link, origin, origin_slot, target, target_slot, link_type])
        next_link += 1

    add(45, 0, 48, 0, "IMAGE")
    add(46, 0, 48, 1, "IMAGE")
    add(47, 0, 48, 2, "IMAGE")
    add(48, 0, 49, 0, "IMAGE")
    add(12, 0, 49, 1, "VAE")
    add(37, 0, 50, 0, "IMAGE")
    add(12, 0, 50, 1, "VAE")
    add(8, 0, 51, 0, "MODEL")
    add(50, 0, 51, 1, "LATENT")
    add(49, 0, 51, 2, "LATENT")
    # ref_boost controls the LAST reference (Alex); ref_boost_a controls the
    # FIRST reference (the preserved first-pass photograph).
    add(59, 0, 51, 3, "FLOAT")
    add(58, 0, 51, 4, "FLOAT")
    add(12, 0, 51, 6, "VAE")
    add(37, 0, 51, 7, "IMAGE")
    add(48, 0, 51, 8, "IMAGE")
    add(15, 0, 51, 9, "LATENT")
    add(11, 0, 52, 0, "CLIP")
    add(37, 0, 52, 2, "IMAGE")
    add(48, 0, 52, 3, "IMAGE")
    add(11, 0, 53, 0, "CLIP")
    add(37, 0, 53, 2, "IMAGE")
    add(48, 0, 53, 3, "IMAGE")
    add(51, 0, 54, 0, "MODEL")
    add(52, 0, 54, 1, "CONDITIONING")
    add(53, 0, 54, 2, "CONDITIONING")
    add(15, 0, 54, 3, "LATENT")
    add(5, 0, 54, 4, "INT")
    add(4, 0, 54, 5, "INT")
    add(4, 1, 54, 6, "FLOAT")
    add(4, 2, 54, 7, node_by_id(workflow, 36)["inputs"][7]["type"])
    add(4, 3, 54, 8, node_by_id(workflow, 36)["inputs"][8]["type"])
    add(54, 0, 55, 0, "LATENT")
    add(12, 0, 55, 1, "VAE")
    add(37, 0, 57, 0, "IMAGE")
    add(55, 0, 57, 1, "IMAGE")
    add(56, 0, 57, 2, "BOOLEAN")
    add(57, 0, 38, 0, "IMAGE")
    add(60, 0, 16, 3, "FLOAT")
    add(15, 0, 61, 0, "LATENT")
    add(14, 0, 61, 1, "LATENT")
    add(1, 2, 61, 2, "BOOLEAN")
    add(61, 0, 16, 8, "LATENT")
    add(61, 1, 16, 9, [
        "aligned (trained)",
        "beside (right of target)",
        "bag of features",
    ])
    add(61, 0, 36, 3, "LATENT")
    add(61, 2, 36, 9, "FLOAT")

    # Rebuild all per-node link references from the canonical link table.
    nodes_by_id = {node["id"]: node for node in workflow["nodes"]}
    for node in workflow["nodes"]:
        reset_links(node)
    for link_id, origin, origin_slot, target, target_slot, _ in links:
        output = nodes_by_id[origin]["outputs"][origin_slot]
        if output.get("links") is None:
            output["links"] = []
        output["links"].append(link_id)
        nodes_by_id[target]["inputs"][target_slot]["link"] = link_id

    workflow["last_node_id"] = max(nodes_by_id)
    workflow["last_link_id"] = max(link[0] for link in links)

    # Structural checks catch accidental dangling or duplicate links.
    link_ids = [link[0] for link in links]
    assert len(link_ids) == len(set(link_ids))
    assert node_by_id(workflow, 38)["inputs"][0]["link"] is not None
    assert node_by_id(workflow, 57)["outputs"][0]["links"]

    OUTPUT_PATH.write_text(json.dumps(workflow, indent=2) + "\n")
    print(OUTPUT_PATH)
    print(f"nodes={len(workflow['nodes'])} links={len(workflow['links'])}")


if __name__ == "__main__":
    main()
