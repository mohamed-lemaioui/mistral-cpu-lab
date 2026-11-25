"""Reconstructed offline SHA-256 verification of the pinned checkpoint."""
import hashlib
from huggingface_hub import hf_hub_download
NAME = "mistralai/Ministral-3-3B-Base-2512"
REV = "6f9c4b12a95b139af68670a6713616b757923735"
EXPECTED = [
    "0494c0a285767920a5e469af9710b499115667f84e17c225a956a5155459249f",
    "3cd41d76f1d8e7b2fa64668d69177358dffdbd15231ccf6177798bca9de1a797",
]
for i, expected in enumerate(EXPECTED, 1):
    name = f"model-{i:05d}-of-00002.safetensors"
    with open(hf_hub_download(NAME, name, revision=REV, local_files_only=True), "rb") as f:
        actual = hashlib.file_digest(f, "sha256").hexdigest()
    if actual != expected:
        raise ValueError(f"{name}: SHA-256 mismatch")
    print(name, actual, "OK", flush=True)
