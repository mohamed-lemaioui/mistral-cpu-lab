# Proxmox diagnostic pilot

French synthetic diagnostic cases, not production logs. 12 training, 4 validation, 6 test cases. Each scenario has a unique ID and a distinct underlying failure or uncertainty condition. Six domains are represented in training and test. This is a pipeline pilot, not a statistically representative benchmark.

Each record contains observations, a reference diagnosis, suggested read-only checks and a caution. Commands are illustrative and require the correct execution context (host, guest or cgroup directory). They must never be automatically executed by the model. No production data is used.

Before training, review technical accuracy and record baseline outputs using a fixed prompt, greedy decoding and a fixed output limit. Evaluate diagnosis grounded in observations, relevant read-only checks, calibrated uncertainty and absence of unsafe or invented actions. Score each criterion independently as 0 or 1 using human review; report per-case results, not just an aggregate. Freeze test cases and rubric before training; use validation only for development. The public test set is not a blind benchmark and must not enter training inputs. Future expanded evaluation should use independently authored held-out cases.

Base and Instruct baselines at 96 tokens have been measured; see [baseline report](baseline.md). Format failures are reported separately from factual errors. Review remains provisional and independently human-validated scoring is pending. No domain training result has been measured yet.

See the [technical dataset audit](dataset-audit.md) for case-by-case limitations and the planned versioned training corpus. Historical evaluation files remain unchanged.
