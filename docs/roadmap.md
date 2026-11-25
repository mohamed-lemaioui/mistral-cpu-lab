# Roadmap

- [x] Validate full pretrained Ministral text-only FP32 loading and one LoRA update.
- [x] Measure 128/256-token sequences, three optimizer steps per length, record process RSS.
- Repeat independent trials and capture final cgroup peak memory.
- Build a synthetic systems-diagnostic dataset with independent train/validation/test splits.
- Compare baseline and adapted model on held-out tasks, factual accuracy and abstention.
- Evaluate CPU inference and quantization; publish reproducible adapter and dataset cards when validated.
- Share tutorials and consider upstream contributions.
