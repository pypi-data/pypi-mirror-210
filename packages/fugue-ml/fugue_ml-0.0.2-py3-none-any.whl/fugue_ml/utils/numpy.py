import numpy as np
from typing import Tuple


def compute_l2_square_matrix(vec1: np.array, vec2: np.array) -> np.array:
    """Compute the l2 square matrix between the two set of vectors.

    :param vec1: the first set of vectors, shape (n1, d)
    :param vec2: the second set of vectors, shape (n2, d)
    :return: the l2 square matrix, shape (n1, n2), where at position (i, j)
        is the l2 square distance between vec1[i] and vec2[j]
    """
    a2 = np.sum(np.square(vec1), axis=1)
    b2 = np.sum(np.square(vec2), axis=1)
    b2, a2 = np.meshgrid(b2, a2)
    _2ab = np.matmul(vec1, vec2.T) * 2
    c = a2 + b2 - _2ab
    return c


def compute_cos_matrix(vec1: np.array, vec2: np.array) -> np.array:
    """Compute the 1-cos matrix between the two set of vectors.

    :param vec1: the first set of vectors, shape (n1, d)
    :param vec2: the second set of vectors, shape (n2, d)
    :return: the l2 square matrix, shape (n1, n2), where at position (i, j)
        is 1 - cos(vec1[i], vec2[j])
    """
    norm1 = np.linalg.norm(vec1, 2, axis=1)
    norm2 = np.linalg.norm(vec2, 2, axis=1)
    v1 = vec1 / norm1[:, None]
    v2 = vec2 / norm2[:, None]
    return 1 - np.matmul(v1, v2.T)


def find_best_n_matches(
    vec1: np.array, vec2: np.array, metric: str, n: int
) -> Tuple[np.array, np.array]:
    """Find the best n matches for each vector in vec1 from vec2

    :param vec1: the first set of vectors, shape (n1, d)
    :param vec2: the second set of vectors, shape (n2, d)
    :param metric: the metric to use, 'l2' or 'cos'
    :param n: top n matches with the smallest distance
    :return: the indices and distances of the best n matches for
        each vector in vec1, shape (n1, n)
    """
    if metric == "l2":
        dist = np.sqrt(compute_l2_square_matrix(vec1, vec2))
    elif metric == "cos":
        dist = compute_cos_matrix(vec1, vec2)
    else:
        raise ValueError(f"Unknown metric {metric}")
    if n == 1:
        idx = np.argmin(dist, axis=1)[:, None]
        res = np.take_along_axis(dist, idx, axis=1)
    elif n < dist.shape[1]:
        idx = np.argpartition(dist, n, axis=1)[:, :n]
        res = np.take_along_axis(dist, idx, axis=1)
    else:
        idx = np.tile(np.arange(dist.shape[1]), (dist.shape[0], 1))
        res = dist
    return idx, res
