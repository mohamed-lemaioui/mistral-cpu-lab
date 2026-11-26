"""Controlled Instruct system-prompt comparison; no remote code."""
import argparse
import json
import resource
import time
from pathlib import Path

import torch
from accelerate import init_empty_weights
from huggingface_hub import hf_hub_download
from safetensors import safe_open
from transformers import AutoConfig, AutoTokenizer, Ministral3ForCausalLM

NAME = 'mistralai/Ministral-3-3B-Instruct-2512-BF16'
REV = 'ef287ce8b4b5f858eaf679e9d6402265beb8624f'
PREFIX = 'language_model.'


PROMPT = """Diagnostic Proxmox en français. Analyse uniquement les observations fournies. Propose des vérifications en lecture seule. Si les preuves sont insuffisantes, indique-le. Ne prétends pas avoir exécuté de commandes.
Observations : {observations}
Diagnostic :"""


def main():
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="JSONL file with id and observations, or - for stdin")
    parser.add_argument("--max-new-tokens", type=int, choices=[96, 256], default=96)
    parser.add_argument("--stream", action="store_true", help="Display generated text incrementally; disabled for timing benchmarks")
    parser.add_argument("--system", choices=["native", "concise"], required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in (sys.stdin if args.data == "-" else Path(args.data).read_text().splitlines()) if line.strip()]
    assert rows and len({r["id"] for r in rows}) == len(rows)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(42)
    dtype = torch.float32
    def fetch(f):
        return hf_hub_download(NAME, f, revision=REV, local_files_only=True)
    cfg = AutoConfig.from_pretrained(NAME, revision=REV, trust_remote_code=False,
                                     local_files_only=True).text_config
    cfg.use_cache = True
    tokenizer = AutoTokenizer.from_pretrained(NAME, revision=REV, trust_remote_code=False,
                                               local_files_only=True)
    index = json.loads(Path(fetch('model.safetensors.index.json')).read_text())['weight_map']
    mapping = {k: v for k, v in index.items() if k.startswith(PREFIX)}
    with init_empty_weights():
        base = Ministral3ForCausalLM(cfg)
    base.tie_weights()
    expected = set(base.state_dict())
    assert expected - {k[len(PREFIX):] for k in mapping} == {'lm_head.weight'}
    assert not ({k[len(PREFIX):] for k in mapping} - expected)
    assert len(mapping) == 236
    t = time.perf_counter()
    for shard in sorted(set(mapping.values())):
        print('SHARD', shard, flush=True)
        with safe_open(fetch(shard), framework='pt', device='cpu') as handle:
            for key in mapping:
                if mapping[key] != shard:
                    continue
                target = key[len(PREFIX):]
                tensor = handle.get_tensor(key)
                assert tensor.dtype == torch.bfloat16
                old = base.get_parameter(target)
                assert old.shape == tensor.shape and old.is_meta
                # BF16 uses mmap; FP32 converts one tensor at a time.
                tensor = tensor.to(dtype=dtype)
                parent, leaf = target.rsplit('.', 1)
                setattr(base.get_submodule(parent), leaf, torch.nn.Parameter(tensor, requires_grad=False))
    base.tie_weights()
    assert base.get_input_embeddings().weight is base.get_output_embeddings().weight
    assert not any(p.is_meta for p in base.parameters())
    assert sum(p.numel() for p in base.parameters()) == 3429006336
    print('LOADED', time.perf_counter()-t, 'RSS_MIB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024, flush=True)
    base.eval()
    assert not any(p.requires_grad for p in base.parameters())
    for row in rows:
        prompt = PROMPT.format(observations=row["observations"])
        messages = [{"role": "user", "content": prompt}]
        if args.system == "concise":
            messages.insert(0, {"role": "system", "content": "Tu es un assistant de diagnostic Proxmox."})
        inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt")
        print("PROMPT_MODE", args.system, row["id"], inputs["input_ids"].shape[1], flush=True)
        generation_kwargs = {}
        if args.stream:
            from transformers import TextStreamer
            print("STREAM_BEGIN", row["id"], flush=True)
            generation_kwargs["streamer"] = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        t = time.perf_counter()
        with torch.inference_mode():
            output = base.generate(**inputs, do_sample=False, max_new_tokens=args.max_new_tokens, use_cache=True,
                                   pad_token_id=tokenizer.eos_token_id, **generation_kwargs)
        elapsed = time.perf_counter()-t
        if args.stream:
            print("STREAM_END", row["id"], flush=True)
        new = output[0, inputs["input_ids"].shape[1]:]
        print("RESULT", json.dumps(dict(id=row["id"], prompt=prompt,
              system_mode=args.system, answer=tokenizer.decode(new, skip_special_tokens=True),
              generated_tokens=len(new), max_new_tokens=args.max_new_tokens,
              prompt_tokens=inputs["input_ids"].shape[1], reached_cap=len(new)==args.max_new_tokens, seconds=elapsed,
              rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),
              ensure_ascii=False), flush=True)
    print("BASELINE_OK", len(rows), flush=True)


if __name__ == "__main__":
    main()
