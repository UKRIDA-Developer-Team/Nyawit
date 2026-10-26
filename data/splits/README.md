# Split beku

`grouped_split.csv` adalah **split blok** (image_id → train/val/test) yang dipakai melatih semua model E0–E7 di Google Colab: 3.434 latih / 658 validasi / 636 uji.

Mengapa dibekukan: `StratifiedGroupKFold` (scikit-learn) mengacak kelompok secara berbeda sejak versi 1.8. Dengan input dan seed yang sama, scikit-learn ≤ 1.7 menghasilkan split ini, sedangkan ≥ 1.8 menghasilkan split lain (3.368/680/680). Agar hasil dapat direproduksi di mesin mana pun, `scripts/audit_dataset.py` memakai berkas ini bila daftar gambarnya cocok, alih-alih menghitung ulang.

Menghitung ulang (tidak disarankan; hasil bergantung versi): `python scripts/audit_dataset.py --regenerate-split`.
