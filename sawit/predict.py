"""Inferensi pada gambar baru (dipakai oleh demo Gradio dan skrip CLI)."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from .constants import CLASS_NAMES_ID
from .gradcam import GradCAM, overlay_heatmap
from .losses import logits_to_pred, logits_to_probs
from .models import build_model, gradcam_target_layer, num_outputs_for
from .utils import get_device

# Di bawah ambang ini demo menampilkan peringatan "periksa manual".
# Dipilih dari data VALIDASI E3 seed 42 (bukan test): pada ambang 0,9, 13% foto ditandai
# dan hanya ~51% di antaranya benar, sedangkan sisanya 93% benar. Ambang 0,5 hanya
# menandai 0,2% foto sehingga hampir tidak pernah berbunyi.
LOW_CONFIDENCE_THRESHOLD = 0.9


class Predictor:
    """Memuat checkpoint `best.pt` dan memprediksi tingkat kematangan."""

    def __init__(self, checkpoint_path: str | Path, device: str = "auto"):
        from .data import build_transforms

        self.device = get_device(device)
        ckpt = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.head = ckpt["head"]
        self.backbone = ckpt["backbone"]
        self.num_classes = int(ckpt["num_classes"])
        self.class_names = ckpt.get("class_names", CLASS_NAMES_ID)
        self.config = ckpt["config"]
        self.experiment_name = self.config.get("experiment_name", "?")
        self.model = build_model(self.backbone, num_outputs_for(self.head, self.num_classes), pretrained=False)
        self.model.load_state_dict(ckpt["model_state"])
        self.model.to(self.device).eval()
        self.transform = build_transforms(self.config, train=False)
        self._gradcam = None

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        return self.transform(image.convert("RGB")).unsqueeze(0).to(self.device)

    @torch.no_grad()
    def predict(self, image: Image.Image) -> dict:
        """Prediksi satu gambar; mengembalikan label, peluang, dan latensi."""
        x = self.preprocess(image)
        if self.device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        logits = self.model(x).float()
        if self.device.type == "cuda":
            torch.cuda.synchronize()
        latency_ms = (time.perf_counter() - t0) * 1000
        probs = logits_to_probs(logits, self.head)[0].cpu().numpy()
        pred = int(logits_to_pred(logits, self.head)[0])
        return {
            "pred_level": pred,
            "pred_name": self.class_names[pred],
            "probs": {name: float(p) for name, p in zip(self.class_names, probs)},
            "confidence": float(probs[pred]),
            "expected_level": float((probs * np.arange(len(probs))).sum()),
            "low_confidence": bool(probs[pred] < LOW_CONFIDENCE_THRESHOLD),
            "latency_ms": latency_ms,
            "model": f"{self.experiment_name} ({self.backbone}, kepala {self.head})",
        }

    def gradcam(self, image: Image.Image, target_class: int | None = None) -> Image.Image:
        """Overlay Grad-CAM di atas gambar yang sudah di-resize/crop seperti input model."""
        if self._gradcam is None:
            self._gradcam = GradCAM(self.model, gradcam_target_layer(self.model, self.backbone), self.head)
        x = self.preprocess(image)
        with torch.enable_grad():
            cam, _ = self._gradcam(x, target_class)
        size = int(self.config["data"]["image_size"])
        from torchvision import transforms as T

        shown = T.Compose([T.Resize(int(round(size * 256 / 224))), T.CenterCrop(size)])(image.convert("RGB"))
        return overlay_heatmap(shown, cam)
