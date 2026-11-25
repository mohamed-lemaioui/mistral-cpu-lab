# Experimental report — 2026-11-25

## Hardware and software

Legacy dual Intel Xeon E5-2620, 12 physical cores / 24 hardware threads, AVX without AVX2 or FMA, no AI accelerator. Linux container with 8 vCPUs and initially 16 GiB memory, later increased to 32 GiB for planned Ministral tests. The reported Ministral probes use four threads. Python 3.13.5, PyTorch 2.15.0+cpu, Transformers 5.24.1, PEFT 0.22.0, Accelerate 1.16.0, Safetensors 0.8.0, NumPy 2.5.5.

## Ministral feasibility

Upstream: https://huggingface.co/mistralai/Ministral-3-3B-Base-2512 — revision 6f9c4b12a95b139af68670a6713616b757923735. The official index has 236 language tensors, 218 vision tensors and four projector tensors. Language keys map to Ministral3ForCausalLM after prefix removal; lm_head.weight is tied to input embeddings. Unique text parameter count after tying: 3,429,006,336 (approximately 12.77 GiB in FP32, 6.39 GiB in BF16). The stored multimodal checkpoint has 3,849,090,048 BF16 values. Text-only loading excludes vision weights, but both original shards are required.

Miniature random Ministral: two layers, hidden size 64, vocabulary 256, 32 tokens. FP32 and BF16 forward/backward/AdamW completed with finite LoRA gradients. Initial test failed after removing model-specific RoPE fields; retaining official RoPE configuration resolved it. A synthetic mmap loading check initially differed from a reference cast globally to BF16; preserving FP32 rotary buffers produced exact logits against an assign-based reference. Full checkpoint equivalence remains untested.

A single representative matrix multiplication (32x3072 by 3072x9216), frozen weights, forward/backward with four threads, took 0.13292 s FP32 and 10.83084 s BF16. Both gradients were finite. This was a single trial without warm-up and is not a full-model benchmark. It motivates FP32 on this hardware, not a general claim about BF16.

Both official checkpoint shards were downloaded and checked against published SHA-256 metadata. Full pretrained Ministral training has not yet been validated. The experimental loader is included for review; its latest changes have only been syntax checked.
