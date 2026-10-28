#!/usr/bin/env python3
"""Isolate Krea2 subject duplication in the three-way benchmark.

This keeps the model, reference geometry, sampler, seed, and resolution fixed.
It tests an explicit single-subject instruction with (a) the published style
stack and (b) the General Edit identity LoRA alone.
"""

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
OUTPUT_ROOT = "research-three-way-ablation"
SEEDS = (27012026, 27012027)


def single_subject_scene():
    source = next(scene for scene in BENCH.SCENES if scene.name == "street")
    instruction = (
        "Create one candid full-body iPhone photograph containing exactly one "
        "foreground woman: the same fictional woman shown in the reference. "
        "Never duplicate, clone, mirror, or repeat her. The photographer and "
        "phone are outside the frame. Preserve her exact facial identity, eye "
        "color, facial proportions, and long center-parted dark-blonde hair. "
        "She is walking alone along a quiet European side street in soft "
        "afternoon daylight, captured at eye level during an ordinary mid-step. "
        "She glances toward the camera with a relaxed closed-mouth expression. "
        "She wears a plain charcoal T-shirt, straight-leg blue jeans, and worn "
        "white sneakers. One hand holds a small canvas shoulder-bag strap and the "
        "other hangs naturally. Parked bicycles and stucco walls form an "
        "unobtrusive background. Ordinary 26 mm phone lens, casual off-center "
        "composition, realistic body proportions and fabric folds, natural skin "
        "texture, restrained smartphone processing, no beauty filter. Authentic "
        "personal Instagram post."
    )
    return BENCH.Scene(source.name, source.sdxl_prompt, instruction)


def build(scene, seed: int, prefix: str, full_style: bool):
    graph = BENCH.build_krea(scene, seed, prefix)
    if not full_style:
        # Keep General Edit V2 for identity/geometry; bypass FameGrid and Realism
        # Engine so their visual and composition effects are isolated.
        graph["10"]["inputs"]["model"] = ["2", 0]
        del graph["3"]
        del graph["4"]
    return graph


def main() -> None:
    graphs = RESULTS / "api-graphs"
    manifests = RESULTS / "manifests"
    graphs.mkdir(parents=True, exist_ok=True)
    manifests.mkdir(parents=True, exist_ok=True)
    scene = single_subject_scene()
    summary = []
    for variant, full_style in (("krea_single_full", True), ("krea_single_core", False)):
        for seed in SEEDS:
            run = f"{variant}_street_seed{seed}"
            prefix = f"{OUTPUT_ROOT}/{run}"
            graph = build(scene, seed, prefix, full_style)
            (graphs / f"{run}.json").write_text(json.dumps(graph, indent=2) + "\n")
            print(f"RUN {run}", flush=True)
            prompt_id, history, elapsed = BENCH.submit_and_wait("http://127.0.0.1:8188", graph)
            record = {
                "run": run,
                "variant": variant,
                "seed": seed,
                "prompt_id": prompt_id,
                "elapsed_seconds": round(elapsed, 3),
                "outputs": history.get("outputs", {}),
                "status": history.get("status", {}),
            }
            (manifests / f"{run}.json").write_text(json.dumps(record, indent=2) + "\n")
            summary.append(record)
            print(json.dumps({"run": run, "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
    (RESULTS / "krea-ablation-summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
