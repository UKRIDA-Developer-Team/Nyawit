"""Paket `sawit`: klasifikasi ordinal tingkat kematangan buah kelapa sawit.

Modul utama:
- constants : nama kelas dan konstanta dataset
- config    : pemuatan konfigurasi YAML (dengan pewarisan `_base_`)
- data      : pembacaan metadata, dataset PyTorch, transformasi, dan loader
- audit     : hash persepsi (dHash) dan deteksi near-duplicate untuk audit kebocoran
- models    : pembangun backbone pra-latih (torchvision)
- losses    : loss cross-entropy dan CORN (ordinal), serta konversi logit -> probabilitas
- metrics   : metrik klasifikasi + metrik ordinal (MAE, QWK, kesalahan berat)
- engine    : loop pelatihan dan evaluasi
- predict   : kelas `Predictor` untuk inferensi pada gambar baru
- gradcam   : visualisasi Grad-CAM
"""

__version__ = "1.0.0"
