"""Uji model pada sampel foto + penjelasan Grad-CAM (masukan asisten dosen).

Dua mode:
  1. Sampel dataset: N foto per kelas diambil acak dari data UJI split blok
     (foto yang tidak pernah dilihat model saat pelatihan).
         python scripts/uji_sampel.py --dataset 10

  2. Foto dari luar dataset (mis. internet): letakkan foto di subfolder per kelas,
     nama subfolder diawali angka kelas atau memuat nama kelas, contoh:
         data/uji_internet/0_mentah/foto1.jpg
         data/uji_internet/3_terlalu_matang/foto7.png
     Foto yang diletakkan langsung di folder utama dianggap tanpa label.
         python scripts/uji_sampel.py --folder data/uji_internet

Keluaran (default results/uji_sampel/<nama>/):
  hasil.csv     satu baris per foto: label, prediksi, keyakinan, peluang per tingkat
  ringkasan.md  akurasi, akurasi ±1 tingkat, rincian per kelas, foto berkeyakinan rendah
  galeri*.jpg   foto asli berdampingan dengan peta Grad-CAM beserta label dan prediksi
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.data import find_dataset_root, load_metadata  # noqa: E402
from sawit.predict import LOW_CONFIDENCE_THRESHOLD, Predictor  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
# Kata kunci nama subfolder -> label (urutan penting: "matang_penuh" dicek sebelum "matang").
FOLDER_KEYWORDS = [
    ("setengah", 1), ("partially", 1), ("terlalu", 3), ("over", 3),
    ("penuh", 2), ("fully", 2), ("mentah", 0), ("immature", 0),
    ("busuk", 4), ("decayed", 4),
]


def label_from_folder(name: str) -> int | None:
    lower = name.lower()
    if lower[:1].isdigit() and int(lower[0]) < len(CLASS_NAMES_ID):
        return int(lower[0])
    for keyword, label in FOLDER_KEYWORDS:
        if keyword in lower:
            return label
    return None


def sample_dataset(n_per_class: int, seed: int) -> list[tuple[Path, int | None]]:
    """N foto acak per kelas dari data uji split blok."""
    df = load_metadata("data/processed/metadata.csv")
    root = find_dataset_root("data/raw/Dataset")
    test = df[df["grouped_split"] == "test"]
    items = []
    for label in range(len(CLASS_NAMES_ID)):
        part = test[test["label"] == label]
        take = part.sample(n=min(n_per_class, len(part)), random_state=seed)
        items += [(root / p, label) for p in take["rel_path"]]
    return items


def collect_folder(folder: Path) -> list[tuple[Path, int | None]]:
    items = []
    for path in sorted(folder.rglob("*")):
        if path.suffix.lower() not in EXTENSIONS:
            continue
        label = label_from_folder(path.parent.name) if path.parent != folder else None
        items.append((path, label))
    return items


def side_by_side(photo: Image.Image, cam: Image.Image, size: int = 224) -> Image.Image:
    """Foto (dipotong seperti input model) di kiri, Grad-CAM di kanan."""
    shown = photo.copy()
    shown.thumbnail((size * 2, size * 2))
    side = min(shown.size)
    left, top = (shown.width - side) // 2, (shown.height - side) // 2
    shown = shown.crop((left, top, left + side, top + side)).resize((size, size))
    canvas = Image.new("RGB", (size * 2 + 4, size), "white")
    canvas.paste(shown, (0, 0))
    canvas.paste(cam.resize((size, size)), (size + 4, 0))
    return canvas


def save_gallery(rows: list[dict], images: list[Image.Image], path: Path, title: str, ncols: int = 4) -> None:
    if not rows:
        return
    nrows = int(np.ceil(len(rows) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.2 * nrows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, row, img in zip(axes.flat, rows, images):
        ax.imshow(img)
        if row["label"] is None:
            caption, color = f"Prediksi: {row['prediksi']} ({row['keyakinan']:.2f})", "black"
        else:
            mark = "BENAR" if row["benar"] else f"SALAH ({row['selisih']:+d} tingkat)"
            caption = f"Label: {row['label_nama']}\nPrediksi: {row['prediksi']} ({row['keyakinan']:.2f}) - {mark}"
            color = "black" if row["benar"] else "red"
        if row["keyakinan_rendah"]:
            caption += "\n[keyakinan rendah: periksa manual]"
        ax.set_title(f"{row['berkas']}\n{caption}", fontsize=7.5, color=color)
    fig.suptitle(title + "  (kiri: foto, kanan: Grad-CAM)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=110, pil_kwargs={"quality": 85})
    plt.close(fig)


def summarize(df: pd.DataFrame, source: str, model: str) -> str:
    md = ["# Uji sampel", "", f"- Sumber foto: {source}", f"- Model: {model}",
          f"- Jumlah foto: {len(df)}",
          f"- Ambang keyakinan rendah: {LOW_CONFIDENCE_THRESHOLD}", ""]
    labelled = df[df["label"].notna()].astype({"label": int, "benar": bool, "selisih": int})
    if not labelled.empty:
        md += [f"**Akurasi: {labelled['benar'].mean():.0%}** ({int(labelled['benar'].sum())} dari {len(labelled)}); "
               f"meleset paling jauh 1 tingkat: {(labelled['selisih'].abs() <= 1).mean():.0%}.", "",
               "| Kelas | Jumlah | Benar | Prediksi yang salah |", "|---|---|---|---|"]
        for label in range(len(CLASS_NAMES_ID)):
            part = labelled[labelled["label"] == label]
            if part.empty:
                continue
            wrong = part[~part["benar"]]["prediksi"].value_counts()
            wrong_txt = ", ".join(f"{k} ({v})" for k, v in wrong.items()) or "-"
            md.append(f"| {CLASS_NAMES_ID[label]} | {len(part)} | {int(part['benar'].sum())} | {wrong_txt} |")
        md.append("")
    low = df[df["keyakinan_rendah"]]
    md += [f"Foto berkeyakinan rendah (< {LOW_CONFIDENCE_THRESHOLD}): {len(low)}."]
    md += [f"- {r.berkas}: prediksi {r.prediksi} ({r.keyakinan:.2f}), kedua {r.kedua} ({r.peluang_kedua:.2f})"
           for r in low.itertuples()]
    md += ["", "Cara membaca Grad-CAM: area merah/kuning paling memengaruhi prediksi. "
           "Penjelasan yang wajar berada di tandan buah; bila panas berada di latar (tanah, daun, langit), "
           "prediksi patut dicurigai walaupun benar."]
    return "\n".join(md) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Uji model pada sampel foto dengan Grad-CAM.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dataset", type=int, metavar="N", help="N foto acak per kelas dari data uji split blok.")
    group.add_argument("--folder", help="Folder foto dari luar dataset (subfolder per kelas bila berlabel).")
    parser.add_argument("--checkpoint", default="outputs/runs/e3_cnn_corn/seed42/best.pt")
    parser.add_argument("--out", default=None, help="Folder keluaran (default results/uji_sampel/<nama>).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    if args.dataset:
        items = sample_dataset(args.dataset, args.seed)
        name, source = f"dataset_{args.dataset}_per_kelas", f"data uji split blok, {args.dataset} foto acak per kelas (seed {args.seed})"
    else:
        folder = Path(args.folder).expanduser()
        items = collect_folder(folder)
        name, source = folder.name, f"folder `{folder}`"
    if not items:
        raise SystemExit("Tidak ada foto ditemukan.")
    out = resolve_path(args.out or f"results/uji_sampel/{name}")
    out.mkdir(parents=True, exist_ok=True)

    predictor = Predictor(resolve_path(args.checkpoint), device=args.device)
    rows, panels = [], []
    for path, label in items:
        with Image.open(path) as img:
            photo = img.convert("RGB")
        pred = predictor.predict(photo)
        probs = np.array(list(pred["probs"].values()))
        second = int(np.argsort(probs)[-2])
        row = {
            "berkas": path.name,
            "label": label,
            "label_nama": CLASS_NAMES_ID[label] if label is not None else "",
            "prediksi": pred["pred_name"],
            "tingkat_prediksi": pred["pred_level"],
            "keyakinan": pred["confidence"],
            "kedua": CLASS_NAMES_ID[second],
            "peluang_kedua": float(probs[second]),
            "nilai_harapan": pred["expected_level"],
            "keyakinan_rendah": pred["low_confidence"],
            "benar": (label == pred["pred_level"]) if label is not None else None,
            "selisih": (pred["pred_level"] - label) if label is not None else None,
            **{f"p_{k}": v for k, v in pred["probs"].items()},
            "path": str(path),
        }
        rows.append(row)
        panels.append(side_by_side(photo, predictor.gradcam(photo, target_class=pred["pred_level"])))
        mark = "" if label is None else ("  benar" if row["benar"] else "  SALAH")
        print(f"{path.name[:34]:<34} -> {pred['pred_name']:<16} {pred['confidence']:.2f}{mark}")

    df = pd.DataFrame(rows)
    df.to_csv(out / "hasil.csv", index=False)
    (out / "ringkasan.md").write_text(summarize(df, source, predictor.experiment_name), encoding="utf-8")

    if args.dataset:
        for label in range(len(CLASS_NAMES_ID)):
            idx = [i for i, r in enumerate(rows) if r["label"] == label]
            save_gallery([rows[i] for i in idx], [panels[i] for i in idx],
                         out / f"galeri_{label}_{CLASS_NAMES_ID[label].lower().replace(' ', '_')}.jpg",
                         f"Kelas {label} - {CLASS_NAMES_ID[label]}")
    else:
        save_gallery(rows, panels, out / "galeri.jpg", f"Foto dari {source}")
    print(f"\nHasil tersimpan di {out}")
    print((out / "ringkasan.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
