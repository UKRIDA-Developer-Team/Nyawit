"""Pembacaan dataset, pembuatan metadata, transformasi, dan DataLoader.

Struktur Dataset.zip (diperiksa langsung dari arsip resmi):

    Dataset/
      Images/0Immature/Immature0.jpg ...
      Images/1PartiallyRipe/...
      Images/2FullyRipe/...
      Images/3OverRipe/...
      Images/4Decayed/...
      Train_val_test_split/Training.txt | Validation.txt | Testing.txt

Berkas split hanya berisi nama berkas (mis. `Decayed0.jpg`). Nama berkas unik
di seluruh dataset karena diberi awalan nama kelas.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import transforms as T

from .audit import dhash_hex
from .constants import (
    CLASS_FOLDERS,
    CLASS_NAMES_ID,
    IMAGENET_MEAN,
    IMAGENET_STD,
    SPLIT_FILES,
)
from .utils import resolve_path, seed_worker

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------
def find_dataset_root(path: str | Path) -> Path:
    """Mencari folder yang berisi `Images/` (boleh diberi folder induknya)."""
    path = resolve_path(path)
    if (path / "Images").is_dir():
        return path
    for candidate in sorted(path.rglob("Images")):
        if candidate.is_dir() and any((candidate / c).is_dir() for c in CLASS_FOLDERS):
            return candidate.parent
    raise FileNotFoundError(
        f"Folder 'Images/' dengan subfolder kelas tidak ditemukan di bawah {path}. "
        "Jalankan dulu: python scripts/download_data.py"
    )


def read_official_splits(dataset_root: Path) -> dict[str, str]:
    """Membaca berkas split resmi -> {nama_berkas: 'train'|'val'|'test'}."""
    split_dir = dataset_root / "Train_val_test_split"
    mapping: dict[str, str] = {}
    if not split_dir.is_dir():
        return mapping
    for split, filename in SPLIT_FILES.items():
        split_file = split_dir / filename
        if not split_file.exists():
            continue
        for line in split_file.read_text(encoding="utf-8").splitlines():
            name = Path(line.strip()).name
            if not name:
                continue
            if name in mapping and mapping[name] != split:
                raise ValueError(f"Berkas {name} muncul di dua split: {mapping[name]} dan {split}")
            mapping[name] = split
    return mapping


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_metadata(dataset_root: str | Path, compute_hashes: bool = True) -> pd.DataFrame:
    """Memindai seluruh gambar dan membuat tabel metadata.

    Kolom: image_id, rel_path, label, label_name, official_split, width, height,
    md5 (duplikat persis), dhash (near-duplicate).
    """
    root = find_dataset_root(dataset_root)
    split_map = read_official_splits(root)
    rows = []
    for label, folder in enumerate(CLASS_FOLDERS):
        class_dir = root / "Images" / folder
        if not class_dir.is_dir():
            raise FileNotFoundError(f"Folder kelas tidak ditemukan: {class_dir}")
        for img_path in sorted(class_dir.iterdir()):
            if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            row = {
                "image_id": img_path.name,
                "rel_path": img_path.relative_to(root).as_posix(),
                "label": label,
                "label_name": CLASS_NAMES_ID[label],
                "official_split": split_map.get(img_path.name, "unassigned"),
            }
            with Image.open(img_path) as img:
                row["width"], row["height"] = img.size
                if compute_hashes:
                    row["dhash"] = dhash_hex(img)
            if compute_hashes:
                row["md5"] = _md5(img_path)
            rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError(f"Tidak ada gambar ditemukan di {root}")
    return df


def load_metadata(path: str | Path) -> pd.DataFrame:
    path = resolve_path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Metadata tidak ditemukan: {path}. Jalankan: python scripts/prepare_data.py"
        )
    return pd.read_csv(path)


def split_column(scheme: str) -> str:
    """Nama kolom split sesuai skema pada konfigurasi."""
    columns = {"official": "official_split", "grouped": "grouped_split"}
    if scheme not in columns:
        raise ValueError(f"Skema split tidak dikenal: {scheme} (pilih: {list(columns)})")
    return columns[scheme]


# ---------------------------------------------------------------------------
# Dataset & transformasi
# ---------------------------------------------------------------------------
class PalmFruitDataset(Dataset):
    """Dataset PyTorch: mengembalikan (tensor_gambar, label, indeks_baris)."""

    def __init__(self, df: pd.DataFrame, dataset_root: str | Path, transform: Callable | None = None):
        self.df = df.reset_index(drop=True)
        self.root = find_dataset_root(dataset_root)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        with Image.open(self.root / row["rel_path"]) as img:
            image = img.convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, int(row["label"]), idx


def build_transforms(cfg: dict, train: bool) -> T.Compose:
    """Transformasi latih (dengan augmentasi) atau evaluasi (deterministik).

    Catatan desain: augmentasi `hue` default 0 karena warna kulit buah adalah
    isyarat utama kematangan; pengaruhnya diuji pada eksperimen terkontrol E4.
    """
    size = int(cfg["data"]["image_size"])
    normalize = T.Normalize(IMAGENET_MEAN, IMAGENET_STD)
    if not train:
        return T.Compose([
            T.Resize(int(round(size * 256 / 224))),
            T.CenterCrop(size),
            T.ToTensor(),
            normalize,
        ])

    aug = cfg.get("augment", {})
    ops: list = [T.RandomResizedCrop(size, scale=tuple(aug.get("crop_scale", [0.6, 1.0])))]
    if aug.get("hflip", True):
        ops.append(T.RandomHorizontalFlip())
    if aug.get("vflip", False):
        ops.append(T.RandomVerticalFlip())
    if aug.get("rotation", 0):
        ops.append(T.RandomRotation(aug["rotation"]))
    jitter = {k: float(aug.get(k, 0.0)) for k in ("brightness", "contrast", "saturation", "hue")}
    if any(v > 0 for v in jitter.values()):
        ops.append(T.ColorJitter(**jitter))
    ops += [T.ToTensor(), normalize]
    return T.Compose(ops)


def make_loaders(cfg: dict, metadata: pd.DataFrame, seed: int) -> dict[str, DataLoader]:
    """Membuat DataLoader train/val/test sesuai skema split pada konfigurasi."""
    col = split_column(cfg["data"].get("split_scheme", "official"))
    if col not in metadata.columns:
        raise KeyError(
            f"Kolom '{col}' belum ada di metadata. Jalankan scripts/audit_dataset.py "
            "untuk membuat split berkelompok."
        )
    root = cfg["data"]["root"]
    num_workers = int(cfg["data"].get("num_workers", 2))
    batch_size = int(cfg["train"]["batch_size"])
    limit = cfg["data"].get("limit_per_split")  # hanya untuk uji asap

    loaders = {}
    for split in ("train", "val", "test"):
        part = metadata[metadata[col] == split]
        if limit:
            part = part.groupby("label", group_keys=False).head(max(1, int(limit) // 5))
        dataset = PalmFruitDataset(part, root, build_transforms(cfg, train=(split == "train")))
        generator = torch.Generator()
        generator.manual_seed(seed)
        sampler = None
        shuffle = split == "train"
        if split == "train" and cfg["train"].get("balanced_sampler", False):
            # Sampler berbobot: setiap kelas diambil dengan peluang setara.
            counts = part["label"].value_counts().to_dict()
            weights = part["label"].map(lambda y: 1.0 / counts[y]).to_numpy()
            sampler = WeightedRandomSampler(
                torch.as_tensor(weights, dtype=torch.double),
                num_samples=len(weights),
                replacement=True,
                generator=generator,
            )
            shuffle = False
        loaders[split] = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
            worker_init_fn=seed_worker,
            generator=generator,
            drop_last=False,
            persistent_workers=num_workers > 0,
        )
    return loaders


def class_distribution(metadata: pd.DataFrame, col: str = "official_split") -> pd.DataFrame:
    """Tabel jumlah gambar per kelas x split (untuk audit dan laporan)."""
    table = pd.crosstab(metadata["label"], metadata[col])
    table.index = [f"{i} - {CLASS_NAMES_ID[i]}" for i in table.index]
    ordered = [c for c in ("train", "val", "test", "unassigned") if c in table.columns]
    table = table[ordered]
    table["total"] = table.sum(axis=1)
    table.loc["Total"] = table.sum(axis=0)
    return table


def to_numpy_image(tensor: torch.Tensor) -> np.ndarray:
    """Membalik normalisasi ImageNet -> array HxWx3 dalam [0, 1] (untuk visualisasi)."""
    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD).view(3, 1, 1)
    img = (tensor.cpu() * std + mean).clamp(0, 1)
    return img.permute(1, 2, 0).numpy()
