"""Uji unit metrik klasifikasi dan ordinal."""

import math

from sawit.metrics import compute_metrics


def test_perfect_prediction():
    y = [0, 1, 2, 3, 4, 2]
    m = compute_metrics(y, y)
    assert m["accuracy"] == 1.0 and m["macro_f1"] == 1.0
    assert m["mae"] == 0.0 and m["severe_error_rate"] == 0.0
    assert math.isclose(m["qwk"], 1.0)


def test_ordinal_metrics_distinguish_error_distance():
    y_true = [0, 0, 0, 0]
    near = compute_metrics(y_true, [1, 1, 0, 0])
    far = compute_metrics(y_true, [4, 4, 0, 0])
    # Akurasi sama, tetapi metrik ordinal membedakan jarak kesalahan.
    assert near["accuracy"] == far["accuracy"]
    assert near["mae"] < far["mae"]
    assert near["severe_error_rate"] == 0.0 and far["severe_error_rate"] == 0.5
    assert near["off_by_one_acc"] == 1.0


def test_confusion_matrix_shape():
    m = compute_metrics([0, 1, 2], [0, 2, 2])
    assert len(m["confusion_matrix"]) == 5 and all(len(r) == 5 for r in m["confusion_matrix"])
    assert m["per_class"]["Mentah"]["recall"] == 1.0
