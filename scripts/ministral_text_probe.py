"""Pinned text-only BF16/FP32 loader and CPU LoRA probe; no remote code."""
import argparse
import json
import resource
import time
from pathlib import Path

import torch
from accelerate import init_empty_weights
from huggingface_hub import hf_hub_download
from peft import LoraConfig, get_peft_model
from safetensors import safe_open
from transformers import AutoConfig, AutoTokenizer, Ministral3ForCausalLM

NAME = 'mistralai/Ministral-3-3B-Base-2512'
REV = '6f9c4b12a95b139af68670a6713616b757923735'
PREFIX = 'language_model.'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dtype', choices=['fp32', 'bf16'], default='fp32')
    parser.add_argument('--download', action='store_true', help='Permit downloading pinned shards')
    parser.add_argument('--tokens', type=int, default=32, choices=[32, 128, 256])
    parser.add_argument("--steps", type=int, choices=[1, 3], default=1)
    args = parser.parse_args()
    dtype = torch.float32 if args.dtype == 'fp32' else torch.bfloat16
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(42)
    def fetch(f):
        return hf_hub_download(NAME, f, revision=REV, local_files_only=not args.download)
    cfg = AutoConfig.from_pretrained(NAME, revision=REV, trust_remote_code=False,
                                     local_files_only=not args.download).text_config
    cfg.use_cache = False
    tokenizer = AutoTokenizer.from_pretrained(NAME, revision=REV, trust_remote_code=False,
                                               local_files_only=not args.download)
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
    model = get_peft_model(base, LoraConfig(r=4,lora_alpha=8,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    text = 'Diagnostic de laboratoire : vérifier les ressources du conteneur et le stockage. Les observations doivent provenir des outils. '
    ids = tokenizer(text*(args.tokens//8+1), add_special_tokens=False)['input_ids'][:args.tokens]
    assert len(ids) == args.tokens
    x = torch.tensor([ids])
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=1e-4)
    assert sum(p.numel() for p in trainable) == 1171456
    before = [p.detach().clone() for p in trainable]
    frozen = base.get_input_embeddings().weight
    assert not frozen.requires_grad
    frozen_before = frozen.detach()[:8].clone()
    model.train()
    step_times = []
    losses = []
    for step in range(args.steps):
        optimizer.zero_grad(set_to_none=True)
        t = time.perf_counter()
        loss = model(input_ids=x, labels=x, use_cache=False).loss
        forward_seconds = time.perf_counter()-t
        loss.backward()
        assert torch.isfinite(loss).item()
        assert all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in trainable)
        optimizer.step()
        elapsed = time.perf_counter()-t
        step_times.append(elapsed)
        losses.append(loss.item())
        print('STEP', json.dumps(dict(step=step+1, seconds=elapsed, forward_seconds=forward_seconds, loss=loss.item())), flush=True)
    assert any(not torch.equal(p.detach(), b) for p,b in zip(trainable,before))
    assert frozen.grad is None and torch.equal(frozen.detach()[:8], frozen_before)
    with torch.no_grad():
        after = model(input_ids=x, labels=x, use_cache=False).loss.item()
    assert torch.isfinite(torch.tensor(after)).item()
    print('ADAPTER_UPDATE_OK', 'FROZEN_EMBEDDING_SAMPLE_OK', flush=True)
    print('LOSS_AFTER', after, flush=True)
    print('MINISTRAL_PRETRAINED_STEP_OK', json.dumps({'dtype':args.dtype,'tokens':args.tokens,'steps':args.steps,'seconds':sum(step_times)/len(step_times),'step_seconds':step_times,'loss':losses[0],'step_losses':losses,'loss_after':after,'trainable':sum(p.numel() for p in trainable),'rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}),flush=True)

if __name__ == '__main__':
    main()
