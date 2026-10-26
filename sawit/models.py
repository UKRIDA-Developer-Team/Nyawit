"""Pembangun model: backbone pra-latih ImageNet dari torchvision + kepala baru.

Jumlah keluaran kepala bergantung pada jenis loss:
- `ce`   : K logit (satu per kelas), softmax.
- `corn` : K-1 logit (satu per batas "apakah tingkat > k"), lihat losses.py.
"""

from __future__ import annotations

import torch.nn as nn
from torchvision import models as tvm

SUPPORTED_BACKBONES = ("efficientnet_b0", "resnet18", "resnet50", "mobilenet_v3_large")


def num_outputs_for(head: str, num_classes: int) -> int:
    if head == "ce":
        return num_classes
    if head == "corn":
        return num_classes - 1
    raise ValueError(f"Jenis kepala tidak dikenal: {head} (pilih 'ce' atau 'corn')")


def build_model(backbone: str, num_outputs: int, pretrained: bool = True, dropout: float = 0.2) -> nn.Module:
    """Membuat backbone dan mengganti lapisan klasifikasi terakhir."""
    if backbone == "efficientnet_b0":
        weights = tvm.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        model = tvm.efficientnet_b0(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(nn.Dropout(dropout), nn.Linear(in_features, num_outputs))
    elif backbone in ("resnet18", "resnet50"):
        builder = getattr(tvm, backbone)
        enum = tvm.ResNet18_Weights if backbone == "resnet18" else tvm.ResNet50_Weights
        model = builder(weights=enum.IMAGENET1K_V1 if pretrained else None)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(nn.Dropout(dropout), nn.Linear(in_features, num_outputs))
    elif backbone == "mobilenet_v3_large":
        weights = tvm.MobileNet_V3_Large_Weights.IMAGENET1K_V2 if pretrained else None
        model = tvm.mobilenet_v3_large(weights=weights)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_outputs)
    else:
        raise ValueError(f"Backbone tidak didukung: {backbone}. Pilihan: {SUPPORTED_BACKBONES}")
    return model


def gradcam_target_layer(model: nn.Module, backbone: str) -> nn.Module:
    """Lapisan konvolusi terakhir yang dipakai Grad-CAM."""
    if backbone in ("efficientnet_b0", "mobilenet_v3_large"):
        return model.features[-1]
    if backbone in ("resnet18", "resnet50"):
        return model.layer4[-1]
    raise ValueError(f"Backbone tidak didukung: {backbone}")


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
