# Analisis kesalahan: e2_cnn_ce_seed42

- Gambar test: 636; salah: 60 (9.4%).
- Kesalahan tetangga (1 tingkat): 51; kesalahan berat (≥2 tingkat): 9.
- Tingkat kesalahan pada gambar yang punya near-duplicate di train: 0.0% (n=2); tanpa near-duplicate: 9.5% (n=634).

Akurasi per rentang keyakinan (untuk menentukan ambang peringatan di demo):

| Keyakinan | n | Akurasi |
|---|---|---|
| (-0.001, 0.5] | 0 | nan |
| (0.5, 0.7] | 40 | 0.525 |
| (0.7, 0.9] | 66 | 0.758 |
| (0.9, 1.0] | 530 | 0.953 |

Pasangan yang paling sering tertukar:

| Label | Prediksi | Selisih | Jumlah |
|---|---|---|---|
| Matang Penuh | Setengah Matang | 1 | 16 |
| Terlalu Matang | Matang Penuh | 1 | 8 |
| Mentah | Setengah Matang | 1 | 7 |
| Setengah Matang | Matang Penuh | 1 | 7 |
| Matang Penuh | Terlalu Matang | 1 | 5 |
| Terlalu Matang | Busuk | 1 | 5 |
| Setengah Matang | Mentah | 1 | 3 |
| Setengah Matang | Terlalu Matang | 2 | 3 |

Kelas dengan recall terendah: **Terlalu Matang** (recall 0.848, n=105).

Kategori penyebab diisi manual pada `kategori_manual.csv` setelah melihat galeri.
