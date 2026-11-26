# Diagnostic dataset audit — 2026-11-26

AI-assisted technical review of the 22 original synthetic cases. Independent human review remains pending. Preserve original JSONL files and historical scoring; corrections below are guidance for a separately versioned training corpus, not retroactive changes to evaluation.

| Case | Review |
|---|---|
| thin_data | Correct distinction between data and metadata utilization; identify the affected pool explicitly. |
| thin_meta | Correct interpretation; confirm pool and metadata capacity. |
| bridge_link | NO-CARRIER indicates absent carrier, not necessarily a defective cable; check interface administrative state and physical link. |
| vlan_mismatch | Plausible missing tagged VLAN on uplink; verify bridge VLAN filtering and switch configuration. |
| memory_limit | oom_kill is cumulative; confirm timestamps and local versus hierarchical events before attributing to current quota. Read files in the correct cgroup. |
| rootfs_full | Block exhaustion supported; confirm filesystem and reserved blocks. du can be expensive on large trees. |
| boot_order | Network-only configured boot order is supported; VM ID 901 is illustrative, not observed. |
| missing_iso | Missing referenced volume supported; VM ID 902 is illustrative, not observed. |
| backup_space | Destination capacity is a plausible cause; verify the exact target mount. |
| backup_permission | Permission failure supported; path /mnt/backup is illustrative. Verify actual export, UID/GID and mapping. |
| proxy_down | Inactive pveproxy and absent listener support service unavailability; root cause unknown. |
| quorum | Loss of quorum supported; never force quorum as an automatic diagnostic action. |
| inode_full | Inode exhaustion supported; df -i confirms it, rather than identifying which directories consumed inodes. |
| duplicate_ip | Duplicate IP probable; proxy ARP or unusual network configurations can also produce replies. |
| pid_limit | cgroup task limit reached; counts include threads. Read the correct cgroup, not a per-CPU limit. |
| api_unclear | Insufficient evidence; pveproxy and TCP 8006 are appropriate default checks. |
| storage_offline | Inactive storage supported; missing mount does not establish why. Check storage type and configuration. |
| missing_gateway | No default route in the displayed routing table; policy routing or other tables may matter. |
| lock | Backup lock does not prove active backup; VM ID 903 is illustrative. |
| backup_unknown | Insufficient evidence; locate the actual task log before attributing a cause. |
| read_only | Read-only mount and EXT4 error supported; temporal causal link not established. Kernel logs may require host access. |
| certificate | Verify certificate presented by the actual endpoint, SNI and client clock; localhost may present a different certificate. |

## Structural checks

12 train / 4 validation / 6 test; unique IDs and exact observations; consistent schema. Exact uniqueness does not prove semantic independence. Validation and test lack independent authorship and are public, with repeated exposure during development.

## Next training corpus

Keep the original pilot immutable. Use a separate versioned training dataset with explicit execution context, concise grounded answers, no invented identifiers or paths, and examples of insufficient evidence across multiple domains. Avoid direct variants of evaluation incidents. Record provenance and distinguish AI-authored examples from human-reviewed examples. Do not execute generated commands. Verify command syntax and technical content before training.

A small pilot SFT run should test the pipeline, not claim operational competence. Before a meaningful quality claim, use an independently authored held-out evaluation set, frozen before training. The current historical evaluation remains useful for comparison but is not blind.

Selected starting configuration: pinned Ministral Instruct FP32, native conversation template, LoRA q/v. Assistant-only loss masking must be verified with the actual tokenizer; do not truncate away the assistant target. The native system message adds substantial context, so training sequence length and memory/time must be measured rather than extrapolated from earlier 256-token probes.
