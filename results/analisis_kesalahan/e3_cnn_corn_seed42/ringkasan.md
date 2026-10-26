# Analisis kesalahan: e3_cnn_corn_seed42

- Gambar test: 636; salah: 65 (10.2%).
- Kesalahan tetangga (1 tingkat): 55; kesalahan berat (≥2 tingkat): 10.
- Tingkat kesalahan pada gambar yang punya near-duplicate di train: 0.0% (n=2); tanpa near-duplicate: 10.3% (n=634).

Akurasi per rentang keyakinan (untuk menentukan ambang peringatan di demo):

| Keyakinan | n | Akurasi |
|---|---|---|
| (-0.001, 0.5] | 3 | 0.000 |
| (0.5, 0.7] | 36 | 0.667 |
| (0.7, 0.9] | 58 | 0.690 |
| (0.9, 1.0] | 539 | 0.941 |

Pasangan yang paling sering tertukar:

| Label | Prediksi | Selisih | Jumlah |
|---|---|---|---|
| Terlalu Matang | Matang Penuh | 1 | 14 |
| Matang Penuh | Setengah Matang | 1 | 10 |
| Setengah Matang | Matang Penuh | 1 | 9 |
| Matang Penuh | Terlalu Matang | 1 | 8 |
| Terlalu Matang | Busuk | 1 | 6 |
| Setengah Matang | Terlalu Matang | 2 | 4 |
| Mentah | Setengah Matang | 1 | 4 |
| Busuk | Terlalu Matang | 1 | 4 |

Kelas dengan recall terendah: **Terlalu Matang** (recall 0.790, n=105).

Kategori penyebab diisi manual pada `kategori_manual.csv` setelah melihat galeri.
