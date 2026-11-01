"""Demo interaktif (Gradio): unggah foto tandan sawit -> tingkat kematangan.

Menjalankan:
    python app/app.py                                   # checkpoint default E3 seed 42
    python app/app.py --checkpoint path/ke/best.pt --share   # tautan publik sementara (Colab)

Bila Gradio bermasalah saat demo, gunakan cadangan CLI:
    python scripts/predict.py --image foto.jpg --gradcam keluaran/

Tampilan ada di `app/style.css`; berkas ini hanya merangkai komponen dan HTML hasil.
"""

from __future__ import annotations

import argparse
import html
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr  # noqa: E402

from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.predict import LOW_CONFIDENCE_THRESHOLD, Predictor  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402

STYLE_PATH = Path(__file__).resolve().parent / "style.css"

LEVEL_ADVICE = {
    0: "Belum layak panen; rendemen minyak rendah.",
    1: "Mendekati matang; sebaiknya ditunggu.",
    2: "Kondisi panen ideal.",
    3: "Lewat matang; kadar asam lemak bebas (ALB) cenderung naik.",
    4: "Busuk; kualitas minyak buruk.",
}

LIMITATIONS = (
    "Model dilatih pada foto dari perkebunan di Kalimantan Tengah (dataset Kamal dkk., 2024). "
    "Hasil pada foto dari kondisi yang jauh berbeda (mis. tumpukan di pabrik, malam hari) belum teruji. "
    "Ini adalah alat bantu belajar dan penelitian, bukan pengganti penilaian grader di pabrik."
)


# ---------------------------------------------------------------------------
# Potongan HTML (semua teks dinamis di-escape)
# ---------------------------------------------------------------------------

def _scale_html(active: int | None = None, expected: float | None = None) -> str:
    """Skala 5 tingkat. `active` menandai tingkat prediksi, `expected` posisi penanda."""
    segs = "".join(
        f'<div class="nw-seg{" is-on" if i == active else ""}" data-level="{i}">{html.escape(name)}</div>'
        for i, name in enumerate(CLASS_NAMES_ID)
    )
    marker = ""
    if expected is not None:
        pos = (min(max(expected, 0.0), len(CLASS_NAMES_ID) - 1) + 0.5) / len(CLASS_NAMES_ID) * 100
        marker = f'<div class="nw-marker" style="--pos:{pos:.1f}%" aria-hidden="true"></div>'
    return f'<div class="nw-scale">{marker}<div class="nw-scale-track">{segs}</div></div>'


def render_empty() -> str:
    return (
        '<div class="nw-card nw-empty">'
        '<p class="nw-eyebrow">Hasil</p>'
        "<h3>Unggah satu foto tandan untuk mulai</h3>"
        "<ol>"
        "<li>Pilih foto satu tandan buah segar yang terlihat jelas dan tidak terlalu gelap, "
        "atau klik salah satu contoh di bawah foto.</li>"
        "<li>Tekan <b>Prediksi</b>. Foto yang baru diunggah langsung diproses.</li>"
        "<li>Baca tingkat kematangan, peluang tiap tingkat, dan peta Grad-CAM untuk "
        "memeriksa bagian foto yang dilihat model.</li>"
        "</ol>"
        f"{_scale_html()}"
        '<p class="nw-scale-cap">Lima tingkat berurutan, dari paling mentah sampai busuk.</p>'
        "</div>"
    )


def render_loading() -> str:
    return (
        '<div class="nw-card" role="status" aria-label="Memproses foto">'
        '<div class="nw-skel"><i></i><i></i><i></i><i></i><i></i><i></i></div>'
        "</div>"
    )


def render_error(message: str) -> str:
    return (
        '<div class="nw-card">'
        '<p class="nw-eyebrow">Hasil</p>'
        f'<div class="nw-notice nw-notice--error" role="alert">{html.escape(message)}</div>'
        "</div>"
    )


def render_result(result: dict, device: str) -> str:
    level = int(result["pred_level"])
    probs = result["probs"]
    rows = "".join(
        f'<li class="nw-prob{" is-top" if i == level else ""}">'
        f"<span>{html.escape(name)}</span>"
        f'<div class="nw-bar"><span style="--w:{p * 100:.1f}%;--c:var(--nw-s{i})"></span></div>'
        f"<output>{p:.1%}</output></li>"
        for i, (name, p) in enumerate(probs.items())
    )
    notice = ""
    if result["low_confidence"]:
        notice = (
            f'<p class="nw-notice" role="status">Keyakinan di bawah {LOW_CONFIDENCE_THRESHOLD:.0%}: '
            "hasil meragukan, sebaiknya diperiksa manual.</p>"
        )
    return (
        '<div class="nw-card nw-result">'
        '<p class="nw-eyebrow">Hasil prediksi</p>'
        f'<h2>{html.escape(result["pred_name"])}</h2>'
        f'<p class="nw-sub">Tingkat <b>{level}</b> dari 4</p>'
        f"{notice}"
        f'{_scale_html(active=level, expected=result["expected_level"])}'
        '<p class="nw-scale-cap">Penanda ▼ = nilai harapan tingkat (rerata berbobot peluang).</p>'
        f'<ul class="nw-probs" aria-label="Peluang per tingkat">{rows}</ul>'
        f'<p class="nw-advice">{html.escape(LEVEL_ADVICE.get(level, "-"))}</p>'
        '<dl class="nw-meta">'
        f'<div><dt>Keyakinan</dt><dd>{result["confidence"]:.1%}</dd></div>'
        f'<div><dt>Nilai harapan</dt><dd>{result["expected_level"]:.2f}</dd></div>'
        f'<div><dt>Latensi model</dt><dd>{result["latency_ms"]:.1f} ms <small>{html.escape(str(device))}</small></dd></div>'
        f'<div class="nw-meta-wide"><dt>Model</dt><dd><small>{html.escape(result["model"])}</small></dd></div>'
        "</dl>"
        "</div>"
    )


def render_header(predictor: Predictor) -> str:
    return (
        '<header class="nw-header"><div>'
        "<h1>Kematangan buah sawit</h1>"
        "<p>Unggah foto tandan buah segar (TBS). Model memprediksi satu dari lima tingkat kematangan "
        "yang berurutan: Mentah, Setengah Matang, Matang Penuh, Terlalu Matang, Busuk.</p>"
        "</div>"
        f'<span class="nw-chip">Model <b>{html.escape(str(predictor.experiment_name))}</b> · '
        f"{html.escape(str(predictor.device))}</span>"
        "</header>"
    )


# ---------------------------------------------------------------------------
# Antarmuka
# ---------------------------------------------------------------------------

def build_interface(predictor: Predictor) -> gr.Blocks:
    def run(image):
        """Generator: skeleton dulu, lalu hasil. Gambar kosong mengembalikan keadaan awal."""
        if image is None:
            yield render_empty(), gr.Image(value=None, visible=False)
            return
        yield render_loading(), gr.Image(value=None, visible=False)
        try:
            result = predictor.predict(image)
            overlay = predictor.gradcam(image, target_class=result["pred_level"])
        except Exception as exc:  # tampilkan di kartu, jangan biarkan demo macet
            yield render_error(f"Gagal memproses foto: {exc}"), gr.Image(value=None, visible=False)
            return
        yield render_result(result, predictor.device), gr.Image(value=overlay, visible=True)

    def reset():
        return render_empty(), gr.Image(value=None, visible=False)

    with gr.Blocks(title="Klasifikasi Kematangan Sawit - Kelompok 3") as demo:
        gr.HTML(render_header(predictor))
        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=300):
                image_in = gr.Image(type="pil", label="Foto tandan sawit", sources=["upload", "clipboard"])
                button = gr.Button("Prediksi", elem_classes=["nw-predict"])
                examples_dir = resolve_path("app/contoh")
                example_files = sorted(str(p) for p in examples_dir.glob("*.jpg")) if examples_dir.is_dir() else []
                if example_files:
                    gr.Examples(examples=example_files, inputs=image_in, label="Contoh gambar (dari test set)")
                # Grad-CAM di bawah foto asli agar mudah dibandingkan; muncul setelah ada hasil.
                cam_out = gr.Image(
                    label="Grad-CAM: area yang paling memengaruhi prediksi",
                    visible=False,
                    interactive=False,
                )
            with gr.Column(scale=6, min_width=320):
                result_out = gr.HTML(render_empty())
        with gr.Accordion("Batasan model", open=False):
            gr.HTML(f'<p class="nw-foot">{html.escape(LIMITATIONS)}</p>')
        gr.HTML(
            '<p class="nw-foot">Kelompok 3 · Visi Komputer IF0PP006 · 2026/2027. '
            'Dataset: Kamal dkk. (2024), Mendeley Data, CC BY 4.0.</p>'
        )

        outputs = [result_out, cam_out]
        button.click(run, inputs=image_in, outputs=outputs, api_name="prediksi", show_progress="hidden")
        image_in.upload(run, inputs=image_in, outputs=outputs, show_progress="hidden")
        image_in.clear(reset, outputs=outputs)
    return demo


def launch_options() -> dict:
    """Gradio 6 memindahkan `css`/`theme` dari Blocks ke launch(); dukung kedua versi."""
    theme = gr.themes.Base(
        primary_hue=gr.themes.colors.green,
        neutral_hue=gr.themes.colors.stone,
        font=[gr.themes.GoogleFont("Figtree"), "system-ui", "sans-serif"],
        radius_size=gr.themes.sizes.radius_md,
    )
    return {"css": STYLE_PATH.read_text(encoding="utf-8"), "theme": theme}


def launch(demo: gr.Blocks, *, share: bool = False, port: int = 7860) -> None:
    opts = launch_options()
    if "css" in inspect.signature(demo.launch).parameters:
        demo.launch(share=share, server_port=port, footer_links=[], **opts)
    else:  # Gradio < 6: gaya diberikan lewat atribut Blocks sebelum launch
        demo.css = opts["css"]
        demo.theme = opts["theme"]
        demo.launch(share=share, server_port=port)


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo Gradio klasifikasi kematangan sawit.")
    parser.add_argument("--checkpoint", default="outputs/runs/e3_cnn_corn/seed42/best.pt")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--share", action="store_true", help="Buat tautan publik sementara (berguna di Colab).")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    checkpoint = resolve_path(args.checkpoint)
    if not checkpoint.exists():
        raise SystemExit(f"Checkpoint tidak ditemukan: {checkpoint}\n"
                         "Latih model dulu: python -m sawit.train --config configs/e3_cnn_corn.yaml")
    predictor = Predictor(checkpoint, device=args.device)
    launch(build_interface(predictor), share=args.share, port=args.port)


if __name__ == "__main__":
    main()