"""Reconstructed architecture and checkpoint index checks; offline by default."""
import json
from collections import Counter
from pathlib import Path
from accelerate import init_empty_weights
from huggingface_hub import hf_hub_download
from transformers import AutoConfig, AutoTokenizer, Ministral3ForCausalLM
from peft import LoraConfig, get_peft_model
NAME = "mistralai/Ministral-3-3B-Base-2512"
REV = "6f9c4b12a95b139af68670a6713616b757923735"
cfg = AutoConfig.from_pretrained(NAME, revision=REV, local_files_only=True).text_config
with init_empty_weights():
    model = Ministral3ForCausalLM(cfg)
model.tie_weights()
index = json.loads(Path(hf_hub_download(NAME, "model.safetensors.index.json", revision=REV, local_files_only=True)).read_text())
keys = index["weight_map"]
counts = Counter(k.split(".")[0] for k in keys)
text = {k.removeprefix("language_model.") for k in keys if k.startswith("language_model.")}
assert set(model.state_dict()) - text == {"lm_head.weight"}
assert not text - set(model.state_dict())
n = sum(p.numel() for p in model.parameters())
assert n == 3429006336
model = get_peft_model(model, LoraConfig(r=4, lora_alpha=8, target_modules=["q_proj","v_proj"], task_type="CAUSAL_LM"))
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
assert trainable == 1171456
tok = AutoTokenizer.from_pretrained(NAME, revision=REV, local_files_only=True)
print(json.dumps(dict(tensors=dict(counts), text_parameters=n, fp32_gib=n*4/2**30, bf16_gib=n*2/2**30, trainable=trainable, vocab=tok.vocab_size, stored_bytes=index["metadata"]["total_size"]), sort_keys=True))
