"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 4 Barycentric Interpolation
"""
from numerical.interpolate.barycentric import barycentric_boundary
from typing import Callable
import matplotlib.pyplot as plt
import math


def errors(
    a: float,
    b: float,
    alpha: float,
    beta: float,
    q: Callable[[float], float],
    f: Callable[[float], float],
    u: Callable[[float], float],
    print_table: bool=True
) -> list[float]:
    n_pts = 1000
    errors = []
    ns = [16, 32, 64, 128]
    for n in ns:
        bary = barycentric_boundary((a, b), (alpha, beta), q, f, n)

        # evaluate the biggest error within the interval
        app = []
        exact = []
        max_error = 0
        pts = [a + (i - 0.5) * (b - a) / n_pts for i in range(n_pts)]
        for p in pts:
            err = abs(u(p) - bary(p))
            if max_error < err:
                max_error = err
            app.append(bary(p))
            exact.append(u(p))
        errors.append(max_error)

        # Visualization
        plt.plot(pts, app)
        plt.plot(pts, exact)
        plt.show()

    if print_table:
        table(ns, errors, a, b, alpha, beta)
    return errors


def example1():
    def q(x: float) -> float:
        return 6 * (x ** 2) / (1 + x ** 2) ** 2

    def f(x: float) -> float:
        return 2 / (1 + x ** 2) ** 3

    def u(x: float) -> float:
        return 1 / (1 + x ** 2)

    print(f"{' Example 1 ':=^80}\n")
    errors(a=-5.0, b=5.0, alpha=1/26, beta=1/26, q=q, f=f, u=u)


def example2():
    def q(_: float) -> float:
        return 10000.0

    def f(_: float) -> float:
        return 0.0

    def u(x: float) -> float:
        return math.sinh(100 * x) / math.sinh(100)

    print(f"\n{' Example 2 ':=^80}\n")
    errors(a=0.0, b=1.0, alpha=0.0, beta=1.0, q=q, f=f, u=u)


def table(ns: list[int], errors: list[float], a, b, alpha, beta):
    """Table:
    Number of points; maximum error; interval; end-values.
    """
    div = "+" + "-" * 9 + "+" + "-" * 33 + "+" + "-" * 16 + "+" + "-" * 17 + "+"
    print(
        f"{div}\n|{' #Points ':^9}|{'Maximum Error':^33}|"
        f"{'Interval':^16}|{'End values':^17}|\n{div}"
    )
    for n, e in zip(ns, errors):
        print(
            f"|{f'{n}':^9}|{f'{e}':^33}|"
            f"{f'[{a}, {b}]':^16}|{f'({alpha:.4f}, {beta:.4f})':^17}|\n{div}"
        )


def main():
    example1()
    example2()


if __name__ == "__main__":
    main()
