"""Uji integrasi kecil: dataset sintetis -> metadata -> audit -> latih 1 epoch -> prediksi."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True, capture_output=True, text=True)


@pytest.fixture(scope="module")
def synthetic(tmp_path_factory):
    base = tmp_path_factory.mktemp("sintetis")
    run("scripts/make_synthetic_dataset.py", "--out", str(base), "--per-class", "12")
    run("scripts/prepare_data.py", "--root", str(base / "Dataset"), "--out", str(base / "metadata.csv"))
    run("scripts/audit_dataset.py", "--metadata", str(base / "metadata.csv"), "--root", str(base / "Dataset"),
        "--out-dir", str(base / "audit"))
    return base


def test_metadata_and_audit(synthetic):
    import pandas as pd

    meta = pd.read_csv(synthetic / "metadata.csv")
    assert len(meta) == 5 * 13
    assert {"near_dup_in_train", "grouped_split", "dup_group", "split_group", "file_number",
            "neighbor_in_train_official"} <= set(meta.columns)
    # Satu kelompok split tidak boleh tersebar ke lebih dari satu split.
    assert (meta.groupby("split_group")["grouped_split"].nunique() == 1).all()
    # Kembaran sintetis yang sengaja ditaruh di test harus terdeteksi bocor.
    assert meta.loc[meta.image_id == "Immature12.jpg", "near_dup_in_train"].item()
    assert (synthetic / "audit" / "ringkasan_audit.md").exists()


@pytest.mark.parametrize("head,scheme", [("ce", "grouped"), ("corn", "grouped"), ("corn", "official")])
def test_train_and_predict(synthetic, tmp_path, head, scheme):
    from sawit.config import load_config
    from sawit.predict import Predictor
    from sawit.train import run_experiment
    from sawit.utils import get_device

    cfg = load_config(ROOT / "configs/smoke_test.yaml", [
        f"data.root={synthetic / 'Dataset'}",
        f"data.metadata_csv={synthetic / 'metadata.csv'}",
        f"output_root={tmp_path}",
        f"model.head={head}",
        f"data.split_scheme={scheme}",
        "train.epochs=1",
    ])
    run_dir = run_experiment(cfg, seed=0, device=get_device("cpu"))
    for name in ("best.pt", "metrics_test.json", "predictions_test.csv", "summary.json"):
        assert (run_dir / name).exists(), name
    # Subset test bersih (dHash) hanya dihitung untuk split resmi.
    assert (run_dir / "metrics_test_clean.json").exists() == (scheme == "official")

    predictor = Predictor(run_dir / "best.pt", device="cpu")
    img = Image.open(next((synthetic / "Dataset/Images/2FullyRipe").glob("*.jpg")))
    out = predictor.predict(img)
    assert 0 <= out["pred_level"] <= 4
    assert abs(sum(out["probs"].values()) - 1) < 1e-4
    assert predictor.gradcam(img).size == (64, 64)


def test_config_inheritance():
    from sawit.config import load_config

    cfg = load_config(ROOT / "configs/e4_cnn_corn_hue.yaml")
    assert cfg["model"]["head"] == "corn"          # dari e3
    assert cfg["augment"]["hue"] == 0.1            # ditimpa e4
    assert cfg["train"]["lr"] == 3.0e-4            # dari base
    assert yaml.safe_dump(cfg)
