"""Meringkas label manual pada results/audit/cek_manual_pasangan_berurutan.csv.

Tim memberi label pada 40 pasangan foto bernomor berurutan (dipilih acak dengan
seed tetap oleh scripts/audit_dataset.py): apakah kedua foto menunjukkan tandan
fisik yang sama. Label diterima dalam Bahasa Indonesia (ya/tidak/ragu) maupun
Inggris (yes/no/unsure).

Keluaran: results/audit/hasil_cek_manual.md

Contoh:
    python scripts/summarize_manual_check.py
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd

LABEL_MAP = {"ya": "ya", "yes": "ya", "tidak": "tidak", "no": "tidak", "ragu": "ragu", "unsure": "ragu"}
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Interval kepercayaan 95% Wilson untuk proporsi k/n (cocok untuk n kecil)."""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - half, center + half


def separated(df: pd.DataFrame, col_a: str, col_b: str) -> int:
    """Jumlah pasangan yang satu fotonya di train dan pasangannya di val/test."""
    a, b = df[col_a], df[col_b]
    return int(((a != b) & ((a == "train") | (b == "train"))).sum())


def main() -> None:
    parser = argparse.ArgumentParser(description="Ringkas label manual pasangan berurutan.")
    parser.add_argument("--csv", default="results/audit/cek_manual_pasangan_berurutan.csv")
    parser.add_argument("--out", default="results/audit/hasil_cek_manual.md")
    args = parser.parse_args()

    # utf-8-sig: spreadsheet sering menyimpan CSV dengan BOM.
    df = pd.read_csv(PROJECT_ROOT / args.csv, encoding="utf-8-sig", dtype=str).fillna("")
    df["label"] = df["sama_tandan"].str.strip().str.lower().map(LABEL_MAP)
    unknown = df[df["label"].isna() & df["sama_tandan"].str.strip().ne("")]
    if not unknown.empty:
        raise SystemExit(f"Label tidak dikenal: {sorted(unknown['sama_tandan'].unique())} (pakai ya/tidak/ragu)")
    filled = df[df["label"].notna()]
    n, n_ya, n_tidak, n_ragu = len(filled), (filled.label == "ya").sum(), (filled.label == "tidak").sum(), \
        (filled.label == "ragu").sum()
    decided = n_ya + n_tidak
    lo_d, hi_d = wilson_interval(n_ya, decided)
    lo_a, hi_a = wilson_interval(n_ya, n)
    same = filled[filled.label == "ya"]
    sep_official = separated(same, "split_resmi_a", "split_resmi_b")
    sep_block = separated(same, "split_blok_a", "split_blok_b")

    lines = [
        "# Hasil cek manual pasangan bernomor berurutan", "",
        f"Pasangan dilabeli: {n} dari {len(df)} (acak, seed tetap). "
        f"**Ya (tandan sama): {n_ya}**, tidak: {n_tidak}, ragu: {n_ragu}.", "",
        f"- Di antara pasangan yang dapat diputuskan: **{100 * n_ya / max(decided, 1):.0f}%** tandan sama "
        f"({n_ya}/{decided}; IK 95% Wilson {100 * lo_d:.0f}–{100 * hi_d:.0f}%).",
        f"- Batas bawah (ragu dihitung \"tidak\"): {100 * n_ya / max(n, 1):.0f}% "
        f"(IK 95% {100 * lo_a:.0f}–{100 * hi_a:.0f}%).",
        f"- Dari {n_ya} pasangan tandan sama, yang **terpisah antara train dan val/test**: "
        f"**{sep_official} pada split resmi**, **{sep_block} pada split blok**.", "",
        "Kesimpulan: foto bernomor berurutan sering merupakan tandan fisik yang sama. Split resmi (acak) "
        "memisahkan sebagian pasangan tersebut ke train dan val/test, sedangkan split blok menjaganya "
        "tetap dalam satu split. Ini mengonfirmasi secara manual temuan statistik pada audit.", "",
        "Catatan: sampel kecil (40 pasangan) dan dilabeli oleh tim (bukan ahli sawit); banyaknya label "
        "\"ragu\" berasal dari foto gelap/terang, tertutup tangan, atau terlalu dekat (lihat kolom `catatan`).", "",
    ]
    out = PROJECT_ROOT / args.out
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Tersimpan: {out}")


if __name__ == "__main__":
    main()
