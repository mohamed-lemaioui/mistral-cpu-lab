"""Reconstructed synthetic check of mmap assignment versus state-dict assignment."""
import tempfile
from pathlib import Path
import torch
from accelerate import init_empty_weights
from safetensors import safe_open
from safetensors.torch import save_file
from transformers import AutoConfig, Ministral3ForCausalLM
torch.set_num_threads(4)
torch.manual_seed(42)
cfg = AutoConfig.from_pretrained("mistralai/Ministral-3-3B-Base-2512",revision="6f9c4b12a95b139af68670a6713616b757923735",local_files_only=True).text_config
cfg.num_hidden_layers=2
cfg.hidden_size=64
cfg.intermediate_size=128
cfg.num_attention_heads=4
cfg.num_key_value_heads=2
cfg.head_dim=16
cfg.vocab_size=256
cfg.pad_token_id=None
cfg.bos_token_id=1
cfg.eos_token_id=2
cfg.use_cache=False
if getattr(cfg,"layer_types",None):
    cfg.layer_types=cfg.layer_types[:2]
source=Ministral3ForCausalLM(cfg)
weights={k:p.detach().to(torch.bfloat16).contiguous() for k,p in source.named_parameters()}
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/"synthetic.safetensors"
    save_file(weights,path)
    reference=Ministral3ForCausalLM(cfg)
    reference.load_state_dict(weights,strict=False,assign=True)
    reference.tie_weights()
    with init_empty_weights():
        loaded=Ministral3ForCausalLM(cfg)
    with safe_open(path,framework="pt",device="cpu") as handle:
        for key in handle.keys():
            parent,leaf=key.rsplit(".",1)
            setattr(loaded.get_submodule(parent),leaf,torch.nn.Parameter(handle.get_tensor(key),requires_grad=False))
    loaded.tie_weights()
    assert not any(p.is_meta for p in loaded.parameters())
    for (k,a),(j,b) in zip(reference.named_parameters(),loaded.named_parameters()):
        assert k==j and torch.equal(a,b)
    for (k,a),(j,b) in zip(reference.named_buffers(),loaded.named_buffers()):
        assert k==j and torch.equal(a,b)
    x=torch.randint(0,256,(1,32))
    with torch.no_grad():
        a=reference.eval()(input_ids=x).logits
        b=loaded.eval()(input_ids=x).logits
    assert torch.equal(a,b)
    print("MMAP_EQUIVALENCE_OK max_abs", (a-b).abs().max().item(),flush=True)
