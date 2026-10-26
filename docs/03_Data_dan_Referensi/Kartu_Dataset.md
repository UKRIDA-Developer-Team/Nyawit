# Kartu Dataset (CP03 – Audit Dataset)

## Identitas

| | |
|---|---|
| Nama | An Ordinal Dataset for Ripeness Level Classification in Oil Palm Fruit Quality Grading |
| Versi | 1 (dipublikasikan 26 November 2024) |
| Penyusun | Imam Mustafa Kamal, Solichin Mochammad, Latifah Nurahmi (Institut Teknologi Sepuluh Nopember), Azis Natawijaya, Muhammad Kalili |
| Pendanaan | Bumitama Innovation Center, PT Bumitama Gunajaya Agro (BGA Group) |
| DOI / tautan | https://doi.org/10.17632/424y96m6sw.1 · https://data.mendeley.com/datasets/424y96m6sw/1 |
| Lisensi | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| Berkas | `Dataset.zip`, 272.151.984 byte, SHA-256 `c3cf88db3194fedd24894a35e27fada3841977e1a09a405a4e064db02ebde0c5` |

## Izin penggunaan

CC BY 4.0 mengizinkan penggunaan, modifikasi, dan distribusi ulang, termasuk untuk keperluan akademik, **dengan atribusi** kepada penyusun. Atribusi dicantumkan di README, proposal, laporan, slide, dan halaman demo. Dataset tidak berisi wajah atau data pribadi (objeknya tandan buah). Kami tidak mendistribusikan ulang arsip penuh lewat repositori; skrip mengunduh langsung dari sumber resmi.

## Isi dan struktur

```
Dataset/
  Images/0Immature/      758 JPG   (Immature0.jpg ...)
  Images/1PartiallyRipe/ 1.405 JPG
  Images/2FullyRipe/     1.489 JPG
  Images/3OverRipe/      665 JPG
  Images/4Decayed/       411 JPG
  Train_val_test_split/Training.txt (3.306) | Validation.txt (704) | Testing.txt (718)
```

Struktur dan jumlah di atas diverifikasi langsung dari arsip di server (lihat `../02_Proposal_UTS/bukti_kelayakan_data.md`). Berkas split berisi nama berkas saja. Nama berkas unik di seluruh dataset, dan setiap gambar tercantum di tepat satu split.

## Label

| Tingkat | Label asli | Label Indonesia | Jumlah | % |
|---|---|---|---|---|
| 0 | Immature | Mentah | 758 | 16,0 |
| 1 | Partially Ripe | Setengah Matang | 1.405 | 29,7 |
| 2 | Fully Ripe | Matang Penuh | 1.489 | 31,5 |
| 3 | Overripe | Terlalu Matang | 665 | 14,1 |
| 4 | Decayed | Busuk | 411 | 8,7 |

Label ditetapkan oleh penyusun, dengan kategori yang didefinisikan bersama masukan ahli; kami tidak mengubah label. Urutan 0–4 dipakai sebagai urutan ordinal.

## Contoh data

`results/audit/contoh_per_kelas.jpg` (dibuat oleh `scripts/audit_dataset.py`) menampilkan 5 contoh acak (seed tetap) per kelas.

## Statistik awal, bias, dan kebocoran

Audit dijalankan pada data asli (3 Okt 2026); rincian lengkap di [`results/audit/ringkasan_audit.md`](../../results/audit/ringkasan_audit.md). Ringkasan:

- Semua gambar **256×256** piksel; 1 pasangan duplikat persis (MD5), dalam split dan label yang sama.
- dHash ≤ 5: 13 pasangan *near-duplicate*; semuanya foto tandan yang sama dengan nomor berkas berurutan; hanya 6 gambar test resmi (0,8%).
- Kemiripan warna: **50%** pasangan bernomor berurutan lebih mirip dari persentil-5 pasangan acak (harapan tanpa urutan: 5%); masih 13% pada selisih 50 nomor. Foto berdekatan berasal dari tandan/sesi yang sama ([grafik](../../results/audit/kemiripan_berurutan.png), [contoh pasangan](../../results/audit/contoh_pasangan_berurutan.jpg)).
- **92%** gambar test resmi (662/718) dan 95% gambar validasi resmi punya tetangga bernomor ±1 di train resmi.
- Split blok: 3.434/658/636; test yang bertetangga ±1 dengan train tinggal 8,3% (batas blok).
- Label manual tim pada 40 pasangan berurutan acak ([CSV](../../results/audit/cek_manual_pasangan_berurutan.csv), [ringkasan](../../results/audit/hasil_cek_manual.md)): 18 tandan sama, 11 berbeda, 11 ragu (**62%** tandan sama di antara yang dapat diputuskan, IK 95% 44–77%). Dari 18 pasangan tandan sama, 6 terpisah train/val-test pada split resmi, 0 pada split blok.

## Risiko bias yang dicatat

| Risiko | Penjelasan | Penanganan |
|---|---|---|
| Ketidakseimbangan kelas | Matang Penuh : Busuk ≈ 3,6 : 1 | macro-F1, recall per kelas, E5 (sampler seimbang) |
| Foto beruntun tandan/sesi yang sama tersebar acak di split resmi | **terbukti**: 92% test resmi punya tetangga bernomor ±1 di train | split blok sebagai split utama; split resmi hanya pembanding (E6, E7) |
| Shortcut resolusi | — | **tidak ada**: audit menemukan seluruh gambar 256×256 |
| Domain sempit | satu wilayah (Kalimantan Tengah), foto lapangan | batas klaim di laporan & demo |
| Ambiguitas label bertetangga | batas tingkat bersifat kontinu | akurasi ±1, pemeriksaan pasangan near-duplicate dengan label berbeda |

## Rencana split

1. **Utama: split blok** (`grouped_split`, train/val/test = 3.434/658/636, dibekukan di `data/splits/grouped_split.csv`). Nomor berkas tiap kelas dibagi menjadi blok 20 nomor berurutan, digabung dengan kelompok dHash, lalu dibagi dengan StratifiedGroupKFold (seed 42). Alasan: audit menemukan foto bernomor berdekatan berasal dari tandan/sesi yang sama.
2. **Pembanding: split resmi** (3.306/704/718, acak stratified) untuk mengukur seberapa optimistis skornya (E0/E1 resmi, E6, E7).
3. Subset test "bersih" versi dHash tetap dihitung untuk split resmi, tetapi tidak dipakai sebagai hasil karena hanya membuang 6 gambar dan skornya hampir sama dengan test penuh.
4. Validasi dipakai untuk pemilihan checkpoint dan hiperparameter. Test hanya dievaluasi sekali per run.
