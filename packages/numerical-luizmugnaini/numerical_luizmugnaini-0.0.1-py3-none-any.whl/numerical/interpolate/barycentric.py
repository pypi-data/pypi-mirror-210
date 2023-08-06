"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 4 Barycentric Interpolation
"""
from typing import Callable
import numpy as np
import math


class Barycentric:
    def __init__(
        self,
        interval: tuple[float, float],
        boundary: tuple[float, float],
        q: Callable[[float], float],
        f: Callable[[float], float],
        n: int,
    ):
        """Barycentric interpolation for the boundary problem:
            -u''(x) + q(x) * u(x) = f(x), where u(a) = alpha and u(b) = beta
        The goal is to find an approximation for the function `u`. The needed
        parameters for the computation are:

        `interval`: tuple ``(a, b)`` containing the end points of the interval.
        `boundary`: tuple ``(alpha, beta)`` of boundary values.
        `q` and `f`: boundary problem functions.
        `n`: number of points to use in the interpolation.
        """
        self.xs = Barycentric.chebyshev_points(interval[0], interval[1], n)
        self.n = len(self.xs)
        self.ws = self.weights()
        self.ys = self.values(boundary[0], boundary[1], q, f)

    @staticmethod
    def chebyshev_points(a: float, b: float, n: int) -> np.ndarray:
        """Chebyshev points:
        Given endpoints `a` and `b`, returns a list of `n` Chebyshev points in
        the interval defined by `a` and `b`
        """
        return np.array([
            (a + b) / 2 - (b - a) / 2 * math.cos(j * math.pi / n)
            for j in range(n)
        ])

    def get_knots(self) -> np.ndarray:
        """Returns the computed knots for the barycentric interpolant"""
        return self.xs

    def weights(self, chebyshev: bool=True) -> np.ndarray:
        """Finds the weights of the Barycentric polynomial.
        By default it assumes that the used knots are Chebyshev points,
        returning the Chebyshev weights for the interval [-1, 1].

        Such behaviour can be controlled by setting `chebyshev=False` as an
        argument. The method will return the weights based on the general
        formula for a given set of knots.
        """
        if chebyshev:
            def cheby(i: int) -> float:
                """Calculates the Chebyshev weight at index `i`"""
                if i in [0, self.n - 1]:
                    return ((i % 2 == 0) - (i % 2 != 0)) * 0.5
                else:
                    return (i % 2 == 0) - (i % 2 != 0)

            return np.array([cheby(i) for i in range(self.n)])

        else:
            ws = np.ones(self.n, dtype=float)
            for j in range(self.n):
                w_inv = 1
                for (k, x) in [e for e in enumerate(self.xs) if e[0] != k]:
                    w_inv *= (self.xs[j] - x)
                ws[j] = 1 / w_inv

            return ws

    def get_weights(self) -> np.ndarray:
        """Returns the weights for the barycentric interpolant"""
        return self.ws

    def values(
        self,
        alpha: float,
        beta: float,
        q: Callable[[float], float],
        f: Callable[[float], float]
    ) -> np.ndarray:
        """Values at the knots.
        Calculates values at the collocation knots for the barycentric
        interpolant polynomial for the boundary-value problem
            -u''(x) + q(x) * u(x) = f(x), where u(a) = alpha and u(b) = beta.
        The method returns the array of values for the interpolant polynomial,
        including the boundary values.

        `alpha` and `beta`: boundary values.
        `q` and `f`: functions of the boundary-value problem.
        """
        # Number of values to search
        size = self.n - 2

        def ell2(j: int, i: int) -> float:
            """Second derivative of the interpolant at a given knot.
            `j`: interpolant index.
            `i`: knot index.
            """
            if i != j:
                # sum of the interpolant first derivatives
                s = 0
                for k in [k for k in range(self.n) if k != i]:
                    s += (self.ws[k] / self.ws[i]) / (self.xs[i] - self.xs[k])

                return (
                    -2 * (self.ws[j] / self.ws[i]) / (self.xs[i] - self.xs[j])
                    * (s + 1 / (self.xs[i] - self.xs[j]))
                )
            else:
                ells = 0
                for k in [k for k in range(self.n) if k != i]:
                    ells -= ell2(k, i)
                return ells

        def row(i: int) -> np.ndarray:
            """`i`th row of `coeff`"""
            ii = i + 1
            r = np.zeros(size, dtype=float)
            r[i] = q(self.xs[ii]) - ell2(ii, ii)
            for j in [j for j in range(size) if j != i]:
                r[j] = -ell2(j + 1, ii)
            return r

        def vec_at(i: int) -> float:
            """`i`th element of `vec`"""
            ii = i + 1
            return f(self.xs[ii]) + ell2(0, ii) * alpha \
                   + ell2(self.n - 1, ii) * beta

        coeff = np.array([row(i) for i in range(size)])
        vec = np.array([vec_at(i) for i in range(size)])

        # Values at the collocation knots
        vals = np.linalg.solve(coeff, vec)

        # Insert boundary values and return
        return np.insert(vals, (0, len(vals)), (alpha, beta))

    def get_values(self) -> np.ndarray:
        """Returns the values of the interpolant polynomial at the knots"""
        return self.ys

    def __call__(self, x: float) -> float:
        """Evaluates the interpolant polynomial at `x`"""
        def quotient(j: int) -> float:
            assert x != self.xs[j], f"Cannot evaluate function at knot {j}"
            return self.ws[j] / (x - self.xs[j])

        return sum(self.ys[j] * quotient(j) for j in range(self.n)) \
               / sum(quotient(j) for j in range(self.n))


def barycentric_boundary(
        interval: tuple[float, float],
        boundary: tuple[float, float],
        q: Callable[[float], float],
        f: Callable[[float], float],
        n: int,
) -> Barycentric:
    """Barycentric polynomial for boundary-value problem.
    Returns a polynomial approximation for the problem:
        -u''(x) + q(x) * u(x) = f(x), where u(a) = alpha and u(b) = beta

    `interval`: tuple ``(a, b)`` containing the end points of the interval.
    `boundary`: tuple ``(alpha, beta)`` of boundary values.
    `q` and `f`: boundary problem functions.
    `n`: number of points to use in the interpolation.
    """
    return Barycentric(interval, boundary, q, f, n)
