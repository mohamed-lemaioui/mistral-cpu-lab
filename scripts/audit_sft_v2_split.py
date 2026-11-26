"""Screen train/evaluation pairs for exact reuse and lexical near neighbours."""
import argparse
import collections
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

MAX_CONTAINMENT = 0.5
MAX_JACCARD = 0.85
MAX_COSINE = 0.85


def read(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def normalize(text):
    plain = unicodedata.normalize("NFKD", text.casefold())
    return " ".join(re.findall(r"[a-z0-9]+", "".join(c for c in plain if not unicodedata.combining(c))))


def content(row):
    # Observe the symptom and the conclusion. Shared template text is never added.
    return normalize(row["observations"] + " " + row.get("answer", row.get("diagnosis", "")))


def ngrams(text, size):
    words = text.split()
    return set(tuple(words[i:i+size]) for i in range(max(0, len(words)-size+1)))


def chargrams(text, size=5):
    return set(text[i:i+size] for i in range(max(0, len(text)-size+1)))


def jaccard(left, right):
    return len(left & right) / len(left | right) if left | right else 0.0


def containment(part, whole):
    return len(part & whole) / len(part) if part else 0.0


def require(rows, fields, name):
    for row in rows:
        missing = set(fields) - set(row)
        if missing:
            raise ValueError(f"{name}: {row.get('id')} misses {sorted(missing)}")
        for field in fields:
            if field == "abstain":
                if not isinstance(row[field], bool):
                    raise ValueError(f"{name}: {row['id']} has a non-boolean abstain field")
            elif not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"{name}: {row['id']} has an empty {field}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdout", type=Path, required=True)
    args = parser.parse_args()
    data = Path(__file__).resolve().parents[1] / "data"
    train = read(data / "proxmox_sft_v2.jsonl")
    holdout = read(args.holdout)
    historical_eval = read(data / "proxmox_validation.jsonl") + read(data / "proxmox_test.jsonl")
    previous_train = read(data / "proxmox_train.jsonl") + read(data / "proxmox_sft_v1.jsonl")

    require(train, ("id", "domain", "source", "locator", "observations", "answer"), "train")
    require(holdout, ("id", "source", "oracle", "observations", "diagnosis", "check",
                      "unsupported", "abstain"), "holdout")
    require(historical_eval, ("id", "observations", "diagnosis"), "historical eval")
    require(previous_train, ("id", "observations"), "previous train")

    if (len(train), len(holdout), len(historical_eval), len(previous_train)) != (100, 12, 10, 16):
        raise ValueError("Unexpected split size")
    rows = train + holdout + historical_eval + previous_train
    for row in rows:
        row["_content"] = content(row)
    for field in ("id", "observations", "_content"):
        values = [normalize(row[field]) for row in rows]
        if len(values) != len(set(values)):
            raise ValueError(f"Repeated {field}")
    answers = [normalize(row.get("answer", row.get("diagnosis", ""))) for row in rows]
    if len(answers) != len(set(answers)):
        raise ValueError("Repeated answer or diagnosis")

    # Lexical near neighbours, including cases where only the answer was reused.
    def closest(case, pool):
        case_ngrams, case_chars = ngrams(case["_content"], 12), chargrams(case["_content"])
        scored = [(containment(case_ngrams, ngrams(other["_content"], 12)),
                   jaccard(case_chars, chargrams(other["_content"])), other["id"])
                  for other in pool]
        return max(scored) if scored else (0.0, 0.0, None)

    failures = []
    for case in holdout + historical_eval:
        cont, jac, best = closest(case, train)
        if cont >= MAX_CONTAINMENT or jac >= MAX_JACCARD:
            failures.append((case["id"], "train", cont, jac, best))
        history = [row for row in historical_eval + previous_train if row["id"] != case["id"]]
        cont, jac, best = closest(case, history)
        if cont >= MAX_CONTAINMENT or jac >= MAX_JACCARD:
            failures.append((case["id"], "historical", cont, jac, best))
    for index, left in enumerate(train):
        for right in train[index+1:]:
            jac = jaccard(chargrams(left["_content"]), chargrams(right["_content"]))
            if jac >= MAX_JACCARD:
                failures.append((left["id"], right["id"], 0.0, jac, "intra-train"))

    # Existing TF-IDF view, retained as a readable ranking.
    df = collections.Counter()
    term_counts = {}
    for row in rows:
        text = row["_content"]
        terms = collections.Counter(text[i:i+4] for i in range(len(text)-3))
        term_counts[row["id"]] = terms
        df.update(terms.keys())
    vectors = {}
    for id_, terms in term_counts.items():
        weights = {t: (1 + math.log(n)) * (1 + math.log((len(rows)+1)/(df[t]+1)))
                   for t, n in terms.items()}
        norm = math.sqrt(sum(v*v for v in weights.values()))
        vectors[id_] = {t: v/norm for t, v in weights.items()}
    print("HOLDOUT_SHA256", hashlib.sha256(args.holdout.read_bytes()).hexdigest())
    max_cosine = 0.0
    for case in holdout:
        vector = vectors[case["id"]]
        scores = [(sum(w*vector.get(t, 0) for t, w in vectors[row["id"]].items()), row["id"])
                  for row in train]
        best = sorted(scores, reverse=True)[:3]
        max_cosine = max(max_cosine, best[0][0])
        print(case["id"], *(f"{id_}={score:.3f}" for score, id_ in best))

    train_domains = {row["domain"] for row in train}
    holdout_sources = {row["source"] for row in holdout}
    print("DOMAINS", len(train_domains), "HOLDOUT_SOURCES", sorted(holdout_sources),
          "SOURCE_OVERLAP", len({row["source"] for row in train} & holdout_sources))
    print("ABSTAIN", sum(row["abstain"] for row in holdout), "OF", len(holdout))
    print("MAX_COSINE", f"{max_cosine:.3f}")
    print("EXACT_OK", len(rows), "TRAIN_HOLDOUT_PAIRS", len(train)*len(holdout))
    if failures or max_cosine >= MAX_COSINE:
        for failure in failures:
            print("CONTAMINATION_FAIL", *failure)
        if max_cosine >= MAX_COSINE:
            print("CONTAMINATION_FAIL cosine", f"{max_cosine:.3f}")
        sys.exit(1)
    print("CONTAMINATION_OK")


if __name__ == "__main__":
    main()
