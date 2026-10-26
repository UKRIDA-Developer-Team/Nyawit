### Tabel utama - test split blok (split utama)

| Eksperimen | Seed | n test | Akurasi ↑ | Macro-F1 ↑ | MAE ↓ | Kesalahan berat ↓ | Akurasi ±1 ↑ | QWK ↑ |
|---|---|---|---|---|---|---|---|---|
| E0 Kelas mayoritas | 1 | 636 | 0.314 | 0.096 | 0.892 | 0.206 | 0.794 | 0.000 |
| E1 HSV + regresi logistik | 1 | 636 | 0.679 | 0.657 | 0.506 | 0.129 | 0.871 | 0.607 |
| E2 EfficientNet-B0 + CE (baseline) | 3 | 636 | **0.908 ± 0.006** | **0.914 ± 0.007** | **0.111 ± 0.006** | **0.017 ± 0.003** | **0.983 ± 0.003** | **0.940 ± 0.003** |
| E3 EfficientNet-B0 + CORN (utama) | 3 | 636 | 0.900 ± 0.002 | 0.905 ± 0.008 | 0.121 ± 0.003 | 0.019 ± 0.004 | 0.981 ± 0.004 | 0.935 ± 0.004 |
