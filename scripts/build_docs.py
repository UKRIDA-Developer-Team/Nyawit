"""Membangun PDF proposal, slide, dan laporan dari sumber Markdown.

Alur: Markdown → (sisipkan hasil eksperimen) → HTML → PDF lewat Chromium/Chrome headless.

Direktif khusus di Markdown:
    <!-- slides -->                         baris pertama: berkas adalah slide 16:9, dipisah '---'
    <!-- include: path/berkas.md -->        sisipkan isi berkas (path relatif akar repo)
    <!-- include: path notitle -->          ... tanpa judul pertama
    <!-- include: path excerpt=Teks -->     ... hanya bagian dengan judul mengandung "Teks"
    ![alt](gambar.png){: style="max-height:3in"}   atur ukuran gambar (ekstensi attr_list)
Berkas yang belum ada (mis. hasil sebelum eksperimen dijalankan) diganti
catatan "belum tersedia", sehingga dokumen tetap dapat dibangun kapan saja.

Contoh:
    python scripts/build_docs.py                 # semua dokumen
    python scripts/build_docs.py --only proposal
    python scripts/build_docs.py --html-only     # tanpa Chromium
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

# Akar repositori; sengaja tidak mengimpor paket `sawit` agar dokumen dapat
# dibangun tanpa memasang PyTorch.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS = {
    "proposal": "docs/02_Proposal_UTS/K03_KematanganSawit_Proposal_v01.md",
    "slide_uts": "docs/02_Proposal_UTS/K03_KematanganSawit_SlideUTS_v01.md",
    "laporan": "docs/06_Laporan_UAS/K03_KematanganSawit_LaporanFinal.md",
    "slide_uas": "docs/06_Laporan_UAS/K03_KematanganSawit_SlideUAS.md",
}

INCLUDE_RE = re.compile(r"<!--\s*include:\s*(\S+)((?:\s+[^\s>]+)*)\s*-->")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

BASE_CSS = """
:root { --teks:#1b2733; --aksen:#1f5f8b; --garis:#cfd8e3; --latar:#f4f7fb; }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Arial, "Liberation Sans", sans-serif; color: var(--teks); line-height: 1.45; }
h1, h2, h3, h4 { color: #12263a; line-height: 1.2; }
h2 { border-bottom: 2px solid var(--aksen); padding-bottom: 3px; }
a { color: var(--aksen); text-decoration: none; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 0.86em; }
th { background: #0c2238; color: #fff; text-align: left; padding: 5px 7px; }
td { border-bottom: 1px solid var(--garis); padding: 4px 7px; vertical-align: top; }
tr:nth-child(even) td { background: var(--latar); }
code { background: #eef2f7; padding: 1px 4px; border-radius: 3px; font-size: 0.9em; }
pre { background: #eef2f7; padding: 8px 10px; border-radius: 4px; overflow-x: auto; font-size: 0.82em; }
pre code { background: none; padding: 0; }
blockquote { margin: 10px 0; padding: 8px 12px; background: #fff7e6; border-left: 4px solid #e0a12b; }
.belum { background: #eef2f7; border: 1px dashed #8aa0b6; padding: 10px; color: #4a5d70; font-style: italic; margin: 8px 0; }
figure { margin: 12px 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 420px; }
figcaption { font-size: 0.85em; color: #4a5d70; margin-top: 4px; }
"""

DOC_CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
body { font-size: 10.5pt; }
h1 { font-size: 18pt; margin-top: 0; }
h2 { font-size: 13.5pt; margin-top: 18px; }
h3 { font-size: 11.5pt; }
tr, img { page-break-inside: avoid; }
"""

SLIDE_CSS = """
@page { size: 13.333in 7.5in; margin: 0; }
body { margin: 0; font-size: 17pt; }
section.slide { width: 13.333in; height: 7.5in; padding: 0.45in 0.6in; overflow: hidden;
                page-break-after: always; position: relative; background: #fff; }
section.slide:first-child { background: #0c2238; color: #fff; display: flex; flex-direction: column; justify-content: center; }
section.slide:first-child h1 { color: #fff; font-size: 34pt; }
section.slide h1 { font-size: 28pt; } section.slide h2 { font-size: 22pt; margin-top: 0; }
section.slide table { font-size: 12.5pt; } section.slide li { margin-bottom: 6px; }
section.slide figure img, section.slide img { max-height: 5.2in; max-width: 100%; }
section.slide .nomor { position: absolute; bottom: 0.2in; right: 0.4in; font-size: 10pt; color: #7a8a9a; }
"""


def extract_section(text: str, keyword: str) -> str:
    """Mengambil bagian dengan judul yang mengandung `keyword` sampai judul setingkat berikutnya."""
    lines, out, level = text.splitlines(), [], None
    for line in lines:
        m = HEADING_RE.match(line)
        if m and level is None and keyword.lower() in m.group(2).lower():
            level = len(m.group(1))
            out.append(line)
            continue
        if level is not None:
            if m and len(m.group(1)) <= level:
                break
            out.append(line)
    return "\n".join(out)


def resolve_includes(text: str) -> str:
    def replace(match: re.Match) -> str:
        rel, opts = match.group(1), match.group(2).split()
        path = PROJECT_ROOT / rel
        if not path.exists():
            return (f'<div class="belum">Belum tersedia: <code>{html.escape(rel)}</code> dibuat otomatis '
                    "oleh pipeline (lihat README, bagian Menjalankan eksperimen).</div>")
        body = path.read_text(encoding="utf-8")
        for opt in opts:
            if opt.startswith("excerpt="):
                body = extract_section(body, opt.split("=", 1)[1].replace("_", " "))
        lines = body.splitlines()
        if "notitle" in opts and lines and HEADING_RE.match(lines[0]):
            lines = lines[1:]
        # Judul di dalam berkas sisipan dijadikan teks tebal agar tidak merusak penomoran bab.
        lines = [f"**{HEADING_RE.match(ln).group(2)}**" if HEADING_RE.match(ln) else ln for ln in lines]
        return "\n" + "\n".join(lines) + "\n"

    return INCLUDE_RE.sub(replace, text)


def fix_images(html_text: str, source_dir: Path, as_figure: bool) -> str:
    """Mengubah path gambar relatif menjadi URI file absolut; gambar hilang diganti catatan."""

    def replace(match: re.Match) -> str:
        tag = match.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        alt_match = re.search(r'alt="([^"]*)"', tag)
        alt = alt_match.group(1) if alt_match else ""
        if re.match(r"^(https?:|file:|data:)", src):
            uri = src
        else:
            path = (source_dir / src).resolve()
            if not path.exists():
                rel = path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path
                caption = f" ({html.escape(alt)})" if alt else ""
                return f'<div class="belum">Gambar belum tersedia: <code>{html.escape(str(rel))}</code>{caption}</div>'
            uri = path.as_uri()
        style_match = re.search(r'style="([^"]*)"', tag)
        style = f' style="{style_match.group(1)}"' if style_match else ""
        img = f'<img src="{uri}" alt="{alt}"{style}>'
        if as_figure and alt:
            return f"<figure>{img}<figcaption>{alt}</figcaption></figure>"
        return img

    html_text = re.sub(r"<p>\s*(<img [^>]+>)\s*</p>", r"\1", html_text)
    return re.sub(r"<img [^>]+>", replace, html_text)


def md_to_html(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])


def build_html(source: Path) -> str:
    raw = source.read_text(encoding="utf-8")
    is_slides = raw.lstrip().startswith("<!-- slides -->")
    text = resolve_includes(raw)
    title = next((m.group(2) for m in map(HEADING_RE.match, text.splitlines()) if m), source.stem)
    if is_slides:
        parts = re.split(r"^---\s*$", text, flags=re.MULTILINE)
        sections = []
        for i, part in enumerate(parts, start=1):
            body = fix_images(md_to_html(part), source.parent, as_figure=False)
            sections.append(f'<section class="slide">{body}<div class="nomor">{i}</div></section>')
        body_html, css = "\n".join(sections), BASE_CSS + SLIDE_CSS
    else:
        body_html, css = fix_images(md_to_html(text), source.parent, as_figure=True), BASE_CSS + DOC_CSS
    return (f'<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
            f"<style>{css}</style></head><body>{body_html}</body></html>")


def find_browser() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge"):
        path = shutil.which(name)
        if path:
            return path
    return None


def html_to_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
           "--print-to-pdf-no-header", f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bangun PDF dokumen proyek.")
    parser.add_argument("--only", choices=list(DOCUMENTS), nargs="*", help="Bangun dokumen tertentu saja.")
    parser.add_argument("--html-only", action="store_true", help="Simpan HTML saja (tanpa PDF).")
    args = parser.parse_args()

    browser = None if args.html_only else find_browser()
    if not args.html_only and browser is None:
        print("Chromium/Chrome tidak ditemukan: hanya HTML yang dibuat. Buka HTML lalu Cetak → Simpan sebagai PDF.")
    for key in args.only or DOCUMENTS:
        source = PROJECT_ROOT / DOCUMENTS[key]
        html_text = build_html(source)
        if browser:
            with tempfile.TemporaryDirectory() as tmp:
                html_path = Path(tmp) / f"{source.stem}.html"
                html_path.write_text(html_text, encoding="utf-8")
                pdf_path = source.with_suffix(".pdf")
                html_to_pdf(browser, html_path, pdf_path)
                print(f"PDF : {pdf_path.relative_to(PROJECT_ROOT)}")
        else:
            out = source.with_suffix(".html")
            out.write_text(html_text, encoding="utf-8")
            print(f"HTML: {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
