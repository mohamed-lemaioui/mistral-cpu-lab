"""Download only the pinned official BF16 Transformers checkpoint, verify SHA256."""
import hashlib
from huggingface_hub import hf_hub_download
NAME="mistralai/Ministral-3-3B-Instruct-2512-BF16"
REV="ef287ce8b4b5f858eaf679e9d6402265beb8624f"
for name in ("config.json","generation_config.json","tokenizer.json","tokenizer_config.json","special_tokens_map.json","chat_template.jinja","model.safetensors.index.json"):
    hf_hub_download(NAME,name,revision=REV)
for name,sha in [
    ("model-00001-of-00002.safetensors","b3821ebc30884f66e3d26d339e161641f34b91ed916627011e7b08e5f1edd884"),
    ("model-00002-of-00002.safetensors","718d087fa591fd4356b7241f293c24219399d86f092d46cf36f765051498033a")]:
    path=hf_hub_download(NAME,name,revision=REV)
    with open(path,"rb") as f:
        assert hashlib.file_digest(f,"sha256").hexdigest()==sha
    print(name,sha,"OK",flush=True)
print("INSTRUCT_DOWNLOAD_VERIFIED",flush=True)
