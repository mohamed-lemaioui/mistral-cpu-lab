"""Reconstructed miniature architecture test; randomly initialized weights."""
import json
import time
import torch
from transformers import AutoConfig, Ministral3ForCausalLM
from peft import LoraConfig, get_peft_model
torch.set_num_threads(4)
torch.set_num_interop_threads(1)
for dtype in (torch.float32, torch.bfloat16):
    torch.manual_seed(42)
    cfg = AutoConfig.from_pretrained("mistralai/Ministral-3-3B-Base-2512", revision="6f9c4b12a95b139af68670a6713616b757923735", local_files_only=True).text_config
    cfg.num_hidden_layers = 2
    cfg.hidden_size = 64
    cfg.intermediate_size = 128
    cfg.num_attention_heads = 4
    cfg.num_key_value_heads = 2
    cfg.head_dim = 16
    cfg.vocab_size = 256
    cfg.use_cache = False
    cfg.pad_token_id = None
    cfg.bos_token_id = 1
    cfg.eos_token_id = 2
    if getattr(cfg, "layer_types", None):
        cfg.layer_types = cfg.layer_types[:2]
    model = get_peft_model(Ministral3ForCausalLM(cfg).to(dtype), LoraConfig(r=4,lora_alpha=8,target_modules=["q_proj","v_proj"],task_type="CAUSAL_LM"))
    x = torch.randint(0,256,(1,32))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params,lr=1e-4)
    t = time.perf_counter()
    loss = model(input_ids=x,labels=x).loss
    loss.backward()
    assert torch.isfinite(loss)
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in params)
    opt.step()
    print(json.dumps(dict(dtype=str(dtype),loss=loss.item(),seconds=time.perf_counter()-t,finite_gradients=True)),flush=True)
