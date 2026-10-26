"""Bukti kelayakan awal (CP06): memeriksa isi Dataset.zip TANPA mengunduh seluruhnya.

Skrip membaca direktori pusat (central directory) arsip ZIP di server Mendeley
memakai HTTP Range request (hanya ~1-2 MB yang diambil), lalu melaporkan:
- daftar folder dan jumlah gambar per kelas;
- isi tiga berkas split resmi dan distribusi kelas di setiap split.

Hasil ditulis ke docs/02_Proposal_UTS/bukti_kelayakan_data.md.

Contoh:
    python scripts/inspect_remote_zip.py
"""

from __future__ import annotations

import collections
import io
import re
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sawit.constants import CLASS_NAMES_ID, CLASS_PREFIXES, DATASET_SIZE_BYTES, DATASET_URL  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402

HEADERS = {"User-Agent": "Mozilla/5.0 (proyek-visi-komputer)"}


class RemoteFile(io.RawIOBase):
    """Objek berkas baca-saja yang mengambil potongan byte lewat HTTP Range."""

    def __init__(self, url: str, size: int):
        self.url, self.size, self.pos, self.bytes_fetched = url, size, 0, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else (self.pos + offset if whence == 1 else self.size + offset)
        return self.pos

    def tell(self):
        return self.pos

    def readinto(self, buffer):
        if self.pos >= self.size:
            return 0
        end = min(self.pos + len(buffer), self.size) - 1
        request = urllib.request.Request(self.url, headers={**HEADERS, "Range": f"bytes={self.pos}-{end}"})
        data = urllib.request.urlopen(request).read()
        buffer[:len(data)] = data
        self.pos += len(data)
        self.bytes_fetched += len(data)
        return len(data)


def resolve_redirect(url: str) -> str:
    """Mendapatkan URL akhir (S3) setelah redirect dari Mendeley."""
    request = urllib.request.Request(url, headers={**HEADERS, "Range": "bytes=0-0"})
    with urllib.request.urlopen(request) as response:
        return response.geturl()


def main() -> None:
    remote = RemoteFile(resolve_redirect(DATASET_URL), DATASET_SIZE_BYTES)
    archive = zipfile.ZipFile(io.BufferedReader(remote, buffer_size=1 << 16))
    names = [n for n in archive.namelist() if not n.endswith("/")]
    images = [n for n in names if n.lower().endswith(".jpg")]
    per_folder = collections.Counter(n.split("/")[-2] for n in images)

    lines = ["# Bukti Kelayakan Data (dibuat otomatis)", "",
             f"Tanggal pemeriksaan: {date.today().isoformat()}. Dibuat oleh `scripts/inspect_remote_zip.py` "
             "dengan membaca direktori ZIP di server Mendeley Data (HTTP Range), tanpa mengunduh seluruh arsip.", "",
             f"- Ukuran arsip: {DATASET_SIZE_BYTES:,} byte. Total entri berkas: {len(names)}; gambar JPG: {len(images)}.",
             "", "## Jumlah gambar per folder kelas", "", "| Folder | Jumlah |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(per_folder.items())]

    lines += ["", "## Split resmi (Train_val_test_split/*.txt)", "",
              "| Split | " + " | ".join(CLASS_NAMES_ID) + " | Total |", "|" + "---|" * (len(CLASS_NAMES_ID) + 2)]
    all_names = {n.split("/")[-1] for n in images}
    for split_name in ("Training", "Validation", "Testing"):
        txt = archive.read(f"Dataset/Train_val_test_split/{split_name}.txt").decode("utf-8", "replace")
        entries = [line.strip() for line in txt.splitlines() if line.strip()]
        counts = collections.Counter(re.sub(r"\d+\.jpg$", "", e) for e in entries)
        missing = len(set(entries) - all_names)
        lines.append(f"| {split_name} | " + " | ".join(str(counts.get(p, 0)) for p in CLASS_PREFIXES)
                     + f" | {len(entries)} |" + (f" (tidak ditemukan: {missing})" if missing else ""))
    lines += ["", f"Data yang diambil dari server untuk pemeriksaan ini: {remote.bytes_fetched / 1e6:.2f} MB.", ""]

    out = resolve_path("docs/02_Proposal_UTS/bukti_kelayakan_data.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Tersimpan: {out}")


if __name__ == "__main__":
    main()
