# Mistral CPU Lab

CPU-only fine-tuning and deployment research for specialized small language models (SLMs), with a focus on Mistral open-weight models and legacy x86 hardware.

This independent personal research project explores whether useful domain-specific models can be developed without GPU acceleration. The initial target is read-only systems administration assistance using synthetic examples and deterministic tools.

## Experimental status — 2026-11-25

| Experiment | Status |
|---|---|
| Ministral 3B architecture and LoRA compatibility | Passed on miniature model |
| Ministral text-only checkpoint mapping | Validated against index; synthetic loading tested |
| Official Ministral checkpoint download | SHA-256 verified |
| Full pretrained Ministral CPU LoRA | Not yet validated |
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

## Reproduce

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

The command above is a proposed reproduction procedure, not a validated full-model result. Use an isolated environment with an appropriate memory limit. Remove `--download` to require a populated local cache.

The experimental Ministral loader is not yet validated at full scale. It defaults to FP32, requires a local checkpoint unless `--download` is explicitly supplied, and should only be run with sufficient memory (32 GiB laboratory quota recommended, not a measured minimum). It downloads approximately 7.7 GB of weights. No model weights are distributed here.

## Research integrity

All examples are synthetic. Recorded measurements are summarized from laboratory notes, not independently reproduced on another machine. Code and documentation were developed with AI assistance under the project owner's direction; results, limitations and failed experiments are reported separately from plans. This project is independent and is not endorsed by Mistral AI.

See [roadmap](docs/roadmap.md). Upstream model weights retain their respective licenses.
