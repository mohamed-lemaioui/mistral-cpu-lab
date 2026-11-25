# Mistral CPU Lab

CPU-only fine-tuning and deployment research for specialized small language models (SLMs), with a focus on Mistral open-weight models and legacy x86 hardware.

This independent personal research project explores whether useful domain-specific models can be developed without GPU acceleration. The initial target is read-only systems administration assistance using synthetic examples and deterministic tools.

## Experimental status — 2026-11-25

| Experiment | Status |
|---|---|
| Qwen3 miniature LoRA and adapter reload | Passed |
| Pretrained Qwen3 0.6B CPU LoRA | Passed |
| Ministral 3B architecture and LoRA compatibility | Passed on miniature model |
| Ministral text-only checkpoint mapping | Validated against index; synthetic loading tested |
| Official Ministral checkpoint download | SHA-256 verified |
| Full pretrained Ministral CPU LoRA | Not yet validated |
| Domain-specific evaluation | Planned |

## Baseline results

Four CPU threads, FP32, batch size 1, three optimizer steps per sequence length on Qwen3 0.6B. See [experimental report](docs/experiments.md) and [recorded measurements](benchmarks/qwen3.csv).

| Tokens | Mean seconds/step | Peak process RSS (MiB) |
|---:|---:|---:|
| 29 | 1.91 | 4866.86 |
| 128 | 7.984 | 4833.41 |
| 256 | 14.195 | 4833.19 |

These are short mechanism benchmarks, not evidence of domain competence or generalization.

## Reproduce

Linux, Python 3.13.5 in the recorded environment. Install the CPU build of PyTorch first, then the recorded dependencies. Package availability depends on platform and release index.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python scripts/lora_smoke.py
python scripts/qwen_cpu_benchmark.py
python scripts/qwen_context_benchmark.py 128
python scripts/qwen_context_benchmark.py 256
```

The first pretrained Qwen script downloads the model and does not pin its revision; the context benchmark requires the recorded pinned revision in the local cache. For exact reproduction, prefetch that revision independently.

The experimental Ministral loader is not yet validated at full scale. It defaults to FP32, requires a local checkpoint unless `--download` is explicitly supplied, and should only be run with sufficient memory (32 GiB laboratory quota recommended, not a measured minimum). It downloads approximately 7.7 GB of weights. No model weights are distributed here.

## Research integrity

All examples are synthetic. Recorded measurements are summarized from laboratory notes, not independently reproduced on another machine. Code and documentation were developed with AI assistance under the project owner's direction; results, limitations and failed experiments are reported separately from plans. This project is independent and is not endorsed by Mistral AI.

See [roadmap](docs/roadmap.md). Upstream model weights retain their respective licenses.
