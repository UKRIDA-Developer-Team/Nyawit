# Uji sampel

- Sumber foto: folder `data/uji_internet_2`
- Model: e3_cnn_corn
- Jumlah foto: 16
- Ambang keyakinan rendah: 0.9

**Akurasi: 50%** (8 dari 16); meleset paling jauh 1 tingkat: 81%.

| Kelas | Jumlah | Benar | Prediksi yang salah |
|---|---|---|---|
| Mentah | 4 | 0 | Setengah Matang (2), Busuk (1), Terlalu Matang (1) |
| Setengah Matang | 4 | 4 | - |
| Matang Penuh | 4 | 1 | Setengah Matang (3) |
| Terlalu Matang | 4 | 3 | Setengah Matang (1) |

Foto berkeyakinan rendah (< 0.9): 7.
- Unripe_3.jpg: prediksi Busuk (0.75), kedua Terlalu Matang (0.22)
- Under_Ripe_2.jpg: prediksi Setengah Matang (0.84), kedua Matang Penuh (0.15)
- Under_Ripe_3.jpg: prediksi Setengah Matang (0.43), kedua Matang Penuh (0.29)
- Ripe_1.jpg: prediksi Setengah Matang (0.70), kedua Matang Penuh (0.29)
- Ripe_4.jpg: prediksi Matang Penuh (0.84), kedua Setengah Matang (0.11)
- Over_Ripe_2.jpg: prediksi Terlalu Matang (0.59), kedua Setengah Matang (0.34)
- Over_Ripe_3.jpg: prediksi Setengah Matang (0.59), kedua Terlalu Matang (0.38)

Cara membaca Grad-CAM: area merah/kuning paling memengaruhi prediksi. Penjelasan yang wajar berada di tandan buah; bila panas berada di latar (tanah, daun, langit), prediksi patut dicurigai walaupun benar.
