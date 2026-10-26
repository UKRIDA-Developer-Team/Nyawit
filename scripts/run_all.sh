#!/usr/bin/env bash
# Menjalankan seluruh pipeline eksperimen dari awal sampai tabel hasil beku.
#
# Pemakaian:
#   bash scripts/run_all.sh                 # 3 seed (42 43 44), semua eksperimen
#   SEEDS="42" bash scripts/run_all.sh      # cepat: 1 seed saja
#   EXPS="e2_cnn_ce e3_cnn_corn" bash scripts/run_all.sh
#
# Perkiraan waktu (Colab GPU T4): ~8-12 menit per run EfficientNet-B0;
# 6 eksperimen CNN x 3 seed = 18 run ~ 2,5-3,5 jam. Urutan EXPS = urutan prioritas. Run yang sudah punya summary.json dilewati
# sehingga skrip aman dijalankan ulang setelah sesi Colab terputus.
set -euo pipefail
cd "$(dirname "$0")/.."

SEEDS="${SEEDS:-42 43 44}"
EXPS="${EXPS:-e2_cnn_ce e3_cnn_corn e4_cnn_corn_hue e5_cnn_corn_balanced e6_cnn_ce_official e7_cnn_corn_official}"

echo "== 1. Unduh dan siapkan data =="
python scripts/download_data.py
[ -f data/processed/metadata.csv ] || python scripts/prepare_data.py

echo "== 2. Audit dataset dan kebocoran =="
python scripts/audit_dataset.py

echo "== 3. Baseline klasik (E0, E1) pada split blok dan split resmi =="
python scripts/run_classic_baselines.py
python scripts/run_classic_baselines.py --split-scheme official

echo "== 4. Eksperimen CNN =="
for exp in $EXPS; do
  for seed in $SEEDS; do
    if [ -f "outputs/runs/${exp}/seed${seed}/summary.json" ]; then
      echo "-- lewati ${exp} seed ${seed} (sudah selesai)"
      continue
    fi
    python -m sawit.train --config "configs/${exp}.yaml" --seed "${seed}"
  done
done

echo "== 5. Ringkasan hasil =="
python scripts/aggregate_results.py

echo "== 6. Analisis kesalahan (baseline dan metode utama, seed pertama) =="
first_seed="${SEEDS%% *}"
for exp in e2_cnn_ce e3_cnn_corn; do
  [ -d "outputs/runs/${exp}/seed${first_seed}" ] && python scripts/error_analysis.py --run-dir "outputs/runs/${exp}/seed${first_seed}"
done

echo "== 7. Latensi =="
python scripts/benchmark_latency.py --checkpoint "outputs/runs/e3_cnn_corn/seed${first_seed}/best.pt" --device cpu
if python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)"; then
  python scripts/benchmark_latency.py --checkpoint "outputs/runs/e3_cnn_corn/seed${first_seed}/best.pt" --device cuda
fi

python scripts/make_demo_examples.py
echo "Selesai. Lihat folder results/."
