"""Train one ordered epoch of the approved v2 corpus, with restartable PEFT checkpoints."""
import argparse
import fcntl
import hashlib
import json
import math
import os
import random
import resource
import tempfile
import time
from importlib.metadata import version
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoTokenizer

from ministral_instruct_baseline import NAME, REV, load_text_model
from ministral_sft_format import encode

SEED = 42
ADAPTER = dict(r=4, lora_alpha=8, lora_dropout=0.0, target_modules=["q_proj", "v_proj"],
               task_type="CAUSAL_LM")
LR = 1e-4
EXPECTED_ROWS = 100
EXPECTED_TRAINABLE = 1171456
MAX_SEQ_LEN = 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint_base():
    """Hash the pinned config, index and every weight shard in full."""
    def fetch(name):
        return Path(hf_hub_download(NAME, name, revision=REV, local_files_only=True))

    def file_digest(path):
        state = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                state.update(chunk)
        return state.hexdigest()

    config = fetch("config.json")
    index_path = fetch("model.safetensors.index.json")
    index = json.loads(index_path.read_text())["weight_map"]
    shards = {}
    for shard in sorted(set(index.values())):
        path = fetch(shard)
        shards[shard] = dict(size=path.stat().st_size, sha256=file_digest(path))
    return dict(config_sha256=digest(config.read_bytes()),
                index_sha256=digest(index_path.read_bytes()), shards=shards)


def prepare_plan(raw, root, base_fingerprint):
    # Persist exact native prompt IDs. Re-rendering after midnight can change the prefix.
    identity = dict(model=NAME, revision=REV, corpus_sha256=digest(raw), seed=SEED,
                    adapter=ADAPTER, lr=LR, base=base_fingerprint,
                    threads=dict(intra=torch.get_num_threads(),
                                 interop=torch.get_num_interop_threads()),
                    versions={p: version(p) for p in
                    ("torch", "transformers", "peft", "safetensors", "tokenizers")},
                    code={f: digest(Path(__file__).with_name(f).read_bytes()) for f in
                    ("ministral_sft_epoch.py", "ministral_sft_format.py", "ministral_instruct_baseline.py")})
    rows = [json.loads(line) for line in raw.splitlines()]
    if len(rows) != EXPECTED_ROWS or len({r["id"] for r in rows}) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} unique training rows")
    for row in rows:
        if not {"id", "observations", "answer"} <= row.keys():
            raise ValueError("Training row misses id, observations or answer")
        if any(not isinstance(row[key], str) or not row[key].strip()
               for key in ("id", "observations", "answer")):
            raise ValueError("Training row contains an empty required field")
    order = list(rows)
    random.Random(SEED).shuffle(order)
    path = root / "plan.json"
    if path.exists():
        plan = json.loads(path.read_bytes())
        if plan["identity"] != identity or [x["id"] for x in plan["examples"]] != [r["id"] for r in order]:
            raise ValueError("Corpus, recipe, order or environment changed")
        if len(plan.get("examples", [])) != len(order):
            raise ValueError("Invalid token plan example count")
        for row, example in zip(order, plan["examples"], strict=True):
            if example.get("id") != row["id"]:
                raise ValueError("Token plan ID/order mismatch")
            ids, labels = example.get("ids"), example.get("labels")
            if (not isinstance(ids, list) or not isinstance(labels, list)
                    or not ids or len(ids) != len(labels) or len(ids) > MAX_SEQ_LEN
                    or any(type(token) is not int or token < 0 for token in ids)
                    or any(type(label) is not int or label < -100 for label in labels)
                    or not any(label != -100 for label in labels)):
                raise ValueError(f"Invalid token plan for {row['id']}")
            if not any(label == -100 for label in labels):
                raise ValueError(f"Missing prompt mask in token plan for {row['id']}")
        token_hash = digest(json.dumps(plan["examples"], sort_keys=True, separators=(",", ":")).encode())
        if plan.get("plan_sha256") != token_hash:
            raise ValueError("Token plan integrity hash mismatch")
    else:
        if any(root.glob("step-*")):
            raise ValueError("Missing token plan for existing checkpoints")
        tokenizer = AutoTokenizer.from_pretrained(NAME, revision=REV, local_files_only=True,
                                                  trust_remote_code=False)
        examples = []
        for row in order:
            ids, labels = encode(tokenizer, row)
            if len(ids) != len(labels) or len(ids) > MAX_SEQ_LEN:
                raise ValueError(f"Invalid token length for {row['id']}")
            examples.append(dict(id=row["id"], ids=ids, labels=labels))
        plan = dict(identity=identity, examples=examples)
        plan["plan_sha256"] = digest(json.dumps(examples, sort_keys=True, separators=(",", ":")).encode())
        with tempfile.NamedTemporaryFile(mode="w", dir=root, delete=False) as tmp:
            json.dump(plan, tmp)
        os.replace(tmp.name, path)
    token_hash = digest(json.dumps(plan["examples"], sort_keys=True, separators=(",", ":")).encode())
    if plan.get("plan_sha256") != token_hash:
        raise ValueError("Token plan integrity hash mismatch")
    return plan["examples"], token_hash


def checkpoint(root, step, model, optimizer, names, plan_hash, loss, grad_norm,
               adapter_delta, elapsed):
    dest = root / f"step-{step:03d}"
    if dest.exists():
        raise FileExistsError(f"Checkpoint already exists: {dest}")
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        stage = Path(tmp) / "checkpoint"
        model.save_pretrained(stage, safe_serialization=True, save_embedding_layers=False)
        torch.save(dict(optimizer=optimizer.state_dict(), rng=torch.get_rng_state()), stage / "state.pt")
        hashes = {f: digest((stage / f).read_bytes()) for f in
                  ("adapter_model.safetensors", "adapter_config.json", "state.pt")}
        info = dict(model=NAME, revision=REV, step=step, plan_sha256=plan_hash,
                    trainable=sum(p.numel() for p in model.parameters() if p.requires_grad),
                    parameters=names, sha256=hashes, loss=loss, grad_norm=grad_norm,
                    adapter_delta=adapter_delta, step_seconds=elapsed,
                    threads=dict(intra=torch.get_num_threads(),
                                 interop=torch.get_num_interop_threads()))
        (stage / "run.json").write_text(json.dumps(info, indent=2) + "\n")
        os.rename(stage, dest)


def train(base, examples, root, plan_hash, start_checkpoint, steps_this_session, expected_params):
    start = 0
    if start_checkpoint:
        info = json.loads((start_checkpoint / "run.json").read_bytes())
        if info.get("model") != NAME or info.get("revision") != REV:
            raise ValueError("Checkpoint model or revision mismatch")
        if info.get("trainable") != expected_params:
            raise ValueError("Checkpoint trainable parameter count mismatch")
        start = info["step"]
        if (info["plan_sha256"] != plan_hash or start_checkpoint.name != f"step-{start:03d}"
                or not 0 < start <= len(examples)):
            raise ValueError("Checkpoint does not match this token plan or cursor")
        for file in ("adapter_model.safetensors", "adapter_config.json", "state.pt"):
            if digest((start_checkpoint / file).read_bytes()) != info["sha256"][file]:
                raise ValueError(f"Damaged checkpoint file: {file}")
        adapter_config = json.loads((start_checkpoint / "adapter_config.json").read_text())
        for key, value in ADAPTER.items():
            if adapter_config.get(key) != value:
                raise ValueError(f"Adapter configuration mismatch: {key}")
        model = PeftModel.from_pretrained(base, start_checkpoint, is_trainable=True)
    else:
        model = get_peft_model(base, LoraConfig(**ADAPTER))
    model.train()
    frozen = base.get_input_embeddings().weight
    frozen_sample = frozen[:8].detach().clone()
    params = {}
    for name, p in model.named_parameters():
        adapter = any(f".{proj}.lora_{side}.default.weight" in name
                      for proj in ADAPTER["target_modules"] for side in ("A", "B"))
        if p.requires_grad != adapter:
            raise RuntimeError(f"Unexpected gradient eligibility: {name}")
        if adapter:
            params[name] = p
    if sum(p.numel() for p in params.values()) != expected_params:
        raise RuntimeError("Unexpected trainable parameter count")
    optimizer = torch.optim.AdamW(params.values(), lr=LR)
    if start_checkpoint:
        if list(params) != info["parameters"]:
            raise ValueError("Optimizer parameter order changed")
        state = torch.load(start_checkpoint / "state.pt", map_location="cpu", weights_only=True)
        optimizer.load_state_dict(state["optimizer"])
        torch.set_rng_state(state["rng"])
    end = min(len(examples), start + steps_this_session)
    for idx in range(start, end):
        row = examples[idx]
        started = time.perf_counter()
        optimizer.zero_grad(set_to_none=True)
        loss = model(input_ids=torch.tensor([row["ids"]]), labels=torch.tensor([row["labels"]]),
                     use_cache=False).loss
        if not torch.isfinite(loss):
            raise FloatingPointError("Nonfinite loss")
        loss.backward()
        grads = [p.grad for p in params.values()]
        if not all(g is not None and torch.isfinite(g).all() for g in grads):
            raise FloatingPointError("Missing or nonfinite gradient")
        grad_sq = sum(float(g.pow(2).sum()) for g in grads)
        if not math.isfinite(grad_sq) or grad_sq <= 0:
            raise FloatingPointError("Zero or nonfinite gradient norm")
        grad_norm = math.sqrt(grad_sq)
        snapshot = {name: p.detach().clone() for name, p in params.items()}
        optimizer.step()
        if not all(torch.isfinite(p).all() for p in params.values()):
            raise FloatingPointError("Nonfinite adapter")
        adapter_delta = max(float((p.detach() - snapshot[name]).abs().max())
                            for name, p in params.items())
        if not math.isfinite(adapter_delta) or adapter_delta == 0:
            raise RuntimeError("Adapter unchanged after optimizer step")
        if frozen.grad is not None or not torch.equal(frozen[:8], frozen_sample):
            raise RuntimeError("Frozen embedding sample changed")
        elapsed = time.perf_counter() - started
        checkpoint(root, idx + 1, model, optimizer, list(params), plan_hash, loss.item(),
                   grad_norm, adapter_delta, elapsed)
        print("COMMITTED", idx + 1, row["id"], "loss", loss.item(), "grad_norm", grad_norm,
              "adapter_delta", adapter_delta, "seconds", elapsed,
              "RSS_MIB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, flush=True)
    return end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--approved-sha256", required=True, help="Exact corpus digest reviewed by the owner")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--steps-this-session", type=int, default=100)
    args = parser.parse_args()
    raw = args.data.read_bytes()
    if digest(raw) != args.approved_sha256 or args.steps_this_session < 1:
        parser.error("Corpus digest mismatch or invalid session length")
    root = args.run_dir
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        exists = (root / "plan.json").exists()
        if exists != args.resume:
            parser.error("Use --resume with an existing plan, or a fresh directory for a new run")
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        torch.manual_seed(SEED)
        base_fingerprint = fingerprint_base()
        examples, plan_hash = prepare_plan(raw, root, base_fingerprint)
        print("PLAN", json.dumps(dict(plan_sha256=plan_hash, examples=len(examples),
              max_tokens=max(len(x["ids"]) for x in examples),
              threads=dict(intra=torch.get_num_threads(),
                           interop=torch.get_num_interop_threads()))), flush=True)
        checkpoints = sorted(root.glob("step-[0-9][0-9][0-9]"))
        if any(not path.is_dir() for path in checkpoints):
            raise ValueError("Checkpoint path is not a directory")
        if [p.name for p in checkpoints] != [f"step-{i:03d}" for i in range(1, len(checkpoints)+1)]:
            raise ValueError("Non-contiguous checkpoint sequence")
        base = load_text_model(use_cache=False)
        end = train(base, examples, root, plan_hash, checkpoints[-1] if checkpoints else None,
                    args.steps_this_session, EXPECTED_TRAINABLE)
        print("EPOCH_OK" if end == len(examples) else "SESSION_OK", end, flush=True)


if __name__ == "__main__":
    main()
