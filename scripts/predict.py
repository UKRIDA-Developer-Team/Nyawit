"""Inferensi dari baris perintah (cadangan teknis bila demo Gradio bermasalah).

Contoh:
    python scripts/predict.py --image foto_sawit.jpg
    python scripts/predict.py --image folder_foto/ --gradcam hasil_gradcam/ --json hasil.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image  # noqa: E402

from sawit.predict import Predictor  # noqa: E402
from sawit.utils import resolve_path, to_serializable  # noqa: E402

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Prediksi tingkat kematangan buah sawit.")
    parser.add_argument("--checkpoint", default="outputs/runs/e3_cnn_corn/seed42/best.pt")
    parser.add_argument("--image", required=True, help="Berkas gambar atau folder berisi gambar.")
    parser.add_argument("--gradcam", default=None, help="Folder untuk menyimpan overlay Grad-CAM.")
    parser.add_argument("--json", default=None, help="Simpan hasil ke berkas JSON.")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    predictor = Predictor(resolve_path(args.checkpoint), device=args.device)
    target = Path(args.image).expanduser()
    paths = sorted(p for p in target.iterdir() if p.suffix.lower() in EXTENSIONS) if target.is_dir() else [target]
    if not paths:
        raise SystemExit(f"Tidak ada gambar di {target}")

    results = []
    print(f"Model: {predictor.experiment_name} ({predictor.device})")
    print(f"{'Berkas':<32} {'Prediksi':<16} {'Keyakinan':>9} {'Nilai harapan':>13} {'Latensi':>9}")
    for path in paths:
        with Image.open(path) as img:
            image = img.convert("RGB")
        out = predictor.predict(image)
        out["file"] = str(path)
        results.append(out)
        warn = "  (keyakinan rendah, periksa manual)" if out["low_confidence"] else ""
        print(f"{path.name[:32]:<32} {out['pred_name']:<16} {out['confidence']:>9.3f} "
              f"{out['expected_level']:>13.2f} {out['latency_ms']:>7.1f}ms{warn}")
        if args.gradcam:
            gdir = Path(args.gradcam)
            gdir.mkdir(parents=True, exist_ok=True)
            predictor.gradcam(image).save(gdir / f"{path.stem}_gradcam.png")

    if args.json:
        Path(args.json).write_text(json.dumps(to_serializable(results), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Hasil JSON: {args.json}")


if __name__ == "__main__":
    main()
