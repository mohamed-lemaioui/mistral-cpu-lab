# Reproduction guide

Install the environment described in the README. All scripts run on CPU. The model-dependent scripts use the exact pinned upstream revision and local cache. To populate the cache once, use the following command in a suitable isolated environment (requires about 7.7 GB of downloads, and sufficient disk space):

```bash
python -c 'from huggingface_hub import snapshot_download; snapshot_download("mistralai/Ministral-3-3B-Base-2512", revision="6f9c4b12a95b139af68670a6713616b757923735")'
```

Run individually from the repository root:

```bash
python scripts/ministral_verify_shards.py
python scripts/ministral_preflight.py
python scripts/ministral_tiny_lora.py
python scripts/ministral_mmap_check.py
python scripts/ministral_projection_benchmark.py
nice -n 10 timeout 600 python -u scripts/ministral_text_probe.py --dtype fp32 --tokens 32
```

Use an isolated memory-limited environment. The first five scripts were rerun with a 4 GiB memory limit, CPU quota 400%, nice 10, no swap and 180 s runtime limit per script. The full-size probe used 26 GiB, CPU quota 400%, nice 10, no swap and 600 s runtime limit. These limits are not measured minimum requirements.

| Script | Provenance and purpose |
|---|---|
| ministral_verify_shards.py | Reconstructed: verify both pinned SHA-256 hashes |
| ministral_preflight.py | Reconstructed: metadata, tied parameters, index mapping, LoRA parameter count and tokenizer |
| ministral_tiny_lora.py | Reconstructed: synthetic randomly initialized miniature FP32/BF16 forward/backward and AdamW |
| ministral_mmap_check.py | Reconstructed: synthetic BF16 weight loading and FP32 buffer/logit equivalence |
| ministral_projection_benchmark.py | Reconstructed: one random projection trial per dtype, no warmup |
| ministral_text_probe.py | Original executable full-size text-only CPU LoRA probe |

The intermediate experiments were originally executed as inline commands; these standalone versions reproduce the documented methods, not necessarily the exact original random tensors or timing conditions. All five reconstructed scripts completed successfully on the original hardware on 2026-11-25. Their captured result lines are in [rerun output](../benchmarks/ministral_reconstructed_20261125.txt). The original pretrained probe result lines are [here](../benchmarks/ministral_pretrained_20261125.txt). Historical CSVs remain unchanged. These files are selected output lines, not complete terminal transcripts. The earlier failed tests are described in the experimental report rather than presented as successful runs.

The projection rerun used random weights and yielded 0.094434 s FP32 and 10.299881 s BF16. This supports the original hardware-specific observation, not a general BF16 performance claim. The miniature losses differ from the original runs; exact random-state reproduction was not established. The mmap test checks only the synthetic model, not complete pretrained logits equivalence.

## Sequence-length runs

The original probe now accepts --steps 1 or 3 (default 1). Run separately with a suitable 26 GiB service memory limit and 600 s timeout:

```bash
nice -n 10 timeout 600 python -u scripts/ministral_text_probe.py --dtype fp32 --tokens 128 --steps 3
nice -n 10 timeout 600 python -u scripts/ministral_text_probe.py --dtype fp32 --tokens 256 --steps 3
```

Captured logs: [128 tokens](../benchmarks/ministral_context_128_20261125.txt), [256 tokens](../benchmarks/ministral_context_256_20261125.txt). The original 32-token log is preserved; the updated script emits STEP records instead of FORWARD.
