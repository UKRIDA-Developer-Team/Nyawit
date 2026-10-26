# Hasil Eksperimen (dibuat otomatis oleh scripts/aggregate_results.py)

Format sel: rerata ± simpangan baku antar seed. Nilai terbaik per kolom dicetak tebal. Kesalahan berat = proporsi prediksi yang meleset ≥ 2 tingkat.

### Tabel utama - test split blok (split utama)

| Eksperimen | Seed | n test | Akurasi ↑ | Macro-F1 ↑ | MAE ↓ | Kesalahan berat ↓ | Akurasi ±1 ↑ | QWK ↑ |
|---|---|---|---|---|---|---|---|---|
| E0 Kelas mayoritas | 1 | 636 | 0.314 | 0.096 | 0.892 | 0.206 | 0.794 | 0.000 |
| E1 HSV + regresi logistik | 1 | 636 | 0.679 | 0.657 | 0.506 | 0.129 | 0.871 | 0.607 |
| E2 EfficientNet-B0 + CE (baseline) | 3 | 636 | **0.908 ± 0.006** | **0.914 ± 0.007** | **0.111 ± 0.006** | **0.017 ± 0.003** | **0.983 ± 0.003** | **0.940 ± 0.003** |
| E3 EfficientNet-B0 + CORN (utama) | 3 | 636 | 0.900 ± 0.002 | 0.905 ± 0.008 | 0.121 ± 0.003 | 0.019 ± 0.004 | 0.981 ± 0.004 | 0.935 ± 0.004 |

### Eksperimen terkontrol pada split blok (rujukan: E3)

| Eksperimen | Seed | n test | Akurasi ↑ | Macro-F1 ↑ | MAE ↓ | Kesalahan berat ↓ | Akurasi ±1 ↑ | QWK ↑ |
|---|---|---|---|---|---|---|---|---|
| E3 EfficientNet-B0 + CORN (utama) | 3 | 636 | **0.900 ± 0.002** | 0.905 ± 0.008 | **0.121 ± 0.003** | **0.019 ± 0.004** | **0.981 ± 0.004** | **0.935 ± 0.004** |
| E4 = E3 + hue jitter | 3 | 636 | 0.895 ± 0.004 | **0.905 ± 0.004** | 0.133 ± 0.004 | 0.026 ± 0.003 | 0.974 ± 0.003 | 0.924 ± 0.004 |
| E5 = E3 + sampler seimbang | 3 | 636 | 0.896 ± 0.007 | 0.903 ± 0.011 | 0.125 ± 0.012 | **0.019 ± 0.006** | **0.981 ± 0.006** | 0.932 ± 0.010 |

| Perbandingan | Δ Akurasi ↑ | Δ Macro-F1 ↑ | Δ MAE ↓ | Δ Kesalahan berat ↓ | Δ Akurasi ±1 ↑ | Δ QWK ↑ |
|---|---|---|---|---|---|---|
| E4 = E3 + hue jitter − E3 | -0.005 | +0.000 | +0.012 | +0.007 | -0.007 | -0.010 |
| E5 = E3 + sampler seimbang − E3 | -0.004 | -0.002 | +0.004 | +0.000 | -0.000 | -0.002 |

### Uji kebocoran: split resmi (acak) vs split blok

| Eksperimen | Seed | n test | Akurasi ↑ | Macro-F1 ↑ | MAE ↓ | Kesalahan berat ↓ | Akurasi ±1 ↑ | QWK ↑ |
|---|---|---|---|---|---|---|---|---|
| E1 HSV + regresi logistik [split resmi] | 1 | 718 | 0.689 | 0.681 | 0.468 | 0.120 | 0.880 | 0.670 |
| E1 HSV + regresi logistik | 1 | 636 | 0.679 | 0.657 | 0.506 | 0.129 | 0.871 | 0.607 |
| E6 = E2 [split resmi] | 3 | 718 | 0.956 ± 0.011 | 0.961 ± 0.010 | 0.051 ± 0.013 | 0.006 ± 0.003 | 0.994 ± 0.003 | 0.976 ± 0.006 |
| E2 EfficientNet-B0 + CE (baseline) | 3 | 636 | 0.908 ± 0.006 | 0.914 ± 0.007 | 0.111 ± 0.006 | 0.017 ± 0.003 | 0.983 ± 0.003 | 0.940 ± 0.003 |
| E7 = E3 [split resmi] | 3 | 718 | 0.953 ± 0.004 | 0.958 ± 0.005 | 0.054 ± 0.006 | 0.007 ± 0.002 | 0.993 ± 0.002 | 0.975 ± 0.004 |
| E3 EfficientNet-B0 + CORN (utama) | 3 | 636 | 0.900 ± 0.002 | 0.905 ± 0.008 | 0.121 ± 0.003 | 0.019 ± 0.004 | 0.981 ± 0.004 | 0.935 ± 0.004 |

Selisih split resmi − split blok (positif pada metrik ↑ = skor resmi lebih tinggi):

| Model | Δ Akurasi ↑ | Δ Macro-F1 ↑ | Δ MAE ↓ | Δ Kesalahan berat ↓ | Δ Akurasi ±1 ↑ | Δ QWK ↑ |
|---|---|---|---|---|---|---|
| E1 HSV + regresi logistik | +0.010 | +0.024 | -0.038 | -0.009 | +0.009 | +0.063 |
| E2 EfficientNet-B0 + CE | +0.048 | +0.046 | -0.060 | -0.011 | +0.011 | +0.036 |
| E3 EfficientNet-B0 + CORN | +0.053 | +0.053 | -0.066 | -0.012 | +0.012 | +0.040 |

Catatan: kedua split memakai test set berbeda, sehingga selisih adalah indikasi besarnya optimisme split resmi, bukan perbandingan berpasangan.

### Recall dan F1 per kelas (rerata seed, test split blok)

| Kelas | Recall E2 | Recall E3 | Recall E5 | F1 E2 | F1 E3 | F1 E5 |
|---|---|---|---|---|---|---|
| Mentah | 0.958 | 0.958 | 0.933 | 0.956 | 0.958 | 0.941 |
| Setengah Matang | 0.917 | 0.900 | 0.883 | 0.910 | 0.904 | 0.885 |
| Matang Penuh | 0.892 | 0.892 | 0.915 | 0.904 | 0.893 | 0.899 |
| Terlalu Matang | 0.848 | 0.848 | 0.822 | 0.859 | 0.851 | 0.855 |
| Busuk | 0.987 | 0.948 | 0.961 | 0.944 | 0.918 | 0.933 |

### Perbandingan berpasangan per seed: E3 − E2 (split blok)

| Seed | Δ Macro-F1 ↑ | Δ MAE ↓ | Δ Kesalahan berat ↓ | Δ QWK ↑ |
|---|---|---|---|---|
| 42 | -0.015 | +0.009 | +0.002 | -0.006 |
| 43 | -0.015 | +0.019 | +0.005 | -0.011 |
| 44 | +0.001 | +0.002 | -0.002 | -0.000 |

E3 EfficientNet-B0 + CORN (utama) lebih baik daripada E2 EfficientNet-B0 + CE (baseline) pada: Macro-F1 ↑ 1/3 seed, MAE ↓ 0/3 seed, Kesalahan berat ↓ 1/3 seed, QWK ↑ 0/3 seed.
