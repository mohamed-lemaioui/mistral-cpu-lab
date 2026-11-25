# Experimental report — 2026-11-25

## Hardware and software

Legacy dual Intel Xeon E5-2620, 12 physical cores / 24 hardware threads, AVX without AVX2 or FMA, no AI accelerator. Linux container with 8 vCPUs and initially 16 GiB memory, later increased to 32 GiB for planned Ministral tests. All reported training benchmarks use four threads. Python 3.13.5, PyTorch 2.15.0+cpu, Transformers 5.24.1, PEFT 0.22.0, Accelerate 1.16.0, Safetensors 0.8.0, NumPy 2.5.5.

## Qwen3 baseline

A randomly initialized miniature Qwen3 model (84,096 total parameters, 1,792 trainable) completed 20 LoRA optimizer steps in 0.346 s; loss fell from 4.10765 to 3.32689. A sampled frozen parameter remained unchanged, adapters changed, and reloaded logits matched within tolerance.

Pretrained Qwen/Qwen3-0.6B: 596,623,360 parameters including 573,440 trainable; LoRA r=4, alpha=8, q_proj/v_proj, AdamW learning rate 1e-4, FP32. Observed checkpoint revision c1899de289a04d12100db370d81485cdf75e47ca. The first 29-token run did not explicitly pin the revision. The later 128/256-token runs did. Each run repeated one synthetic sequence three times. Timings and losses are in the CSV. Losses across different sequences are not directly comparable. RSS is process peak, not container-wide memory.

## Ministral feasibility

Upstream: https://huggingface.co/mistralai/Ministral-3-3B-Base-2512 — revision 6f9c4b12a95b139af68670a6713616b757923735. The official index has 236 language tensors, 218 vision tensors and four projector tensors. Language keys map to Ministral3ForCausalLM after prefix removal; lm_head.weight is tied to input embeddings. Unique text parameter count after tying: 3,429,006,336 (approximately 12.77 GiB in FP32, 6.39 GiB in BF16). The stored multimodal checkpoint has 3,849,090,048 BF16 values. Text-only loading excludes vision weights, but both original shards are required.

Miniature random Ministral: two layers, hidden size 64, vocabulary 256, 32 tokens. FP32 and BF16 forward/backward/AdamW completed with finite LoRA gradients. Initial test failed after removing model-specific RoPE fields; retaining official RoPE configuration resolved it. A synthetic mmap loading check initially differed from a reference cast globally to BF16; preserving FP32 rotary buffers produced exact logits against an assign-based reference. Full checkpoint equivalence remains untested.

A single representative matrix multiplication (32x3072 by 3072x9216), frozen weights, forward/backward with four threads, took 0.13292 s FP32 and 10.83084 s BF16. Both gradients were finite. This was a single trial without warm-up and is not a full-model benchmark. It motivates FP32 on this hardware, not a general claim about BF16.

Both official checkpoint shards were downloaded and checked against published SHA-256 metadata. Full pretrained Ministral training has not yet been validated. The experimental loader is included for review; its latest changes have only been syntax checked.
