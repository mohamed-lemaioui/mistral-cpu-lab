# Experimental report — 2026-11-25

## Hardware and software

Legacy dual Intel Xeon E5-2620, 12 physical cores / 24 hardware threads, AVX without AVX2 or FMA, no AI accelerator. Linux container with 8 vCPUs and initially 16 GiB memory, later increased to 32 GiB for planned Ministral tests. The reported Ministral probes use four threads. Python 3.13.5, PyTorch 2.15.0+cpu, Transformers 5.24.1, PEFT 0.22.0, Accelerate 1.16.0, Safetensors 0.8.0, NumPy 2.5.5.

## Ministral feasibility

Upstream: https://huggingface.co/mistralai/Ministral-3-3B-Base-2512 — revision 6f9c4b12a95b139af68670a6713616b757923735. The official index has 236 language tensors, 218 vision tensors and four projector tensors. Language keys map to Ministral3ForCausalLM after prefix removal; lm_head.weight is tied to input embeddings. Unique text parameter count after tying: 3,429,006,336 (approximately 12.77 GiB in FP32, 6.39 GiB in BF16). The stored multimodal checkpoint has 3,849,090,048 BF16 values. Text-only loading excludes vision weights, but both original shards are required.

Miniature random Ministral: two layers, hidden size 64, vocabulary 256, 32 tokens. FP32 and BF16 forward/backward/AdamW completed with finite LoRA gradients. Initial test failed after removing model-specific RoPE fields; retaining official RoPE configuration resolved it. A synthetic mmap loading check initially differed from a reference cast globally to BF16; preserving FP32 rotary buffers produced exact logits against an assign-based reference. Full checkpoint equivalence remains untested.

A single representative matrix multiplication (32x3072 by 3072x9216), frozen weights, forward/backward with four threads, took 0.13292 s FP32 and 10.83084 s BF16. Both gradients were finite. This was a single trial without warm-up and is not a full-model benchmark. It motivates FP32 on this hardware, not a general claim about BF16.

Both official checkpoint shards were downloaded and checked against published SHA-256 metadata. A full-size text-only FP32 optimizer step has now been validated; domain training remains untested.

## First pretrained Ministral LoRA step — 2026-11-25

Pinned official checkpoint, local cache, text-only FP32, 32 synthetic tokens, batch 1, four threads, seed 42, LoRA r=4 alpha=8 on q_proj/v_proj, AdamW learning rate 1e-4. Model loading 4.17055033 s; forward 4.509849208 s; complete optimizer step 8.713357601 s; initial loss 3.882768154144287, post-update loss on the same sequence 3.808133602142334; peak process RSS 16216.359375 MiB. 1,171,456 trainable parameters. Finite gradients, adapter update and frozen embedding sample checks passed; process exit code 0. A temporary systemd unit enforced 26 GiB memory, no swap, CPU quota 400%, nice 10 and 600 s runtime limit. No container OOM events or swap use observed. One trial, no persisted adapter, no held-out evaluation. The 32 GiB container quota is not a measured minimum. Full checkpoint logits equivalence has not been tested.

## Reconstructed intermediate experiments

All five standalone reconstructions passed on 2026-11-25. See the [reproduction guide](reproduction.md) for commands, provenance, separate rerun measurements and limitations. Historical measurements remain unchanged.
