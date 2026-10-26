"""Grad-CAM (Selvaraju dkk., 2017) untuk memeriksa area gambar yang dipakai model.

Skor target = log-peluang kelas yang diprediksi. Karena kedua jenis kepala
(`ce` dan `corn`) sama-sama menghasilkan distribusi K kelas yang dapat
diturunkan, perlakuan ini seragam untuk keduanya.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from .losses import logits_to_probs


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module, head: str):
        self.model = model
        self.head = head
        self._activations = None
        self._gradients = None
        # Gradien diambil lewat hook pada tensor keluaran (bukan backward hook
        # modul) agar aman untuk lapisan dengan aktivasi in-place.
        target_layer.register_forward_hook(self._save_activation)

    def _save_activation(self, _module, _inputs, output):
        self._activations = output.detach()
        if output.requires_grad:
            output.register_hook(self._save_gradient)

    def _save_gradient(self, grad):
        self._gradients = grad.detach()

    def __call__(self, x: torch.Tensor, target_class: int | None = None) -> tuple[np.ndarray, int]:
        """Mengembalikan peta panas (H x W, nilai 0..1) dan kelas target."""
        self.model.eval()
        x = x.clone().requires_grad_(True)
        self.model.zero_grad(set_to_none=True)
        logits = self.model(x).float()
        probs = logits_to_probs(logits, self.head)
        if target_class is None:
            target_class = int(probs[0].argmax())
        score = torch.log(probs[0, target_class].clamp_min(1e-8))
        score.backward()
        weights = self._gradients.mean(dim=(2, 3), keepdim=True)
        cam = F.relu((weights * self._activations).sum(dim=1, keepdim=True))
        cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)[0, 0]
        cam = cam - cam.min()
        cam = cam / cam.max().clamp_min(1e-8)
        return cam.cpu().numpy(), target_class


def overlay_heatmap(image: Image.Image, cam: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """Menumpuk peta panas (colormap 'jet') di atas gambar asli."""
    import matplotlib

    heat = matplotlib.colormaps["jet"](cam)[..., :3]
    heat_img = Image.fromarray((heat * 255).astype(np.uint8)).resize(image.size, Image.Resampling.BILINEAR)
    return Image.blend(image.convert("RGB"), heat_img, alpha)
