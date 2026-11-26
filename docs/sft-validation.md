# Does one SFT update change diagnostic answers?

This paired development evaluation compares the original Ministral Instruct checkpoint with the same checkpoint plus the saved SFT v1 adapter. Training used one example about CPU bandwidth. The four validation cases concern inode exhaustion, duplicate IP detection, a cgroup task limit and an unavailable web interface. The task-limit case shares cgroup terminology with training but tests a different controller. The six historical test cases are reserved for a final configuration.

## Results

The adapter retained the same three diagnoses. It changed two answer texts. On inode exhaustion the original supplied a relevant check and the adapted answer ran out of tokens while describing a goal. Both models failed to abstain when the only observation was that the web interface was unavailable.

| Frozen validation, four cases | Original Instruct | One-step SFT |
| --- | ---: | ---: |
| Diagnosis | 3/4 | 3/4 |
| Relevant read-only check | 1/4 | 0/4 |
| Calibrated uncertainty | 1/4 | 1/4 |
| Safe and grounded | 1/4 | 0/4 |
| Complete format | 0/4 | 0/4 |
| Explicit abstention on insufficient evidence | 0/1 | 0/1 |
| Responses reaching 256 generated tokens | 4/4 | 4/4 |
| Mean generation time (s per case) | 234.33 | 204.86 |
| Aggregate generated tokens/s | 1.092 | 1.250 |
| Peak process RSS (MiB) | 16,132.92 | 16,133.03 |

| Case | What changed within 256 tokens |
| --- | --- |
| Inode exhaustion | Both identify full inode use. The adapted answer speculates about metadata corruption and stops before delivering a check. The original proposed confirming inode use on the affected mount. |
| Duplicate IP | The answer is identical, including the plausible duplicate-IP hypothesis and an unsupported explanation about the ARP cache. |
| Task limit | Both recognize the limit and both use imprecise PID-counter terminology. The original tentatively linked the fork failure to a process limit. The adapted answer explicitly attributes it to exhaustion of the PID counter and ends mid-command. This stronger claim loses the grounding point. The observed maximum is a cgroup task limit. |
| Unavailable web interface | The answer is identical. Both focus on Apache/Nginx and ports 80/443. Neither acknowledges that the evidence is insufficient or reaches a Proxmox-specific service check. |

The largest scoring ambiguity is grounding on the task-limit case. Counting the original's imprecise wording as a failure too would make this criterion 0/4 in both arms. The one-check loss and the absence of a diagnostic gain are unaffected. No generated command was executed.

The adapted unit finished successfully in 835.114 s with zero unit swap. A previous unadapted native-prompt run produced the same four texts in 182.97 s per case on average. The adapted time falls between the two unadapted measurements. These runs provide no evidence of a reproducible speedup.

The results support keeping original Instruct as the comparison reference. They do not establish the effect of a longer training run or generalization to new incidents. See the [original output](../benchmarks/ministral_instruct_baseline_validation_256_20261126.txt), [original review](../benchmarks/ministral_instruct_baseline_validation_256_review.csv), [adapted output](../benchmarks/ministral_sft_validation_256_20261126.txt) and [adapted review](../benchmarks/ministral_sft_validation_256_review.csv).

## Protocol

The comparator is the archived four-case **Instruct** validation run with the 256-token cap. A second native-prompt run on the same day had already reproduced its answer texts. We reused the original run and its existing scores. Both arms used the same checkpoint revision, native template on 26 November 2026, user prompts, case order, four CPU threads, FP32 text weights, greedy decoding and KV cache. Only IDs and observations were supplied to the generation process. The model saw the observations inside the instruction and never received the reference answers. The comparison script verifies matching user prompts and input token counts. The original run did not log token-ID digests.

The adapted arm loaded the unmerged, frozen PEFT adapter in a fresh process. Its weight SHA256 was `bf850d3c5017b363337822d7eb1b06c69ad4312e01b5850072405f1a8002f540`. Its config SHA256 was `6fda88a4fa576917043a29ca17702ce13fc758fcc497a468f8b8e3a2e20e5f4c`. The [training report](sft-v1.md) identifies the model revision and adapter recipe. No further updates were applied.

The five binary criteria are a grounded diagnosis, at least one relevant read-only check, calibrated uncertainty, safe and grounded content, and a complete answer in the requested format. Scores apply only to the visible response. An answer can contain a valid diagnosis and also fail safety/grounding due to an invented explanation. For the web-interface case we also examine whether the model explicitly says there is insufficient evidence. This is a provisional AI review of four previously exposed synthetic cases.

## Reproduction

Use the project environment and a populated offline cache inside a bounded unit (MemoryMax=26G, MemorySwapMax=0, CPUQuota=400%, Nice=10, RuntimeMaxSec=2400). Supply the saved adapter directory including its training metadata. The same script runs the original model when the adapter argument is omitted.

```bash
python -u scripts/ministral_instruct_baseline.py --data data/proxmox_validation.jsonl --max-new-tokens 256 --adapter "$ADAPTER_DIR"
python scripts/compare_sft_validation.py
```

Elapsed generation time includes prompt processing and decoding. RSS is the maximum resident set size of each process. These were separate runs with uncontrolled host and cache conditions. The difference in timing cannot isolate adapter overhead.
