"""Baseline non-deep learning (E0 dan E1), dijalankan pada split yang sama dengan CNN.

E0 - Kelas mayoritas : selalu menebak kelas terbanyak di train (batas bawah).
E1 - Histogram HSV + regresi logistik : fitur warna sederhana. Karena
     kematangan sawit terutama terlihat dari perubahan warna (hitam/ungu ->
     merah/oranye -> kusam/gelap), baseline ini menguji seberapa jauh warna
     saja sudah cukup, sebelum memakai CNN.

Keluaran mengikuti format run CNN (outputs/runs/<nama>/seed42/...) sehingga
dapat diringkas bersama oleh scripts/aggregate_results.py.

Contoh:
    python scripts/run_classic_baselines.py                          # split blok (utama)
    python scripts/run_classic_baselines.py --split-scheme official  # split resmi (pembanding)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from sawit.data import find_dataset_root, load_metadata, split_column  # noqa: E402
from sawit.features import load_or_compute_hsv  # noqa: E402
from sawit.metrics import compute_metrics  # noqa: E402
from sawit.plots import plot_confusion  # noqa: E402
from sawit.utils import resolve_path, save_json  # noqa: E402


def save_run(name: str, desc: str, split_df: dict, preds: dict, out_root: Path, extra: dict) -> None:
    run_dir = out_root / name / "seed42"
    run_dir.mkdir(parents=True, exist_ok=True)
    val_m = compute_metrics(split_df["val"]["label"], preds["val"])
    test_m = compute_metrics(split_df["test"]["label"], preds["test"])
    save_json(val_m, run_dir / "metrics_val.json")
    save_json(test_m, run_dir / "metrics_test.json")
    table = split_df["test"][["image_id", "rel_path", "label"]].copy()
    table["pred"] = preds["test"]
    table["abs_err"] = (table["label"] - table["pred"]).abs()
    if "near_dup_in_train" in split_df["test"].columns:
        table["near_dup_in_train"] = split_df["test"]["near_dup_in_train"].to_numpy()
    table.to_csv(run_dir / "predictions_test.csv", index=False)
    plot_confusion(test_m["confusion_matrix"], run_dir / "confusion_test.png", title=f"{name} - test")
    summary = {
        "experiment_name": name,
        "description": desc,
        "seed": 42,
        "test": {k: v for k, v in test_m.items() if k not in ("per_class", "confusion_matrix")},
        **extra,
    }
    if "near_dup_in_train" in table.columns and extra.get("split_scheme") == "official":
        clean = table[~table["near_dup_in_train"].astype(bool)]
        clean_m = compute_metrics(clean["label"], clean["pred"])
        save_json(clean_m, run_dir / "metrics_test_clean.json")
        summary["test_clean"] = {k: v for k, v in clean_m.items() if k not in ("per_class", "confusion_matrix")}
    save_json(summary, run_dir / "summary.json")
    print(f"[{name}] test acc {test_m['accuracy']:.4f} macro-F1 {test_m['macro_f1']:.4f} "
          f"MAE {test_m['mae']:.4f} kesalahan berat {test_m['severe_error_rate']:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline kelas mayoritas dan HSV + regresi logistik.")
    parser.add_argument("--metadata", default="data/processed/metadata.csv")
    parser.add_argument("--root", default="data/raw/Dataset")
    parser.add_argument("--split-scheme", default="grouped", choices=["official", "grouped"],
                        help="grouped = split blok (utama); official = split resmi (pembanding)")
    parser.add_argument("--output-root", default="outputs/runs")
    parser.add_argument("--suffix", default=None,
                        help="Akhiran nama run (default: '' untuk grouped, '_official' untuk official)")
    args = parser.parse_args()

    df = load_metadata(args.metadata)
    root = find_dataset_root(args.root)
    col = split_column(args.split_scheme)
    out_root = resolve_path(args.output_root)
    if args.suffix is None:
        args.suffix = "" if args.split_scheme == "grouped" else "_official"

    # Fitur dihitung sekali (juga dipakai audit) lalu disimpan di cache.
    t0 = time.time()
    features = load_or_compute_hsv(df, root, resolve_path(args.metadata).with_name("hsv_features.npz"))
    print(f"Fitur HSV siap: {len(df)} gambar ({time.time() - t0:.1f} s)")

    parts = {s: df[df[col] == s] for s in ("train", "val", "test")}
    X = {s: features[parts[s].index.to_numpy()] for s in parts}
    y = {s: parts[s]["label"].to_numpy() for s in parts}

    # E0 - kelas mayoritas
    dummy = DummyClassifier(strategy="most_frequent").fit(X["train"], y["train"])
    save_run(f"e0_majority{args.suffix}", "Selalu menebak kelas mayoritas train",
             parts, {s: dummy.predict(X[s]) for s in ("val", "test")}, out_root,
             {"split_scheme": args.split_scheme})

    # E1 - HSV + regresi logistik; C dipilih dari macro-F1 validasi (test tidak disentuh).
    from sklearn.metrics import f1_score

    best = None
    # Grid mencakup nilai besar karena C terbaik sempat jatuh di batas grid (100).
    for C in (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0):
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000))
        clf.fit(X["train"], y["train"])
        score = f1_score(y["val"], clf.predict(X["val"]), average="macro")
        print(f"  E1 C={C:<6} macro-F1 val = {score:.4f}")
        if best is None or score > best[0]:
            best = (score, C, clf)
    _, best_c, clf = best
    t0 = time.perf_counter()
    test_pred = clf.predict(X["test"])
    ms_per_img = (time.perf_counter() - t0) * 1000 / len(X["test"])
    save_run(f"e1_hsv_logreg{args.suffix}", f"Histogram HSV (40 fitur) + regresi logistik, C={best_c}",
             parts, {"val": clf.predict(X["val"]), "test": test_pred}, out_root,
             {"split_scheme": args.split_scheme, "selected_C": best_c,
              "classifier_ms_per_image_excl_features": ms_per_img})


if __name__ == "__main__":
    main()
