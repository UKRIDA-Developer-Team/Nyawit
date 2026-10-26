"""Gambar untuk laporan: confusion matrix, kurva pelatihan, galeri contoh."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # tanpa layar (server/Colab)
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

from .constants import CLASS_NAMES_ID  # noqa: E402


def plot_confusion(cm, path: str | Path, title: str = "Confusion matrix", names=CLASS_NAMES_ID) -> None:
    """Confusion matrix ternormalisasi per baris (recall) dengan jumlah absolut."""
    cm = np.asarray(cm, dtype=float)
    row_sum = cm.sum(axis=1, keepdims=True)
    norm = np.divide(cm, row_sum, out=np.zeros_like(cm), where=row_sum > 0)
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    im = ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(names)), names, rotation=35, ha="right")
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("Prediksi")
    ax.set_ylabel("Label sebenarnya")
    ax.set_title(title)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            color = "white" if norm[i, j] > 0.5 else "black"
            ax.text(j, i, f"{norm[i, j]:.2f}\n({int(cm[i, j])})", ha="center", va="center", fontsize=8, color=color)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_history(history: pd.DataFrame, path: str | Path) -> None:
    """Kurva loss dan metrik validasi per epoch."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    axes[0].plot(history["epoch"], history["train_loss"], label="train")
    axes[0].plot(history["epoch"], history["val_loss"], label="validasi")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].set_title("Loss")
    axes[1].plot(history["epoch"], history["val_macro_f1"], label="macro-F1 val")
    axes[1].plot(history["epoch"], history["val_accuracy"], label="akurasi val")
    ax2 = axes[1].twinx()
    ax2.plot(history["epoch"], history["val_mae"], color="tab:red", linestyle="--", label="MAE val")
    ax2.set_ylabel("MAE (tingkat)")
    axes[1].set_xlabel("Epoch")
    axes[1].set_title("Metrik validasi")
    lines = axes[1].get_lines() + ax2.get_lines()
    axes[1].legend(lines, [line.get_label() for line in lines], loc="center right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def image_grid(paths: list[Path], captions: list[str], path: str | Path, ncols: int = 5, title: str | None = None) -> None:
    """Galeri gambar dengan keterangan (contoh data, contoh salah klasifikasi)."""
    if not paths:
        return
    nrows = int(np.ceil(len(paths) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.0 * ncols, 3.2 * nrows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, img_path, caption in zip(axes.flat, paths, captions):
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img.thumbnail((320, 320))
            ax.imshow(img)
        ax.set_title(caption, fontsize=8)
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    # Galeri berisi foto: JPEG jauh lebih kecil daripada PNG (penting untuk repositori).
    extra = {"pil_kwargs": {"quality": 85}} if str(path).lower().endswith((".jpg", ".jpeg")) else {}
    fig.savefig(path, dpi=110, **extra)
    plt.close(fig)
