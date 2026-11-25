import json, time, resource, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
torch.set_num_threads(4)
torch.set_num_interop_threads(1)
torch.manual_seed(42)
name='Qwen/Qwen3-0.6B'
t=time.perf_counter()
tokenizer=AutoTokenizer.from_pretrained(name,trust_remote_code=False)
model=AutoModelForCausalLM.from_pretrained(name,dtype=torch.float32,trust_remote_code=False)
print('MODEL_LOADED',round(time.perf_counter()-t,3),'revision',getattr(model.config,'_commit_hash',None),flush=True)
model.config.use_cache=False
model=get_peft_model(model,LoraConfig(r=4,lora_alpha=8,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
params=sum(p.numel() for p in model.parameters()); trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
text='Diagnostic synthétique : un conteneur de laboratoire est arrêté. Vérifier son état avant de proposer une action.'
x=tokenizer(text,return_tensors='pt',truncation=True,max_length=64)['input_ids']
opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=1e-4)
model.train(); losses=[]; timings=[]
for step in range(3):
    t=time.perf_counter(); opt.zero_grad(); loss=model(input_ids=x,labels=x,use_cache=False).loss; loss.backward(); opt.step(); losses.append(loss.item()); timings.append(time.perf_counter()-t)
    print('STEP',step+1,'loss',losses[-1],'seconds',timings[-1],flush=True)
assert all(torch.isfinite(torch.tensor(losses)))
print(json.dumps(dict(model=name,parameters=params,trainable=trainable,tokens=x.numel(),steps=3,threads=4,losses=losses,step_seconds=timings,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),indent=2),flush=True)
print('PRETRAINED_LORA_CPU_OK',flush=True)
