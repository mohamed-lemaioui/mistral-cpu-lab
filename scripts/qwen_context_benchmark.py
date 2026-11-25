import json, time, resource, sys, statistics
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
n=int(sys.argv[1])
assert n in (128,256)
torch.set_num_threads(4); torch.set_num_interop_threads(1); torch.manual_seed(42)
name='Qwen/Qwen3-0.6B'; revision='c1899de289a04d12100db370d81485cdf75e47ca'
t=time.perf_counter()
tokenizer=AutoTokenizer.from_pretrained(name,revision=revision,local_files_only=True,trust_remote_code=False)
base=AutoModelForCausalLM.from_pretrained(name,revision=revision,local_files_only=True,dtype=torch.float32,trust_remote_code=False)
base.config.use_cache=False
model=get_peft_model(base,LoraConfig(r=4,lora_alpha=8,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
text='Diagnostic de laboratoire : vérifier l’état du conteneur, les ressources et le stockage. Les observations doivent provenir des outils. Si une information manque, signaler cette limite. '
ids=tokenizer(text*(n//8+1),add_special_tokens=False)['input_ids'][:n]
assert len(ids)==n
x=torch.tensor([ids]); opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=1e-4)
model.train(); losses=[]; timings=[]
for step in range(3):
    t=time.perf_counter(); opt.zero_grad(); loss=model(input_ids=x,labels=x,use_cache=False).loss; loss.backward(); opt.step(); losses.append(loss.item()); timings.append(time.perf_counter()-t)
    print('STEP',step+1,'tokens',n,'loss',losses[-1],'seconds',timings[-1],flush=True)
assert torch.isfinite(torch.tensor(losses)).all()
print(json.dumps(dict(model=name,revision=revision,tokens=n,threads=4,steps=3,losses=losses,step_seconds=timings,mean_seconds=statistics.mean(timings),peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)),flush=True)
print('CONTEXT_LENGTH_OK',n,flush=True)
