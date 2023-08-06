import numpy as np
from pytest import raises

from fugue_ml.utils.numpy import (
    compute_cos_matrix,
    compute_l2_square_matrix,
    find_best_n_matches,
)


def test_compute_l2_square_matrix():
    v1 = np.array([[1, 2, 3], [4, 5, 6]])
    v2 = np.array([[0, 1, 0], [3, 2, 1], [6, 5, 4]])
    res = np.zeros((2, 3))
    for i in range(2):
        for j in range(3):
            res[i, j] = np.sum(np.square(v1[i] - v2[j]))
    assert np.allclose(res, compute_l2_square_matrix(v1, v2))


def test_compute_cos_matrix():
    v1 = np.array([[1, 2, 3], [4, 5, 6]])
    v2 = np.array([[0, 1, 0], [3, 2, 1], [6, 5, 4]])
    res = np.zeros((2, 3))
    for i in range(2):
        for j in range(3):
            a, b = v1[i], v2[j]
            res[i, j] = 1 - np.dot(a, b) / (np.linalg.norm(a, 2) * np.linalg.norm(b, 2))
    assert np.allclose(res, compute_cos_matrix(v1, v2))


def test_find_best_n_matches():
    v1 = np.array([[1, 2, 3], [4, 5, 6]])
    v2 = np.array([[4.1, 5.1, 6.1], [3, 3, 3], [1.1, 2.1, 3.1]])
    res = np.zeros((2, 3))
    idx, res = find_best_n_matches(v1, v2, metric="l2", n=1)
    assert np.allclose(idx, np.array([[2], [0]]))
    assert np.allclose(
        res,
        np.array(
            [[np.linalg.norm(v2[2] - v1[0], 2)], [np.linalg.norm(v2[0] - v1[1], 2)]]
        ),
    )
    idx, res = find_best_n_matches(v1, v2, metric="l2", n=2)
    assert np.allclose(idx, np.array([[2, 1], [0, 1]]))
    assert np.allclose(
        res,
        np.array(
            [
                [np.linalg.norm(v2[2] - v1[0], 2), np.linalg.norm(v2[1] - v1[0], 2)],
                [np.linalg.norm(v2[0] - v1[1], 2), np.linalg.norm(v2[1] - v1[1], 2)],
            ]
        ),
    )
    idx, res = find_best_n_matches(v1, v2, metric="cos", n=3)
    assert np.allclose(idx, np.array([[0, 1, 2], [0, 1, 2]]))
    assert np.allclose(res, compute_cos_matrix(v1, v2))

    with raises(ValueError):
        find_best_n_matches(v1, v2, metric="unknown", n=1)
