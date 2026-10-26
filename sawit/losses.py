"""Loss dan dekoding keluaran untuk dua jenis kepala: `ce` dan `corn`.

CORN (Conditional Ordinal Regression for Neural networks; Shi, Cao & Raschka,
2023) memecah masalah K kelas berurutan menjadi K-1 tugas biner bersyarat:

    tugas k : "apakah y > k, dengan syarat y > k-1?"   (k = 0..K-2)

Tugas k hanya dilatih pada sampel dengan y >= k. Peluang tak bersyarat
P(y > k) diperoleh dari perkalian kumulatif peluang bersyarat, sehingga
monoton turun terhadap k (konsisten secara peringkat). Prediksi akhir =
jumlah k dengan P(y > k) > 0,5.

Implementasi ditulis ulang dari deskripsi makalah; dicocokkan dengan
implementasi rujukan `coral-pytorch` (Raschka dkk., lisensi MIT) tanpa
menyalin kode.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# CORN
# ---------------------------------------------------------------------------
def corn_loss(logits: torch.Tensor, targets: torch.Tensor, num_classes: int) -> torch.Tensor:
    """Loss CORN: rata-rata BCE dari seluruh tugas biner bersyarat.

    logits  : (N, K-1)
    targets : (N,) bilangan bulat 0..K-1
    """
    total = logits.new_zeros(())
    count = 0
    for k in range(num_classes - 1):
        # Sampel yang relevan untuk tugas k: yang tingkatnya >= k.
        mask = targets >= k
        n_k = int(mask.sum())
        if n_k == 0:
            continue
        binary_target = (targets[mask] > k).float()
        total = total + F.binary_cross_entropy_with_logits(
            logits[mask, k], binary_target, reduction="sum"
        )
        count += n_k
    return total / max(count, 1)


def corn_cumulative_probs(logits: torch.Tensor) -> torch.Tensor:
    """P(y > k) untuk k = 0..K-2, hasil perkalian kumulatif peluang bersyarat."""
    return torch.cumprod(torch.sigmoid(logits), dim=1)


def corn_class_probs(logits: torch.Tensor) -> torch.Tensor:
    """Mengubah K-1 peluang kumulatif menjadi distribusi K kelas.

    P(y=0)   = 1 - P(y>0)
    P(y=k)   = P(y>k-1) - P(y>k)
    P(y=K-1) = P(y>K-2)
    """
    cum = corn_cumulative_probs(logits)
    ones = torch.ones_like(cum[:, :1])
    zeros = torch.zeros_like(cum[:, :1])
    upper = torch.cat([ones, cum], dim=1)
    lower = torch.cat([cum, zeros], dim=1)
    return (upper - lower).clamp_min(0.0)


def corn_predict(logits: torch.Tensor) -> torch.Tensor:
    """Aturan prediksi CORN: banyaknya batas yang terlampaui (P(y>k) > 0,5)."""
    return (corn_cumulative_probs(logits) > 0.5).sum(dim=1)


# ---------------------------------------------------------------------------
# Antarmuka umum untuk kedua jenis kepala
# ---------------------------------------------------------------------------
def compute_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    head: str,
    num_classes: int,
    label_smoothing: float = 0.0,
) -> torch.Tensor:
    if head == "ce":
        return F.cross_entropy(logits, targets, label_smoothing=label_smoothing)
    if head == "corn":
        return corn_loss(logits, targets, num_classes)
    raise ValueError(f"Jenis kepala tidak dikenal: {head}")


def logits_to_probs(logits: torch.Tensor, head: str) -> torch.Tensor:
    """Distribusi peluang K kelas (dipakai untuk tampilan, ROC, dan Grad-CAM)."""
    if head == "ce":
        return torch.softmax(logits, dim=1)
    return corn_class_probs(logits)


def logits_to_pred(logits: torch.Tensor, head: str) -> torch.Tensor:
    """Label prediksi sesuai aturan dekoding masing-masing kepala."""
    if head == "ce":
        return logits.argmax(dim=1)
    return corn_predict(logits)
