# Folder data

Folder ini tidak di-commit (lihat `.gitignore`). Isi dibuat oleh skrip:

| Path | Dibuat oleh | Isi |
|---|---|---|
| `data/raw/Dataset/` | `python scripts/download_data.py` | Dataset.zip resmi yang sudah diekstrak (4.728 JPG + 3 berkas split) |
| `data/processed/metadata.csv` | `scripts/prepare_data.py`, lalu diperbarui `scripts/audit_dataset.py` | satu baris per gambar: label, split resmi, ukuran, dHash, MD5, kelompok near-duplicate, split berkelompok |
| `data/processed/hsv_features.npz` | `scripts/run_classic_baselines.py` | cache fitur HSV untuk baseline E1 |
| `data/synthetic/` | `scripts/make_synthetic_dataset.py` | data **sintetis** untuk uji asap saja |

Sumber data: Kamal, I. M., Mochammad, S., Nurahmi, L., Natawijaya, A., & Kalili, M. (2024).
*An Ordinal Dataset for Ripeness Level Classification in Oil Palm Fruit Quality Grading* (Versi 1).
Mendeley Data. https://doi.org/10.17632/424y96m6sw.1 - Lisensi CC BY 4.0.
