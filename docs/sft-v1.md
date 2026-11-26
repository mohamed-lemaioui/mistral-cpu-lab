# First assistant-only SFT pilot

Four French training records in `data/proxmox_sft_v1.jsonl` were authored by AI for this experiment. Each record supplies a synthetic observation, its execution context and a concise answer. Human technical review is pending for all four. The historical 12/4/6 split is frozen. The new records have distinct IDs and observations across all 26 cases. The semantic comparison below is an author review.

| Record | Evidence and scope | Separation from historical tasks |
| --- | --- | --- |
| md_mirror | The host sees one active member in a two-slot Linux MD RAID1. The reason for the missing member is unknown. [Kernel MD interface](https://docs.kernel.org/admin-guide/md.html) | Array redundancy differs from thin-pool capacity, mount availability and filesystem errors. |
| cpu_bandwidth | The service's cgroup shows a 50 ms quota per 100 ms period and a contemporaneous throttling counter increase. [CPU controller](https://docs.kernel.org/admin-guide/cgroup-v2.html) | The inference depends on CPU time over an interval. Historical cases concern memory and task limits. |
| timer_schedule | Guest unit enablement alone cannot establish timer activation or service execution. [systemctl reference](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) | Targets scheduling and missing evidence. The historical service cases concern the API listener. |
| rx_counter | A cumulative guest-interface drop count lacks a baseline at the incident time. [Kernel network statistics](https://docs.kernel.org/networking/statistics.html) | Tests time attribution. Historical networking cases concern carrier, tagging, duplicate addresses and routing. |

## Format and reproduction

Use the pinned Instruct checkpoint in the local cache and the project software environment. Execute these commands sequentially in separate bounded units as the unprivileged experiment user. The unit settings were MemoryMax=26G, MemorySwapMax=0, CPUQuota=400%, Nice=10 and RuntimeMaxSec=180 for the tokenizer audit or 900 for the optimizer step.

```sh
python scripts/ministral_sft_format.py --data data/proxmox_sft_v1.jsonl
python -u scripts/ministral_sft_step.py --data data/proxmox_sft_v1.jsonl --output-parent ./outputs/sft-v1
```

The user message uses the same French instruction as the historical baseline. The native template supplies the system message, including its date. The audit checks that the inference prefix exactly matches the start of the full conversation. It masks that prefix with -100 and decodes the remaining tokens to check exact agreement with the complete answer plus one terminal EOS. No padding or truncation is used. The raw log records token ID digests, which can change with the system date.

The pilot selects the longest record by token count, batch size one. It uses the text-only FP32 loader and applies one AdamW update to rank-four q/v adapters. It checks trainable parameter identities, finite losses and gradients, adapter changes and a frozen embedding sample. It unloads the trained adapter, attaches the saved weights to the same base and compares the final-position logits on the training sequence. This is an in-process serialization check.

The historical validation and test cases have been exposed during development. A claim of diagnostic improvement requires a separately authored frozen evaluation and independent scoring.

## Measured on 26 November 2026

The tokenizer audit passed on all four examples. In corpus order, the total/supervised token counts were 697/60, 715/61, 702/66 and 711/59. The optimizer step on `cpu_bandwidth` took 317.21 s with a pre-update loss of 4.15654. All 1,171,456 trainable parameters belonged to the adapters. The full unit including loading, saving and verification finished in 578.02 s with peak process RSS of 18,171.90 MiB and zero unit swap. The reloaded final-position logits matched exactly. The adapter weight file contains 4,699,504 bytes.

A four-step pass at this measured step time would spend about 21 minutes in training, plus loading and verification. Only one sequence was timed. No before/after diagnostic scores are available for this adapter. See the [tokenizer log](../benchmarks/ministral_sft_format_20261126.txt) and [training log](../benchmarks/ministral_sft_step_20261126.txt).
