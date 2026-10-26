"""Mengukur latensi inferensi, ukuran model, dan jumlah parameter (CP12).

Prosedur ukur (dicatat agar konsisten antar perangkat):
- input 1 gambar (batch 1), ukuran sesuai konfigurasi (224x224);
- 10 iterasi pemanasan tidak dihitung, lalu 100 iterasi diukur;
- dilaporkan median dan persentil-90 (ms) serta FPS = 1000 / median;
- hanya forward pass model (pra-pemrosesan diukur terpisah).

Contoh:
    python scripts/benchmark_latency.py --checkpoint outputs/runs/e3_cnn_corn/seed42/best.pt --device cpu
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402

from sawit.models import count_parameters  # noqa: E402
from sawit.predict import Predictor  # noqa: E402
from sawit.utils import environment_info, resolve_path, save_json  # noqa: E402


def time_it(fn, device: torch.device, warmup: int, runs: int) -> np.ndarray:
    for _ in range(warmup):
        fn()
    times = []
    for _ in range(runs):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        fn()
        if device.type == "cuda":
            torch.cuda.synchronize()
        times.append((time.perf_counter() - t0) * 1000)
    return np.array(times)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark latensi model.")
    parser.add_argument("--checkpoint", default="outputs/runs/e3_cnn_corn/seed42/best.pt")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--threads", type=int, default=None, help="Jumlah thread CPU (default: bawaan PyTorch)")
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--out", default="results/latensi")
    args = parser.parse_args()

    if args.threads:
        torch.set_num_threads(args.threads)
    ckpt_path = resolve_path(args.checkpoint)
    predictor = Predictor(ckpt_path, device=args.device)
    size = int(predictor.config["data"]["image_size"])
    image = Image.fromarray(np.random.default_rng(0).integers(0, 255, (480, 640, 3), dtype=np.uint8))
    x = predictor.preprocess(image)

    with torch.no_grad():
        model_ms = time_it(lambda: predictor.model(x), predictor.device, args.warmup, args.runs)
    pre_ms = time_it(lambda: predictor.preprocess(image), predictor.device, 3, 30)

    result = {
        "checkpoint": str(ckpt_path),
        "experiment": predictor.experiment_name,
        "backbone": predictor.backbone,
        "head": predictor.head,
        "input_size": f"1x3x{size}x{size}",
        "device": str(predictor.device),
        "torch_threads": torch.get_num_threads(),
        "parameters": count_parameters(predictor.model),
        "checkpoint_mb": ckpt_path.stat().st_size / 1e6,
        "model_ms_median": float(np.median(model_ms)),
        "model_ms_p90": float(np.percentile(model_ms, 90)),
        "fps_model": float(1000 / np.median(model_ms)),
        "preprocess_ms_median": float(np.median(pre_ms)),
        "warmup": args.warmup,
        "runs": args.runs,
        "environment": environment_info(predictor.device),
    }
    out = resolve_path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tag = f"{predictor.experiment_name}_{predictor.device.type}"
    save_json(result, out / f"latensi_{tag}.json")
    md = [f"### Latensi {predictor.experiment_name} ({predictor.device})", "",
          "| Parameter | Ukuran checkpoint | Median (ms) | P90 (ms) | FPS | Pra-pemrosesan (ms) | Perangkat |",
          "|---|---|---|---|---|---|---|",
          f"| {result['parameters'] / 1e6:.2f} M | {result['checkpoint_mb']:.1f} MB | {result['model_ms_median']:.1f} | "
          f"{result['model_ms_p90']:.1f} | {result['fps_model']:.1f} | {result['preprocess_ms_median']:.1f} | "
          f"{result['environment'].get('gpu', result['environment']['platform'])}, {result['torch_threads']} thread |", "",
          f"Prosedur: batch 1, input {result['input_size']}, {args.warmup} iterasi pemanasan, "
          f"{args.runs} iterasi diukur, forward pass saja.", ""]
    (out / f"latensi_{tag}.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
