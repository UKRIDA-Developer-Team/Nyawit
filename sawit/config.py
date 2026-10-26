"""Pemuatan konfigurasi eksperimen dari berkas YAML.

Setiap berkas konfigurasi boleh memiliki kunci `_base_` yang menunjuk berkas
lain (relatif terhadap dirinya). Nilai pada berkas anak menimpa nilai berkas
induk secara rekursif, sehingga setiap eksperimen hanya mencatat perbedaannya
dari konfigurasi dasar. Ini menjaga perbandingan tetap terkontrol.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Iterable

import yaml


def deep_merge(base: dict, override: dict) -> dict:
    """Menggabungkan dua dict secara rekursif; nilai `override` menang."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def set_by_dotted_key(cfg: dict, dotted_key: str, value: Any) -> None:
    """Mengisi nilai bersarang, mis. `train.epochs` -> cfg['train']['epochs']."""
    keys = dotted_key.split(".")
    node = cfg
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


def load_config(path: str | Path, overrides: Iterable[str] | None = None) -> dict:
    """Memuat konfigurasi YAML beserta induknya dan menerapkan override CLI.

    Override berbentuk string `kunci.bersarang=nilai`; nilai di-parse sebagai
    YAML sehingga `train.epochs=3` menjadi integer dan `model.pretrained=false`
    menjadi boolean.
    """
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    base_name = cfg.pop("_base_", None)
    if base_name:
        cfg = deep_merge(load_config(path.parent / base_name), cfg)

    for item in overrides or []:
        if "=" not in item:
            raise ValueError(f"Override tidak valid (harus kunci=nilai): {item}")
        key, raw_value = item.split("=", 1)
        set_by_dotted_key(cfg, key.strip(), yaml.safe_load(raw_value))
    return cfg


def save_config(cfg: dict, path: str | Path) -> None:
    """Menyimpan konfigurasi final (setelah merge) agar run dapat direproduksi."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
