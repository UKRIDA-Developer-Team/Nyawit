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
