# K03 – Klasifikasi Ordinal Tingkat Kematangan Buah Sawit

**Proyek Akhir Visi Komputer (IF0PP006) · Kelas 5PITA · Semester Ganjil 2026/2027 · Kelompok 3**
Juanito Dante (412024001) · Yedija Teofilus Yonatan (412024011) · Steven Iwan (412024010)

Model visi komputer yang memprediksi **tingkat kematangan tandan buah segar (TBS) kelapa sawit** dari satu foto: *Mentah → Setengah Matang → Matang Penuh → Terlalu Matang → Busuk*. Karena kelasnya berurutan, proyek ini membandingkan secara terkontrol **cross-entropy (CE)** dengan loss ordinal **CORN** pada **EfficientNet-B0** pra-latih. Proyek ini juga mengaudit kebocoran data: audit pada data asli menunjukkan bahwa foto bernomor berurutan berasal dari tandan/sesi yang sama, sehingga split acak resmi terlalu optimistis. Karena itu evaluasi utama memakai **split blok**.

| Pertanyaan | Eksperimen |
|---|---|
| **P1** Apakah CORN menurunkan MAE dan kesalahan ≥ 2 tingkat dibanding CE tanpa menurunkan macro-F1 > 0,02? | E2 vs **E3** |
| **P2** Seberapa optimistis split resmi (acak) dibanding split blok yang menjaga foto berurutan tetap bersama? | E1, E6 vs E2, E7 vs E3 |
| **P3** Apakah augmentasi hue/saturasi merusak isyarat warna kematangan? | E3 vs E4 |

---

## Status

| Bagian | Status |
|---|---|
| Kode pipeline (data, audit, baseline, pelatihan, evaluasi, analisis kesalahan, latensi, demo) | ✅ selesai; **21 uji lulus**; uji asap ujung-ke-ujung lulus di CPU; kode CNN diuji beberapa batch pada data asli |
| Dataset asli | ✅ diunduh dan SHA-256 cocok (`data/raw/`, tidak di-commit) |
| Audit data (CP03) | ✅ **dijalankan pada data asli**: foto bernomor berurutan berasal dari tandan/sesi yang sama; 92% test resmi bertetangga dengan train. Dikonfirmasi label manual tim (62% pasangan berurutan = tandan sama). **Split blok** menjadi split utama. Lihat `results/audit/` |
| Baseline klasik E0/E1 (CP04) | ✅ **dijalankan pada data asli**, kedua split; lihat `results/tabel_utama.md` dan `results/tabel_kebocoran.md` |
| Dokumen UTS (proposal, slide, bukti kelayakan, tracker CP00–CP06) | ✅ draf lengkap + PDF, berisi angka audit & baseline asli |
| Eksperimen CNN (E2–E7 × 3 seed) | ✅ **selesai** di Google Colab (Tesla T4, 18 run, 7–15 menit per run); checkpoint di Google Drive, tabel di `results/` |
| Analisis kesalahan, latensi, contoh demo | ✅ dijalankan di CPU laptop: `results/analisis_kesalahan/`, `results/latensi/` (median 12,3 ms per foto), `app/contoh/` |
| Laporan & slide UAS | ✅ draf berisi hasil nyata; kelompok wajib membaca, memahami, dan menyunting interpretasinya; bagian **[…]** yang tersisa (kontribusi anggota, kategori manual kesalahan) diisi kelompok |

> Semua tabel hasil dibuat oleh skrip dari run yang benar-benar dijalankan (`python scripts/aggregate_results.py`), jadi **jangan menulis angka secara manual**.
>
> **Hasil utama (split blok, rerata 3 seed):** EfficientNet-B0 + CE macro-F1 0,914, MAE 0,111; + CORN macro-F1 0,905, MAE 0,121; baseline warna 0,657. CORN **tidak** lebih baik daripada CE pada data ini (P1 negatif). Split resmi menaikkan akurasi CNN sekitar 5 poin (P2). Augmentasi hue memperburuk metrik ordinal di ketiga seed (P3).

---

## Struktur folder

```
K03_KematanganSawit/
├── README.md                  ← dokumen ini
├── requirements.txt           ← dependensi Python
├── pytest.ini, .gitignore
├── sawit/                     ← paket Python utama
│   ├── constants.py           ← nama kelas, URL + SHA-256 dataset
│   ├── config.py              ← YAML dengan pewarisan `_base_` + override CLI
│   ├── data.py                ← metadata, Dataset PyTorch, augmentasi, DataLoader
│   ├── audit.py               ← dHash, kemiripan foto berurutan, blok nomor, split blok
│   ├── features.py            ← fitur warna HSV (baseline E1 & audit)
│   ├── models.py              ← EfficientNet-B0 / ResNet / MobileNetV3 (torchvision)
│   ├── losses.py              ← cross-entropy & CORN (loss, peluang, prediksi)
│   ├── metrics.py             ← akurasi, macro-F1, per kelas, MAE, kesalahan berat, QWK
│   ├── engine.py              ← loop latih/evaluasi, jadwal warmup+cosine
│   ├── train.py               ← `python -m sawit.train` (satu eksperimen × satu seed)
│   ├── evaluate.py            ← evaluasi ulang checkpoint (penuh / test bersih)
│   ├── predict.py             ← kelas `Predictor` untuk gambar baru
│   ├── gradcam.py             ← Grad-CAM
│   └── plots.py               ← confusion matrix, kurva, galeri
├── configs/                   ← satu YAML per eksperimen (E2–E7 + uji asap)
├── scripts/                   ← unduh, siapkan, audit, baseline, ringkas, analisis, latensi, demo, dokumen
├── app/app.py                 ← demo Gradio (+ app/contoh/ gambar contoh)
├── notebooks/K03_KematanganSawit_Colab.ipynb   ← pipeline lengkap di Google Colab
├── tests/                     ← uji unit & integrasi (pytest)
├── data/                      ← (tidak di-commit) dataset & metadata; lihat data/README.md
├── outputs/                   ← (tidak di-commit) checkpoint & log per run
├── results/                   ← (di-commit) tabel & gambar hasil beku, dibuat otomatis
└── docs/                      ← berkas akademik, mengikuti struktur Drive pada panduan bagian 11
    ├── 01_Administrasi_dan_Tracker/   CP00 kontrak, CP01 matriks kandidat, tracker CSV, logbook, catatan keputusan
    ├── 02_Proposal_UTS/               proposal + slide UTS (MD & PDF), bukti kelayakan data
    ├── 03_Data_dan_Referensi/         kartu dataset (CP03), referensi + ringkasan relevansi (CP02)
    ├── 05_Demo_dan_Model/             skenario demo, kartu model
    ├── 06_Laporan_UAS/                laporan teknis + slide UAS (MD & PDF)
    └── assets/                        diagram pipeline (SVG)
```

Folder Drive `04_Kode_dan_Eksperimen/` = **repositori ini** (atau `K03_KematanganSawit_SourceCode.zip`).

---

## Instalasi

### Opsi A – Google Colab (disarankan untuk pelatihan)

1. Unggah proyek ke GitHub (isi `REPO_URL` di sel 1b) atau unggah `K03_KematanganSawit.zip` ke Google Drive.
2. Buka `notebooks/K03_KematanganSawit_Colab.ipynb` di browser (Runtime → T4 GPU) atau di VS Code (lihat bagian **Menjalankan di GPU**), lalu jalankan sel berurutan.

### Opsi B – Lokal

Membutuhkan Python ≥ 3.10 (diuji pada 3.12).

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python -m pytest
```

Untuk GPU NVIDIA lokal, pasang PyTorch versi CUDA sesuai petunjuk di pytorch.org sebelum `requirements.txt`.

---

## Penggunaan

### 1. Uji asap (tanpa dataset asli, < 1 menit di CPU)

```bash
bash scripts/smoke_test.sh
```

Perintah ini membuat dataset **sintetis** berstruktur sama dengan dataset asli, lalu menjalankan seluruh pipeline: metadata → audit → baseline → latih CE & CORN → evaluasi → analisis kesalahan → latensi → prediksi CLI. Hasilnya **bukan** hasil penelitian.

### 2. Pipeline lengkap pada dataset asli

```bash
bash scripts/run_all.sh
```

Langkah 1–3 (unduh, audit, baseline) cukup di CPU (< 1 menit); langkah pelatihan CNN butuh GPU. Versi cepat dengan satu seed:

```bash
SEEDS="42" bash scripts/run_all.sh
```

Langkah yang dijalankan (dapat juga dijalankan satu per satu):

| Langkah | Perintah | Keluaran |
|---|---|---|
| Unduh (~260 MB, SHA-256 diverifikasi) | `python scripts/download_data.py` | `data/raw/Dataset/` |
| Metadata | `python scripts/prepare_data.py` | `data/processed/metadata.csv` |
| Audit & split blok | `python scripts/audit_dataset.py` | `results/audit/`, kolom `grouped_split` (split blok) dll. |
| Baseline E0, E1 | `python scripts/run_classic_baselines.py` lalu `… --split-scheme official` | `outputs/runs/e0_*`, `e1_*` (+ `_official`) |
| Latih satu eksperimen | `python -m sawit.train --config configs/e3_cnn_corn.yaml --seed 42` | `outputs/runs/e3_cnn_corn/seed42/` |
| Ringkas hasil | `python scripts/aggregate_results.py` | `results/tabel_*.md`, `results/gambar/` |
| Analisis kesalahan | `python scripts/error_analysis.py --run-dir outputs/runs/e3_cnn_corn/seed42` | `results/analisis_kesalahan/` |
| Latensi | `python scripts/benchmark_latency.py --device cpu` | `results/latensi/` |
| Contoh demo | `python scripts/make_demo_examples.py` | `app/contoh/` |
| PDF dokumen | `python scripts/build_docs.py` | PDF di `docs/02_…` dan `docs/06_…` |

Override konfigurasi tanpa mengubah berkas: `python -m sawit.train --config configs/e3_cnn_corn.yaml --set train.epochs=5 data.num_workers=4`.

### 3. Demo

```bash
python app/app.py --checkpoint outputs/runs/e3_cnn_corn/seed42/best.pt
```

Tambahkan `--share` di Colab untuk tautan publik sementara. Cadangan tanpa browser:

```bash
python scripts/predict.py --image app/contoh --gradcam hasil_gradcam
```

---

## Menjalankan di GPU

Laptop kelompok memakai GPU **AMD Radeon RX 6600**. PyTorch versi CUDA hanya mendukung GPU NVIDIA, jadi cara paling mudah adalah GPU T4 gratis dari Google Colab.

**Dari VS Code (ekstensi resmi "Google Colab"):**

1. Pasang ekstensi **Google Colab** (penerbit: Google) dari Extensions (`Ctrl+Shift+X`); ekstensi Jupyter ikut terpasang.
2. Kode berjalan di server Google, **bukan** di laptop. Berkas lokal tidak terlihat, jadi unggah proyek ke GitHub (atau `K03_KematanganSawit.zip` ke Google Drive).
3. Buka `notebooks/K03_KematanganSawit_Colab.ipynb` → **Select Kernel → Colab → New Colab Server** → pilih **GPU** (T4) → masuk dengan akun Google.
4. Jalankan sel berurutan. Sel **1d** berhenti dengan pesan jelas bila GPU tidak aktif. Log pelatihan juga menampilkan `perangkat=cuda`; jika tertulis `perangkat=cpu`, hentikan dan ganti server.
5. Hasil disimpan ke Google Drive (`K03_KematanganSawit_outputs/` dan `K03_KematanganSawit_results/`). Salin `results/` kembali ke repositori lalu jalankan `python scripts/build_docs.py`.

**Alternatif lokal (AMD, tidak resmi):** PyTorch versi ROCm dapat berjalan pada RX 6600 di Linux dengan variabel `HSA_OVERRIDE_GFX_VERSION=10.3.0`. Kode proyek tidak perlu diubah (ROCm tampil sebagai `cuda` di PyTorch), tetapi GPU ini tidak didukung resmi oleh ROCm, jadi Colab tetap disarankan.

---

## Eksperimen

| ID | Konfigurasi | Perbedaan terhadap rujukan |
|---|---|---|
| E0 | `scripts/run_classic_baselines.py` | kelas mayoritas (kedua split) |
| E1 | `scripts/run_classic_baselines.py` | histogram HSV (40 fitur) + regresi logistik, C dipilih di validasi (kedua split) |
| E2 | `configs/e2_cnn_ce.yaml` | EfficientNet-B0 + **cross-entropy** (baseline), split blok |
| **E3** | `configs/e3_cnn_corn.yaml` | sama dengan E2, kepala/loss **CORN** (metode utama) |
| E4 | `configs/e4_cnn_corn_hue.yaml` | E3 + hue 0,1 & saturasi 0,2 |
| E5 | `configs/e5_cnn_corn_balanced.yaml` | E3 + sampler seimbang kelas (iterasi CP11) |
| E6 | `configs/e6_cnn_ce_official.yaml` | E2 pada **split resmi** (pembanding kebocoran) |
| E7 | `configs/e7_cnn_corn_official.yaml` | E3 pada **split resmi** (pembanding kebocoran) |

**Split utama = split blok.** Audit menemukan foto bernomor berurutan berasal dari tandan/sesi yang sama dan 92% test resmi bertetangga dengan train. Split blok membagi nomor berkas per kelas menjadi blok 20 nomor dan menjaga satu blok di satu split (3.434/658/636). Split ini **dibekukan** di `data/splits/grouped_split.csv` (lihat `data/splits/README.md`): `StratifiedGroupKFold` mengacak kelompok berbeda sejak scikit-learn 1.8, sehingga split yang dihitung ulang bisa berbeda dari split yang dipakai melatih model. Split resmi tetap dipakai sebagai pembanding.

Konfigurasi bersama ada di `configs/base.yaml`: AdamW, lr 3·10⁻⁴, *weight decay* 10⁻², *warmup* 1 epoch + *cosine*, maksimal 25 epoch, *early stopping* 7, batch 32, input 224. Checkpoint dipilih dari **macro-F1 validasi**, dan test dievaluasi sekali per run. Seed 42, 43, dan 44.

**Reproduksibilitas:** seed dikunci (Python/NumPy/PyTorch/worker DataLoader, cuDNN deterministik). Setiap run menyimpan `config.yaml` final, `history.csv`, `summary.json` (versi pustaka, GPU, waktu), dan prediksi per gambar. Unduhan dataset diverifikasi dengan SHA-256.

---

## Pemetaan ke berkas wajib panduan

| Berkas panduan | Lokasi |
|---|---|
| **UTS** Proposal | `docs/02_Proposal_UTS/K03_KematanganSawit_Proposal_v01.md` / `.pdf` |
| **UTS** Slide | `docs/02_Proposal_UTS/K03_KematanganSawit_SlideUTS_v01.md` / `.pdf` |
| **UTS** Proposal versi template dosen (Abstrak, Bab 1, Bab 2) | `docs/02_Proposal_UTS/template_dosen/K03_KematanganSawit_ProposalUTS.pdf` (sumber HTML + `gambar/`) |
| **UTS** Slide pitch + naskah 3 pembicara | deck Slides (tautan di naskah) · `docs/02_Proposal_UTS/K03_KematanganSawit_NaskahPitch.md` |
| **UTS** Bukti kelayakan | `docs/02_Proposal_UTS/bukti_kelayakan_data.md`, `scripts/smoke_test.sh`, `tests/` |
| Tracker CP00–CP13 & logbook | `docs/01_Administrasi_dan_Tracker/` (CSV untuk diimpor ke Google Sheets) |
| **UAS** Laporan teknis | `docs/06_Laporan_UAS/K03_KematanganSawit_LaporanFinal.md` / `.pdf` |
| **UAS** Kode | repositori ini (README, `requirements.txt`, `configs/`, seed, cara memperoleh data & menjalankan) |
| **UAS** Hasil | `results/` (tabel metrik, konfigurasi, contoh berhasil/gagal) |
| **UAS** Demo | `app/app.py`, `scripts/predict.py`, `docs/05_Demo_dan_Model/Skenario_Demo.md`; video `K03_KematanganSawit_Demo.mp4` di Drive |
| **UAS** Slide | `docs/06_Laporan_UAS/K03_KematanganSawit_SlideUAS.md` / `.pdf` |

---

## Asumsi (bagian panduan yang tidak dijelaskan rinci)

1. **Template laporan teknis** disebut pada panduan tetapi tidak dilampirkan. Laporan mengikuti isi minimum bagian 8: abstrak 200–250 kata, pendahuluan, metodologi, hasil dan pembahasan, kesimpulan, referensi, dengan setiap tabel/gambar dirujuk di teks. Sesuaikan bila template resmi tersedia.
2. **Bahasa kode.** Panduan tidak mengatur bahasa identifier. Nama variabel/fungsi memakai bahasa Inggris (konvensi Python dan pustaka), sedangkan komentar, docstring, pesan log, teks UI, label, dan dokumen memakai Bahasa Indonesia.
3. **Struktur folder.** Struktur bagian 11 ditujukan untuk Google Drive. Repositori memakai struktur kode standar, dan `docs/01…06` meniru folder Drive agar mudah diunggah. Folder `04_Kode_dan_Eksperimen` = repositori ini. Checkpoint model disimpan di Drive `05_Demo_dan_Model/`, tidak di-commit.
4. **Tracker** resmi berada di Google Sheets; berkas CSV di `docs/01…` adalah salinan yang dapat diimpor. Kolom status hanya diubah dosen/asisten.
5. **Logbook** sengaja dikosongkan: setiap anggota wajib menulis kegiatan nyatanya sendiri.
6. **Format slide:** panduan mengizinkan PDF atau PPTX; slide ditulis dalam Markdown dan dibangun menjadi PDF 16:9 (`scripts/build_docs.py`, membutuhkan Chromium/Chrome).
7. **Penamaan berkas** mengikuti pola `K03_JudulSingkat_…` dengan judul singkat `KematanganSawit`.
8. **Peran anggota** mengikuti pembagian pada dokumen tugas mingguan sebelumnya (Juanito: data; Steven: baseline/model; Yedija: cadangan & etika → dokumentasi/demo) dan dapat diubah di `CP00_Kontrak_Kerja.md`.
9. **Tanggal checkpoint** dicatat per minggu sesuai panduan; tanggal kalender diisi kelompok.
10. **Bukti kelayakan (CP06)** dipenuhi dengan pemeriksaan isi arsip dataset dari server, audit + baseline klasik pada data asli (CPU), uji kode CNN beberapa batch pada data asli, dan uji asap pipeline. Pelatihan CNN penuh dilakukan di GPU Colab.
11. **Jumlah seed** (3), ambang near-duplicate (dHash ≤ 5), dan ukuran blok split (20 nomor) tidak diatur panduan; dipilih sebagai kompromi waktu GPU, kehati-hatian, dan jumlah blok yang cukup untuk kelas terkecil. Sensitivitas ambang dilaporkan.
12. **Lisensi kode proyek** belum ditetapkan (keputusan kelompok), sehingga tidak ada berkas LICENSE.
13. **Split utama diganti** dari split resmi ke split blok setelah audit data (sebelum ada hasil model), sesuai rencana cadangan di proposal. Alasan dan bukti ada di `docs/01_Administrasi_dan_Tracker/Catatan_Keputusan.md`.
14. **Split blok dibekukan** setelah ditemukan bahwa scikit-learn ≥ 1.8 menghasilkan split berbeda (3.368/680/680) dari split yang dipakai di Colab (≤ 1.7: 3.434/658/636). Semua hasil memakai split beku tersebut. Nilai baseline E1 juga sedikit berbeda antarlingkungan (versi Pillow/scikit-learn); angka resmi diambil dari run Colab, sama dengan CNN.

---

## Atribusi dan lisensi

- **Dataset:** Kamal, I. M., Mochammad, S., Nurahmi, L., Natawijaya, A., & Kalili, M. (2024). *An Ordinal Dataset for Ripeness Level Classification in Oil Palm Fruit Quality Grading* (V1). Mendeley Data. https://doi.org/10.17632/424y96m6sw.1, **CC BY 4.0**. Dataset tidak didistribusikan ulang lewat repositori; skrip mengunduh dari sumber resmi. Gambar contoh di `app/contoh/` (bila diisi) adalah milik penyusun dataset dengan lisensi yang sama.
- **Metode:** CORN – Shi, Cao & Raschka (2023); EfficientNet – Tan & Le (2019); Grad-CAM – Selvaraju dkk. (2017). Implementasi CORN ditulis ulang dari makalah dan dicocokkan dengan perilaku `coral-pytorch` (MIT) tanpa menyalin kode.
- **Pustaka:** PyTorch/torchvision (BSD-3; bobot ImageNet dari torchvision), scikit-learn, NumPy, pandas (BSD-3), Matplotlib, Pillow, PyYAML, Markdown, Gradio (Apache-2.0).
- **Bantuan eksternal (wajib dicatat menurut panduan bagian 10):** kerangka kode, konfigurasi, dan draf dokumen proyek ini disusun dengan bantuan asisten AI (Claude, Anthropic). Setiap anggota tetap bertanggung jawab memahami, menjalankan, memeriksa, dan mengubah seluruh isi, serta mencatat di logbook bagian yang dipakai dan perubahan yang dilakukan.

Daftar referensi lengkap: `docs/03_Data_dan_Referensi/Referensi.md`.

## Kontribusi anggota

| Anggota | Peran | Kontribusi (diisi dari logbook) |
|---|---|---|
| Yedija Teofilus Yonatan | koordinator; dokumentasi & demo | [isi] |
| Juanito Dante | data & audit | [isi] |
| Steven Iwan | model & eksperimen | [isi] |
# Nyawit---Computer-Vision-Final-Project
