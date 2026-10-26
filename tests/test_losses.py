"""Uji unit untuk loss CORN dan dekodingnya."""

import torch

from sawit.losses import corn_class_probs, corn_loss, corn_predict, logits_to_pred, logits_to_probs


def test_corn_probs_sum_to_one_and_nonnegative():
    logits = torch.randn(16, 4)
    probs = corn_class_probs(logits)
    assert probs.shape == (16, 5)
    assert torch.all(probs >= 0)
    assert torch.allclose(probs.sum(dim=1), torch.ones(16), atol=1e-6)


def test_corn_predict_counts_thresholds():
    big = 10.0
    # Semua peluang bersyarat ~1 -> tingkat tertinggi (4); semua ~0 -> tingkat 0.
    assert corn_predict(torch.full((1, 4), big)).item() == 4
    assert corn_predict(torch.full((1, 4), -big)).item() == 0
    # Lolos dua batas pertama lalu berhenti -> tingkat 2.
    assert corn_predict(torch.tensor([[big, big, -big, big]])).item() == 2


def test_corn_loss_decreases_for_correct_logits():
    targets = torch.tensor([0, 1, 2, 3, 4])
    good = torch.tensor([[-5, -5, -5, -5], [5, -5, -5, -5], [5, 5, -5, -5], [5, 5, 5, -5], [5, 5, 5, 5]], dtype=torch.float)
    bad = -good
    assert corn_loss(good, targets, 5) < corn_loss(bad, targets, 5)
    assert torch.equal(corn_predict(good), targets)


def test_corn_loss_has_gradient():
    logits = torch.randn(8, 4, requires_grad=True)
    loss = corn_loss(logits, torch.randint(0, 5, (8,)), 5)
    loss.backward()
    assert logits.grad is not None and torch.isfinite(logits.grad).all()


def test_ce_interface():
    logits = torch.tensor([[0.1, 3.0, 0.2, 0.0, -1.0]])
    assert logits_to_pred(logits, "ce").item() == 1
    assert torch.allclose(logits_to_probs(logits, "ce").sum(), torch.tensor(1.0))
