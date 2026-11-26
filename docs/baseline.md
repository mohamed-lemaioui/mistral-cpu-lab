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

Official BF16 checkpoint: mistralai/Ministral-3-3B-Instruct-2512-BF16, revision ef287ce8b4b5f858eaf679e9d6402265beb8624f, Apache-2.0. The two Transformers shards total 7698241056 bytes. The comparison uses its native chat template with the same user prompt, greedy decoding, 96-token cap, four threads, FP32 text-only weights and no adapters. The template differs intentionally to test each checkpoint in its intended interface; the experiment cannot isolate post-training from formatting effects. Download and inference scripts validated on the four validation scenarios.

## Instruct validation — 96-token protocol

All four scenarios completed and reached the generation cap. The model explicitly identified the PID limit, mentioned inode saturation without completing the causal explanation, began explaining ARP without concluding duplicate IP, and suggested Apache/Nginx for the unavailable interface. None supplied relevant read-only checks within the cap. Under the strict rubric, 1/4 diagnoses passed versus 0/4 for Base. Incomplete answers are scored on their actual text, not on presumed continuations. AI-assisted review remains provisional. All four outputs were truncated at the configured token cap. Mean response time 107.86 s, aggregate 0.89 tokens/s, peak process RSS 16204.19140625 MiB. The measured Base validation throughput was 1.81 tokens/s; the cause of the difference is not established. No generated command was executed.

The six-case Instruct test is complete under the 96-token protocol; see the results below. A separate 256-token comparison for both checkpoints is proposed to examine truncation effects, with a fixed prompt and scoring rubric. Longer-cap results are reported below.

## Longer-output validation protocol

Both baseline scripts now accept --max-new-tokens 256 (default remains 96). For the complementary experiment, run only the four validation scenarios for each checkpoint, sequentially, with the original prompt, native formatting, FP32, four threads, greedy decoding and KV cache unchanged. Log prompt token count, generated token count, whether the generation cap is reached, elapsed time and peak process RSS. Apply the same four criteria to actual output without assuming a continuation. A longer generation cap is an experimental change, not a demonstrated improvement. The six-case 96-token test used the original generation settings; no test outputs are used to tune the prompt. Re-evaluation on validation data is exploratory; it is not a new independent held-out test.

```bash
python -u scripts/ministral_baseline.py --data data/proxmox_validation.jsonl --max-new-tokens 256
python -u scripts/ministral_instruct_baseline.py --data data/proxmox_validation.jsonl --max-new-tokens 256
```

Use the same isolated resource controls as the earlier experiments, and allow sufficient runtime for the longer generation limit. Do not run both models concurrently.

## Native prompt overhead audit

A tokenizer-only audit of the inode-exhaustion scenario measured 80 input tokens for Base and 622 for Instruct (7.775 times as many). The native Instruct template automatically inserts a default system prompt covering assistant identity, date, tools, web access and multimodal capabilities. The text configuration dictionaries were identical. This is a plausible contributor to the observed end-to-end throughput difference, not proof of its cause. Prefill and decode times were not separately measured. The template includes a dynamic date; the measured count corresponds to 2026-11-25. A follow-up with a fixed, concise explicit system prompt and the native message delimiters is proposed to isolate the overhead on Instruct. This would be a distinct experimental configuration. The existing test protocol remains unchanged.

## Instruct test results — 2026-11-25 to 2026-11-26

All six distinct test cases completed at the 96-token cap. The first process was intentionally stopped after three completed cases; the remaining three ran the next day with identical generation settings and new length logging. The native template date changed, cache state and host conditions may differ, and the two runs are not independent repeats. Original captured logs are preserved separately; the combined JSONL contains six outputs with source-log provenance.

| Criterion | Base | Instruct |
|---|---:|---:|
| Diagnosis | 1/6 | 3/6 |
| Relevant read-only checks | 0/6 | 0/6 |
| Calibrated uncertainty | 1/6 | 0/6 |
| Safe and grounded | 2/6 | 4/6 |
| Complete format (supplementary) | 0/6 | 0/6 |

Instruct identified inactive storage, missing default route and expired HTTPS certificate. It conflated a backup lock with an active backup, did not explicitly establish insufficient evidence for the failed backup, and did not complete the read-only filesystem diagnosis. The certificate response included unsupported SSH/VPN implications. Scores are provisional AI-assisted judgments on actual generated text; no independent human validation. Absence of an unsafe command does not establish operational safety.

Mean generation-call time: 121.60 s, aggregate throughput 0.789 tokens/s, maximum process RSS 16204.27 MiB. Base test: 49.46 s, 1.941 tokens/s. These measurements include prefill and decoding, with different prompt lengths, dates and process conditions; they do not isolate decoding speed or the effect of post-training. All outputs reached the cap. No generated command was executed. The pilot does not establish general capability or a domain-adapted model.

See [per-case review](../benchmarks/ministral_instruct_test_review.csv) and [combined outputs](../benchmarks/ministral_instruct_test_combined.jsonl). Next: longer-output validation, then a separate concise-system-prompt experiment.

## Optional live text display

Both baseline scripts accept `--stream` to display decoded text incrementally through Transformers TextStreamer. The final RESULT JSON record is still emitted. The streamer is disabled by default; omit this flag for comparative timing measurements to avoid display overhead. Streaming is buffered at text boundaries, not necessarily one visible fragment per token. A single-case Instruct streaming smoke test completed successfully on 2026-11-26. The displayed text exactly matched the final JSON and earlier 96-token baseline. Fragment arrival intervals were not measured; the captured log is benchmarks/ministral_stream_smoke_20261126.txt. This is a functional test, not a throughput comparison. The running 256-token comparison was not interrupted: Base uses the earlier script and Instruct will use the updated script with streaming disabled.

Example (run only in an isolated environment with the checkpoint cached and no concurrent benchmark):

```bash
python -u scripts/ministral_instruct_baseline.py --data data/proxmox_validation.jsonl --max-new-tokens 256 --stream
```

## Validation at 256 generated tokens — 2026-11-26

Both four-case runs completed sequentially (overall process exit 0). All eight answers reached the cap. The same prompts and decoding settings were retained except the increased output limit. Streaming was disabled. Provisional AI-assisted scores:

| Criterion | Base 96 | Base 256 | Instruct 96 | Instruct 256 |
|---|---:|---:|---:|---:|
| Diagnosis | 0/4 | 0/4 | 1/4 | 3/4 |
| Relevant checks | 0/4 | 0/4 | 0/4 | 1/4 |
| Calibrated uncertainty | 0/4 | 0/4 | 0/4 | 1/4 |
| Safe and grounded | 2/4 | 2/4 | 3/4 | 1/4 |
| Complete format | 0/4 | 0/4 | 0/4 | 0/4 |

The longer Instruct answers identify inode exhaustion, probable duplicate IP and the process limit. They also expose unsupported explanations. The web-interface case still focuses on Apache/Nginx and ports 80/443 instead of pveproxy and 8006. Base repeats text, suggests destructive file operations and invents database failures. Safety scoring penalizes unsupported technical explanations as well as unsafe actions; earlier short outputs expose fewer claims. The scores are provisional and require independent human review; no command was executed. These repeated validation cases are not a fresh test set.

| Model | Mean generation-call seconds | Aggregate tokens/s | Peak RSS MiB |
|---|---:|---:|---:|
| baseline | 158.18 | 1.618 | 16132.41 |
| instruct_baseline | 234.33 | 1.092 | 16132.92 |

Timing includes prefill and decode, and cache state, date and host conditions differ across runs. The next experiment will compare explicit concise and native system prompts on Instruct, without training.

## System-prompt comparison

The separate script `scripts/ministral_system_prompt.py` compares the native default system message with the explicit fixed message "Tu es un assistant de diagnostic Proxmox." The user prompt and 256-token generation cap are unchanged. Run the four validation cases sequentially in native then concise mode, with the same pinned Instruct checkpoint and resource controls. The script logs input tokens, total generation-call duration, output and RSS; it does not separately measure prefill and decoding. The two prompts differ in content as well as length. Streaming remains disabled for timing. Results are reported below.

```bash
python -u scripts/ministral_system_prompt.py --data data/proxmox_validation.jsonl --max-new-tokens 256 --system native
python -u scripts/ministral_system_prompt.py --data data/proxmox_validation.jsonl --max-new-tokens 256 --system concise
```


### System-prompt results — 2026-11-26

Both modes completed four validation cases, all reaching 256 generated tokens. The native outputs were textually identical to the earlier 256-token Instruct baseline.

| Metric | Native | Concise |
|---|---:|---:|
| Mean input tokens | 611.25 | 84.25 |
| Mean generation-call seconds | 182.96 | 202.29 |
| Aggregate tokens/s | 1.399 | 1.266 |
| Peak RSS MiB | 16132.86 | 16133.14 |
| Diagnosis | 3/4 | 1/4 |
| Relevant checks | 1/4 | 0/4 |
| Calibrated uncertainty | 1/4 | 2/4 |
| Safe and grounded | 1/4 | 0/4 |
| Complete format | 0/4 | 0/4 |

The concise prompt reduced total input tokens by 86.22%, but mean end-to-end generation time increased by 10.56% in this run. It missed inode exhaustion, misinterpreted the cgroup PID limit as per CPU, and retained the misleading Apache/Nginx diagnosis. The duplicate-IP diagnosis remained correct. The native prompt produced a stronger diagnostic result under the provisional AI-assisted rubric. No independent human review has been performed.

The native rerun itself varied from the earlier mean of 234.33 seconds to 182.96 seconds despite identical generated text. Fixed run order, uncontrolled host/cache conditions, content differences and no isolated prefill/decode timings prevent attributing the measured slowdown causally to prompt length. These four repeatedly used validation scenarios do not establish general model behavior. Retain the native prompt as the current reference; no domain training has occurred. No generated command was executed.
