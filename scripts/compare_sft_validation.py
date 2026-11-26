"""Reproduce the four-case SFT v1 comparison using the frozen logs and reviews."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
FIELDS = ("diagnosis", "relevant_checks", "calibrated_uncertainty", "safe_grounded",
          "format_complete")


def read_run(stem, cases):
    lines = (BENCH / f"{stem}_20261126.txt").read_text().splitlines()
    rows = [json.loads(line.removeprefix("RESULT ")) for line in lines if line.startswith("RESULT ")]
    with (BENCH / f"{stem}_review.csv").open(newline="") as file:
        review = list(csv.DictReader(file))
    ids = [case["id"] for case in cases]
    assert [r["id"] for r in rows] == [r["id"] for r in review] == ids
    assert lines.count(f"BASELINE_OK {len(ids)}") == 1
    for case, row, score in zip(cases, rows, review, strict=True):
        assert case["observations"] in row["prompt"]
        assert row["answer"] and row["seconds"] > 0 and row["rss_mib"] > 0
        assert 0 < row["generated_tokens"] <= row["max_new_tokens"] == 256
        assert row["reached_cap"] == (row["generated_tokens"] == 256)
        assert all(score[key] in {"0", "1"} for key in FIELDS)
    seconds = sum(r["seconds"] for r in rows)
    tokens = sum(r["generated_tokens"] for r in rows)
    return rows, dict(scores={k: sum(int(r[k]) for r in review) for k in FIELDS},
                      mean_seconds=seconds / len(rows), tokens_per_second=tokens / seconds,
                      total_tokens=tokens, max_rss_mib=max(r["rss_mib"] for r in rows),
                      capped=sum(r["reached_cap"] for r in rows))


def main():
    raw = (ROOT / "data/proxmox_validation.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "701d49298162cc35aeb6482be51da5cacb9a0893f6737a2ae20f351304eed6b3"
    cases = [json.loads(line) for line in raw.splitlines()]
    original, before = read_run("ministral_instruct_baseline_validation_256", cases)
    adapted, after = read_run("ministral_sft_validation_256", cases)
    for a, b in zip(original, adapted, strict=True):
        assert (a["prompt"], a["prompt_tokens"]) == (b["prompt"], b["prompt_tokens"])
    print(json.dumps(dict(original=before, adapted=after,
                     identical_answers=[a["id"] for a, b in zip(original, adapted, strict=True)
                                        if a["answer"] == b["answer"]]), indent=2))


if __name__ == "__main__":
    main()
