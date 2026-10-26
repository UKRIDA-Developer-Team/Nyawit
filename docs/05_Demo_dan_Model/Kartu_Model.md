# Kartu Model: K03 Kematangan Sawit (E3, EfficientNet-B0 + CORN)

## Ringkasan

| | |
|---|---|
| Tugas | Klasifikasi ordinal 5 tingkat kematangan TBS dari satu foto RGB |
| Arsitektur | EfficientNet-B0 (torchvision, pra-latih ImageNet-1k) + Dropout 0,2 + Linear(1280 → 4) |
| Loss | CORN (Shi dkk., 2023) |
| Input | RGB, resize sisi pendek 256 → center crop 224, normalisasi ImageNet |
| Output | tingkat 0–4 (Mentah, Setengah Matang, Matang Penuh, Terlalu Matang, Busuk), distribusi peluang 5 tingkat, nilai harapan tingkat |
| Data latih | Kamal dkk. (2024), train **split blok** (3.434 gambar), CC BY 4.0 |
| Pemilihan checkpoint | macro-F1 validasi terbaik (658 gambar, split blok) |
| Berkas | `outputs/runs/e3_cnn_corn/seed42/best.pt` (tidak di-commit; salinan di Drive) |

## Kinerja

Test split blok (636 foto), rerata 3 seed: **akurasi 0,900 · macro-F1 0,905 · MAE 0,121 · kesalahan ≥ 2 tingkat 1,9% · QWK 0,935**. Checkpoint demo (seed 42): akurasi 0,898, macro-F1 0,896. Latensi model di CPU laptop (Ryzen 5 5600, 6 thread): median **12,3 ms** per foto; ukuran checkpoint 16,3 MB; 4,01 juta parameter.

Sebagai perbandingan, EfficientNet-B0 + cross-entropy (E2) sedikit lebih baik (macro-F1 0,914, MAE 0,111); lihat laporan bagian 3.1. Tabel lengkap: [`results/tabel_utama.md`](../../results/tabel_utama.md), latensi: [`results/latensi/`](../../results/latensi/).

## Penggunaan yang dimaksudkan

- Alat bantu belajar dan penelitian untuk penilaian kematangan TBS dari foto lapangan.
- Pendapat kedua yang konsisten, **bukan** keputusan akhir grading atau penentuan harga.

## Di luar cakupan / tidak dianjurkan

- Foto tumpukan TBS di pabrik, foto malam hari, foto dengan banyak tandan dalam satu bingkai, varietas atau wilayah lain: **belum diuji**.
- Keputusan finansial (harga, penolakan TBS) tanpa verifikasi manusia.

## Keterbatasan yang diketahui

- Satu sumber data (satu wilayah, satu tim pelabel). Batas antar-tingkat bertetangga bersifat ambigu.
- Foto bernomor berdekatan berasal dari tandan/sesi yang sama; split blok mengurangi tetapi tidak menghapus kemiripan sesi antara train dan test.
- Keyakinan model tidak dikalibrasi secara khusus. Ambang peringatan demo 0,9 dipilih dari data **validasi** (E3 seed 42): 13% foto ditandai dan hanya ~51% di antaranya benar, sedangkan sisanya 93% benar. Data uji menunjukkan pola yang sama (15% ditandai, 66% benar; sisanya 94%).

## Etika

Dataset tidak berisi data pribadi. Atribusi CC BY 4.0 dicantumkan di demo. Model tidak boleh diklaim aman, adil, atau siap produksi berdasarkan eksperimen kelas ini (panduan bagian 10).
