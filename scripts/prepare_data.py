"""Membuat tabel metadata (satu baris per gambar) dari dataset yang sudah diekstrak.

Kolom keluaran: image_id, rel_path, label, label_name, official_split,
width, height, dhash, md5. Berkas ini menjadi satu-satunya sumber kebenaran
untuk loader, audit, dan baseline, sehingga semua eksperimen memakai daftar
gambar dan split yang sama persis.

Contoh:
    python scripts/prepare_data.py
    python scripts/prepare_data.py --root data/synthetic/Dataset --out data/synthetic/metadata.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sawit.data import build_metadata, class_distribution  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Bangun metadata dataset.")
    parser.add_argument("--root", default="data/raw/Dataset", help="Folder berisi Images/ dan Train_val_test_split/")
    parser.add_argument("--out", default="data/processed/metadata.csv")
    args = parser.parse_args()

    df = build_metadata(args.root)
    out = resolve_path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    print(f"Metadata: {len(df)} gambar -> {out}")
    print(class_distribution(df).to_string())
    unassigned = (df["official_split"] == "unassigned").sum()
    if unassigned:
        print(f"PERINGATAN: {unassigned} gambar tidak tercantum di berkas split resmi.")


if __name__ == "__main__":
    main()
