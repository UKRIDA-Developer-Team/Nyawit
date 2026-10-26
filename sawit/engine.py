"""Loop pelatihan dan evaluasi yang dipakai bersama oleh train.py dan evaluate.py."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from .losses import compute_loss, logits_to_pred, logits_to_probs


def warmup_cosine_schedule(optimizer, warmup_steps: int, total_steps: int):
    """Learning rate naik linear selama warmup, lalu turun mengikuti kosinus."""

    def factor(step: int) -> float:
        if step < warmup_steps:
            return (step + 1) / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * min(1.0, progress)))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, factor)


def train_one_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler,
    scaler: torch.amp.GradScaler,
    head: str,
    num_classes: int,
    device: torch.device,
    use_amp: bool,
    label_smoothing: float = 0.0,
    max_batches: int | None = None,
) -> float:
    """Satu epoch pelatihan; mengembalikan rata-rata loss per sampel."""
    model.train()
    total_loss, total_n = 0.0, 0
    for batch_idx, (images, targets, _) in enumerate(loader):
        if max_batches is not None and batch_idx >= max_batches:
            break
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, enabled=use_amp):
            logits = model(images)
        # Loss dihitung dalam float32 agar stabil secara numerik.
        loss = compute_loss(logits.float(), targets, head, num_classes, label_smoothing)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()
        total_loss += float(loss.item()) * len(targets)
        total_n += len(targets)
    return total_loss / max(total_n, 1)


@torch.no_grad()
def predict_loader(
    model: torch.nn.Module,
    loader: DataLoader,
    head: str,
    num_classes: int,
    device: torch.device,
    max_batches: int | None = None,
) -> dict:
    """Menjalankan model pada seluruh loader dan mengumpulkan prediksi."""
    model.eval()
    ys, preds, probs, indices = [], [], [], []
    total_loss, total_n = 0.0, 0
    for batch_idx, (images, targets, idx) in enumerate(loader):
        if max_batches is not None and batch_idx >= max_batches:
            break
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)
        logits = model(images).float()
        total_loss += float(compute_loss(logits, targets, head, num_classes).item()) * len(targets)
        total_n += len(targets)
        ys.append(targets.cpu())
        preds.append(logits_to_pred(logits, head).cpu())
        probs.append(logits_to_probs(logits, head).cpu())
        indices.append(idx)
    if total_n == 0:
        raise RuntimeError("Loader kosong: tidak ada sampel untuk dievaluasi.")
    return {
        "y_true": torch.cat(ys).numpy(),
        "y_pred": torch.cat(preds).numpy(),
        "probs": torch.cat(probs).numpy(),
        "indices": torch.cat(indices).numpy(),
        "loss": total_loss / total_n,
    }


def predictions_table(result: dict, df: pd.DataFrame) -> pd.DataFrame:
    """Menyusun tabel prediksi per gambar (untuk analisis kesalahan)."""
    rows = df.iloc[result["indices"]].reset_index(drop=True)
    probs = result["probs"]
    levels = np.arange(probs.shape[1])
    table = pd.DataFrame({
        "image_id": rows["image_id"],
        "rel_path": rows["rel_path"],
        "label": result["y_true"],
        "pred": result["y_pred"],
    })
    table["abs_err"] = (table["label"] - table["pred"]).abs()
    table["confidence"] = probs.max(axis=1)
    table["expected_level"] = (probs * levels).sum(axis=1)
    for k in levels:
        table[f"prob_{k}"] = probs[:, k]
    for extra in ("near_dup_in_train", "dup_group"):
        if extra in rows.columns:
            table[extra] = rows[extra].to_numpy()
    return table
