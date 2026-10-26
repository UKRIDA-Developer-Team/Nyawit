"""Membuat dataset SINTETIS kecil dengan struktur folder yang sama persis dengan
Dataset.zip resmi. Dipakai HANYA untuk uji asap (smoke test) dan unit test agar
pipeline dapat diperiksa tanpa mengunduh 260 MB. Hasilnya bukan data penelitian
dan tidak boleh dilaporkan sebagai hasil eksperimen.

Contoh:
    python scripts/make_synthetic_dataset.py --out data/synthetic --per-class 30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from sawit.constants import CLASS_FOLDERS, CLASS_PREFIXES, SPLIT_FILES  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402

# Warna dasar "tandan" per tingkat: ungu kehitaman -> merah -> oranye -> coklat -> kelabu.
BASE_COLORS = [(60, 30, 50), (140, 40, 30), (230, 110, 20), (150, 80, 30), (90, 85, 75)]


def make_image(label: int, rng: np.random.Generator, size: int = 96) -> Image.Image:
    bg = rng.integers(40, 120, size=3)
    arr = np.clip(bg + rng.normal(0, 18, (size, size, 3)), 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    color = np.clip(np.array(BASE_COLORS[label]) + rng.normal(0, 15, 3), 0, 255).astype(int)
    cx, cy = rng.integers(size // 3, 2 * size // 3, size=2)
    rx, ry = rng.integers(size // 5, size // 3, size=2)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=tuple(int(c) for c in color))
    for _ in range(25):  # "buah" kecil di permukaan tandan
        px, py = cx + rng.integers(-rx, rx), cy + rng.integers(-ry, ry)
        r = int(rng.integers(2, 5))
        shade = tuple(int(c) for c in np.clip(color + rng.normal(0, 25, 3), 0, 255))
        draw.ellipse([px - r, py - r, px + r, py + r], fill=shade)
    return img.filter(ImageFilter.GaussianBlur(0.6))


def main() -> None:
    parser = argparse.ArgumentParser(description="Buat dataset sintetis untuk uji asap.")
    parser.add_argument("--out", default="data/synthetic")
    parser.add_argument("--per-class", type=int, default=30)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    root = resolve_path(args.out) / "Dataset"
    split_lists = {s: [] for s in SPLIT_FILES}
    for label, (folder, prefix) in enumerate(zip(CLASS_FOLDERS, CLASS_PREFIXES)):
        class_dir = root / "Images" / folder
        class_dir.mkdir(parents=True, exist_ok=True)
        for i in range(args.per_class):
            name = f"{prefix}{i}.jpg"
            make_image(label, rng).save(class_dir / name, quality=90)
            frac = i / args.per_class
            split = "train" if frac < 0.6 else ("val" if frac < 0.8 else "test")
            split_lists[split].append(name)
        # Satu near-duplicate lintas split (train -> test) untuk menguji audit kebocoran.
        twin = f"{prefix}{args.per_class}.jpg"
        with Image.open(class_dir / f"{prefix}0.jpg") as src:
            arr = np.asarray(src, dtype=np.int16)
        noisy = np.clip(arr + rng.integers(-2, 3, arr.shape), 0, 255).astype(np.uint8)
        Image.fromarray(noisy).save(class_dir / twin, quality=90)
        split_lists["test"].append(twin)

    split_dir = root / "Train_val_test_split"
    split_dir.mkdir(parents=True, exist_ok=True)
    for split, filename in SPLIT_FILES.items():
        (split_dir / filename).write_text("\n".join(sorted(split_lists[split])) + "\n", encoding="utf-8")
    total = sum(len(v) for v in split_lists.values())
    print(f"Dataset sintetis: {total} gambar di {root}")


if __name__ == "__main__":
    main()
