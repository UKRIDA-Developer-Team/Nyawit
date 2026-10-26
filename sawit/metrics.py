"""Metrik evaluasi.

Metrik klasifikasi (wajib menurut panduan, bagian 8): accuracy, macro-F1,
precision/recall per kelas, confusion matrix.

Metrik ordinal (pertanyaan utama proyek):
- MAE                : rata-rata |prediksi - label| dalam satuan tingkat.
- severe_error_rate  : proporsi prediksi yang meleset >= 2 tingkat
                       (mis. "Mentah" diprediksi "Terlalu Matang").
- off_by_one_acc     : proporsi prediksi yang meleset paling banyak 1 tingkat.
- QWK                : quadratic weighted kappa (Cohen, 1968); kesepakatan yang
                       menghukum kesalahan jauh lebih berat.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from .constants import CLASS_NAMES_ID, NUM_CLASSES


def compute_metrics(y_true, y_pred, num_classes: int = NUM_CLASSES) -> dict:
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    labels = list(range(num_classes))
    abs_err = np.abs(y_true - y_pred)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    names = CLASS_NAMES_ID if num_classes == NUM_CLASSES else [str(i) for i in labels]
    per_class = {
        names[i]: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i in labels
    }
    # QWK tidak terdefinisi bila hanya ada satu kelas; kembalikan NaN.
    try:
        qwk = float(cohen_kappa_score(y_true, y_pred, labels=labels, weights="quadratic"))
    except ValueError:
        qwk = float("nan")

    return {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "mae": float(abs_err.mean()) if len(abs_err) else float("nan"),
        "off_by_one_acc": float((abs_err <= 1).mean()) if len(abs_err) else float("nan"),
        "severe_error_rate": float((abs_err >= 2).mean()) if len(abs_err) else float("nan"),
        "qwk": qwk,
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


# Metrik utama yang ditampilkan di tabel ringkasan (urutan kolom laporan).
SUMMARY_METRICS = ["accuracy", "macro_f1", "mae", "severe_error_rate", "off_by_one_acc", "qwk"]

# Arah "lebih baik" untuk setiap metrik (dipakai saat menandai nilai terbaik).
HIGHER_IS_BETTER = {
    "accuracy": True,
    "macro_f1": True,
    "mae": False,
    "severe_error_rate": False,
    "off_by_one_acc": True,
    "qwk": True,
}
