"""Menyalin satu gambar test per kelas ke app/contoh/ sebagai contoh di demo Gradio.

Gambar diambil dari split TEST blok (`grouped_split`, split model utama E3),
sehingga tidak pernah dilihat saat pelatihan model demo; seed tetap. Gambar tetap milik penyusun dataset (CC BY 4.0, lihat README).

Contoh:
    python scripts/make_demo_examples.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.data import find_dataset_root, load_metadata  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Siapkan contoh gambar demo.")
    parser.add_argument("--metadata", default="data/processed/metadata.csv")
    parser.add_argument("--root", default="data/raw/Dataset")
    parser.add_argument("--out", default="app/contoh")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    df = load_metadata(args.metadata)
    root = find_dataset_root(args.root)
    out = resolve_path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    test = df[df["grouped_split"] == "test"]
    for label, name in enumerate(CLASS_NAMES_ID):
        row = test[test["label"] == label].sample(1, random_state=args.seed).iloc[0]
        dest = out / f"{label}_{name.replace(' ', '_').lower()}_{row['image_id']}"
        shutil.copy(root / row["rel_path"], dest)
        print(f"{name:<16} -> {dest.name}")


if __name__ == "__main__":
    main()
