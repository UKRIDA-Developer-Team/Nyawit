# Ringkasan Audit Dataset

## Distribusi kelas

| index | train | val | test | total |
| --- | --- | --- | --- | --- |
| 0 - Mentah | 530 | 113 | 115 | 758 |
| 1 - Setengah Matang | 982 | 210 | 213 | 1405 |
| 2 - Matang Penuh | 1042 | 222 | 225 | 1489 |
| 3 - Terlalu Matang | 465 | 98 | 102 | 665 |
| 4 - Busuk | 287 | 61 | 63 | 411 |
| Total | 3306 | 704 | 718 | 4728 |

Proporsi kelas (%): 0 - Mentah: 16.0, 1 - Setengah Matang: 29.7, 2 - Matang Penuh: 31.5, 3 - Terlalu Matang: 14.1, 4 - Busuk: 8.7.
Rasio kelas terbesar/terkecil = 3.62.

## Resolusi gambar

Lebar: min 256, median 256, maks 256 px. Tinggi: min 256, median 256, maks 256 px.
Jumlah ukuran unik: 1. Ukuran yang berbeda antar kelas dapat menjadi jalan pintas (shortcut); lihat resolusi.csv.

## Duplikat persis (MD5 identik)

1 kelompok, 2 berkas. Lintas split: 0 kelompok; label berbeda: 0 kelompok.

## Near-duplicate dan risiko kebocoran

Metode: dHash 64-bit, pasangan dengan jarak Hamming <= 5 dianggap near-duplicate.

- Pasangan near-duplicate: 13 (lintas split resmi: 10).
- Kelompok berisi >1 gambar: 13.
- Gambar validasi yang punya kembaran di train: 3.
- Gambar test yang punya kembaran di train: 6 dari 718 (0.8%). Sisanya (712) membentuk subset **test bersih**.
- Pasangan dengan label berbeda (indikasi label ambigu/salah): 0.

Catatan: dHash dapat menghasilkan positif palsu pada komposisi yang mirip (mis. latar sama). Contoh pasangan perlu diperiksa manual pada `contoh_near_duplicate.jpg`; lihat juga `sensitivitas_ambang.csv`.

## Pemotretan beruntun (tandan sama, sudut berbeda)

dHash hanya menangkap foto yang nyaris identik. Untuk memeriksa foto tandan yang sama dari sudut sedikit berbeda, dihitung jarak fitur warna HSV (terstandardisasi) antara gambar sekelas yang nomor berkasnya berselisih k, lalu dibandingkan dengan pasangan acak sekelas yang nomornya berjauhan (> 50). Bila nomor berkas tidak berkaitan dengan urutan pemotretan, sekitar 5% pasangan akan lebih mirip daripada persentil-5 pasangan acak.

| Selisih nomor k | Pasangan | Median jarak | % lebih mirip dari persentil-5 acak |
|---|---|---|---|
| 1 | 4722 | 4.15 | 49.6% |
| 2 | 4717 | 4.78 | 40.8% |
| 3 | 4712 | 5.19 | 34.8% |
| 5 | 4702 | 5.52 | 30.4% |
| 10 | 4677 | 5.80 | 24.4% |
| 20 | 4628 | 6.21 | 19.1% |
| 50 | 4478 | 6.73 | 13.3% |

Rujukan pasangan acak: median jarak 7.86, persentil-5 4.13.

**Temuan:** 50% pasangan bernomor berurutan (k=1) sangat mirip, jauh di atas 5% yang diharapkan, dan kemiripan menurun perlahan seiring k. Artinya nomor berkas mengikuti urutan pemotretan: gambar bernomor berdekatan kemungkinan besar berasal dari tandan atau sesi yang sama.

- Gambar **test** resmi yang punya tetangga bernomor ±1 (kelas sama) di train resmi: **662 dari 718 (92%)**.
- Gambar validasi resmi dengan tetangga ±1 di train: 670 dari 704 (95%).
- Konsekuensi: split resmi (acak) kemungkinan besar **terlalu optimistis**. Subset "test bersih" berbasis dHash tidak cukup untuk mengatasinya.
- Pemeriksaan visual: lihat `contoh_pasangan_berurutan.jpg`; tim memberi label manual pada `cek_manual_pasangan_berurutan.csv` (kolom `sama_tandan`: ya/tidak/ragu) untuk memperkirakan proporsi tandan yang sama secara langsung.

## Split blok berkelompok (split utama)

Nomor berkas setiap kelas dibagi menjadi blok berisi 20 nomor berurutan; blok digabung dengan kelompok dHash, lalu dibagi dengan StratifiedGroupKFold (seed 42) sehingga satu blok selalu berada di split yang sama (~70/15/15). Split ini dipakai sebagai **split utama**; split resmi tetap dilaporkan sebagai pembanding.
Sumber split: berkas beku `data/splits/grouped_split.csv`.

| index | train | val | test | total |
| --- | --- | --- | --- | --- |
| 0 - Mentah | 580 | 98 | 80 | 758 |
| 1 - Setengah Matang | 1025 | 180 | 200 | 1405 |
| 2 - Matang Penuh | 1069 | 220 | 200 | 1489 |
| 3 - Terlalu Matang | 460 | 100 | 105 | 665 |
| 4 - Busuk | 300 | 60 | 51 | 411 |
| Total | 3434 | 658 | 636 | 4728 |

- Kelompok: 238 (blok 20 nomor + gabungan dHash).
- Gambar test (split blok) yang punya tetangga ±1 di train: 53 dari 636 (8.3%), hanya di batas blok (bandingkan 92% pada split resmi).
- Keterbatasan: korelasi sesi pemotretan masih terlihat hingga selisih puluhan nomor, sehingga split blok mengurangi, tetapi tidak menghapus sepenuhnya, kemiripan antara train dan test.

Metadata diperbarui: `data/processed/metadata.csv` (kolom file_number, dup_group, near_dup_in_train, neighbor_in_train_official, split_group, grouped_split).
