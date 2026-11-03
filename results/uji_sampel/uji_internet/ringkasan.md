# Uji sampel

- Sumber foto: folder `data/uji_internet`
- Model: e3_cnn_corn
- Jumlah foto: 12
- Ambang keyakinan rendah: 0.9

**Akurasi: 33%** (4 dari 12); meleset paling jauh 1 tingkat: 83%.

| Kelas | Jumlah | Benar | Prediksi yang salah |
|---|---|---|---|
| Mentah | 4 | 4 | - |
| Setengah Matang | 4 | 0 | Mentah (4) |
| Matang Penuh | 4 | 0 | Setengah Matang (2), Mentah (2) |

Foto berkeyakinan rendah (< 0.9): 2.
- FullyRipe_2.jpg: prediksi Setengah Matang (0.89), kedua Mentah (0.10)
- FullyRipe_4.jpg: prediksi Mentah (0.88), kedua Setengah Matang (0.12)

Cara membaca Grad-CAM: area merah/kuning paling memengaruhi prediksi. Penjelasan yang wajar berada di tandan buah; bila panas berada di latar (tanah, daun, langit), prediksi patut dicurigai walaupun benar.
