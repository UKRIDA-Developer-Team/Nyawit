<!-- slides -->
# Klasifikasi Ordinal Kematangan Buah Sawit

**Hasil, Demo, dan Pembelajaran**

Kelompok 3 · Juanito Dante · Yedija Teofilus · Steven Iwan

Sidang UAS · Visi Komputer IF0PP006 · 2026/2027

---

## Masalah dan pertanyaan

- Grading TBS masih visual dan subjektif, padahal memengaruhi harga yang diterima pekebun
- Lima tingkat **berurutan**: Mentah → Setengah Matang → Matang Penuh → Terlalu Matang → Busuk
- **P1** CORN vs CE: apakah MAE dan kesalahan ≥ 2 tingkat turun tanpa mengorbankan macro-F1?
- **P2** Seberapa optimistis split resmi (acak) dibanding split blok?
- **P3** Apakah augmentasi hue merusak isyarat warna?

---

## Data dan audit

- 4.728 foto lapangan 256×256 (Kalimantan Tengah), CC BY 4.0; tidak seimbang (Matang Penuh 1.489 vs Busuk 411)
- Foto bernomor berurutan = tandan/sesi yang sama: **50%** pasangan berurutan sangat mirip (tanpa urutan: 5%)
- **92%** test resmi punya tetangga ±1 di train, sehingga **split blok** (3.434 / 658 / 636) menjadi split utama

![Kemiripan berurutan](../../results/audit/kemiripan_berurutan.png){: style="max-height:3.6in"}

---

## Baseline dan metode

![Diagram pipeline](../assets/diagram_pipeline.svg)

---

## Hasil utama (test split blok, 3 seed)

<!-- include: results/tabel_utama.md notitle -->

<!-- include: results/tabel_berpasangan.md notitle -->

**P1 negatif:** CORN tidak lebih baik daripada CE (MAE 0,121 lawan 0,111); selisihnya kecil, setara variasi antar seed.

---

## Split resmi vs split blok, dan eksperimen terkontrol

<!-- include: results/tabel_kebocoran.md notitle -->

<!-- include: results/tabel_terkontrol.md notitle -->

**P2:** split resmi menggelembungkan akurasi CNN ±5 poin. **P3:** augmentasi hue memperburuk MAE dan kesalahan berat di ketiga seed.

---

## Di mana model gagal

![Kesalahan berat](../../results/analisis_kesalahan/e3_cnn_corn_seed42/galeri_salah_berat.jpg)

Kesalahan berkelompok per sesi (10 kesalahan berat dari 5 blok); dugaan label ambigu dan close-up ekstrem; sampler seimbang (E5) tidak membantu.

---

## Grad-CAM: model melihat apa?

![Grad-CAM](../../results/analisis_kesalahan/e3_cnn_corn_seed42/galeri_gradcam.jpg)

---

## Demo

- `python app/app.py`: unggah foto → tingkat, peluang per tingkat, nilai harapan, Grad-CAM, latensi
- Peringatan bila keyakinan < 0,9 (ambang dipilih dari data validasi); cadangan CLI `scripts/predict.py`; video cadangan 2–3 menit

<!-- include: results/latensi/latensi_e3_cnn_corn_cpu.md notitle -->

---

## Batasan dan langkah berikutnya

- Satu wilayah dan satu tim pelabel; belum diuji pada foto tumpukan di PKS atau malam hari
- Tiga seed: belum cukup untuk uji signifikansi yang kuat; keyakinan model belum dikalibrasi
- Berikutnya: uji lintas dataset, kalibrasi (*temperature scaling*), kuantisasi untuk ponsel

---

## Kontribusi anggota

| Anggota | Kontribusi utama | Bukti |
|---|---|---|
| Yedija Teofilus | **[isi]** | logbook, commit |
| Juanito Dante | **[isi]** | logbook, commit |
| Steven Iwan | **[isi]** | logbook, commit |

**Terima kasih — pertanyaan?**
