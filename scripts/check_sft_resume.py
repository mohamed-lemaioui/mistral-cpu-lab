"""Check two-step checkpoint continuity and rejection paths on a tiny synthetic CPU model."""
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import torch
from safetensors.torch import load_file
from transformers import LlamaConfig, LlamaForCausalLM

from ministral_sft_epoch import prepare_plan, train


def tiny_base():
    torch.manual_seed(42)
    model = LlamaForCausalLM(LlamaConfig(vocab_size=32, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=2))
    model.requires_grad_(False)
    return model


def main():
    torch.set_num_threads(1)
    raw = b"\n".join(json.dumps({"id": f"fixture-{i}", "observations": f"observation {i}",
                                 "answer": f"answer {i}"}).encode() for i in range(100))
    fixture = {"fixture": "tiny"}

    def synthetic_encode(_, row):
        last = int(row["id"].split("-")[1]) % 27 + 4
        return [1, 2, 3, last], [-100, -100, 3, last]

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        with patch("ministral_sft_epoch.AutoTokenizer.from_pretrained"), \
             patch("ministral_sft_epoch.encode", side_effect=synthetic_encode):
            examples, signature = prepare_plan(raw, root, fixture)
        with patch("ministral_sft_epoch.encode", side_effect=AssertionError("plan re-rendered")):
            assert prepare_plan(raw, root, fixture) == (examples, signature)
        # Alter a token in an initial plan before any checkpoint exists.
        plan_path = root / "plan.json"
        altered = json.loads(plan_path.read_text())
        altered["examples"][0]["ids"][0] += 1
        plan_path.write_text(json.dumps(altered))
        try:
            prepare_plan(raw, root, fixture)
        except ValueError as exc:
            assert "integrity hash mismatch" in str(exc)
        else:
            raise AssertionError("Altered initial plan accepted")
        plan_path.unlink()
        with patch("ministral_sft_epoch.AutoTokenizer.from_pretrained"), \
             patch("ministral_sft_epoch.encode", side_effect=synthetic_encode):
            examples, signature = prepare_plan(raw, root, fixture)

        try:
            prepare_plan(raw, root, {"fixture": "other"})
        except ValueError as exc:
            assert "environment changed" in str(exc)
        else:
            raise AssertionError("Changed base fingerprint accepted")

        straight, split = root / "straight", root / "split"
        straight.mkdir()
        split.mkdir()
        train(tiny_base(), examples, straight, signature, None, 2, 256)
        train(tiny_base(), examples, split, signature, None, 1, 256)
        # Force the opposite ordering to exercise PEFT's unordered target modules.
        config_path = split / "step-001" / "adapter_config.json"
        config = json.loads(config_path.read_text())
        config["target_modules"] = ["v_proj", "q_proj"]
        config_path.write_text(json.dumps(config))
        meta_path = split / "step-001" / "run.json"
        meta = json.loads(meta_path.read_text())
        meta["sha256"]["adapter_config.json"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        meta_path.write_text(json.dumps(meta))
        train(tiny_base(), examples, split, signature, split / "step-001", 1, 256)
        a, b = [load_file(d / "step-002" / "adapter_model.safetensors") for d in (straight, split)]
        assert a.keys() == b.keys() and all(torch.equal(a[k], b[k]) for k in a)
        x, y = [torch.load(d / "step-002" / "state.pt", weights_only=True) for d in (straight, split)]
        assert torch.equal(x["rng"], y["rng"])
        assert x["optimizer"]["param_groups"] == y["optimizer"]["param_groups"]
        for k, state in x["optimizer"]["state"].items():
            assert all(torch.equal(v, y["optimizer"]["state"][k][name]) for name, v in state.items())

        # A damaged newest checkpoint must fail closed.
        (split / "step-002" / "state.pt").write_bytes(b"incomplete")
        try:
            train(tiny_base(), examples, split, signature, split / "step-002", 1, 256)
        except ValueError as exc:
            assert "Damaged checkpoint" in str(exc)
        else:
            raise AssertionError("Damaged checkpoint accepted")

        # A checkpoint from another model must be rejected before loading it.
        wrong_model = root / "wrong-model"
        wrong_model.mkdir()
        shutil.copytree(split / "step-001", wrong_model / "step-001")
        meta_path = wrong_model / "step-001" / "run.json"
        meta = json.loads(meta_path.read_text())
        meta["model"] = "other/model"
        meta_path.write_text(json.dumps(meta))
        try:
            train(tiny_base(), examples, wrong_model, signature, wrong_model / "step-001", 1, 256)
        except ValueError as exc:
            assert "model or revision" in str(exc)
        else:
            raise AssertionError("Wrong model checkpoint accepted")

        # A checkpoint whose adapter recipe differs must be rejected.
        wrong_adapter = root / "wrong-adapter"
        wrong_adapter.mkdir()
        shutil.copytree(split / "step-001", wrong_adapter / "step-001")
        config_path = wrong_adapter / "step-001" / "adapter_config.json"
        config = json.loads(config_path.read_text())
        config["r"] = 8
        config_path.write_text(json.dumps(config))
        meta_path = wrong_adapter / "step-001" / "run.json"
        meta = json.loads(meta_path.read_text())
        meta["sha256"]["adapter_config.json"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        meta_path.write_text(json.dumps(meta))
        try:
            train(tiny_base(), examples, wrong_adapter, signature,
                  wrong_adapter / "step-001", 1, 256)
        except ValueError as exc:
            assert "Adapter configuration" in str(exc)
        else:
            raise AssertionError("Wrong adapter recipe accepted")

    print("RESUME_OK exact adapters, AdamW state and RNG; corrupted, wrong-model and "
          "wrong-recipe checkpoints rejected")


if __name__ == "__main__":
    main()
