# Catatan Keputusan Teknis

Format: tanggal · keputusan · alasan · bukti · siapa. Keputusan yang sudah tercatat tidak dihapus; perubahan ditulis sebagai baris baru.

| Tanggal | Keputusan | Alasan | Bukti | Oleh |
|---|---|---|---|---|
| 2026-10-03 | Topik diganti dari "Deteksi Timpa Teks" ke kematangan sawit | data timpa teks harus dikumpulkan manual, akses grup terbatas | CP01_Matriks_Kandidat_Topik.md | [isi] |
| 2026-10-03 | Memakai split resmi sebagai split utama, ditambah subset test bersih & split berkelompok | sebanding dengan penyusun dataset sekaligus mengendalikan kebocoran | scripts/audit_dataset.py | [isi] |
| 2026-10-03 | Checkpoint dipilih dari macro-F1 validasi untuk semua eksperimen | metrik netral terhadap CE maupun CORN | configs/base.yaml (`select_metric`) | [isi] |
| 2026-10-03 | Hue/saturation jitter = 0 pada konfigurasi dasar | warna adalah isyarat utama kematangan; diuji terpisah di E4 | configs/e4_cnn_corn_hue.yaml | [isi] |
| 2026-10-03 | EfficientNet-B0 sebagai backbone | 5,3 juta parameter, cocok untuk Colab gratis dan demo CPU | Proposal bagian 6 | [isi] |
| 2026-10-03 | Dataset diunduh dan diaudit di CPU; baseline E0/E1 dijalankan pada kedua split | bukti CP03/CP04 dari data asli, sebelum memakai GPU | results/audit/, results/tabel_utama.md | [isi] |
| 2026-10-03 | **Split blok menjadi split utama**; split resmi menjadi pembanding (E6, E7); E6 lama (E3 pada split berkelompok) dihapus | 50% pasangan foto berurutan sangat mirip (harapan 5%); 92% test resmi bertetangga ±1 dengan train; dHash hanya menangkap 0,8% | results/audit/ringkasan_audit.md, kemiripan_berurutan.png | [isi] |
| 2026-10-03 | Ukuran blok = 20 nomor | blok kecil masih memberi ≥ 20 blok untuk kelas terkecil (Busuk, 411 gambar) sehingga pembagian 70/15/15 tetap mungkin; test di batas blok tinggal 5,6% | configs/base.yaml, scripts/audit_dataset.py | [isi] |
| 2026-10-03 | Grid C baseline E1 diperluas sampai 1000 | C terbaik jatuh di batas grid (100); dipilih dari validasi, test tidak disentuh | scripts/run_classic_baselines.py | [isi] |
| 2026-10-09 | Label manual 40 pasangan berurutan selesai; split blok dipertahankan | 18 ya / 11 tidak / 11 ragu (62% tandan sama dari yang dapat diputuskan); 6 dari 18 pasangan tandan sama terpisah train/val-test pada split resmi, 0 pada split blok | results/audit/hasil_cek_manual.md | [isi] |
| 2026-10-10 | 18 run CNN + baseline selesai di Colab (Tesla T4); hasil dipakai sebagai angka resmi | semua angka dari satu lingkungan | outputs/runs (Drive), results/ | [isi] |
| 2026-10-10 | **Split blok dibekukan** di data/splits/grouped_split.csv (3.434/658/636) | scikit-learn ≥ 1.8 menghasilkan split berbeda (3.368/680/680) dari input dan seed yang sama; model dilatih dengan split versi ≤ 1.7 | data/splits/README.md | [isi] |
| 2026-10-10 | Ambang peringatan demo 0,5 → 0,9 | dipilih dari data **validasi**: pada 0,5 hanya 0,2% foto ditandai; pada 0,9, 13% ditandai dengan akurasi ~51% | sawit/predict.py, laporan 3.5 | [isi] |
| 2026-10-10 | Demo tetap memakai E3 seed 42 walau E2 sedikit lebih baik di test | memilih ulang model berdasarkan test = memakai data uji untuk seleksi; selisih kecil | laporan 3.3 | [isi] |
