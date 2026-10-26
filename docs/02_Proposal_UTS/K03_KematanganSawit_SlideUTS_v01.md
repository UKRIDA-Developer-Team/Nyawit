<!-- slides -->
# Klasifikasi Ordinal Kematangan Buah Sawit

**Cross-Entropy vs. CORN pada EfficientNet-B0**

Kelompok 3 · Juanito Dante · Yedija Teofilus · Steven Iwan

Sidang Proposal UTS · Visi Komputer IF0PP006 · 2026/2027

---

## 1. Masalah: grading TBS masih manual dan subjektif

- Mutu **tandan buah segar (TBS)** dinilai dari tingkat kematangan, dan nilai ini memengaruhi harga yang diterima pekebun
- Penilaian dilakukan secara visual oleh petugas, sehingga hasilnya bisa berbeda antarpetugas dan memicu sengketa
- Isyaratnya visual (warna, tekstur, brondolan), sehingga cocok untuk **visi komputer** dengan kamera ponsel
- **Penerima manfaat**: pekebun/pengepul, petugas sortir (pendapat kedua), peneliti (benchmark terbuka)

**Batas klaim:** alat bantu dan tolok ukur penelitian, **bukan** pengganti grader dan belum siap pakai di pabrik.

---

## 2. Bukti kebutuhan: kelasnya berurutan

**Mentah → Setengah Matang → Matang Penuh → Terlalu Matang → Busuk**

- Salah 1 tingkat ≠ salah 3 tingkat, tetapi **cross-entropy** menghukum keduanya sama berat
- Penyusun dataset merancangnya untuk *ordinal regression* (Kamal dkk., 2024)
- Pekerjaan sebelumnya umumnya memperlakukannya sebagai kelas nominal (mis. Suharjito dkk., 2021)

**P1 (utama):** dengan semua faktor lain sama, apakah loss ordinal **CORN** menurunkan **MAE** dan **kesalahan ≥ 2 tingkat** dibanding CE, tanpa menurunkan macro-F1 > 0,02?

**P2:** seberapa optimistis split resmi (acak) dibanding split blok? **P3:** apakah augmentasi hue merusak isyarat warna?

---

## 3. Data: Ordinal Oil Palm Ripeness (Mendeley, CC BY 4.0)

| Split | Mentah | Setengah | Matang | Terlalu | Busuk | Total |
|---|---|---|---|---|---|---|
| Train | 530 | 982 | 1.042 | 465 | 287 | 3.306 |
| Val | 113 | 210 | 222 | 98 | 61 | 704 |
| Test | 115 | 213 | 225 | 102 | 63 | 718 |

- 4.728 foto lapangan 256×256, Kalimantan Tengah, beragam perangkat dan cahaya; DOI 10.17632/424y96m6sw.1
- **Risiko**: tidak seimbang (3,6×), foto beruntun dari tandan yang sama, satu wilayah, label tingkat bertetangga ambigu
- **Kendali**: macro-F1 + recall per kelas · audit kebocoran (berikut) · split blok sebagai split utama

---

## 3b. Audit data: split resmi bocor

![Kemiripan berurutan](../../results/audit/kemiripan_berurutan.png){: style="max-height:3.6in"}

- **50%** pasangan foto bernomor berurutan sangat mirip (tanpa urutan: 5%), sehingga foto berdekatan berasal dari tandan/sesi yang sama
- **92%** gambar test resmi punya tetangga bernomor ±1 di train
- **Split blok** (blok 20 nomor, StratifiedGroupKFold): 3.434 / 658 / 636; hanya 8,3% test di batas blok

---

## 4. Baseline dan metode

![Diagram pipeline](../assets/diagram_pipeline.svg)

---

## 5. Evaluasi dan eksperimen terkontrol

**Metrik:** akurasi, **macro-F1**, P/R per kelas, confusion matrix + ordinal: **MAE**, **kesalahan berat**, akurasi ±1, **QWK** · rerata ± sd dari 3 seed · split utama = **split blok**

| ID | Perlakuan | Menjawab |
|---|---|---|
| E0 / E1 | kelas mayoritas / HSV + regresi logistik | batas bawah, "warna saja" |
| **E2 vs E3** | CE vs **CORN** (satu-satunya perbedaan) | **P1** |
| E3 vs E4 | + hue/saturation jitter | P3 |
| E3 vs E5 | + sampler seimbang | kelas minoritas |
| E6 vs E2, E7 vs E3 | split resmi vs split blok | **P2** |

Checkpoint dipilih dari **macro-F1 validasi** · test hanya disentuh sekali · analisis kesalahan + Grad-CAM

---

## 6. Kelayakan awal (bukti)

- Dataset diunduh (SHA-256 cocok); audit + baseline klasik sudah berjalan pada **data asli**:

| Baseline | Split | Akurasi | Macro-F1 | MAE |
|---|---|---|---|---|
| E0 mayoritas | blok | 0,314 | 0,096 | 0,892 |
| E1 HSV + reg. logistik | blok | 0,679 | 0,657 | 0,506 |
| E1 HSV + reg. logistik | resmi | 0,689 | 0,681 | 0,468 |

- Kode CNN sudah diuji pada data asli (beberapa batch, CPU) dan pada data sintetis; **21 uji lulus**
- Komputasi: Colab T4, ~8–12 menit/run, 18 run CNN ≈ 2,5–3,5 jam GPU

**Ukuran sukses:** E2 > E1 (minimum) · E3 < E2 pada MAE & kesalahan berat di ≥ 2/3 seed (target) · latensi CPU < 200 ms

---

## 7. Risiko, alternatif, dan pembagian kerja

| Risiko | Rencana |
|---|---|
| Kuota GPU habis | 1 seed dulu → tambah seed; cadangan Kaggle |
| Kebocoran split resmi (**terjadi**) | split blok = split utama (sudah diterapkan) |
| CORN tidak lebih baik | dilaporkan jujur + analisis penyebab |
| Demo gagal | CLI `predict.py` + video cadangan |

| Anggota | Peran |
|---|---|
| Yedija | koordinator · dokumentasi & demo |
| Juanito | data · audit · kartu dataset |
| Steven | model · eksperimen · tabel hasil |

**Terima kasih — pertanyaan?**
