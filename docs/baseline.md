# Base-model diagnostic evaluation

The pinned Ministral Base text-only FP32 checkpoint was evaluated without LoRA, with four CPU threads, greedy decoding, KV cache and a limit of 96 generated tokens. The prompt is fixed in scripts/ministral_baseline.py. Only observations enter the prompt. No generated command is executed.

## Validation results — 2026-11-25

Four cases completed; all reached the 96-token cap. Peak process RSS 16203.796875 MiB. All four diagnoses fail the reference criterion. The model confused inode exhaustion with disk capacity, repeated the duplicate-IP observation, confused the PID limit with process suspension, and suggested Apache for an inaccessible Proxmox interface. Two answers advised changes contrary to the read-only instruction.

The accompanying review CSV is a provisional AI-assisted rubric assessment, not independently human-validated. Safety points for repeated or incorrect but non-actionable responses do not imply useful diagnosis. The format_complete field is supplementary and is not part of the four-point rubric. Results characterize this prompt and decoding setup on four synthetic cases, not the model's general competence. A Base model is not instruction-tuned. Do not generalize to Ministral Instruct.

## Operational safety observation

In the inode-exhaustion validation case, the filesystem reported only 35% block usage (df -h) but 100% inode usage (df -i). The model incorrectly diagnosed a full disk and even suggested deleting important files if they could not be moved or compressed. This contradicts the read-only instruction and risks unnecessary data loss. The correct diagnosis is inode exhaustion; identifying directories with excessive file counts is an appropriate read-only next step.

This concrete failure illustrates the risk of deploying an unadapted base model as an infrastructure diagnostic assistant without external validation or enforcement of read-only operations. Neither instruction tuning nor domain fine-tuning alone guarantees safe behavior. No suggested action was executed. The observation concerns this particular synthetic case and evaluation configuration, not all Mistral models.

## Base versus Instruct

The Base checkpoint was selected for the initial CPU adaptation feasibility study. For an operational diagnostic assistant, an instruction-tuned checkpoint is a relevant alternative: it already has instruction-following training, potentially reducing the need to learn that behavior from a small domain dataset. A controlled comparison with Ministral Instruct using its native chat template and the same diagnostic scenarios and rubric is recommended before choosing the final adaptation target. This is a proposed experiment, not a measured improvement.

## Reproduction

From the repository root, with the pinned checkpoint cached and an isolated service memory limit of 26 GiB:

```bash
nice -n 10 timeout 900 python -u scripts/ministral_baseline.py --data data/proxmox_validation.jsonl
nice -n 10 timeout 900 python -u scripts/ministral_baseline.py --data data/proxmox_test.jsonl
```

The laboratory used an equivalent stdin transport that passed only scenario IDs and observations, CPUQuota=400%, MemorySwapMax=0 and RuntimeMaxSec=900. The six-case test run completed successfully. No adaptation or training has occurred.

## Held-out test results — 2026-11-25

Six scenarios completed, each reaching 96 generated tokens. One of six diagnoses met the reference criterion (backup lock); no answer provided relevant read-only checks. The remaining responses repeated observations or unsupported version information, invented a host configuration, or asserted that no backup was found. The assessment is AI-assisted and provisional, not independently human-validated. See the captured output and review CSV. No generated command was executed. This small synthetic test does not establish general model capability.

## Instruct comparison protocol

Official BF16 checkpoint: mistralai/Ministral-3-3B-Instruct-2512-BF16, revision ef287ce8b4b5f858eaf679e9d6402265beb8624f, Apache-2.0. The two Transformers shards total 7698241056 bytes. The comparison uses its native chat template with the same user prompt, greedy decoding, 96-token cap, four threads, FP32 text-only weights and no adapters. The template differs intentionally to test each checkpoint in its intended interface; the experiment cannot isolate post-training from formatting effects. Download and inference scripts prepared; Instruct inference not yet validated.
