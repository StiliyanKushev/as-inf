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


def node(workflow: dict, node_id: int) -> dict:
    return next(item for item in workflow["nodes"] if item["id"] == node_id)


def build() -> dict:
    workflow = json.loads(SOURCE.read_text())
    workflow = copy.deepcopy(workflow)

    patch = node(workflow, 16)
    behavior = node(workflow, 61)

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

    for link in workflow["links"]:
        if link[0] == 114:
            link[5] = POSITIONS

    workflow["last_node_id"] = 63
    workflow["last_link_id"] = 120
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


if __name__ == "__main__":
    result = build()
    validate(result)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT)
