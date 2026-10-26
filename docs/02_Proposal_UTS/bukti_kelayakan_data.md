# Bukti Kelayakan Data (dibuat otomatis)

Tanggal pemeriksaan: 2026-10-03. Dibuat oleh `scripts/inspect_remote_zip.py` dengan membaca direktori ZIP di server Mendeley Data (HTTP Range), tanpa mengunduh seluruh arsip.

- Ukuran arsip: 272,151,984 byte. Total entri berkas: 4731; gambar JPG: 4728.

## Jumlah gambar per folder kelas

| Folder | Jumlah |
|---|---|
| 0Immature | 758 |
| 1PartiallyRipe | 1405 |
| 2FullyRipe | 1489 |
| 3OverRipe | 665 |
| 4Decayed | 411 |

## Split resmi (Train_val_test_split/*.txt)

| Split | Mentah | Setengah Matang | Matang Penuh | Terlalu Matang | Busuk | Total |
|---|---|---|---|---|---|---|
| Training | 530 | 982 | 1042 | 465 | 287 | 3306 |
| Validation | 113 | 210 | 222 | 98 | 61 | 704 |
| Testing | 115 | 213 | 225 | 102 | 63 | 718 |

Data yang diambil dari server untuk pemeriksaan ini: 0.71 MB.
