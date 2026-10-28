#!/usr/bin/env python3
"""Test whether explicit phone optics make Krea2 less editorial/DSLR-like."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("three_way", HERE / "run-benchmark.py")
assert SPEC and SPEC.loader
BENCH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BENCH
SPEC.loader.exec_module(BENCH)

RESULTS = Path("/workspace/as-inf/research-results/three-way-2026-10-28")
SEED = 27012026


def phone_scene(source):
    if source.name == "cafe":
        action = (
            "seated at a small outdoor neighborhood cafe in late morning, leaning "
            "slightly toward the camera with a subtle closed-mouth smile, loosely "
            "holding one plain ceramic coffee cup. She wears a simple white linen "
            "sleeveless top and blue jeans. Empty wicker chairs, small tables, and "
            "leafy plants remain clearly recognizable behind her"
        )
    else:
        action = (
            "walking alone along a quiet European side street in soft afternoon "
            "daylight during an ordinary mid-step. She wears a plain charcoal "
            "T-shirt, straight-leg blue jeans, worn white sneakers, and carries a "
            "small canvas shoulder bag. Parked bicycles and stucco walls remain "
            "clearly recognizable behind her"
        )
    instruction = (
        "Create one candid everyday smartphone photograph containing exactly one "
        "foreground woman: the same fictional woman shown in the reference. Never "
        "duplicate, clone, mirror, or repeat her. The photographer and phone are "
        "outside the frame. Preserve her exact facial identity, eye color, facial "
        "proportions, freckles, and long center-parted dark-blonde hair. She is "
        f"{action}. Use an ordinary 26 mm equivalent phone lens at eye level with "
        "casual slightly imperfect framing. Use natural deep focus typical of a "
        "small phone sensor: subject and environmental background are both "
        "legible. No portrait mode, no artificial lens blur, no creamy bokeh, no "
        "cinematic depth of field, no studio or fashion lighting. Include mild "
        "phone-sensor micrograin, restrained computational HDR, slight highlight "
        "clipping, ordinary color, and restrained edge sharpening. Natural pores, "
        "fine skin texture, realistic anatomy and fabric folds. Authentic unedited "
        "personal Instagram post rather than a professional portrait."
    )
    return BENCH.Scene(source.name, source.sdxl_prompt, instruction)


def main():
    graphs = RESULTS / "api-graphs"
    manifests = RESULTS / "manifests"
    summary = []
    for source in BENCH.SCENES:
        scene = phone_scene(source)
        run = f"krea_phone_core_{scene.name}_seed{SEED}"
        prefix = f"research-three-way-ablation/{run}"
        graph = BENCH.build_krea(scene, SEED, prefix)
        graph["10"]["inputs"]["model"] = ["2", 0]
        del graph["3"]
        del graph["4"]
        (graphs / f"{run}.json").write_text(json.dumps(graph, indent=2) + "\n")
        print(f"RUN {run}", flush=True)
        prompt_id, history, elapsed = BENCH.submit_and_wait("http://127.0.0.1:8188", graph)
        record = {
            "run": run,
            "seed": SEED,
            "prompt_id": prompt_id,
            "elapsed_seconds": round(elapsed, 3),
            "outputs": history.get("outputs", {}),
            "status": history.get("status", {}),
        }
        (manifests / f"{run}.json").write_text(json.dumps(record, indent=2) + "\n")
        summary.append(record)
        print(json.dumps({"run": run, "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
    (RESULTS / "krea-phone-ablation-summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
