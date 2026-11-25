# Mistral CPU Lab

CPU-only fine-tuning and deployment research for specialized small language models (SLMs), with a focus on Mistral open-weight models and legacy x86 hardware.

This independent personal research project explores whether useful domain-specific models can be developed without GPU acceleration. The initial target is read-only systems administration assistance using synthetic examples and deterministic tools.

## Experimental status — 2026-11-25

| Experiment | Status |
|---|---|
| Ministral 3B architecture and LoRA compatibility | Passed on miniature model |
| Ministral text-only checkpoint mapping | Validated against index; synthetic loading tested |
| Official Ministral checkpoint download | SHA-256 verified |
| Pretrained Ministral text-only CPU LoRA | 32, 128 and 256 tokens validated |
| Domain-specific evaluation | Planned |

## Ministral 3B: initial findings

Target: [Ministral-3-3B-Base-2512](https://huggingface.co/mistralai/Ministral-3-3B-Base-2512), pinned revision `6f9c4b12a95b139af68670a6713616b757923735`.

| Finding | Result |
|---|---:|
| Stored multimodal BF16 parameters | 3,849,090,048 |
| Unique text-only parameters | 3,429,006,336 |
| Text-only FP32 weights | 12.77 GiB |
| Text-only BF16 weights | 6.39 GiB |
| Text tensor keys matched | 236 |
| Planned LoRA trainable parameters (r=4, q/v projections) | 1,171,456 |

A representative projection microbenchmark on legacy AVX-only CPUs measured 0.133 s in FP32 versus 10.831 s in BF16 for forward and backward. This single trial without warm-up is not a full-model benchmark. See [experimental report](docs/experiments.md) and [recorded measurements](benchmarks/ministral_projection.csv).

## First pretrained CPU LoRA result

On the text-only 3.429B-parameter checkpoint, one FP32 LoRA optimizer step (32 tokens, batch 1, four threads, r=4, alpha=8) completed in 8.713 seconds. Peak process RSS was 15.84 GiB; loss decreased from 3.882768 to 3.808134. Adapter changes and a sampled frozen embedding were checked. This is a feasibility result, not a domain-quality evaluation. See [measurements](benchmarks/ministral_pretrained.csv).

## Sequence-length benchmark

| Tokens | Optimizer steps | Mean seconds/step | Peak process RSS (MiB) |
|---:|---:|---:|---:|
| 32 | 1 | 8.713 | 16216.36 |
| 128 | 3 | 34.215 | 16212.05 |
| 256 | 3 | 61.101 | 16216.57 |

Each sequence length was tested in a separate process using the same pinned model, FP32, four threads, batch size 1 and LoRA configuration. The 32-token result is an earlier single-step probe. One run per length, repeated synthetic text, no held-out evaluation. Process RSS is not total container memory. See [per-step measurements](benchmarks/ministral_context.csv) and [experimental report](docs/experiments.md).

## Reproduce

See the [complete reproduction guide](docs/reproduction.md) for all six executable scripts, their provenance, commands and captured results.

Linux, Python 3.13.5 in the recorded environment. Install the CPU build of PyTorch first, then the recorded dependencies. Package availability depends on platform and release index.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

After checking available RAM and disk space, the experimental full-size probe can be attempted with:

```bash
nice -n 10 timeout 600 python -u scripts/ministral_text_probe.py --dtype fp32 --tokens 32 --download
```

The 32-token FP32 probe was validated using the pinned checkpoint already cached locally. Use an isolated environment with an appropriate memory limit. Remove `--download` to require a populated local cache.

The text-only loader and FP32 optimizer steps at 32, 128 and 256 tokens have been validated at full parameter scale. It defaults to FP32, requires a local checkpoint unless `--download` is explicitly supplied, and should only be run with sufficient memory (32 GiB laboratory quota recommended, not a measured minimum). It downloads approximately 7.7 GB of weights. No model weights are distributed here.

## Research methodology

This independent research project focuses on reproducible CPU-only experiments using Mistral open-weight models. Experimental results, methodology, and technical limitations are documented throughout the project. Initial training probes use synthetic inputs.

See [roadmap](docs/roadmap.md). Upstream model weights retain their respective licenses.

## Domain diagnostic pilot

A [French synthetic Proxmox diagnostic pilot](docs/dataset-pilot.md) contains 12 training, 4 validation and 6 test scenarios. Baseline evaluation and domain training are pending.
