"""Demo interaktif (Gradio): unggah foto tandan sawit -> tingkat kematangan.

Menjalankan:
    python app/app.py                                   # checkpoint default E3 seed 42
    python app/app.py --checkpoint path/ke/best.pt --share   # tautan publik sementara (Colab)

Bila Gradio bermasalah saat demo, gunakan cadangan CLI:
    python scripts/predict.py --image foto.jpg --gradcam keluaran/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr  # noqa: E402

from sawit.constants import CLASS_NAMES_ID  # noqa: E402
from sawit.predict import LOW_CONFIDENCE_THRESHOLD, Predictor  # noqa: E402
from sawit.utils import resolve_path  # noqa: E402

DESCRIPTION = """
Unggah foto **tandan buah segar (TBS) kelapa sawit**. Model memprediksi satu dari lima tingkat
kematangan yang berurutan: **Mentah → Setengah Matang → Matang Penuh → Terlalu Matang → Busuk**.

Batasan: model dilatih pada foto dari perkebunan di Kalimantan Tengah (dataset Kamal dkk., 2024).
Hasil pada foto dari kondisi yang jauh berbeda (mis. tumpukan di pabrik, malam hari) belum teruji.
Ini adalah alat bantu belajar/penelitian, **bukan** pengganti penilaian grader di pabrik.
"""

LEVEL_ADVICE = {
    0: "Belum layak panen; rendemen minyak rendah.",
    1: "Mendekati matang; sebaiknya ditunggu.",
    2: "Kondisi panen ideal.",
    3: "Lewat matang; kadar asam lemak bebas (ALB) cenderung naik.",
    4: "Busuk; kualitas minyak buruk.",
}


def build_interface(predictor: Predictor) -> gr.Blocks:
    def run(image):
        if image is None:
            return None, "Silakan unggah gambar terlebih dahulu.", None
        result = predictor.predict(image)
        overlay = predictor.gradcam(image, target_class=result["pred_level"])
        level = result["pred_level"]
        lines = [
            f"### Prediksi: {result['pred_name']} (tingkat {level} dari 0-4)",
            f"- Keyakinan: **{result['confidence']:.1%}**",
            f"- Nilai harapan tingkat (rerata berbobot peluang): **{result['expected_level']:.2f}**",
            f"- Keterangan: {LEVEL_ADVICE.get(level, '-')}",
            f"- Latensi model: {result['latency_ms']:.1f} ms ({predictor.device})",
            f"- Model: {result['model']}",
        ]
        if result["low_confidence"]:
            lines.insert(1, f"> ⚠️ Keyakinan di bawah {LOW_CONFIDENCE_THRESHOLD:.0%}: "
                            "hasil meragukan, sebaiknya diperiksa manual.")
        return result["probs"], "\n".join(lines), overlay

    with gr.Blocks(title="Klasifikasi Kematangan Sawit - Kelompok 3") as demo:
        gr.Markdown("# Klasifikasi Tingkat Kematangan Buah Sawit")
        gr.Markdown(DESCRIPTION)
        with gr.Row():
            with gr.Column():
                image_in = gr.Image(type="pil", label="Foto tandan sawit")
                button = gr.Button("Prediksi", variant="primary")
                examples_dir = resolve_path("app/contoh")
                example_files = sorted(str(p) for p in examples_dir.glob("*.jpg")) if examples_dir.is_dir() else []
                if example_files:
                    gr.Examples(examples=example_files, inputs=image_in, label="Contoh gambar (dari test set)")
            with gr.Column():
                probs_out = gr.Label(num_top_classes=len(CLASS_NAMES_ID), label="Peluang per tingkat")
                text_out = gr.Markdown()
                cam_out = gr.Image(label="Grad-CAM: area yang paling memengaruhi prediksi")
        button.click(run, inputs=image_in, outputs=[probs_out, text_out, cam_out], api_name="prediksi")
        image_in.upload(run, inputs=image_in, outputs=[probs_out, text_out, cam_out])
        gr.Markdown("Kelompok 3 - Visi Komputer IF0PP006 - 2026/2027. "
                    "Dataset: Kamal dkk. (2024), Mendeley Data, CC BY 4.0.")
    return demo


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
    build_interface(predictor).launch(share=args.share, server_port=args.port)


if __name__ == "__main__":
    main()
