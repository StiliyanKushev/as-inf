# Three-way Instagram realism results

Open these first:

- `contact-sheet-instagram.jpg` — all 12 primary results.
- `contact-sheet-krea-ablation.jpg` — corrected one-subject prompt, with and
  without the two Krea style LoRAs.
- `contact-sheet-ananya-swap.jpg` — ReActor before/after.
- `contact-sheet-krea-finish.jpg` — FameGrid color finish before/after.

`outputs/` contains the 12 primary runs. `outputs-ablation/` contains six Krea2
follow-ups. Each run retains a native image and a 1080×1350 Instagram export.
`api-graphs/` and `manifests/` contain the exact submitted graph and ComfyUI
execution record for every run.

Read [`docs/THREE_WAY_INSTAGRAM_BENCHMARK_2026-10-28.md`](../../docs/THREE_WAY_INSTAGRAM_BENCHMARK_2026-10-28.md)
for findings and the production recommendation.
