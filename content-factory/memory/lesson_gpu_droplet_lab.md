# GPU droplet lab: image, regions, and benchmark placement asserts

Verified on the self-host-ollama piece (2026-08-12), 8 GPU boots, zero quota walls.

**Provisioning facts:**
- Image `gpu-h100x1-base` ("NVIDIA AI/ML Ready") works on ALL single NVIDIA GPU
  sizes despite the name: Ubuntu 22.04 + driver + CUDA preinstalled, nvidia-smi
  live ~70s after create. Golden snapshot is useless for GPU legs (fra1-only);
  GPU sizes live in tor1/nyc2/atl1 — check `/v2/sizes` regions per size first.
- `do.py create <slug> --size gpu-... --region tor1 --image gpu-h100x1-base`
  already works; no code changes needed.
- Run a cheap E0 fail-fast boot (create → nvidia-smi → destroy, ~2 min) before
  planning a GPU-dependent piece; it also catches account quota walls for ~$0.05.
- Sizes/prices seen 2026-08: RTX 4000 Ada 20GB $0.76/hr · RTX 6000 Ada 48GB
  $1.57/hr · H100 80GB $4.41/hr. Capacity 422s ("Size is not available in this
  region") happen and clear within ~15 min — retry before replanning.

**Benchmark rule that saved this piece — assert accelerator placement, not just
output:** Ollama silently loaded 20/33 layers to GPU at specific
OLLAMA_NUM_PARALLEL values (deterministic across 3 fresh boxes, VRAM drained,
43GB free) and ran 3-4x slow while every request still "succeeded". A GPU
benchmark harness must grep the runner's own placement log
(`journalctl -u ollama | grep offloaded` or equivalent) before each level and
record it as evidence. Related: KV cache = context x parallel slots (32 x 4096
tried to alloc 128GiB on an 80GB card); tune ctx down before raising parallelism.

**Also:** LLM API aggregator sites published wrong prices (gpt-5-mini $1.00 vs
official $2.00). Price claims come from the provider's official page, fetched
day-of, never from aggregators or search snippets.
