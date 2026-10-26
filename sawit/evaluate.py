"""Evaluasi ulang checkpoint pada split tertentu tanpa melatih ulang.

Contoh:
    python -m sawit.evaluate --run-dir outputs/runs/e3_cnn_corn/seed42 --split test
    python -m sawit.evaluate --run-dir outputs/runs/e3_cnn_corn/seed42 --split test --subset clean
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from .constants import NUM_CLASSES
from .data import load_metadata, make_loaders
from .engine import predict_loader, predictions_table
from .metrics import compute_metrics
from .models import build_model, num_outputs_for
from .plots import plot_confusion
from .utils import get_device, resolve_path, save_json


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Evaluasi ulang checkpoint.")
    parser.add_argument("--run-dir", required=True, help="Folder run berisi best.pt")
    parser.add_argument("--split", default="test", choices=["train", "val", "test"])
    parser.add_argument("--subset", default="all", choices=["all", "clean"],
                        help="'clean' = hanya gambar tanpa near-duplicate di train")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args(argv)

    run_dir = resolve_path(args.run_dir)
    device = get_device(args.device)
    ckpt = torch.load(run_dir / "best.pt", map_location=device, weights_only=False)
    cfg = ckpt["config"]
    model = build_model(ckpt["backbone"], num_outputs_for(ckpt["head"], NUM_CLASSES), pretrained=False)
    model.load_state_dict(ckpt["model_state"])
    model.to(device)

    metadata = load_metadata(cfg["data"]["metadata_csv"])
    loader = make_loaders(cfg, metadata, int(ckpt["seed"]))[args.split]
    result = predict_loader(model, loader, ckpt["head"], NUM_CLASSES, device)
    table = predictions_table(result, loader.dataset.df)
    if args.subset == "clean":
        if "near_dup_in_train" not in table.columns:
            raise SystemExit("Kolom near_dup_in_train tidak ada. Jalankan scripts/audit_dataset.py dahulu.")
        table = table[~table["near_dup_in_train"].astype(bool)]

    metrics = compute_metrics(table["label"], table["pred"])
    tag = f"{args.split}_{args.subset}"
    out_dir = Path(run_dir) / "reevaluasi"
    out_dir.mkdir(exist_ok=True)
    save_json(metrics, out_dir / f"metrics_{tag}.json")
    table.to_csv(out_dir / f"predictions_{tag}.csv", index=False)
    plot_confusion(metrics["confusion_matrix"], out_dir / f"confusion_{tag}.png", title=f"{cfg['experiment_name']} - {tag}")
    print({k: round(v, 4) for k, v in metrics.items() if isinstance(v, float)})
    print(f"Hasil disimpan di {out_dir}")


if __name__ == "__main__":
    main()
