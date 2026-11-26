# SFT v2 corpus and training pipeline audit — 2026-11-26

This is a technical and methodological audit of the 100-record synthetic training corpus, its separate 12-case evaluation set, and the formatting and restartable training scripts. It is not an independent human validation of the answer key.

## Reused checks

- The real tokenizer passed formatting and assistant-only loss-mask checks for all 100 records (`FORMAT_OK 100`). Measured sequences were 658–700 tokens, with 31–59 supervised answer tokens.
- The recorded split audit passed exact identity checks and lexical/statistical similarity thresholds across v2 training, v2 evaluation, historical evaluation, and earlier training data (`CONTAMINATION_OK`). The maximum reported TF-IDF cosine score for v2 evaluation against training was 0.180; the v2 evaluation sources do not overlap the training sources.
- A synthetic fixture verified exact checkpoint resume for adapter weights, AdamW state, and RNG; corrupted checkpoints and mismatched model/recipe were rejected (`RESUME_OK`). This was not a domain training run.
- Supporting references were downloaded to a temporary audit directory and include Proxmox, systemd, Linux kernel, OpenZFS, and chrony documentation.

## Corrections and safeguards

Prompt construction now substitutes only the `{observations}` placeholder, so braces in observations or command examples cannot be treated as format fields. The formatter requires exactly one placeholder, rejects sequences over 1,024 tokens without truncation, and checks input/label length equality.

The epoch trainer requires the exact approved corpus SHA256, pins the model revision and recipe in a token plan, records environment and source-code fingerprints, validates checkpoint hashes and adapter configuration, and checks finite nonzero gradients, adapter updates, and frozen weights. Checkpoints are staged atomically and a run-directory lock prevents concurrent writers.

## Residual risks

- The corpus and answer key were AI-assisted and still require independent human technical review. The listed corpus SHA256 is `5b5d9b023b67c716357fa9544d99d67744e7c6a62b4b18ee2f03d860087107a1`; review the exact bytes before authorizing training.
- Lexical and TF-IDF checks cannot prove semantic independence or answer correctness. Thresholds are heuristic.
- No model quality evaluation has been run on the v2 set. The audit supports pipeline feasibility only, not improved diagnostic ability or generalization.
- Fixture timing does not estimate the cost of a full epoch. No training or new benchmark was run for this audit.

See the [case-by-case review](corpus-v2-review.md), [contamination audit](../benchmarks/ministral_sft_v2_contamination_audit_20261126.txt), [token lengths and masks](../benchmarks/ministral_sft_v2_lengths_20261126.txt), and [resume fixture log](../benchmarks/ministral_sft_v2_resume_20261126.txt).

## Independent AI-assisted follow-up review — 2026-11-26

The 100 training observations/answers, 12 evaluation cases, training code and existing logs were inspected. This was not an independent human review or an exhaustive source-by-source verification. The recorded token lengths are 658–700, with **31–62** supervised tokens (correcting the earlier range). Both corpus hashes match the reviewed versions.

The v2 evaluation consists solely of eight Ceph and four chrony cases. It is suitable as a limited out-of-domain transfer probe, not as sufficient evidence of improvement on trained domains. A separate in-domain validation set with distinct scenarios and frozen scoring criteria is needed before training. Public AI-authored cases are not a blind test.

The lexical audit selects a lexicographic maximum of (containment, Jaccard, ID), which can hide a high Jaccard score. Independently recalculating both metrics for every evaluation/historical evaluation pair against v2 training and historical/earlier training (excluding identical IDs) found maximum containment 0 and maximum Jaccard 0.088983 and 0.204545 respectively, with no threshold violations. This does not establish semantic independence.

Before the first checkpoint, an existing token plan can be accepted with altered token IDs or labels despite length checks. Strengthen plan validation and test this case. The recorded resume test is on a tiny synthetic Llama fixture, not the full Ministral model; its script was missing from the published snapshot. These findings require follow-up. No data or training scripts were modified in this review, and no new model run or training was performed. Human approval of the exact training corpus remains pending.

### CPU resume fixture follow-up

The revised fixture initially failed because PEFT serializes target_modules in arbitrary order. Comparing membership and cardinality instead of list order, explicitly testing reversed order, checking supervised labels match token IDs, and restoring the full plan digest for checkpoint binding resolved the failure. The bounded CPU fixture passed RESUME_OK, exit 0, 8.387 s, memory peak 270.9M, no swap. Both failed and successful logs are retained. The internal token hash detects accidental corruption, not deliberate edits with a recomputed hash. No Ministral training was run. The 24-case validation draft contains direct training paraphrases and a backup check suggesting restoration; it requires distinct mechanisms and read-only checks before use. Human approval remains pending.
