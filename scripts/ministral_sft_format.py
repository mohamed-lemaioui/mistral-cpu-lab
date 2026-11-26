"""Audit complete native chat sequences with the pinned offline tokenizer."""
import argparse
import hashlib
import json
import resource
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from transformers import AutoTokenizer

from ministral_instruct_baseline import NAME, PROMPT, REV

MAX_SEQ_LEN = 1024


def encode(tokenizer, row):
    if PROMPT.count("{observations}") != 1:
        raise ValueError("Prompt template must contain exactly one observations placeholder")
    messages = [{"role": "user", "content": PROMPT.replace("{observations}", row["observations"])}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                           return_dict=True, truncation=False)["input_ids"]
    answer = row["answer"]
    messages.append({"role": "assistant", "content": answer})
    ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False,
                                        return_dict=True, truncation=False)["input_ids"]
    target = ids[len(prompt):]
    if not prompt or ids[:len(prompt)] != prompt:
        raise ValueError(f"Template prefix mismatch for {row['id']}")
    if len(target) < 2 or target[-1] != tokenizer.eos_token_id:
        raise ValueError(f"Missing response or EOS for {row['id']}")
    decoded = tokenizer.decode(target[:-1], skip_special_tokens=False, clean_up_tokenization_spaces=False)
    if decoded != answer or any(token in tokenizer.all_special_ids for token in target[:-1]):
        raise ValueError(f"Response boundary or content mismatch for {row['id']}")
    if len(ids) > MAX_SEQ_LEN:
        raise ValueError(f"Sequence too long for {row['id']}: {len(ids)} tokens")
    labels = [-100] * len(prompt) + target
    if len(labels) != len(ids):
        raise ValueError(f"Label length mismatch for {row['id']}")
    return ids, labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    raw = args.data.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    assert rows and len({r["id"] for r in rows}) == len(rows)
    tokenizer = AutoTokenizer.from_pretrained(NAME, revision=REV, local_files_only=True,
                                              trust_remote_code=False)
    print("CONFIG", json.dumps(dict(model=NAME, revision=REV, transformers=version("transformers"),
          torch=version("torch"), utc=datetime.now(timezone.utc).isoformat(),
          corpus_sha256=hashlib.sha256(raw).hexdigest())), flush=True)
    for row in rows:
        ids, labels = encode(tokenizer, row)
        print("MASK", json.dumps(dict(id=row["id"], total=len(ids), masked=labels.count(-100),
              supervised=len(ids)-labels.count(-100), tokens_sha256=hashlib.sha256(
                  json.dumps(ids).encode()).hexdigest())), flush=True)
    print("FORMAT_OK", len(rows), "SECONDS", time.perf_counter()-start,
          "RSS_MIB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)


if __name__ == "__main__":
    main()
