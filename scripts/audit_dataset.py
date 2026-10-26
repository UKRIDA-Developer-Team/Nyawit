"""Audit dataset (CP03): distribusi kelas, resolusi, duplikat, dan kebocoran antar split.

Keluaran di results/audit/ :
    ringkasan_audit.md        ringkasan untuk proposal/laporan (di-include otomatis)
    distribusi_kelas.csv/.png jumlah gambar per kelas x split
    resolusi.csv              statistik lebar/tinggi gambar
    duplikat_persis.csv       kelompok gambar dengan MD5 identik
    near_duplicates.csv       pasangan near-duplicate (dHash, jarak Hamming <= ambang)
    sensitivitas_ambang.csv   jumlah pasangan lintas split untuk berbagai ambang
    kemiripan_berurutan.csv/.png  kemiripan warna gambar bernomor berurutan vs pasangan acak
    contoh_pasangan_berurutan.jpg 10 pasangan bernomor berurutan acak (periksa manual)
    cek_manual_pasangan_berurutan.csv  40 pasangan untuk diberi label "sama_tandan" oleh tim
    cek_manual_pasangan_berurutan.html halaman untuk melihat pasangan tersebut (baris = baris CSV)
    (ringkasan label manual: python scripts/summarize_manual_check.py -> hasil_cek_manual.md)
    distribusi_kelas_grouped.csv  distribusi split blok
    contoh_per_kelas.jpg      contoh gambar tiap kelas
    contoh_near_duplicate.jpg contoh pasangan near-duplicate lintas split (untuk diperiksa manual)

Metadata diperbarui dengan kolom:
    file_number                nomor urut pada nama berkas
    dup_group                  ID kelompok near-duplicate (dHash)
    near_dup_in_train          True bila gambar val/test punya near-duplicate dHash di train resmi
    neighbor_in_train_official True bila gambar val/test punya tetangga bernomor ±1 di train resmi
    split_group                kelompok untuk split blok (blok nomor berurutan + kelompok dHash)
    grouped_split              split blok berkelompok (split UTAMA eksperimen)

Contoh:
    python scripts/audit_dataset.py
    python scripts/audit_dataset.py --threshold 4 --block-size 30
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

from sawit.audit import (  # noqa: E402
    block_group_ids,
    duplicate_groups,
    file_number,
    flag_cross_split_leakage,
    grouped_split,
    merge_groups,
    near_duplicate_pairs,
    neighbor_in_split,
    sequential_similarity,
)
from sawit.features import load_or_compute_hsv  # noqa: E402
from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.data import class_distribution, find_dataset_root, load_metadata  # noqa: E402
from sawit.plots import image_grid  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402


def df_to_markdown(df: pd.DataFrame, index: bool = True) -> str:
    """Tabel markdown sederhana tanpa dependensi `tabulate`."""
    frame = df.reset_index() if index else df
    header = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    sep = "| " + " | ".join("---" for _ in frame.columns) + " |"
    rows = ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([header, sep, *rows])


def write_pair_viewer(cek: pd.DataFrame, id_to_path: dict, root: Path, html_path: Path) -> None:
    """Halaman HTML untuk melihat pasangan pada cek_manual_pasangan_berurutan.csv.

    Nomor "Baris" sama dengan nomor baris di spreadsheet (baris 1 = judul kolom).
    Gambar dirujuk dari folder dataset lokal, sehingga halaman hanya tampil di
    komputer yang sudah menjalankan scripts/download_data.py.
    """
    import html as html_lib
    import os

    def src(image_id: str) -> str:
        return Path(os.path.relpath(root / id_to_path[image_id], html_path.parent)).as_posix()

    cards = []
    for i, r in enumerate(cek.itertuples(), start=2):
        cards.append(
            f'<section><h2>Baris {i}</h2><div class="pair">'
            f'<figure><img src="{src(r.image_a)}"><figcaption>{html_lib.escape(r.image_a)}<br>'
            f"split resmi: {r.split_resmi_a} · split blok: {r.split_blok_a}</figcaption></figure>"
            f'<figure><img src="{src(r.image_b)}"><figcaption>{html_lib.escape(r.image_b)}<br>'
            f"split resmi: {r.split_resmi_b} · split blok: {r.split_blok_b}</figcaption></figure>"
            "</div></section>")
    page = f"""<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">
<title>Cek manual pasangan berurutan</title><style>
body {{ font-family: Arial, sans-serif; margin: 24px; background: #f4f7fb; color: #1b2733; }}
.info {{ background: #fff; border-left: 4px solid #1f5f8b; padding: 10px 16px; max-width: 900px; }}
section {{ background: #fff; margin: 18px 0; padding: 10px 16px; border-radius: 8px; max-width: 900px; }}
h2 {{ margin: 4px 0 8px; font-size: 18px; }}
.pair {{ display: flex; gap: 16px; flex-wrap: wrap; }}
figure {{ margin: 0; }} img {{ width: 420px; max-width: 100%; border-radius: 4px; }}
figcaption {{ font-size: 13px; color: #4a5d70; margin-top: 4px; }}
</style></head><body>
<h1>Cek manual: apakah kedua foto menunjukkan tandan yang sama?</h1>
<div class="info"><p>Isi kolom <b>sama_tandan</b> di <code>cek_manual_pasangan_berurutan.csv</code> pada baris yang sama:</p>
<ul><li><b>ya</b>: tandan fisik yang sama (pola buah, bentuk, duri, kotoran/serat sama), walau sudut,
jarak, atau pencahayaan berbeda;</li>
<li><b>tidak</b>: dua tandan berbeda, walau warnanya mirip atau latarnya sama;</li>
<li><b>ragu</b>: tidak bisa dipastikan (jelaskan di kolom <b>catatan</b>).</li></ul>
<p>Tip: bandingkan detail kecil seperti letak buah yang rontok, serat kering, potongan tangkai, dan benda di latar.</p></div>
{''.join(cards)}
</body></html>"""
    html_path.write_text(page, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit dataset dan kebocoran antar split.")
    parser.add_argument("--metadata", default="data/processed/metadata.csv")
    parser.add_argument("--root", default="data/raw/Dataset")
    parser.add_argument("--out-dir", default="results/audit")
    parser.add_argument("--threshold", type=int, default=5, help="Ambang jarak Hamming dHash (0-64).")
    parser.add_argument("--block-size", type=int, default=20,
                        help="Ukuran blok nomor berkas berurutan per kelas untuk split berkelompok.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split-file", default="data/splits/grouped_split.csv",
                        help="Split blok beku (image_id, grouped_split); dipakai bila cocok dengan metadata.")
    parser.add_argument("--regenerate-split", action="store_true",
                        help="Abaikan berkas split beku dan hitung ulang (hasil bergantung versi scikit-learn).")
    parser.add_argument("--write-split-file", action="store_true",
                        help="Tulis split yang dihitung ulang ke --split-file.")
    args = parser.parse_args()

    meta_path = resolve_path(args.metadata)
    df = load_metadata(meta_path)
    root = find_dataset_root(args.root)
    out = resolve_path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    md: list[str] = ["# Ringkasan Audit Dataset", ""]

    # ---- 1. Distribusi kelas ----
    dist = class_distribution(df)
    dist.to_csv(out / "distribusi_kelas.csv")
    pct = (dist.loc[dist.index != "Total", "total"] / dist.loc["Total", "total"] * 100).round(1)
    ratio = dist.loc[dist.index != "Total", "total"].max() / dist.loc[dist.index != "Total", "total"].min()
    md += ["## Distribusi kelas", "", df_to_markdown(dist), "",
           "Proporsi kelas (%): " + ", ".join(f"{k}: {v}" for k, v in pct.items()) + ".",
           f"Rasio kelas terbesar/terkecil = {ratio:.2f}.", ""]

    fig, ax = plt.subplots(figsize=(7, 3.6))
    body = dist.drop(index="Total").drop(columns="total")
    body.plot(kind="bar", ax=ax)
    ax.set_ylabel("Jumlah gambar")
    ax.set_xlabel("")
    ax.set_title("Distribusi kelas per split resmi")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(out / "distribusi_kelas.png", dpi=150)
    plt.close(fig)

    # ---- 2. Resolusi ----
    res = df.groupby("label_name")[["width", "height"]].describe().round(0)
    res.to_csv(out / "resolusi.csv")
    md += ["## Resolusi gambar", "",
           f"Lebar: min {df.width.min()}, median {int(df.width.median())}, maks {df.width.max()} px. "
           f"Tinggi: min {df.height.min()}, median {int(df.height.median())}, maks {df.height.max()} px.",
           f"Jumlah ukuran unik: {df[['width', 'height']].drop_duplicates().shape[0]}. "
           "Ukuran yang berbeda antar kelas dapat menjadi jalan pintas (shortcut); lihat resolusi.csv.", ""]

    # ---- 3. Duplikat persis (MD5) ----
    dup_md5 = df[df.duplicated("md5", keep=False)].sort_values("md5")
    dup_md5[["image_id", "label_name", "official_split", "md5"]].to_csv(out / "duplikat_persis.csv", index=False)
    md += ["## Duplikat persis (MD5 identik)", "",
           f"{dup_md5['md5'].nunique()} kelompok, {len(dup_md5)} berkas. "
           + ("Tidak ada duplikat persis." if dup_md5.empty else
              f"Lintas split: {(dup_md5.groupby('md5')['official_split'].nunique() > 1).sum()} kelompok; "
              f"label berbeda: {(dup_md5.groupby('md5')['label'].nunique() > 1).sum()} kelompok."), ""]

    # ---- 4. Near-duplicate (dHash) ----
    hashes = df["dhash"].astype(str).tolist()
    max_t = max(10, args.threshold)
    pairs_all = near_duplicate_pairs(hashes, threshold=max_t)
    split = df["official_split"].to_numpy()
    labels = df["label"].to_numpy()
    sens_rows = []
    for t in range(0, max_t + 1):
        p = pairs_all[pairs_all["distance"] <= t]
        cross = split[p["i"]] != split[p["j"]]
        sens_rows.append({
            "ambang": t,
            "pasangan": len(p),
            "pasangan_lintas_split": int(cross.sum()),
            "pasangan_label_berbeda": int((labels[p["i"]] != labels[p["j"]]).sum()),
        })
    pd.DataFrame(sens_rows).to_csv(out / "sensitivitas_ambang.csv", index=False)

    pairs = pairs_all[pairs_all["distance"] <= args.threshold].reset_index(drop=True)
    pair_table = pd.DataFrame({
        "image_i": df["image_id"].to_numpy()[pairs["i"]],
        "image_j": df["image_id"].to_numpy()[pairs["j"]],
        "split_i": split[pairs["i"]],
        "split_j": split[pairs["j"]],
        "label_i": labels[pairs["i"]],
        "label_j": labels[pairs["j"]],
        "distance": pairs["distance"].to_numpy(),
    })
    pair_table.to_csv(out / "near_duplicates.csv", index=False)

    df["dup_group"] = duplicate_groups(len(df), pairs)
    df["near_dup_in_train"] = flag_cross_split_leakage(df, pairs, "official_split")
    n_groups_multi = int((df["dup_group"].value_counts() > 1).sum())
    cross = pair_table[pair_table["split_i"] != pair_table["split_j"]]
    diff_label = pair_table[pair_table["label_i"] != pair_table["label_j"]]
    leak_val = int(df.loc[df.official_split == "val", "near_dup_in_train"].sum())
    leak_test = int(df.loc[df.official_split == "test", "near_dup_in_train"].sum())
    n_test = int((df.official_split == "test").sum())
    md += ["## Near-duplicate dan risiko kebocoran", "",
           f"Metode: dHash 64-bit, pasangan dengan jarak Hamming <= {args.threshold} dianggap near-duplicate.",
           "",
           f"- Pasangan near-duplicate: {len(pair_table)} (lintas split resmi: {len(cross)}).",
           f"- Kelompok berisi >1 gambar: {n_groups_multi}.",
           f"- Gambar validasi yang punya kembaran di train: {leak_val}.",
           f"- Gambar test yang punya kembaran di train: {leak_test} dari {n_test} "
           f"({100 * leak_test / max(n_test, 1):.1f}%). Sisanya ({n_test - leak_test}) membentuk subset **test bersih**.",
           f"- Pasangan dengan label berbeda (indikasi label ambigu/salah): {len(diff_label)}.",
           "",
           "Catatan: dHash dapat menghasilkan positif palsu pada komposisi yang mirip "
           "(mis. latar sama). Contoh pasangan perlu diperiksa manual pada "
           "`contoh_near_duplicate.jpg`; lihat juga `sensitivitas_ambang.csv`.", ""]

    # ---- 5. Pemotretan beruntun (tandan sama, sudut berbeda) ----
    # dHash hanya menangkap foto nyaris identik. Untuk "tandan sama, sudut sedikit
    # berbeda" dipakai jarak fitur warna HSV yang tidak peka pembingkaian.
    df["file_number"] = [file_number(i) for i in df["image_id"]]
    numbers = df["file_number"].to_numpy()
    features = load_or_compute_hsv(df, root, meta_path.with_name("hsv_features.npz"))
    seq, ref = sequential_similarity(features, labels, numbers, seed=args.seed)
    seq.to_csv(out / "kemiripan_berurutan.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.plot(seq["selisih_nomor"], seq["persen_lebih_mirip_dari_p5_acak"], marker="o")
    ax.axhline(5, color="tab:red", linestyle="--", label="tanpa urutan (5%)")
    ax.set_xscale("log")
    ax.set_xlabel("Selisih nomor berkas (kelas sama)")
    ax.set_ylabel("% pasangan sangat mirip")
    ax.set_title("Kemiripan warna gambar bernomor berdekatan")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "kemiripan_berurutan.png", dpi=150)
    plt.close(fig)

    df["neighbor_in_train_official"] = neighbor_in_split(labels, numbers, split, "train", window=1)
    nb_test = int(df.loc[df.official_split == "test", "neighbor_in_train_official"].sum())
    nb_val = int(df.loc[df.official_split == "val", "neighbor_in_train_official"].sum())
    n_val = int((df.official_split == "val").sum())
    k1 = seq[seq.selisih_nomor == 1].iloc[0] if (seq.selisih_nomor == 1).any() else None
    md += ["## Pemotretan beruntun (tandan sama, sudut berbeda)", "",
           "dHash hanya menangkap foto yang nyaris identik. Untuk memeriksa foto tandan yang sama dari sudut "
           "sedikit berbeda, dihitung jarak fitur warna HSV (terstandardisasi) antara gambar sekelas yang "
           "nomor berkasnya berselisih k, lalu dibandingkan dengan pasangan acak sekelas yang nomornya "
           f"berjauhan (> {ref['jarak_nomor_minimum']}). Bila nomor berkas tidak berkaitan dengan urutan "
           "pemotretan, sekitar 5% pasangan akan lebih mirip daripada persentil-5 pasangan acak.", "",
           "| Selisih nomor k | Pasangan | Median jarak | % lebih mirip dari persentil-5 acak |",
           "|---|---|---|---|"]
    md += [f"| {int(r.selisih_nomor)} | {int(r.n_pasangan)} | {r.median_jarak:.2f} | "
           f"{r.persen_lebih_mirip_dari_p5_acak:.1f}% |" for r in seq.itertuples()]
    md += ["", f"Rujukan pasangan acak: median jarak {ref['median_acak']:.2f}, persentil-5 {ref['p5_acak']:.2f}.", ""]
    if k1 is not None:
        md += [f"**Temuan:** {k1.persen_lebih_mirip_dari_p5_acak:.0f}% pasangan bernomor berurutan (k=1) "
               "sangat mirip, jauh di atas 5% yang diharapkan, dan kemiripan menurun perlahan seiring k. "
               "Artinya nomor berkas mengikuti urutan pemotretan: gambar bernomor berdekatan kemungkinan "
               "besar berasal dari tandan atau sesi yang sama.", ""]
    md += [f"- Gambar **test** resmi yang punya tetangga bernomor ±1 (kelas sama) di train resmi: "
           f"**{nb_test} dari {n_test} ({100 * nb_test / max(n_test, 1):.0f}%)**.",
           f"- Gambar validasi resmi dengan tetangga ±1 di train: {nb_val} dari {n_val} "
           f"({100 * nb_val / max(n_val, 1):.0f}%).",
           "- Konsekuensi: split resmi (acak) kemungkinan besar **terlalu optimistis**. Subset \"test bersih\" "
           "berbasis dHash tidak cukup untuk mengatasinya.",
           "- Pemeriksaan visual: lihat `contoh_pasangan_berurutan.jpg`; tim memberi label manual "
           "pada `cek_manual_pasangan_berurutan.csv` (kolom `sama_tandan`: ya/tidak/ragu) untuk "
           "memperkirakan proporsi tandan yang sama secara langsung.", ""]

    # ---- 6. Split blok berkelompok (split UTAMA) ----
    # Setiap kelas butuh cukup banyak blok agar bisa dibagi ~70/15/15; untuk dataset
    # sangat kecil (uji asap) ukuran blok diperkecil otomatis. Data asli: tetap 20.
    min_class = int(np.bincount(labels).min())
    block_size = max(1, min(args.block_size, min_class // 10))
    if block_size != args.block_size:
        print(f"Catatan: ukuran blok diperkecil {args.block_size} -> {block_size} (kelas terkecil {min_class} gambar).")
    blocks = block_group_ids(labels, numbers, block_size)
    df["split_group"] = merge_groups(blocks, df["dup_group"].to_numpy())
    # Split beku: bila berkas split tersedia dan mencakup gambar yang sama persis, pakai itu.
    # Alasan: StratifiedGroupKFold di scikit-learn >= 1.8 mengacak kelompok secara berbeda
    # dari <= 1.7, sehingga split yang dihitung ulang bisa berbeda dari split yang dipakai
    # melatih model. Split beku = split yang dipakai di Colab (scikit-learn 1.7).
    import sklearn

    split_file = resolve_path(args.split_file)
    frozen = pd.read_csv(split_file) if split_file.exists() and not args.regenerate_split else None
    if frozen is not None and set(frozen["image_id"]) == set(df["image_id"]):
        df["grouped_split"] = df["image_id"].map(dict(zip(frozen["image_id"], frozen["grouped_split"])))
        split_source = f"berkas beku `{args.split_file}`"
        # Pemeriksaan: satu kelompok tidak boleh tersebar ke lebih dari satu split.
        spread = (df.groupby("split_group")["grouped_split"].nunique() > 1).sum()
        if spread:
            print(f"PERINGATAN: {spread} kelompok tersebar di >1 split pada berkas beku.")
    else:
        df["grouped_split"] = grouped_split(labels, df["split_group"].to_numpy(), seed=args.seed)
        split_source = f"dihitung ulang (scikit-learn {sklearn.__version__})"
        if frozen is not None:
            print(f"Catatan: {args.split_file} tidak cocok dengan metadata ini; split dihitung ulang.")
        elif not args.regenerate_split:
            print(f"Catatan: {args.split_file} belum ada; split dihitung ulang.")
        if args.write_split_file:
            split_file.parent.mkdir(parents=True, exist_ok=True)
            df[["image_id", "grouped_split"]].to_csv(split_file, index=False)
            print(f"Split ditulis ke {split_file}")
    gsplit = df["grouped_split"].to_numpy()
    residual = neighbor_in_split(labels, numbers, gsplit, "train", window=1)
    g_test = gsplit == "test"
    gdist = class_distribution(df, "grouped_split")
    gdist.to_csv(out / "distribusi_kelas_grouped.csv")
    md += ["## Split blok berkelompok (split utama)", "",
           f"Nomor berkas setiap kelas dibagi menjadi blok berisi {block_size} nomor berurutan; "
           "blok digabung dengan kelompok dHash, lalu dibagi dengan StratifiedGroupKFold (seed "
           f"{args.seed}) sehingga satu blok selalu berada di split yang sama (~70/15/15). "
           "Split ini dipakai sebagai **split utama**; split resmi tetap dilaporkan sebagai pembanding.",
           f"Sumber split: {split_source}.", "",
           df_to_markdown(gdist), "",
           f"- Kelompok: {df['split_group'].nunique()} (blok {block_size} nomor + gabungan dHash).",
           f"- Gambar test (split blok) yang punya tetangga ±1 di train: {int(residual[g_test].sum())} dari "
           f"{int(g_test.sum())} ({100 * residual[g_test].mean():.1f}%), hanya di batas blok "
           f"(bandingkan {100 * nb_test / max(n_test, 1):.0f}% pada split resmi).",
           "- Keterbatasan: korelasi sesi pemotretan masih terlihat hingga selisih puluhan nomor, sehingga "
           "split blok mengurangi, tetapi tidak menghapus sepenuhnya, kemiripan antara train dan test.", ""]

    # Gambar contoh pasangan berurutan + daftar cek manual.
    index = {(lab, num): i for i, (lab, num) in enumerate(zip(labels, numbers))}
    consecutive = [(i, index[(lab, num + 1)]) for (lab, num), i in index.items() if (lab, num + 1) in index]
    rng_pairs = np.random.default_rng(args.seed)
    order = rng_pairs.permutation(len(consecutive))
    cek = pd.DataFrame([{
        "image_a": df.image_id.iloc[a], "image_b": df.image_id.iloc[b],
        "split_resmi_a": split[a], "split_resmi_b": split[b],
        "split_blok_a": gsplit[a], "split_blok_b": gsplit[b],
        "sama_tandan": "", "catatan": "",
    } for a, b in (consecutive[k] for k in order[:40])])
    cek_path = out / "cek_manual_pasangan_berurutan.csv"
    # Jangan menimpa label manual yang sudah diisi tim saat audit dijalankan ulang.
    already_filled = (cek_path.exists()
                      and pd.read_csv(cek_path, dtype=str)["sama_tandan"].fillna("").str.strip().ne("").any())
    if already_filled:
        print(f"Catatan: {cek_path.name} sudah berisi label manual; tidak ditimpa.")
    else:
        cek.to_csv(cek_path, index=False)
    write_pair_viewer(cek, dict(zip(df.image_id, df.rel_path)), root, out / "cek_manual_pasangan_berurutan.html")
    show_pairs = [consecutive[k] for k in order[:10]]
    image_grid([root / df.rel_path.iloc[x] for pair in show_pairs for x in pair],
               [f"{df.image_id.iloc[x]} [{split[x]}]" for pair in show_pairs for x in pair],
               out / "contoh_pasangan_berurutan.jpg", ncols=4,
               title="Pasangan bernomor berurutan (acak): tandan yang sama?")

    df.to_csv(meta_path, index=False)
    md += [f"Metadata diperbarui: `{args.metadata}` (kolom file_number, dup_group, near_dup_in_train, "
           "neighbor_in_train_official, split_group, grouped_split).", ""]

    # ---- 6. Gambar contoh ----
    rng = np.random.default_rng(args.seed)
    sample_paths, sample_caps = [], []
    for label in range(len(CLASS_NAMES_ID)):
        part = df[(df.label == label) & (df.official_split == "train")]
        if part.empty:
            part = df[df.label == label]
        take = part.iloc[rng.choice(len(part), size=min(5, len(part)), replace=False)]
        sample_paths += [root / p for p in take["rel_path"]]
        sample_caps += [f"{CLASS_NAMES_ID[label]}\n{r.image_id} ({r.width}x{r.height})" for r in take.itertuples()]
    image_grid(sample_paths, sample_caps, out / "contoh_per_kelas.jpg", ncols=5,
               title="Contoh gambar per kelas (baris = kelas)")

    show = pd.concat([cross.sort_values("distance").head(8), diff_label.sort_values("distance").head(4)]).drop_duplicates()
    if not show.empty:
        id_to_path = dict(zip(df["image_id"], df["rel_path"]))
        paths, caps = [], []
        for r in show.itertuples():
            paths += [root / id_to_path[r.image_i], root / id_to_path[r.image_j]]
            caps += [f"{r.image_i} [{r.split_i}]\njarak={r.distance}",
                     f"{r.image_j} [{r.split_j}]\njarak={r.distance}"]
        image_grid(paths, caps, out / "contoh_near_duplicate.jpg", ncols=4,
                   title="Pasangan near-duplicate (periksa manual)")

    (out / "ringkasan_audit.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"\nHasil audit tersimpan di {out}")


if __name__ == "__main__":
    main()
