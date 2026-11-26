# In-domain validation v3 — 2026-11-26

This AI-authored candidate replaces v2 validation for future development evaluation only; all historical datasets remain unchanged. It contains 24 cases (two per training domain), including eight explicit abstention cases. Mechanisms were selected to differ from the training scenarios rather than merely paraphrase them. Some conceptual overlap remains (e.g. HA states, network rate limits); this is not evidence of semantic independence or a blind test.

Each case includes an official documentation reference, observations, diagnosis, read-only check, unsupported conclusion and abstention flag. The references are not immutable version pins; archived official documentation was consulted selectively, not exhaustively for all 24 cases. Independent human technical review is pending. Do not train on this dataset or expose the answer key to the model during evaluation.

Use the five binary scoring axes in validation-v2.md (diagnosis, actionable verification, calibrated uncertainty, safety, completeness) and separate abstention accuracy. Freeze the reviewed version and scoring criteria before generating responses. Compare the original Instruct model and adapted model under identical generation settings and prompts containing observations only. Preserve Ceph/chrony v2 evaluation as a separate transfer probe.

## Checks
- 24 unique IDs and observations, 12 domains with two cases each, eight abstentions, required fields present.
- 2,400 pairs against SFT v2, 3,888 against all previous datasets. Independently computed maxima using audit_sft_v2_split helpers: 12-word containment 0, character 5-gram Jaccard 0.158416 against train and 0.210366 against all prior rows. No threshold violations (0.5 / 0.85). Lexical checks are not semantic validation.
- SHA256: a073161a2ac42c7aea2d12ed6b45de3c748690e851e025b7243a59c5f268d9a4.
- No model generation, training, infrastructure changes, or execution of proposed diagnostic commands.

Next: human review of the exact training corpus and candidate validation, then a bounded three-step Ministral pilot with real checkpoint resume.
