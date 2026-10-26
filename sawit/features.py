"""Fitur warna HSV sederhana.

Dipakai oleh dua bagian:
- baseline E1 (histogram HSV + regresi logistik);
- audit kebocoran: jarak fitur warna antar gambar bernomor berurutan, karena
  warna tidak terlalu peka terhadap perubahan sudut/pembingkaian foto
  (berbeda dengan dHash), sehingga cocok untuk mendeteksi "tandan sama,
  sudut berbeda".
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

H_BINS, S_BINS, V_BINS = 18, 8, 8
NUM_FEATURES = H_BINS + S_BINS + V_BINS + 6


def hsv_features(path: Path, size: int = 160) -> np.ndarray:
    """Histogram H/S/V ternormalisasi + rerata & simpangan baku tiap kanal (40 fitur)."""
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((size, size))
        hsv = np.asarray(img.convert("HSV"), dtype=np.float32) / 255.0
    feats = []
    for channel, bins in zip(range(3), (H_BINS, S_BINS, V_BINS)):
        hist, _ = np.histogram(hsv[..., channel], bins=bins, range=(0, 1))
        feats.append(hist / max(hist.sum(), 1))
    flat = hsv.reshape(-1, 3)
    feats += [flat.mean(axis=0), flat.std(axis=0)]
    return np.concatenate(feats).astype(np.float32)


def load_or_compute_hsv(df: pd.DataFrame, dataset_root: Path, cache: Path) -> np.ndarray:
    """Fitur HSV untuk seluruh baris metadata, memakai cache bila daftar gambarnya sama persis."""
    ids = df["image_id"].to_numpy().astype(str)
    if cache.exists():
        cached = np.load(cache)
        if np.array_equal(cached["ids"], ids):
            return cached["features"]
    features = np.stack([hsv_features(dataset_root / p) for p in df["rel_path"]])
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, features=features, ids=ids)
    return features
