# CP01 – Tiga Kandidat Topik dan Keputusan

Matriks singkat (masalah, data, baseline, metrik, komputasi, risiko). Kandidat awal "Deteksi Timpa Teks" (dokumen tugas mingguan sebelumnya) **digugurkan** karena data harus dikumpulkan manual dari grup Facebook yang aksesnya terbatas, belum tentu aktif, dan berisiko etika/hak cipta.

| Aspek | **A. Kematangan buah sawit (dipilih)** | B. Kesegaran ikan dari citra mata | C. Segmentasi area banjir |
|---|---|---|---|
| Masalah | Grading TBS manual & subjektif; kelas berurutan | Konsumen sulit menilai kesegaran ikan | Menilai luas genangan dari foto warga lambat |
| Tugas CV | Klasifikasi ordinal 5 tingkat | Klasifikasi 3 tingkat kesegaran (× 8 spesies) | Segmentasi semantik 5 kelas + latar |
| Data | Mendeley 10.17632/424y96m6sw.1, 4.728 foto, CC BY 4.0, split resmi | Mendeley FFE 10.17632/xzyx7pbr3w.1, 4.392 foto, CC BY 4.0 | Mendeley 10.17632/3kzr8mt8s2.3, ±7.248 frame video, anotasi warna |
| Baseline | HSV + regresi logistik; EfficientNet-B0 + CE | CNN transfer learning + CE | U-Net kecil vs U-Net encoder pra-latih |
| Metrik | macro-F1, MAE, kesalahan ≥2 tingkat, QWK | macro-F1, akurasi lintas spesies | mIoU, IoU banjir, Dice |
| Komputasi | Ringan (Colab T4, ~2–3 jam total) | Ringan | Sedang (segmentasi resolusi tinggi) |
| Risiko utama | near-duplicate lintas split; ketidakseimbangan kelas | foto ikan yang sama di beberapa hari → bocor; pencahayaan per hari | frame berurutan sangat mirip; satu kota; konversi warna → mask |
| Gap/pertanyaan | ordinal vs nominal pada dataset baru + audit kebocoran | generalisasi ke spesies yang tidak dilihat | generalisasi lintas video |

## Keputusan

**Dipilih: A.** Alasan:
1. Data legal, terbuka, cukup besar, dan sudah diverifikasi isinya (lihat `02_Proposal_UTS/bukti_kelayakan_data.md`).
2. Ada pertanyaan teknis yang jelas dan dapat diuji secara terkontrol (CE vs CORN), sesuai panduan bagian 2 tentang *gap*.
3. Komputasi realistis untuk Colab gratis; demo CPU memungkinkan.
4. Relevansi tinggi untuk Indonesia (produsen sawit terbesar).

**Cadangan:** B (kesegaran ikan) bila dataset A tidak dapat diakses.
