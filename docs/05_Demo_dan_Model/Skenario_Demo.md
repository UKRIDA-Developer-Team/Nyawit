# Skenario Demo UAS (CP12)

Format sidang UAS: 7 menit presentasi, **5 menit demonstrasi**, 3 menit tanya jawab. Demo langsung adalah yang utama; video hanya cadangan teknis.

## Persiapan (H-1 dan 30 menit sebelum sidang)

- [ ] `best.pt` E3 seed 42 tersedia di laptop **dan** di Drive `05_Demo_dan_Model/` (jangan di-commit).
- [ ] `pip install -r requirements.txt` sudah dijalankan di laptop demo; uji `python -m pytest`.
- [ ] `python scripts/make_demo_examples.py` → `app/contoh/` berisi 5 gambar test **split blok** (satu per kelas; tidak pernah dilihat model saat latih).
- [ ] Siapkan 2–3 **foto baru** di luar dataset (mis. foto TBS dari internet dengan lisensi jelas atau foto sendiri) untuk menunjukkan input baru, termasuk satu kasus yang kemungkinan gagal (foto tumpukan/malam hari).
- [ ] Jalankan demo sekali dan catat latensi di laptop demo.
- [ ] Video cadangan `K03_KematanganSawit_Demo.mp4` (2–3 menit) sudah diputar ulang dan dapat dibuka.

## Alur 5 menit

| Menit | Pembicara | Aksi | Yang ditunjukkan |
|---|---|---|---|
| 0:00–0:30 | Yedija | `python app/app.py` (sudah dibuka sebelumnya) | antarmuka, batasan di deskripsi |
| 0:30–1:45 | Yedija | klik contoh Mentah dan Matang Penuh | prediksi benar, peluang per tingkat, nilai harapan, Grad-CAM pada tandan |
| 1:45–2:45 | Steven | unggah contoh Terlalu Matang/Busuk | kesalahan tetangga vs berat; kaitkan dengan tabel MAE E2 vs E3 |
| 2:45–3:45 | Juanito | unggah foto baru di luar dataset | perilaku pada domain baru; peringatan keyakinan rendah |
| 3:45–4:30 | Steven | tunjukkan latensi pada keluaran | angka latensi CPU vs tabel `results/latensi/` |
| 4:30–5:00 | Juanito | jalankan cadangan CLI `python scripts/predict.py --image app/contoh` | fallback teknis bila Gradio gagal |

## Rencana cadangan

1. Gradio gagal → CLI `scripts/predict.py` (tanpa internet, tanpa browser).
2. Laptop gagal → Colab notebook bagian 8 (`--share`).
3. Semua gagal → putar video cadangan.

## Isi video cadangan (2–3 menit)

Rekam layar: buka demo → 5 contoh test (satu per kelas) → 1 foto baru → tunjukkan Grad-CAM dan latensi → tutup dengan tabel hasil utama. Simpan sebagai `K03_KematanganSawit_Demo.mp4` di Drive.
