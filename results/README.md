# Folder hasil (di-commit)

Seluruh isi folder ini **dibuat otomatis** oleh pipeline. Isinya hanya tabel dan gambar kecil; checkpoint besar tetap di `outputs/` yang tidak di-commit. Jangan menyunting angka secara manual: jalankan ulang skrip agar tabel tetap konsisten dengan run.

| Path | Dibuat oleh |
|---|---|
| `audit/` | `scripts/audit_dataset.py` |
| `semua_run.csv`, `tabel_*.md`, `hasil_ringkas.md`, `gambar/` | `scripts/aggregate_results.py` |
| `analisis_kesalahan/<eksperimen>_seed<seed>/` | `scripts/error_analysis.py` |
| `latensi/` | `scripts/benchmark_latency.py` |

Status 3 Okt 2026: `audit/` dan baseline E0/E1 (kedua split) sudah dijalankan pada dataset asli di CPU. Hasil CNN (E2–E7) akan muncul setelah pelatihan di GPU (lihat README utama, bagian "Status").
