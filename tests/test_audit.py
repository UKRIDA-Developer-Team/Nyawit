"""Uji unit audit near-duplicate dan split berkelompok."""

import numpy as np
import pandas as pd
from PIL import Image

from sawit.audit import dhash_hex, duplicate_groups, flag_cross_split_leakage, grouped_split, near_duplicate_pairs


def _image(seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    return Image.fromarray(rng.integers(0, 255, (64, 64, 3), dtype=np.uint8))


def test_dhash_identical_and_different():
    a = _image(0)
    assert dhash_hex(a) == dhash_hex(a.copy())
    assert len(dhash_hex(a)) == 16
    assert dhash_hex(a) != dhash_hex(_image(1))


def test_near_duplicate_pairs_and_groups():
    hashes = ["0000000000000000", "0000000000000001", "ffffffffffffffff", "00000000000000ff"]
    pairs = near_duplicate_pairs(hashes, threshold=1)
    assert list(zip(pairs.i, pairs.j)) == [(0, 1)]
    groups = duplicate_groups(len(hashes), pairs)
    assert groups[0] == groups[1] and len(set(groups)) == 3


def test_cross_split_leakage_flag():
    df = pd.DataFrame({"split": ["train", "test", "test", "val"]})
    pairs = pd.DataFrame({"i": [0, 2], "j": [1, 3], "distance": [0, 0]})
    flags = flag_cross_split_leakage(df, pairs, "split")
    assert flags.tolist() == [False, True, False, False]


def test_grouped_split_keeps_groups_together():
    rng = np.random.default_rng(0)
    labels = np.repeat(np.arange(5), 40)
    groups = np.arange(200) // 2  # pasangan berurutan = satu kelompok
    split = grouped_split(labels, groups, seed=0)
    for g in np.unique(groups):
        assert len(set(split[groups == g])) == 1
    assert set(split) == {"train", "val", "test"}
    assert 0.08 < (split == "test").mean() < 0.25
    _ = rng


def test_file_number_and_blocks():
    from sawit.audit import block_group_ids, file_number

    assert file_number("Immature324.jpg") == 324
    assert file_number("OverRipe0.JPG") == 0
    labels = np.array([0, 0, 0, 1, 1])
    numbers = np.array([0, 19, 20, 0, 19])
    groups = block_group_ids(labels, numbers, block_size=20)
    # Blok sama hanya bila kelas sama dan nomor // 20 sama.
    assert groups[0] == groups[1] != groups[2]
    assert groups[3] == groups[4] != groups[0]


def test_merge_groups_is_transitive():
    from sawit.audit import merge_groups

    a = np.array([0, 0, 1, 2, 3])   # 0-1 sekelompok
    b = np.array([5, 6, 6, 7, 8])   # 1-2 sekelompok
    merged = merge_groups(a, b)
    assert merged[0] == merged[1] == merged[2]
    assert len(set(merged)) == 3


def test_neighbor_in_split():
    from sawit.audit import neighbor_in_split

    labels = np.array([0, 0, 0, 1])
    numbers = np.array([1, 2, 5, 3])
    splits = np.array(["train", "test", "test", "train"])
    flags = neighbor_in_split(labels, numbers, splits, "train", window=1)
    assert flags.tolist() == [False, True, False, False]


def test_sequential_similarity_detects_order():
    from sawit.audit import sequential_similarity

    rng = np.random.default_rng(0)
    # Fitur berubah perlahan menurut nomor (meniru pemotretan beruntun).
    numbers = np.arange(300)
    labels = np.zeros(300, dtype=int)
    features = np.cumsum(rng.normal(size=(300, 8)), axis=0)
    table, ref = sequential_similarity(features, labels, numbers, lags=(1, 50), n_ref=2000)
    pct = dict(zip(table.selisih_nomor, table.persen_lebih_mirip_dari_p5_acak))
    assert pct[1] > 50 and pct[1] > pct[50]
    assert ref["p5_acak"] > 0
