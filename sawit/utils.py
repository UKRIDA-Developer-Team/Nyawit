"""Utilitas umum: seed, perangkat, JSON, dan informasi lingkungan."""

from __future__ import annotations

import json
import os
import platform
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch

# Akar repositori (folder yang berisi paket `sawit`).
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_path(path: str | Path) -> Path:
    """Path relatif dianggap relatif terhadap akar repositori."""
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def set_seed(seed: int, deterministic: bool = True) -> None:
    """Mengunci seluruh sumber keacakan agar hasil dapat diulang."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def seed_worker(worker_id: int) -> None:  # noqa: ARG001
    """Seed untuk setiap worker DataLoader (rekomendasi dokumentasi PyTorch)."""
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def get_device(preference: str = "auto") -> torch.device:
    """Memilih perangkat: 'auto' memakai CUDA bila tersedia, lalu MPS, lalu CPU."""
    if preference != "auto":
        return torch.device(preference)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def to_serializable(obj: Any) -> Any:
    """Mengubah tipe numpy/torch menjadi tipe bawaan Python agar bisa ditulis ke JSON."""
    if isinstance(obj, dict):
        return {str(k): to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, torch.Tensor):
        return obj.detach().cpu().tolist()
    if isinstance(obj, Path):
        return str(obj)
    return obj


def save_json(data: Any, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_serializable(data), f, indent=2, ensure_ascii=False)


def load_json(path: str | Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def environment_info(device: torch.device) -> dict:
    """Mencatat versi pustaka dan perangkat keras untuk lampiran reproduksibilitas."""
    import torchvision

    info = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "numpy": np.__version__,
        "device": str(device),
        "cpu_count": os.cpu_count(),
    }
    if device.type == "cuda":
        info["gpu"] = torch.cuda.get_device_name(device)
    return info
