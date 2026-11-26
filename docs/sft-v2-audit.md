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
