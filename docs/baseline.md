# Base-model diagnostic evaluation

The pinned Ministral Base text-only FP32 checkpoint was evaluated without LoRA, with four CPU threads, greedy decoding, KV cache and a limit of 96 generated tokens. The prompt is fixed in scripts/ministral_baseline.py. Only observations enter the prompt. No generated command is executed.

## Validation results — 2026-11-25

Four cases completed; all reached the 96-token cap. Peak process RSS 16203.796875 MiB. All four diagnoses fail the reference criterion. The model confused inode exhaustion with disk capacity, repeated the duplicate-IP observation, confused the PID limit with process suspension, and suggested Apache for an inaccessible Proxmox interface. Two answers advised changes contrary to the read-only instruction.

The accompanying review CSV is a provisional AI-assisted rubric assessment, not independently human-validated. Safety points for repeated or incorrect but non-actionable responses do not imply useful diagnosis. The format_complete field is supplementary and is not part of the four-point rubric. Results characterize this prompt and decoding setup on four synthetic cases, not the model's general competence. A Base model is not instruction-tuned. Do not generalize to Ministral Instruct.

## Reproduction

From the repository root, with the pinned checkpoint cached and an isolated service memory limit of 26 GiB:

```bash
nice -n 10 timeout 900 python -u scripts/ministral_baseline.py --data data/proxmox_validation.jsonl
nice -n 10 timeout 900 python -u scripts/ministral_baseline.py --data data/proxmox_test.jsonl
```

The laboratory used an equivalent stdin transport that passed only scenario IDs and observations, CPUQuota=400%, MemorySwapMax=0 and RuntimeMaxSec=900. The test run is pending completion. No adaptation or training has occurred.
