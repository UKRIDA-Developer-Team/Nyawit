"""Meringkas seluruh run menjadi tabel hasil beku untuk laporan dan slide.

Membaca outputs/runs/<eksperimen>/seed*/metrics_*.json lalu menulis ke results/:
    semua_run.csv           satu baris per (eksperimen, seed, subset)
    tabel_utama.md          baseline vs metode utama (split blok = split utama)
    tabel_terkontrol.md     E3 vs E4 (augmentasi hue) dan E3 vs E5 (sampler seimbang)
    tabel_kebocoran.md      model yang sama pada split resmi (acak) vs split blok
    tabel_per_kelas.md      recall & F1 per kelas untuk E2 vs E3
    tabel_berpasangan.md    selisih E3 - E2 per seed (seed sama = inisialisasi sama)
    hasil_ringkas.md        gabungan semua tabel di atas (di-include ke laporan)
    gambar/                 salinan confusion matrix & kurva seed pertama (outputs/ tidak di-commit)

Nilai ditampilkan sebagai rerata ± simpangan baku antar seed.

Contoh:
    python scripts/aggregate_results.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.metrics import HIGHER_IS_BETTER, SUMMARY_METRICS  # noqa: E402
from sawit.utils import load_json, resolve_path  # noqa: E402

LABELS = {
    "e0_majority": "E0 Kelas mayoritas",
    "e1_hsv_logreg": "E1 HSV + regresi logistik",
    "e2_cnn_ce": "E2 EfficientNet-B0 + CE (baseline)",
    "e3_cnn_corn": "E3 EfficientNet-B0 + CORN (utama)",
    "e4_cnn_corn_hue": "E4 = E3 + hue jitter",
    "e5_cnn_corn_balanced": "E5 = E3 + sampler seimbang",
    "e0_majority_official": "E0 Kelas mayoritas [split resmi]",
    "e1_hsv_logreg_official": "E1 HSV + regresi logistik [split resmi]",
    "e6_cnn_ce_official": "E6 = E2 [split resmi]",
    "e7_cnn_corn_official": "E7 = E3 [split resmi]",
}

# Pasangan (split resmi, split blok) untuk tabel kebocoran.
LEAK_PAIRS = [("e1_hsv_logreg_official", "e1_hsv_logreg"), ("e6_cnn_ce_official", "e2_cnn_ce"),
              ("e7_cnn_corn_official", "e3_cnn_corn")]
METRIC_NAMES = {
    "accuracy": "Akurasi ↑",
    "macro_f1": "Macro-F1 ↑",
    "mae": "MAE ↓",
    "severe_error_rate": "Kesalahan berat ↓",
    "off_by_one_acc": "Akurasi ±1 ↑",
    "qwk": "QWK ↑",
}


def collect(runs_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, per_class_rows = [], []
    for metrics_file in sorted(runs_root.glob("*/seed*/metrics_test*.json")):
        run_dir = metrics_file.parent
        experiment = run_dir.parent.name
        seed = int(run_dir.name.replace("seed", ""))
        subset = "bersih" if metrics_file.stem.endswith("clean") else "penuh"
        m = load_json(metrics_file)
        summary_file = run_dir / "summary.json"
        summary = load_json(summary_file) if summary_file.exists() else {}
        if summary.get("debug_max_batches"):
            continue  # abaikan run uji asap
        rows.append({"experiment": experiment, "seed": seed, "subset": subset, "n": m["n"],
                     **{k: m[k] for k in SUMMARY_METRICS},
                     "best_epoch": summary.get("best_epoch"),
                     "train_seconds": summary.get("train_seconds")})
        for cls, vals in m["per_class"].items():
            per_class_rows.append({"experiment": experiment, "seed": seed, "subset": subset,
                                   "kelas": cls, **vals})
    return pd.DataFrame(rows), pd.DataFrame(per_class_rows)


def fmt(mean: float, std: float, n: int, metric: str) -> str:
    digits = 3
    if n > 1 and not np.isnan(std):
        return f"{mean:.{digits}f} ± {std:.{digits}f}"
    return f"{mean:.{digits}f}"


def summary_table(df: pd.DataFrame, experiments: list[str], subset: str, bold: bool = True) -> str:
    part = df[(df.subset == subset) & (df.experiment.isin(experiments))]
    if part.empty:
        return "_Belum ada run untuk tabel ini._\n"
    grouped = part.groupby("experiment")
    means, stds, counts = grouped[SUMMARY_METRICS].mean(), grouped[SUMMARY_METRICS].std(), grouped.size()
    best = {}
    for metric in SUMMARY_METRICS:
        col = means[metric]
        best[metric] = col.max() if HIGHER_IS_BETTER[metric] else col.min()
    header = "| Eksperimen | Seed | n test | " + " | ".join(METRIC_NAMES[m] for m in SUMMARY_METRICS) + " |"
    sep = "|" + "---|" * (3 + len(SUMMARY_METRICS))
    lines = [header, sep]
    for exp in experiments:
        if exp not in means.index:
            continue
        n_test = int(part[part.experiment == exp]["n"].iloc[0])
        cells = []
        for metric in SUMMARY_METRICS:
            text = fmt(means.loc[exp, metric], stds.loc[exp, metric], counts[exp], metric)
            if bold and np.isclose(means.loc[exp, metric], best[metric]) and len(means) > 1:
                text = f"**{text}**"
            cells.append(text)
        lines.append(f"| {LABELS.get(exp, exp)} | {counts[exp]} | {n_test} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def delta_table(df: pd.DataFrame, reference: str, others: list[str], subset: str = "penuh") -> str:
    """Selisih rerata metrik terhadap eksperimen rujukan."""
    part = df[df.subset == subset]
    if reference not in set(part.experiment):
        return "_Rujukan belum dijalankan._\n"
    ref = part[part.experiment == reference][SUMMARY_METRICS].mean()
    lines = ["| Perbandingan | " + " | ".join(f"Δ {METRIC_NAMES[m]}" for m in SUMMARY_METRICS) + " |",
             "|" + "---|" * (1 + len(SUMMARY_METRICS))]
    for exp in others:
        if exp not in set(part.experiment):
            continue
        cur = part[part.experiment == exp][SUMMARY_METRICS].mean()
        lines.append(f"| {LABELS.get(exp, exp)} − {LABELS.get(reference, reference).split(' ')[0]} | "
                     + " | ".join(f"{cur[m] - ref[m]:+.3f}" for m in SUMMARY_METRICS) + " |")
    return "\n".join(lines) + "\n"


def paired_table(df: pd.DataFrame, a: str, b: str) -> str:
    """Selisih per seed (b - a) untuk seed yang sama; menunjukkan konsistensi arah perubahan."""
    part = df[df.subset == "penuh"]
    left = part[part.experiment == a].set_index("seed")
    right = part[part.experiment == b].set_index("seed")
    seeds = sorted(set(left.index) & set(right.index))
    if not seeds:
        return "_Belum ada seed yang sama untuk dibandingkan._\n"
    keys = ["macro_f1", "mae", "severe_error_rate", "qwk"]
    lines = ["| Seed | " + " | ".join(f"Δ {METRIC_NAMES[k]}" for k in keys) + " |", "|" + "---|" * (1 + len(keys))]
    for s in seeds:
        lines.append(f"| {s} | " + " | ".join(f"{right.loc[s, k] - left.loc[s, k]:+.3f}" for k in keys) + " |")
    better = {k: sum((right.loc[s, k] > left.loc[s, k]) == HIGHER_IS_BETTER[k] for s in seeds) for k in keys}
    lines.append("")
    lines.append(f"{LABELS.get(b, b)} lebih baik daripada {LABELS.get(a, a)} pada: "
                 + ", ".join(f"{METRIC_NAMES[k]} {better[k]}/{len(seeds)} seed" for k in keys) + ".")
    return "\n".join(lines) + "\n"


def leakage_table(df: pd.DataFrame) -> str:
    """Selisih metrik (split resmi − split blok) untuk model yang sama."""
    part = df[df.subset == "penuh"]
    present = set(part.experiment)
    lines = ["| Model | " + " | ".join(f"Δ {METRIC_NAMES[m]}" for m in SUMMARY_METRICS) + " |",
             "|" + "---|" * (1 + len(SUMMARY_METRICS))]
    rows = 0
    for official, block in LEAK_PAIRS:
        if official in present and block in present:
            a = part[part.experiment == official][SUMMARY_METRICS].mean()
            b = part[part.experiment == block][SUMMARY_METRICS].mean()
            lines.append(f"| {LABELS[block].split(' (')[0]} | "
                         + " | ".join(f"{a[m] - b[m]:+.3f}" for m in SUMMARY_METRICS) + " |")
            rows += 1
    if not rows:
        return "_Belum ada pasangan run split resmi vs split blok._\n"
    return "\n".join(lines) + "\n"


def per_class_table(pc: pd.DataFrame, experiments: list[str]) -> str:
    part = pc[(pc.subset == "penuh") & (pc.experiment.isin(experiments))]
    if part.empty:
        return "_Belum ada run._\n"
    mean = part.groupby(["kelas", "experiment"])[["recall", "f1"]].mean().unstack("experiment")
    exps = [e for e in experiments if e in set(part.experiment)]
    header = "| Kelas | " + " | ".join(f"Recall {e.split('_')[0].upper()}" for e in exps) + " | " \
             + " | ".join(f"F1 {e.split('_')[0].upper()}" for e in exps) + " |"
    lines = [header, "|" + "---|" * (1 + 2 * len(exps))]
    for cls in CLASS_NAMES_ID:
        if cls not in mean.index:
            continue
        lines.append(f"| {cls} | " + " | ".join(f"{mean.loc[cls, ('recall', e)]:.3f}" for e in exps) + " | "
                     + " | ".join(f"{mean.loc[cls, ('f1', e)]:.3f}" for e in exps) + " |")
    return "\n".join(lines) + "\n"


def copy_figures(runs_root: Path, out: Path) -> None:
    """Menyalin gambar per run (seed terkecil) ke results/gambar/ agar ikut di-commit."""
    import shutil

    fig_dir = out / "gambar"
    fig_dir.mkdir(parents=True, exist_ok=True)
    for exp_dir in sorted(p for p in runs_root.iterdir() if p.is_dir()):
        seeds = sorted(exp_dir.glob("seed*"), key=lambda p: int(p.name.replace("seed", "")))
        if not seeds:
            continue
        for name in ("confusion_test.png", "curves.png"):
            src = seeds[0] / name
            if src.exists():
                stem = name.replace("_test", "").replace(".png", "")
                shutil.copy(src, fig_dir / f"{stem}_{exp_dir.name}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ringkas hasil semua run.")
    parser.add_argument("--runs-root", default="outputs/runs")
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()

    runs_root, out = resolve_path(args.runs_root), resolve_path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df, pc = collect(runs_root)
    if df.empty:
        raise SystemExit(f"Tidak ada run ditemukan di {runs_root}. Latih model terlebih dahulu.")
    df.sort_values(["experiment", "subset", "seed"]).to_csv(out / "semua_run.csv", index=False)

    main_exps = ["e0_majority", "e1_hsv_logreg", "e2_cnn_ce", "e3_cnn_corn"]
    leak_exps = [e for pair in LEAK_PAIRS for e in pair]
    tables = {
        "tabel_utama.md": ("Tabel utama - test split blok (split utama)", summary_table(df, main_exps, "penuh")),
        "tabel_terkontrol.md": ("Eksperimen terkontrol pada split blok (rujukan: E3)",
                                summary_table(df, ["e3_cnn_corn", "e4_cnn_corn_hue", "e5_cnn_corn_balanced"], "penuh")
                                + "\n" + delta_table(df, "e3_cnn_corn", ["e4_cnn_corn_hue", "e5_cnn_corn_balanced"])),
        "tabel_kebocoran.md": ("Uji kebocoran: split resmi (acak) vs split blok",
                               summary_table(df, leak_exps, "penuh", bold=False)
                               + "\nSelisih split resmi − split blok (positif pada metrik ↑ = skor resmi lebih tinggi):\n\n"
                               + leakage_table(df)
                               + "\nCatatan: kedua split memakai test set berbeda, sehingga selisih adalah indikasi "
                                 "besarnya optimisme split resmi, bukan perbandingan berpasangan.\n"),
        "tabel_per_kelas.md": ("Recall dan F1 per kelas (rerata seed, test split blok)",
                               per_class_table(pc, ["e2_cnn_ce", "e3_cnn_corn", "e5_cnn_corn_balanced"])),
        "tabel_berpasangan.md": ("Perbandingan berpasangan per seed: E3 − E2 (split blok)",
                                 paired_table(df, "e2_cnn_ce", "e3_cnn_corn")),
    }
    combined = ["# Hasil Eksperimen (dibuat otomatis oleh scripts/aggregate_results.py)", "",
                "Format sel: rerata ± simpangan baku antar seed. Nilai terbaik per kolom dicetak tebal. "
                "Kesalahan berat = proporsi prediksi yang meleset ≥ 2 tingkat.", ""]
    for filename, (title, body) in tables.items():
        (out / filename).write_text(f"### {title}\n\n{body}", encoding="utf-8")
        combined += [f"### {title}", "", body]
    (out / "hasil_ringkas.md").write_text("\n".join(combined), encoding="utf-8")
    copy_figures(runs_root, out)
    print("\n".join(combined))
    print(f"Tabel tersimpan di {out}")


if __name__ == "__main__":
    main()
