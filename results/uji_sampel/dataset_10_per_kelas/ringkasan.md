# Uji sampel

- Sumber foto: data uji split blok, 10 foto acak per kelas (seed 42)
- Model: e3_cnn_corn
- Jumlah foto: 50
- Ambang keyakinan rendah: 0.9

**Akurasi: 94%** (47 dari 50); meleset paling jauh 1 tingkat: 98%.

| Kelas | Jumlah | Benar | Prediksi yang salah |
|---|---|---|---|
| Mentah | 10 | 10 | - |
| Setengah Matang | 10 | 9 | Matang Penuh (1) |
| Matang Penuh | 10 | 10 | - |
| Terlalu Matang | 10 | 9 | Setengah Matang (1) |
| Busuk | 10 | 9 | Terlalu Matang (1) |

Foto berkeyakinan rendah (< 0.9): 6.
- Immature736.jpg: prediksi Mentah (0.81), kedua Setengah Matang (0.19)
- PartiallyRipe488.jpg: prediksi Matang Penuh (0.82), kedua Mentah (0.11)
- OverRipe391.jpg: prediksi Terlalu Matang (0.63), kedua Setengah Matang (0.36)
- OverRipe9.jpg: prediksi Setengah Matang (0.52), kedua Terlalu Matang (0.48)
- Decayed324.jpg: prediksi Busuk (0.68), kedua Mentah (0.26)
- Decayed331.jpg: prediksi Terlalu Matang (0.04), kedua Mentah (0.43)

Cara membaca Grad-CAM: area merah/kuning paling memengaruhi prediksi. Penjelasan yang wajar berada di tandan buah; bila panas berada di latar (tanah, daun, langit), prediksi patut dicurigai walaupun benar.
