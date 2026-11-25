"""Inspect native prompt length and text configurations without loading weights."""
from transformers import AutoTokenizer, AutoConfig
import json

MODELS = [
    ("Base", "mistralai/Ministral-3-3B-Base-2512", "6f9c4b12a95b139af68670a6713616b757923735"),
    ("Instruct", "mistralai/Ministral-3-3B-Instruct-2512-BF16", "ef287ce8b4b5f858eaf679e9d6402265beb8624f"),
]
PROMPT = """Diagnostic Proxmox en français. Analyse uniquement les observations fournies. Propose des vérifications en lecture seule. Si les preuves sont insuffisantes, indique-le. Ne prétends pas avoir exécuté de commandes.
Observations : df -h /: 35%; df -i /: 100%; touch: No space left on device
Diagnostic :"""
def main():
    configs = []
    for label, name, rev in MODELS:
        tok = AutoTokenizer.from_pretrained(name, revision=rev, local_files_only=True, trust_remote_code=False)
        configs.append(AutoConfig.from_pretrained(name, revision=rev, local_files_only=True, trust_remote_code=False).text_config.to_dict())
        if label == "Instruct":
            messages = [{"role": "user", "content": PROMPT}]
            ids = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True)["input_ids"]
        else:
            ids = tok(PROMPT)["input_ids"]
        print(label, "PROMPT_TOKENS", len(ids), flush=True)
    a, b = configs
    print("CONFIG_DIFF", json.dumps({k: [a.get(k), b.get(k)] for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)}, default=str))
if __name__ == "__main__":
    main()
