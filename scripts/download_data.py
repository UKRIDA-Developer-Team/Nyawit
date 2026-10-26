"""Mengunduh dan mengekstrak dataset resmi dari Mendeley Data.

Dataset : An Ordinal Dataset for Ripeness Level Classification in Oil Palm
          Fruit Quality Grading (Kamal dkk., 2024), DOI 10.17632/424y96m6sw.1
Lisensi : CC BY 4.0 (wajib mencantumkan atribusi; lihat README).
Berkas  : Dataset.zip, 272.151.984 byte (~260 MB), SHA-256 diverifikasi.

Contoh:
    python scripts/download_data.py                 # unduh + ekstrak ke data/raw/
    python scripts/download_data.py --zip ~/Dataset.zip   # pakai zip yang sudah diunduh manual
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sawit.constants import DATASET_PAGE, DATASET_SHA256, DATASET_SIZE_BYTES, DATASET_URL  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (proyek-visi-komputer)"})
    with urllib.request.urlopen(request) as response, open(dest, "wb") as out:
        total = int(response.headers.get("Content-Length", 0)) or DATASET_SIZE_BYTES
        done = 0
        while True:
            chunk = response.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            print(f"\r  mengunduh {done / 1e6:6.1f} / {total / 1e6:.1f} MB ({100 * done / total:5.1f}%)", end="")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Unduh dataset kematangan sawit (Mendeley Data).")
    parser.add_argument("--dest", default="data/raw", help="Folder tujuan ekstraksi.")
    parser.add_argument("--zip", default=None, help="Path Dataset.zip yang sudah diunduh manual.")
    parser.add_argument("--keep-zip", action="store_true", help="Jangan hapus zip setelah ekstraksi.")
    args = parser.parse_args()

    dest = resolve_path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    if (dest / "Dataset" / "Images").is_dir():
        print(f"Dataset sudah ada di {dest / 'Dataset'}; tidak diunduh ulang.")
        return

    zip_path = Path(args.zip).expanduser() if args.zip else dest / "Dataset.zip"
    if not zip_path.exists():
        print(f"Mengunduh dari Mendeley Data ({DATASET_PAGE}) ...")
        download(DATASET_URL, zip_path)

    print("Memverifikasi SHA-256 ...")
    digest = sha256_of(zip_path)
    if digest != DATASET_SHA256:
        raise SystemExit(
            f"SHA-256 tidak cocok!\n  diharapkan {DATASET_SHA256}\n  didapat    {digest}\n"
            "Berkas mungkin rusak atau versi dataset berubah. Hapus zip lalu unduh ulang."
        )
    print("  cocok.")

    print(f"Mengekstrak ke {dest} ...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    if not args.keep_zip and not args.zip:
        zip_path.unlink()
    n_images = sum(1 for _ in (dest / "Dataset" / "Images").rglob("*.jpg"))
    print(f"Selesai: {n_images} gambar di {dest / 'Dataset'}")


if __name__ == "__main__":
    main()
