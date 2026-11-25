# Proxmox diagnostic pilot

French synthetic diagnostic cases, not production logs. 12 training, 4 validation, 6 test cases. Each scenario has a unique ID and a distinct underlying failure or uncertainty condition. Six domains are represented in training and test. This is a pipeline pilot, not a statistically representative benchmark.

Each record contains observations, a reference diagnosis, suggested read-only checks and a caution. Commands are illustrative and require the correct execution context (host, guest or cgroup directory). They must never be automatically executed by the model. No production data is used.

Before training, review technical accuracy and record baseline outputs using a fixed prompt, greedy decoding and a fixed output limit. Evaluate diagnosis grounded in observations, relevant read-only checks, calibrated uncertainty and absence of unsafe or invented actions. Score each criterion independently as 0 or 1 using human review; report per-case results, not just an aggregate. Freeze test cases and rubric before training; use validation only for development. The public test set is not a blind benchmark and must not enter training inputs. Future expanded evaluation should use independently authored held-out cases.

The model is a Base checkpoint, not an instruction-tuned assistant. Its baseline may fail to follow the requested response format. Report this separately from factual errors. No baseline or domain training result has been measured yet.
