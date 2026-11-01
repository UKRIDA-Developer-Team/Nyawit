"""Pratinjau UI TANPA model: memakai Predictor palsu, tidak butuh torch atau best.pt.

Menjalankan (cukup `pip install gradio pillow`):
    python app/preview_ui.py

Hasil yang tampil hanyalah contoh acak yang konsisten per gambar (bukan prediksi sungguhan).
Klik tiap contoh gambar untuk melihat kelima tingkat. Gambar yang sangat kecil (< 64 px)
memicu keadaan galat, supaya tampilan pesan galat juga bisa diperiksa.
"""

from __future__ import annotations

import hashlib
import math
import sys
import time
import types
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NAMES = ["Mentah", "Setengah Matang", "Matang Penuh", "Terlalu Matang", "Busuk"]


class FakePredictor:
    device = "cpu"
    experiment_name = "PRATINJAU (model palsu)"

    def predict(self, image: Image.Image) -> dict:
        if min(image.size) < 64:
            raise ValueError("gambar terlalu kecil (contoh galat untuk pratinjau)")
        time.sleep(0.9)  # agar keadaan memuat (skeleton) sempat terlihat
        digest = hashlib.sha256(image.convert("RGB").resize((16, 16)).tobytes()).digest()
        level = digest[0] % 5
        sharp = 1.2 + (digest[1] % 40) / 10  # makin besar, makin yakin
        logits = [-sharp * abs(i - level) for i in range(5)]
        z = [math.exp(v) for v in logits]
        probs = [v / sum(z) for v in z]
        return {
            "pred_level": level,
            "pred_name": NAMES[level],
            "probs": dict(zip(NAMES, probs)),
            "confidence": probs[level],
            "expected_level": sum(i * p for i, p in enumerate(probs)),
            "low_confidence": probs[level] < 0.9,
            "latency_ms": 10 + digest[2] % 8 + (digest[3] % 10) / 10,
            "model": "pratinjau (tanpa model sungguhan)",
        }

    def gradcam(self, image: Image.Image, target_class: int | None = None) -> Image.Image:
        base = image.convert("RGB").resize((224, 224))
        yy, xx = np.mgrid[0:224, 0:224]
        heat = np.exp(-(((xx - 110) / 55.0) ** 2 + ((yy - 105) / 50.0) ** 2))
        rgb = np.stack([heat, np.clip(1 - np.abs(heat - 0.5) * 2, 0, 1), 1 - heat], axis=-1)
        overlay = Image.fromarray((rgb * 255).astype(np.uint8))
        return Image.blend(base, overlay, 0.45)


# Ganti modul yang butuh torch dengan versi palsu SEBELUM app.py diimpor.
predict_stub = types.ModuleType("sawit.predict")
predict_stub.Predictor = FakePredictor
predict_stub.LOW_CONFIDENCE_THRESHOLD = 0.9
utils_stub = types.ModuleType("sawit.utils")
utils_stub.resolve_path = lambda p: Path(p) if Path(p).is_absolute() else ROOT / p
sys.modules["sawit.predict"] = predict_stub
sys.modules["sawit.utils"] = utils_stub

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app as nyawit_app  # noqa: E402

if __name__ == "__main__":
    print("Pratinjau UI (model palsu). Buka alamat di bawah, tekan Ctrl+C untuk berhenti.")
    nyawit_app.launch(nyawit_app.build_interface(FakePredictor()))