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
