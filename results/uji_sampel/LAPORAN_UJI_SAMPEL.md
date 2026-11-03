# Uji Sampel dan Penjelasan Grad-CAM

Tindak lanjut masukan asisten dosen (November 2026):

1. Uji inferensi pada 10 foto per kelas.
2. Uji pada sekitar 20 foto dari internet untuk memastikan perangkat lunak berjalan baik.
3. Tambahkan *explainable AI* untuk menjelaskan alasan prediksi.

**Pengaturan semua uji:**

- Model E3 (EfficientNet-B0 + CORN, seed 42), checkpoint `outputs/runs/e3_cnn_corn/seed42/best.pt`.
- Pra-pemrosesan sama dengan demo: *resize* 256, *center crop* 224, normalisasi ImageNet.
- Penjelasan dengan Grad-CAM pada lapisan konvolusi terakhir, untuk tingkat yang diprediksi.
- Ambang "keyakinan rendah" 0,9.

## 1. Ringkasan hasil

| Uji | Sumber foto | Jumlah | Benar | Akurasi | Meleset ≤ 1 tingkat | MAE (tingkat) | Grad-CAM pada buah? |
|---|---|---|---|---|---|---|---|
| A | Data uji split blok, 10 per kelas | 50 | 47 | **94%** | 98% | 0,08 | Ya |
| B | Internet set 2: tandan sudah dipanen | 16 | 8 | **50%** | 81% | 0,88 | Ya |
| C | Internet set 1: tandan masih di pohon | 12 | 4 | **33%** | 83% | 0,83 | Sering tidak |

**Foto yang dikeluarkan.** 12 foto kiriman tim (semua foto *Over Ripe*/*Decayed* set 1 dan *Decayed* set 2) ternyata **identik byte demi byte** dengan foto di dataset kami (MD5 sama, jarak dHash 0). 10 di antaranya berasal dari data latih, sehingga foto-foto ini tidak dipakai sebagai uji. Sebagai pembanding, model menebak benar 8/8 pada foto salinan set 1, wajar karena foto itu sudah pernah dilihat.

## 2. Rincian per kelas

| Kelas | A (dataset) | B (internet, dipanen) | C (internet, di pohon) |
|---|---|---|---|
| Mentah | 10/10 | 0/4 (→ Setengah Matang ×2, Terlalu Matang, Busuk) | 4/4 |
| Setengah Matang | 9/10 (→ Matang Penuh) | 4/4 | 0/4 (→ Mentah ×4) |
| Matang Penuh | 10/10 | 1/4 (→ Setengah Matang ×3) | 0/4 (→ Setengah Matang ×2, Mentah ×2) |
| Terlalu Matang | 9/10 (→ Setengah Matang) | 3/4 (→ Setengah Matang) | - |
| Busuk | 9/10 (→ Terlalu Matang) | - | - |

Tanda "-" berarti tidak ada foto valid untuk kelas itu.

**Peringatan keyakinan rendah (< 0,9):**

| Uji | Prediksi salah | Salah dan ditandai | Benar tetapi ditandai |
|---|---|---|---|
| A | 3 | 3 | 3 |
| B | 8 | 3 | 4 |
| C | 8 | 2 | 0 |

## 3. Temuan

1. **Pada foto sejenis data latih, model andal.** Pada uji A, 47 dari 50 foto benar dan semua kesalahan tertangkap oleh peringatan keyakinan rendah. Hasil ini sejalan dengan hasil uji penuh (akurasi sekitar 0,90).
2. **Kinerja turun pada foto dari sumber lain (uji B).** Grad-CAM tetap berada pada tandan, jadi model melihat bagian yang benar. Sebagian besar kesalahan kemungkinan berasal dari **perbedaan definisi label**. Foto berukuran 640×640 dengan 4 nama kelas (*Unripe*, *Under Ripe*, *Ripe*, *Over Ripe*) tampaknya berasal dari dataset lain. Misalnya foto "Ripe" berwarna merah-ungu gelap dengan sedikit brondolan, yang menurut standar dataset kami tergolong Setengah Matang, dan model memang menebak demikian dengan keyakinan 0,99–1,00.
3. **Model gagal pada kondisi pengambilan foto yang berbeda (uji C).** Semua foto adalah tandan yang **masih di pohon**, sedangkan data latih berisi tandan yang sudah dipanen di tanah. Semua kesalahan berarah sama, yaitu model menebak lebih mentah. Grad-CAM menunjukkan perhatian model jatuh pada **batang dan pelepah**, bukan buah. Brondolan, isyarat utama kematangan dalam dataset, juga tidak terlihat pada tandan yang masih tergantung.
4. **Tandan yang sangat gelap tertukar antara Mentah dan Busuk.** Foto Unripe_3 (uji B), tandan hitam yang jelas mentah, diprediksi Busuk (0,75). Pada Decayed331 (uji A), peluang terbagi antara Mentah (0,43) dan Busuk (0,49). Kedua kelas ekstrem ini sama-sama berwarna gelap.
5. **Sifat CORN saat ragu antara dua tingkat yang berjauhan.** Pada Decayed331, CORN memilih tingkat tengah (Terlalu Matang, peluang 0,04) karena prediksinya adalah median distribusi peluang, bukan kelas dengan peluang terbesar. Peringatan keyakinan rendah menangkap kasus ini.
6. **Pada foto yang asing, model cenderung menebak tingkat tengah dan tetap yakin.** Pada uji B, 10 dari 16 prediksi adalah Setengah Matang. Pada uji C, sebagian besar kesalahan berkeyakinan 0,95–1,00. Artinya, ambang 0,9 efektif untuk foto sejenis data latih, tetapi **tidak dapat diandalkan untuk foto di luar kondisi itu**.

## 4. Lapisan *explainable AI*

- **Grad-CAM** sudah tersedia di demo web: peta panas di atas foto, dengan area merah atau kuning yang paling memengaruhi prediksi. Demo juga menampilkan peluang tiap tingkat, nilai harapan tingkat, peringatan keyakinan rendah, dan saran per tingkat.
- **`scripts/uji_sampel.py` (baru)** menjalankan uji secara massal. Untuk setiap foto, skrip menyimpan foto berdampingan dengan Grad-CAM, label, prediksi, dan pilihan kedua model.
- **Perbaikan:** skrip baris perintah (`predict.py`, `uji_sampel.py`, `error_analysis.py`) kini menjelaskan tingkat yang **ditampilkan**, sama seperti demo. Sebelumnya, pada CORN, peta panas bisa menjelaskan kelas dengan peluang terbesar walaupun kelas itu bukan tingkat yang diprediksi. Hasil uji tidak berubah, dan 21 uji otomatis tetap lulus.
- **Cara membaca:** panas pada tandan berarti penjelasan wajar. Panas pada latar (batang, pelepah, tanah) berarti prediksi patut dicurigai walaupun benar.

## 5. Keterbatasan

- **Sampel kecil.** Uji B dan C hanya berisi 16 dan 12 foto, sehingga satu foto mengubah akurasi 6–8 poin. Hasil ini indikatif, bukan estimasi kinerja yang presisi.
- **Label foto internet tidak terverifikasi.** Label mengikuti nama berkas dari sumbernya, bukan definisi kelas dataset kami, dan sumber serta lisensi foto belum dicatat.
- **Belum ada foto Busuk yang valid dari luar dataset**, dan foto Terlalu Matang hanya ada di uji B.
- **Beberapa foto pada uji C tampak berasal dari video yang sama** (misalnya FullyRipe_1 dan _2), sehingga jumlah foto yang benar-benar independen lebih kecil.
- **Grad-CAM hanya menunjukkan lokasi**, bukan ciri apa yang dipakai (warna, brondolan, atau tekstur), dan resolusinya kasar (7×7 sebelum diperbesar).
- **Ruang lingkup model** tetap: satu tandan yang sudah dipanen, difoto dari dekat, dalam kondisi serupa dengan perkebunan Kalimantan Tengah.

## 6. Kesimpulan

Perangkat lunak berjalan dengan benar, dan pada foto sejenis data latih model memberi hasil yang andal (94%) dengan penjelasan Grad-CAM yang masuk akal. Di luar kondisi itu, kinerja turun. Penurunan terbesar terjadi pada tandan yang masih di pohon, dan Grad-CAM memperlihatkan penyebabnya: perhatian model tidak berada pada buah. Ambang keyakinan saja tidak cukup untuk mendeteksi foto di luar ruang lingkup. Karena itu, demo harus menyatakan dengan jelas bahwa foto yang diharapkan adalah **satu tandan yang sudah dipanen**.

## 7. Langkah berikutnya

1. Kumpulkan sekitar 4 foto per kelas yang benar-benar baru dari luar dataset, terutama Busuk dan Terlalu Matang. Catat sumbernya di `data/uji_internet/SUMBER.csv`.
2. Minta dua anggota melabeli ulang foto uji B dengan definisi kelas dataset kami, untuk memisahkan kesalahan model dari perbedaan definisi label.
3. Opsional: tambahkan petunjuk foto di demo, dan pertimbangkan pemeriksaan "foto di luar ruang lingkup" yang tidak hanya bergantung pada keyakinan model.

## Berkas dan cara mengulang

| Uji | Folder hasil | Foto (tidak diunggah ke Git) |
|---|---|---|
| A | `results/uji_sampel/dataset_10_per_kelas/` (5 galeri, satu per kelas) | `data/raw/` |
| B | `results/uji_sampel/uji_internet_2/` | `data/uji_internet_2/` |
| C | `results/uji_sampel/uji_internet/` | `data/uji_internet/` |
| Salinan dataset | `results/uji_sampel/uji_peer_salinan_dataset/` | `data/uji_peer_salinan_dataset/` |

```bash
python scripts/uji_sampel.py --dataset 10
python scripts/uji_sampel.py --folder data/uji_internet_2
python scripts/uji_sampel.py --folder data/uji_internet
```
