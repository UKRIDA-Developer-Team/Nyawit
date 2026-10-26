"""Audit kebocoran data: hash persepsi (dHash) dan pengelompokan near-duplicate.

Dataset dikumpulkan di lapangan dengan beberapa perangkat. Foto beruntun dari
tandan yang sama dapat terlihat hampir identik. Jika pasangan seperti itu
terpisah ke train dan test, skor test menjadi terlalu optimistis. Modul ini
mendeteksi pasangan tersebut agar dapat (1) dilaporkan, (2) dipakai untuk
menghitung metrik pada subset test "bersih", dan (3) dipakai membuat split
berkelompok (grouped split).

Temuan audit pada dataset asli (Okt 2026): dHash hanya menangkap foto yang
nyaris identik. Foto tandan yang sama dari sudut sedikit berbeda lolos dari
dHash, tetapi terlihat dari nomor berkas yang berurutan (foto diambil beruntun
per sesi). Karena itu split berkelompok dibentuk dari **blok nomor berkas
berurutan** per kelas, digabung dengan kelompok dHash.

dHash (difference hash): gambar diubah ke grayscale 9x8, lalu setiap bit
menyatakan apakah piksel lebih terang dari tetangga kanannya (64 bit).
Jarak Hamming kecil antara dua hash berarti struktur gambar sangat mirip.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
from PIL import Image


def dhash_hex(image: Image.Image, hash_size: int = 8) -> str:
    """Menghitung dHash 64-bit dan mengembalikannya sebagai string heksadesimal."""
    gray = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.asarray(gray, dtype=np.int16)
    bits = (pixels[:, 1:] > pixels[:, :-1]).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:0{hash_size * hash_size // 4}x}"


def _popcount(x: np.ndarray) -> np.ndarray:
    """Jumlah bit 1 per elemen uint64 (dengan cadangan untuk numpy lama)."""
    if hasattr(np, "bitwise_count"):
        return np.bitwise_count(x)
    as_bytes = x.view(np.uint8).reshape(*x.shape, 8)
    return np.unpackbits(as_bytes, axis=-1).sum(axis=-1)


def near_duplicate_pairs(hashes: list[str], threshold: int, chunk: int = 512) -> pd.DataFrame:
    """Mencari semua pasangan (i, j), i < j, dengan jarak Hamming <= threshold.

    Perbandingan dilakukan per potongan (chunk) agar memori tetap kecil:
    4.728 gambar -> ~11 juta pasangan, selesai dalam hitungan detik.
    """
    values = np.array([int(h, 16) for h in hashes], dtype=np.uint64)
    found_i, found_j, found_d = [], [], []
    for start in range(0, len(values), chunk):
        block = values[start:start + chunk]
        dist = _popcount(block[:, None] ^ values[None, :])
        ii, jj = np.nonzero(dist <= threshold)
        ii = ii + start
        keep = jj > ii
        found_i.append(ii[keep])
        found_j.append(jj[keep])
        found_d.append(dist[ii[keep] - start, jj[keep]])
    return pd.DataFrame({
        "i": np.concatenate(found_i) if found_i else np.array([], dtype=int),
        "j": np.concatenate(found_j) if found_j else np.array([], dtype=int),
        "distance": np.concatenate(found_d) if found_d else np.array([], dtype=int),
    })


class UnionFind:
    """Struktur union-find untuk menggabungkan pasangan menjadi kelompok."""

    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def duplicate_groups(n: int, pairs: pd.DataFrame) -> np.ndarray:
    """Memberi ID kelompok; gambar tanpa pasangan menjadi kelompok sendiri."""
    uf = UnionFind(n)
    for i, j in zip(pairs["i"].to_numpy(), pairs["j"].to_numpy()):
        uf.union(int(i), int(j))
    roots = np.array([uf.find(i) for i in range(n)])
    _, group_ids = np.unique(roots, return_inverse=True)
    return group_ids


FILE_NUMBER_RE = re.compile(r"(\d+)\.[A-Za-z]+$")


def file_number(image_id: str) -> int:
    """Nomor urut pada nama berkas, mis. 'Immature324.jpg' -> 324."""
    match = FILE_NUMBER_RE.search(image_id)
    if not match:
        raise ValueError(f"Nama berkas tanpa nomor urut: {image_id}")
    return int(match.group(1))


def block_group_ids(labels: np.ndarray, numbers: np.ndarray, block_size: int) -> np.ndarray:
    """ID kelompok berdasarkan blok nomor berurutan per kelas: (kelas, nomor // block_size)."""
    keys = [f"{label}_{number // block_size}" for label, number in zip(labels, numbers)]
    _, ids = np.unique(np.array(keys), return_inverse=True)
    return ids


def merge_groups(*group_arrays: np.ndarray) -> np.ndarray:
    """Menggabungkan beberapa pengelompokan: dua gambar sekelompok bila berbagi
    kelompok di salah satu pengelompokan (penutupan transitif lewat union-find)."""
    n = len(group_arrays[0])
    uf = UnionFind(n)
    for groups in group_arrays:
        first_seen: dict = {}
        for i, g in enumerate(groups):
            if g in first_seen:
                uf.union(i, first_seen[g])
            else:
                first_seen[g] = i
    _, ids = np.unique([uf.find(i) for i in range(n)], return_inverse=True)
    return ids


def neighbor_in_split(labels, numbers, splits, target: str = "train", window: int = 1) -> np.ndarray:
    """True bila gambar punya tetangga bernomor dalam ±window (kelas sama) di split `target`."""
    lookup = {(lab, num): sp for lab, num, sp in zip(labels, numbers, splits)}
    return np.array([
        any(lookup.get((lab, num + off)) == target for off in range(-window, window + 1) if off)
        for lab, num in zip(labels, numbers)
    ])


def sequential_similarity(features: np.ndarray, labels: np.ndarray, numbers: np.ndarray,
                          lags=(1, 2, 3, 5, 10, 20, 50), n_ref: int = 20000, seed: int = 0) -> tuple[pd.DataFrame, dict]:
    """Membandingkan jarak fitur (terstandardisasi) antar gambar berselisih nomor k
    dengan pasangan acak sekelas yang nomornya berjauhan (> 50, atau lebih kecil
    bila rentang nomor dataset sempit).

    Bila pengambilan foto tidak berurutan per tandan/sesi, proporsi pasangan
    berselisih k yang lebih mirip dari persentil-5 rujukan akan ~5%.
    """
    feats = (features - features.mean(0)) / (features.std(0) + 1e-8)
    labels, numbers = np.asarray(labels), np.asarray(numbers)
    index = {(lab, num): i for i, (lab, num) in enumerate(zip(labels, numbers))}
    # Jarak minimum "berjauhan": 50 nomor, atau lebih kecil untuk dataset kecil (uji asap).
    min_gap = int(min(50, max(1, (numbers.max() - numbers.min()) // 3)))
    rng = np.random.default_rng(seed)
    i, j = rng.integers(0, len(feats), (2, n_ref * 20))
    keep = (labels[i] == labels[j]) & (np.abs(numbers[i] - numbers[j]) > min_gap)
    i, j = i[keep][:n_ref], j[keep][:n_ref]
    if len(i) == 0:
        raise ValueError("Tidak ada pasangan rujukan; dataset terlalu kecil untuk analisis ini.")
    ref = np.linalg.norm(feats[i] - feats[j], axis=1)
    p5 = float(np.percentile(ref, 5))
    rows = []
    for k in lags:
        dists = np.array([np.linalg.norm(feats[i] - feats[index[(lab, num + k)]])
                          for (lab, num), i in index.items() if (lab, num + k) in index])
        if len(dists):
            rows.append({"selisih_nomor": k, "n_pasangan": len(dists), "median_jarak": float(np.median(dists)),
                         "persen_lebih_mirip_dari_p5_acak": float(100 * (dists < p5).mean())})
    return pd.DataFrame(rows), {"median_acak": float(np.median(ref)), "p5_acak": p5, "jarak_nomor_minimum": min_gap}


def flag_cross_split_leakage(df: pd.DataFrame, pairs: pd.DataFrame, split_col: str) -> pd.Series:
    """True untuk gambar val/test yang punya near-duplicate di split train."""
    split = df[split_col].to_numpy()
    flags = np.zeros(len(df), dtype=bool)
    for i, j in zip(pairs["i"].to_numpy(), pairs["j"].to_numpy()):
        si, sj = split[i], split[j]
        if si == "train" and sj in ("val", "test"):
            flags[j] = True
        elif sj == "train" and si in ("val", "test"):
            flags[i] = True
    return pd.Series(flags, index=df.index)


def grouped_split(
    labels: np.ndarray,
    groups: np.ndarray,
    seed: int = 42,
    test_frac: float = 0.15,
    val_frac: float = 0.15,
) -> np.ndarray:
    """Split train/val/test bertingkat (stratified) yang menjaga satu kelompok
    near-duplicate tetap berada di satu split yang sama."""
    from sklearn.model_selection import StratifiedGroupKFold

    n = len(labels)
    result = np.array(["train"] * n, dtype=object)
    idx_all = np.arange(n)

    n_test_folds = max(2, round(1 / test_frac))
    sgkf = StratifiedGroupKFold(n_splits=n_test_folds, shuffle=True, random_state=seed)
    rest_idx, test_idx = next(sgkf.split(idx_all, labels, groups))
    result[test_idx] = "test"

    n_val_folds = max(2, round((1 - test_frac) / val_frac))
    sgkf = StratifiedGroupKFold(n_splits=n_val_folds, shuffle=True, random_state=seed)
    _, val_rel = next(sgkf.split(rest_idx, labels[rest_idx], groups[rest_idx]))
    result[rest_idx[val_rel]] = "val"
    return result
