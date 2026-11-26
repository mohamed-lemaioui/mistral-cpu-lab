# SFT v2 validation and integrity checks

The new `data/proxmox_validation_v2.jsonl` contains 24 synthetic, in-domain cases: two for each of the 12 training domains. It is a public development validation set, not a blind test; do not train on it. Human technical review remains necessary. The [rubric and case format](validation-v2.md) define five binary scoring dimensions and abstention scoring.

The lexical split checker now computes maximum 12-word-ngram containment and character-5-gram Jaccard independently. Its prior tuple maximum prioritized containment and could conceal a larger Jaccard score.

The epoch trainer stores a canonical SHA256 for the tokenized examples in `plan.json`, verifies it on resume, and validates IDs/order, token and label types, length bounds, and masking structure. `scripts/check_sft_resume.py` contains the synthetic CPU fixture, including rejection of a token-plan edit before any checkpoint exists. Run it in the pinned project environment with:

```sh
python scripts/check_sft_resume.py
```

This fixture is a mechanism test, not a Ministral training run. Full training and quality evaluation remain separate and require corpus review and explicit authorization.
