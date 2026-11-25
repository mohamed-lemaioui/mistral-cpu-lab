import tempfile, time, resource, json
import torch
from transformers import Qwen3Config, Qwen3ForCausalLM
from peft import LoraConfig, get_peft_model, PeftModel
torch.set_num_threads(4)
torch.set_num_interop_threads(1)
torch.manual_seed(42)
cfg=Qwen3Config(vocab_size=64, hidden_size=64, intermediate_size=128, num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, head_dim=16, max_position_embeddings=128, pad_token_id=0, bos_token_id=1, eos_token_id=2)
base=Qwen3ForCausalLM(cfg)
model=get_peft_model(base,LoraConfig(r=4,lora_alpha=8,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
trainable=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
assert trainable and all('lora_' in n for n,p in trainable)
frozen=next((p for n,p in model.named_parameters() if not p.requires_grad))
frozen_before=frozen.detach().clone()
before={n:p.detach().clone() for n,p in trainable}
x=torch.tensor([[1,3,4,5,6,7,8,2],[1,3,4,5,6,7,8,2]])
opt=torch.optim.AdamW([p for n,p in trainable],lr=0.02)
model.train(); losses=[]; t=time.perf_counter()
for step in range(20):
    opt.zero_grad(); loss=model(input_ids=x,labels=x,use_cache=False).loss; loss.backward(); opt.step(); losses.append(loss.item())
elapsed=time.perf_counter()-t
assert torch.equal(frozen,frozen_before)
assert any(not torch.equal(p,before[n]) for n,p in trainable)
assert losses[-1]<losses[0], losses
model.eval()
with torch.no_grad(): expected=model(input_ids=x,use_cache=False).logits
with tempfile.TemporaryDirectory() as d:
    model.save_pretrained(d)
    torch.manual_seed(42); restored=PeftModel.from_pretrained(Qwen3ForCausalLM(cfg),d).eval()
    with torch.no_grad(): actual=restored(input_ids=x,use_cache=False).logits
    assert torch.allclose(expected,actual,atol=1e-5,rtol=1e-5)
print(json.dumps(dict(base_arch='Qwen3 synthetic random initialization',parameters=sum(p.numel() for p in model.parameters()),trainable=sum(p.numel() for n,p in trainable),steps=20,threads=4,initial_loss=losses[0],final_loss=losses[-1],seconds=elapsed,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,adapter_reload='OK',frozen_weight_check='OK'),indent=2))
print('LORA_CPU_OK')
