"""Tiny pure-Python linear algebra for the statistical models (small matrices)."""
from __future__ import annotations


def zeros(r, c):
    return [[0.0] * c for _ in range(r)]


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def transpose(A):
    return [list(row) for row in zip(*A)]


def matmul(A, B):
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


def matvec(A, x):
    return [sum(a * xi for a, xi in zip(row, x)) for row in A]


def add(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def scale(A, s):
    return [[a * s for a in row] for row in A]


def outer(u, v):
    return [[ui * vj for vj in v] for ui in u]


def inverse(A):
    """Gauss-Jordan inverse with partial pivoting."""
    n = len(A)
    M = [list(map(float, A[i])) + [1.0 if i == j else 0.0 for j in range(n)]
         for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-15:
            raise ValueError("Singular matrix")
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        M[col] = [v / d for v in M[col]]
        for r in range(n):
            if r != col and M[r][col]:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]
