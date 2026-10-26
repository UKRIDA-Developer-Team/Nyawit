"""Pelatihan satu eksperimen (satu konfigurasi x satu seed).

Contoh:
    python -m sawit.train --config configs/e3_cnn_corn.yaml --seed 42
    python -m sawit.train --config configs/e2_cnn_ce.yaml --set train.epochs=5

Keluaran (outputs/runs/<nama_eksperimen>/seed<seed>/):
    config.yaml              konfigurasi final setelah merge
    history.csv              loss & metrik validasi per epoch
    best.pt                  checkpoint terbaik (dipilih dari metrik validasi)
    metrics_val.json         metrik validasi pada checkpoint terbaik
    metrics_test.json        metrik test penuh
    metrics_test_clean.json  metrik test tanpa near-duplicate dari train (bila ada)
    predictions_test.csv     prediksi per gambar test
    confusion_test.png, curves.png, summary.json
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import torch

from .config import load_config, save_config
from .constants import CLASS_NAMES_ID, NUM_CLASSES
from .data import load_metadata, make_loaders, split_column
from .engine import predict_loader, predictions_table, train_one_epoch, warmup_cosine_schedule
from .metrics import HIGHER_IS_BETTER, compute_metrics
from .models import build_model, count_parameters, num_outputs_for
from .plots import plot_confusion, plot_history
from .utils import environment_info, get_device, resolve_path, save_json, set_seed


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Latih model klasifikasi kematangan sawit.")
    parser.add_argument("--config", required=True, help="Berkas konfigurasi YAML.")
    parser.add_argument("--seed", type=int, default=None, help="Menimpa seed pada konfigurasi.")
    parser.add_argument("--set", nargs="*", default=[], metavar="KUNCI=NILAI",
                        help="Override konfigurasi, mis. train.epochs=3")
    parser.add_argument("--device", default="auto", help="auto | cpu | cuda | mps")
    parser.add_argument("--max-batches", type=int, default=None,
                        help="Batasi jumlah batch per epoch (hanya untuk uji asap).")
    return parser.parse_args(argv)


def run_experiment(cfg: dict, seed: int, device: torch.device, max_batches: int | None = None) -> Path:
    set_seed(seed, deterministic=bool(cfg["train"].get("deterministic", True)))
    name = cfg["experiment_name"]
    run_dir = resolve_path(cfg.get("output_root", "outputs/runs")) / name / f"seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg = {**cfg, "seed": seed}
    save_config(cfg, run_dir / "config.yaml")

    # ----- Data -----
    metadata = load_metadata(cfg["data"]["metadata_csv"])
    loaders = make_loaders(cfg, metadata, seed)
    print(f"[{name} | seed {seed}] perangkat={device} | "
          f"train={len(loaders['train'].dataset)} val={len(loaders['val'].dataset)} "
          f"test={len(loaders['test'].dataset)}")

    # ----- Model -----
    head = cfg["model"]["head"]
    model = build_model(
        cfg["model"]["backbone"],
        num_outputs_for(head, NUM_CLASSES),
        pretrained=bool(cfg["model"].get("pretrained", True)),
        dropout=float(cfg["model"].get("dropout", 0.2)),
    ).to(device)

    tcfg = cfg["train"]
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(tcfg["lr"]),
                                  weight_decay=float(tcfg["weight_decay"]))
    steps_per_epoch = len(loaders["train"]) if max_batches is None else min(max_batches, len(loaders["train"]))
    epochs = int(tcfg["epochs"])
    scheduler = warmup_cosine_schedule(
        optimizer,
        warmup_steps=int(float(tcfg.get("warmup_epochs", 1)) * steps_per_epoch),
        total_steps=epochs * steps_per_epoch,
    )
    use_amp = bool(tcfg.get("amp", True)) and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    select_metric = tcfg.get("select_metric", "macro_f1")
    higher_better = HIGHER_IS_BETTER[select_metric]
    best_score = -float("inf") if higher_better else float("inf")
    best_epoch, patience_left = -1, int(tcfg.get("early_stopping_patience", 5))
    history = []
    t_start = time.time()

    # ----- Loop pelatihan -----
    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss = train_one_epoch(
            model, loaders["train"], optimizer, scheduler, scaler, head, NUM_CLASSES, device,
            use_amp, float(tcfg.get("label_smoothing", 0.0)), max_batches,
        )
        val = predict_loader(model, loaders["val"], head, NUM_CLASSES, device, max_batches)
        val_metrics = compute_metrics(val["y_true"], val["y_pred"])
        row = {
            "epoch": epoch,
            "lr": optimizer.param_groups[0]["lr"],
            "train_loss": train_loss,
            "val_loss": val["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "val_macro_f1": val_metrics["macro_f1"],
            "val_mae": val_metrics["mae"],
            "val_severe_error_rate": val_metrics["severe_error_rate"],
            "epoch_seconds": time.time() - t0,
        }
        history.append(row)
        pd.DataFrame(history).to_csv(run_dir / "history.csv", index=False)

        score = val_metrics[select_metric]
        improved = score > best_score if higher_better else score < best_score
        flag = ""
        if improved:
            best_score, best_epoch = score, epoch
            patience_left = int(tcfg.get("early_stopping_patience", 5))
            torch.save({
                "model_state": model.state_dict(),
                "config": cfg,
                "head": head,
                "backbone": cfg["model"]["backbone"],
                "num_classes": NUM_CLASSES,
                "class_names": CLASS_NAMES_ID,
                "image_size": int(cfg["data"]["image_size"]),
                "seed": seed,
                "epoch": epoch,
                "val_metrics": val_metrics,
            }, run_dir / "best.pt")
            save_json(val_metrics, run_dir / "metrics_val.json")
            flag = "  <- terbaik"
        else:
            patience_left -= 1
        print(f"  epoch {epoch:02d} | loss train {train_loss:.4f} val {val['loss']:.4f} | "
              f"val acc {val_metrics['accuracy']:.4f} F1 {val_metrics['macro_f1']:.4f} "
              f"MAE {val_metrics['mae']:.4f} | {row['epoch_seconds']:.0f}s{flag}")
        if patience_left <= 0:
            print(f"  early stopping: {select_metric} tidak membaik selama "
                  f"{tcfg.get('early_stopping_patience', 5)} epoch.")
            break

    train_seconds = time.time() - t_start
    plot_history(pd.DataFrame(history), run_dir / "curves.png")

    # ----- Evaluasi test memakai checkpoint terbaik -----
    # Test set hanya disentuh SEKALI di sini, setelah pemilihan model selesai.
    checkpoint = torch.load(run_dir / "best.pt", map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state"])
    test = predict_loader(model, loaders["test"], head, NUM_CLASSES, device, max_batches)
    test_metrics = compute_metrics(test["y_true"], test["y_pred"])
    save_json(test_metrics, run_dir / "metrics_test.json")
    preds = predictions_table(test, loaders["test"].dataset.df)
    preds.to_csv(run_dir / "predictions_test.csv", index=False)
    plot_confusion(test_metrics["confusion_matrix"], run_dir / "confusion_test.png",
                   title=f"{name} (seed {seed}) - test")

    summary = {
        "experiment_name": name,
        "description": cfg.get("description", ""),
        "seed": seed,
        "split_scheme": cfg["data"].get("split_scheme", "official"),
        "split_column": split_column(cfg["data"].get("split_scheme", "official")),
        "best_epoch": best_epoch,
        "epochs_run": len(history),
        f"val_{select_metric}": best_score,
        "train_seconds": train_seconds,
        "num_parameters": count_parameters(model),
        "test": {k: v for k, v in test_metrics.items() if k not in ("per_class", "confusion_matrix")},
        "environment": environment_info(device),
        "debug_max_batches": max_batches,
    }

    # Subset test "bersih": tanpa near-duplicate di train (lihat sawit/audit.py).
    if "near_dup_in_train" in preds.columns and summary["split_scheme"] == "official":
        clean = preds[~preds["near_dup_in_train"].astype(bool)]
        if len(clean):
            clean_metrics = compute_metrics(clean["label"], clean["pred"])
            save_json(clean_metrics, run_dir / "metrics_test_clean.json")
            summary["test_clean"] = {k: v for k, v in clean_metrics.items()
                                     if k not in ("per_class", "confusion_matrix")}

    save_json(summary, run_dir / "summary.json")
    print(f"  selesai: epoch terbaik {best_epoch} | test acc {test_metrics['accuracy']:.4f} "
          f"macro-F1 {test_metrics['macro_f1']:.4f} MAE {test_metrics['mae']:.4f} "
          f"kesalahan berat {test_metrics['severe_error_rate']:.4f} -> {run_dir}")
    return run_dir


def main(argv=None) -> None:
    args = parse_args(argv)
    cfg = load_config(args.config, args.set)
    seed = args.seed if args.seed is not None else int(cfg.get("seed", 42))
    run_experiment(cfg, seed, get_device(args.device), args.max_batches)


if __name__ == "__main__":
    main()
