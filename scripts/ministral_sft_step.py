"""One CPU SFT update and an adapter-only save/load round trip."""
import argparse
import hashlib
import json
import os
import resource
import tempfile
import time
from importlib.metadata import version
from pathlib import Path

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoTokenizer

from ministral_instruct_baseline import NAME, REV, load_text_model
from ministral_sft_format import encode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output-parent", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(NAME, revision=REV, local_files_only=True)
    raw = args.data.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    name, (ids, labels) = max(((row["id"], encode(tokenizer, row)) for row in rows),
                              key=lambda item: len(item[1][0]))
    x = torch.tensor([ids])
    y = torch.tensor([labels])
    base = load_text_model(use_cache=False)
    model = get_peft_model(base, LoraConfig(r=4, lora_alpha=8, lora_dropout=0,
                           target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM"))
    trainable = []
    for key, param in model.named_parameters():
        adapter = any(f".{proj}.lora_{side}.default.weight" in key
                      for proj in ("q_proj", "v_proj") for side in ("A", "B"))
        assert param.requires_grad == adapter
        if adapter:
            trainable.append(param)
    assert sum(p.numel() for p in trainable) == 1171456
    initial = [p.detach().clone() for p in trainable]
    frozen = base.get_input_embeddings().weight
    sample = frozen[:8].clone()
    optimizer = torch.optim.AdamW(trainable, lr=1e-4)
    model.train()
    start = time.perf_counter()
    loss = model(input_ids=x, labels=y, use_cache=False).loss
    assert torch.isfinite(loss)
    loss.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in trainable)
    assert all(p.grad is None for p in model.parameters() if not p.requires_grad)
    optimizer.step()
    seconds = time.perf_counter() - start
    assert all(torch.isfinite(p).all() for p in trainable)
    assert any(not torch.equal(p, old) for p, old in zip(trainable, initial))
    assert torch.equal(sample, frozen[:8])
    print("STEP", name, len(ids), loss.item(), seconds, flush=True)
    model.eval()
    with torch.inference_mode():
        reference = model(input_ids=x, logits_to_keep=1).logits.clone()
    # Stage on the same filesystem. Only promote after successful verification.
    args.output_parent.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(dir=args.output_parent) as tmp:
        stage = Path(tmp) / "adapter"
        model.save_pretrained(stage, safe_serialization=True, save_embedding_layers=False)
        base = model.unload()
        restored = PeftModel.from_pretrained(base, stage, is_trainable=False).eval()
        with torch.inference_mode():
            actual = restored(input_ids=x, logits_to_keep=1).logits
        assert torch.isfinite(actual).all() and torch.equal(actual, reference)
        assert not any(p.requires_grad for p in restored.parameters())
        assert (stage / "adapter_model.safetensors").stat().st_size < 5_000_000
        meta = dict(model=NAME, revision=REV, example=name, steps=1, seed=42,
                    trainable=1171456, optimizer="AdamW", lr=1e-4,
                    corpus_sha256=hashlib.sha256(raw).hexdigest(),
                    tokens_sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                    total=len(ids), supervised=len(ids)-labels.count(-100),
                    loss=loss.item(), step_seconds=seconds,
                    versions={p: version(p) for p in ("torch", "peft", "transformers", "safetensors")},
                    rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        (stage / "run.json").write_text(json.dumps(meta, indent=2) + "\n")
        dest = args.output_parent / ("step-" + Path(tmp).name)
        os.rename(stage, dest)
        print("SFT_STEP_OK", dest.name, json.dumps(meta), flush=True)


if __name__ == "__main__":
    main()
