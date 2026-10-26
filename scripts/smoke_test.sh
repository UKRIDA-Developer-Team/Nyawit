#!/usr/bin/env bash
# Uji asap: menjalankan pipeline ujung-ke-ujung pada dataset SINTETIS kecil di CPU
# (< 1 menit). Memastikan kode berjalan sebelum menghabiskan waktu GPU.
# Hasilnya ditulis ke outputs/smoke/ dan results_smoke/ (keduanya di-.gitignore).
set -euo pipefail
cd "$(dirname "$0")/.."

python scripts/make_synthetic_dataset.py --out data/synthetic --per-class 30
python scripts/prepare_data.py --root data/synthetic/Dataset --out data/synthetic/metadata.csv
python scripts/audit_dataset.py --metadata data/synthetic/metadata.csv --root data/synthetic/Dataset --out-dir results_smoke/audit
python scripts/run_classic_baselines.py --metadata data/synthetic/metadata.csv --root data/synthetic/Dataset --output-root outputs/smoke
python scripts/run_classic_baselines.py --metadata data/synthetic/metadata.csv --root data/synthetic/Dataset --output-root outputs/smoke --split-scheme official
python -m sawit.train --config configs/smoke_test.yaml --seed 42
python -m sawit.train --config configs/smoke_test.yaml --seed 42 --set experiment_name=smoke_ce model.head=ce
python -m sawit.train --config configs/smoke_test.yaml --seed 42 --set experiment_name=smoke_official data.split_scheme=official
python -m sawit.evaluate --run-dir outputs/smoke/smoke_official/seed42 --split test --subset clean
python scripts/aggregate_results.py --runs-root outputs/smoke --out-dir results_smoke
python scripts/error_analysis.py --run-dir outputs/smoke/smoke_test/seed42 --root data/synthetic/Dataset --out-dir results_smoke/analisis_kesalahan --n-gradcam 4
python scripts/benchmark_latency.py --checkpoint outputs/smoke/smoke_test/seed42/best.pt --runs 20 --out results_smoke/latensi
python scripts/predict.py --checkpoint outputs/smoke/smoke_test/seed42/best.pt --image data/synthetic/Dataset/Images/2FullyRipe --gradcam results_smoke/gradcam
echo "UJI ASAP BERHASIL"
