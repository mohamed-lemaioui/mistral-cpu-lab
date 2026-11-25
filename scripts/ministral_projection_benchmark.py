"""Reconstructed single-trial projection benchmark, random tensors, no warmup."""
import json
import time
import torch
torch.set_num_threads(4)
torch.set_num_interop_threads(1)
for dtype in (torch.float32, torch.bfloat16):
    torch.manual_seed(42)
    w = torch.randn(9216, 3072, dtype=dtype)
    x = torch.randn(32, 3072, dtype=dtype, requires_grad=True)
    t = time.perf_counter()
    loss = (x @ w.T).float().square().mean()
    loss.backward()
    elapsed = time.perf_counter() - t
    finite = bool(torch.isfinite(x.grad).all())
    assert finite
    print(json.dumps(dict(dtype=str(dtype), seconds=elapsed, finite_input_gradient=finite)), flush=True)
