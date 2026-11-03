# Uji sampel

- Sumber foto: folder `data/uji_peer_salinan_dataset`
- Model: e3_cnn_corn
- Jumlah foto: 8
- Ambang keyakinan rendah: 0.9

**Akurasi: 100%** (8 dari 8); meleset paling jauh 1 tingkat: 100%.

| Kelas | Jumlah | Benar | Prediksi yang salah |
|---|---|---|---|
| Terlalu Matang | 4 | 4 | - |
| Busuk | 4 | 4 | - |

Foto berkeyakinan rendah (< 0.9): 0.

Cara membaca Grad-CAM: area merah/kuning paling memengaruhi prediksi. Penjelasan yang wajar berada di tandan buah; bila panas berada di latar (tanah, daun, langit), prediksi patut dicurigai walaupun benar.
