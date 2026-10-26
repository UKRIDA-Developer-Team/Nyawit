"""Analisis kesalahan (CP11) untuk satu run.

Keluaran di results/analisis_kesalahan/<eksperimen>_seed<seed>/ :
    ringkasan.md              statistik kesalahan (di-include ke laporan)
    pasangan_tertukar.csv     pasangan (label -> prediksi) yang paling sering
    galeri_salah_berat.jpg    kesalahan >= 2 tingkat dengan keyakinan tertinggi
    galeri_salah_tetangga.jpg kesalahan 1 tingkat dengan keyakinan tertinggi
    galeri_gradcam.jpg        Grad-CAM untuk sebagian kesalahan (bila checkpoint ada)
    kategori_manual.csv       daftar kesalahan untuk diberi kategori secara manual

Kategori manual yang disarankan (diisi tim setelah melihat galeri):
    pencahayaan | latar_ramai | oklusi_terpotong | banyak_tandan | blur |
    label_ambigu | lainnya

Contoh:
    python scripts/error_analysis.py --run-dir outputs/runs/e3_cnn_corn/seed42
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.data import find_dataset_root  # noqa: E402
from sawit.plots import image_grid  # noqa: E402
from sawit.utils import load_json, resolve_path  # noqa: E402


def caption(row) -> str:
    conf = f" p={row.confidence:.2f}" if hasattr(row, "confidence") else ""
    return f"{row.image_id}\nlabel: {CLASS_NAMES_ID[row.label]}\nprediksi: {CLASS_NAMES_ID[row.pred]}{conf}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisis kesalahan satu run.")
    parser.add_argument("--run-dir", default="outputs/runs/e3_cnn_corn/seed42")
    parser.add_argument("--root", default="data/raw/Dataset")
    parser.add_argument("--out-dir", default="results/analisis_kesalahan")
    parser.add_argument("--n-gradcam", type=int, default=8)
    args = parser.parse_args()

    run_dir = resolve_path(args.run_dir)
    preds = pd.read_csv(run_dir / "predictions_test.csv")
    root = find_dataset_root(args.root)
    name = f"{run_dir.parent.name}_{run_dir.name}"
    out = resolve_path(args.out_dir) / name
    out.mkdir(parents=True, exist_ok=True)

    errors = preds[preds["label"] != preds["pred"]].copy()
    errors["jenis"] = errors["abs_err"].map(lambda e: "tetangga (1 tingkat)" if e == 1 else "berat (>=2 tingkat)")
    sort_key = "confidence" if "confidence" in errors.columns else "abs_err"

    pairs = (errors.groupby(["label", "pred"]).size().rename("jumlah").reset_index()
             .sort_values("jumlah", ascending=False))
    pairs["label_nama"] = pairs["label"].map(lambda i: CLASS_NAMES_ID[i])
    pairs["prediksi_nama"] = pairs["pred"].map(lambda i: CLASS_NAMES_ID[i])
    pairs["selisih_tingkat"] = (pairs["label"] - pairs["pred"]).abs()
    pairs.to_csv(out / "pasangan_tertukar.csv", index=False)

    severe = errors[errors["abs_err"] >= 2].sort_values(sort_key, ascending=False).head(15)
    adjacent = errors[errors["abs_err"] == 1].sort_values(sort_key, ascending=False).head(10)
    image_grid([root / p for p in severe["rel_path"]], [caption(r) for r in severe.itertuples()],
               out / "galeri_salah_berat.jpg", title="Kesalahan berat dengan keyakinan tertinggi")
    image_grid([root / p for p in adjacent["rel_path"]], [caption(r) for r in adjacent.itertuples()],
               out / "galeri_salah_tetangga.jpg", title="Kesalahan 1 tingkat dengan keyakinan tertinggi")

    manual = errors[["image_id", "label", "pred", "abs_err", "jenis"]
                    + (["confidence"] if "confidence" in errors.columns else [])].copy()
    manual["label_nama"] = manual["label"].map(lambda i: CLASS_NAMES_ID[i])
    manual["prediksi_nama"] = manual["pred"].map(lambda i: CLASS_NAMES_ID[i])
    manual["kategori_manual"] = ""
    manual["catatan"] = ""
    manual.sort_values(["abs_err", sort_key], ascending=False).to_csv(out / "kategori_manual.csv", index=False)

    # Grad-CAM untuk kesalahan teratas (hanya untuk run CNN yang punya checkpoint).
    ckpt = run_dir / "best.pt"
    if ckpt.exists() and args.n_gradcam > 0 and not errors.empty:
        from sawit.predict import Predictor

        predictor = Predictor(ckpt)
        subset = pd.concat([severe, adjacent]).head(args.n_gradcam)
        tmp_paths, caps = [], []
        for r in subset.itertuples():
            with Image.open(root / r.rel_path) as img:
                overlay = predictor.gradcam(img.convert("RGB"))
            p = out / f"_gradcam_{r.image_id}.png"
            overlay.save(p)
            tmp_paths.append(p)
            caps.append(caption(r))
        image_grid(tmp_paths, caps, out / "galeri_gradcam.jpg", ncols=4,
                   title="Grad-CAM pada kesalahan (area merah = paling berpengaruh)")
        for p in tmp_paths:
            p.unlink()

    n = len(preds)
    lines = [f"# Analisis kesalahan: {name}", "",
             f"- Gambar test: {n}; salah: {len(errors)} ({100 * len(errors) / n:.1f}%).",
             f"- Kesalahan tetangga (1 tingkat): {(errors.abs_err == 1).sum()}; "
             f"kesalahan berat (≥2 tingkat): {(errors.abs_err >= 2).sum()}."]
    if "near_dup_in_train" in preds.columns:
        dup = preds["near_dup_in_train"].astype(bool)
        err = preds["label"] != preds["pred"]
        lines.append(f"- Tingkat kesalahan pada gambar yang punya near-duplicate di train: "
                     f"{100 * err[dup].mean():.1f}% (n={dup.sum()}); tanpa near-duplicate: "
                     f"{100 * err[~dup].mean():.1f}% (n={(~dup).sum()}).")
    if "confidence" in preds.columns:
        bins = pd.cut(preds["confidence"], [0, 0.5, 0.7, 0.9, 1.0], include_lowest=True)
        acc = (preds["label"] == preds["pred"]).groupby(bins, observed=False).agg(["mean", "size"])
        lines += ["", "Akurasi per rentang keyakinan (untuk menentukan ambang peringatan di demo):", "",
                  "| Keyakinan | n | Akurasi |", "|---|---|---|"]
        lines += [f"| {idx} | {int(r['size'])} | {r['mean']:.3f} |" for idx, r in acc.iterrows()]
    lines += ["", "Pasangan yang paling sering tertukar:", "", "| Label | Prediksi | Selisih | Jumlah |",
              "|---|---|---|---|"]
    lines += [f"| {r.label_nama} | {r.prediksi_nama} | {r.selisih_tingkat} | {r.jumlah} |"
              for r in pairs.head(8).itertuples()]
    metrics_file = run_dir / "metrics_test.json"
    if metrics_file.exists():
        per_class = load_json(metrics_file)["per_class"]
        weakest = min(per_class.items(), key=lambda kv: kv[1]["recall"])
        lines += ["", f"Kelas dengan recall terendah: **{weakest[0]}** (recall {weakest[1]['recall']:.3f}, "
                      f"n={weakest[1]['support']})."]
    lines += ["", "Kategori penyebab diisi manual pada `kategori_manual.csv` setelah melihat galeri.", ""]
    (out / "ringkasan.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Hasil di {out}")


if __name__ == "__main__":
    main()
