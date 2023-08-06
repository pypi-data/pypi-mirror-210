#!/usr/bin/env python3
"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 3 QR Factorization test
"""
from numerical.matrix.linear_sys import Qr
import numpy as np
import math


class Col:
    QST = "\033[1;32m::\033[0m"
    SOL = "\033[1;35m=>\033[0m"
    INF = "\033[1;34m->\033[0m"
    WAR = "\033[4;33m"
    ERR = "\033[1;31m"
    TITL = "\033[1;35m"
    RES = "\033[0m"


def example1(path: str):
    """Solve linear system"""
    print(f"\n{Col.TITL}{' Example 1 ':-^79}{Col.RES}\n")
    if not path:
        path = "qr_data/ex1.txt"
    file = open(path, "r")
    ls = file.readlines()

    # Read data from `file`
    shape = ls[0]
    m, n = map(int, shape.replace("\n", "").split(" "))
    data = np.zeros((m, n + 1))
    for i in range(1, m + 1):
        data[i - 1, :] = list(map(float, ls[i].replace("\n", "").split(" ")))

    # Solve system
    mat, vec = data[:, :-1], data[:, -1]
    sol = Qr.solve(mat, vec)
    res = vec - np.matmul(mat, sol)
    print(
        f"{Col.INF} Given the system (A b):\n{data}\n\n"
        f"{Col.SOL} The obtained solution is:\n{sol}\n\n"
        f"{Col.INF} Residue norm is: {np.linalg.norm(res)}"
    )


def example2(path: str):
    """Population growth"""
    print(f"\n{Col.TITL}{' Example 2 ':-^79}{Col.RES}\n")
    if not path:
        path = "qr_data/ex2.txt"
    file = open(path, "r")
    ls = file.readlines()

    # Read input data from `file`
    m = int(ls[0].replace("\n", ""))
    data = np.zeros((m, 2))
    for i in range(1, m + 1):
        data[i - 1, :] = list(map(float, ls[i].replace("\n", "").split(" ")))
    year = data[:, 0]
    pop = data[:, 1]

    mat = np.ndarray((m, 4))
    for i in range(m):
        s = (year[i] - 1950.0) / 50.0
        mat[i, 0] = 1.0
        for j in range(1, 4):
            mat[i, j] = s ** j

    sol = Qr.solve(mat, pop)
    pop2010 = sol[0]
    for i in range(1, 4):
        pop2010 += sol[i] * ((6 / 5) ** i)
    res = pop - np.matmul(mat, sol)

    print(
        f"{Col.INF} Given the system (A b):\n{np.column_stack((mat, pop))}\n\n"
        f"{Col.INF} The obtained solution is:\n{sol}\n\n"
        f"{Col.INF} Residue norm is: {np.linalg.norm(res)}\n\n"
        f"{Col.SOL} Approximate population in 2010: {pop2010} million\n"
    )

    # Print required data
    def fit(t: float, c: np.ndarray) -> float:
        s = (t - 1950.0) / 50.0
        return c[0] + c[1] * s + c[2] * (s ** 2) + c[3] * (s ** 3)

    yy = [fit(t, sol) for t in year]
    triple = [x for x in zip(year, pop, yy)]
    print(
        f"{Col.INF} From the input we got the following data:\n"
        "[(t_i, y_i, yy_i)] = ["
    )
    for x in triple:
        print(f"    {x},")
    print("]\n")


def example3(path: str):
    """Planetary orbit"""
    print(f"\n{Col.TITL}{' Example 3 ':-^79}{Col.RES}\n")
    if not path:
        path = "qr_data/ex3.txt"
    file = open(path, "r")
    ls = file.readlines()

    # Read input data from `file`
    m = int(ls[0].replace("\n", ""))
    data = np.zeros((m, 2))
    for i in range(1, m + 1):
        data[i - 1, :] = list(map(float, ls[i].replace("\n", "").split(" ")))
    xs = data[:, 0]
    ys = data[:, 1]

    mat = np.ndarray((m, 5))

    f = np.full(shape=m, fill_value=-1.0, dtype=float)
    for i in range(10):
        mat[i, 0] = xs[i] ** 2
        mat[i, 1] = xs[i] * ys[i]
        mat[i, 2] = ys[i] ** 2
        mat[i, 3] = xs[i]
        mat[i, 4] = ys[i]

    sol = Qr.solve(mat, f)
    res = f - np.matmul(mat, sol)
    print(
        f"{Col.INF} Given the system (A b):\n{np.column_stack((mat, f))}\n\n"
        f"{Col.SOL} The obtained solution is:\n{sol}\n\n"
        f"{Col.INF} Residue norm is: {np.linalg.norm(res)}"
    )

    # Find closest points on ellipse
    def solve(x: float, y: float, coeff: np.ndarray) -> float:
        """Given x, returns the nearest y on the ellipse"""
        a = coeff[2]
        b = x * coeff[1] + coeff[4]
        c = coeff[0] * x * x + coeff[3] * x + 1
        sqt = math.sqrt(b * b - 4 * a * c)
        y0 = (-b - sqt) / (2 * a)
        y1 = (-b + sqt) / (2 * a)
        if abs(y - y0) < abs(y - y1):
            return y0
        else:
            return y1

    yy = [solve(x, y, sol) for x, y in zip(xs, ys)]
    close = zip(xs, ys, yy)
    print(f"{Col.INF} The closest points are:\n[(x_i, y_i, yy_i)] = [")
    for p in close:
        print(f"    {p},")
    print("]\n")


def example4(path: str):
    """Rocket velocity"""
    print(f"\n{Col.TITL}{' Example 4 ':-^79}{Col.RES}\n")
    if not path:
        path = "qr_data/ex4.txt"
    file = open(path, "r")
    ls = file.readlines()

    n = int(ls[0].replace("\n", ""))
    data = np.zeros((n, 2))
    for i in range(1, n + 1):
        data[i - 1, :] = list(map(float, ls[i].replace("\n", "").split(" ")))
    time = data[:, 0]
    height = data[:, 1]

    mat = np.ndarray((n, 1))
    for i in range(n):
        mat[i, 0] = time[i]

    sol = Qr.solve(mat, height)
    res = height - np.matmul(mat, sol)
    print(
        f"{Col.INF} Given the system (A b):\n{np.column_stack((mat, height))}"
        f"\n\n{Col.SOL} The obtained solution is:\n{sol}\n\n"
        f"{Col.INF} Residue norm is: {np.linalg.norm(res)}"
    )


def main():
    print(f"{Col.TITL}{' QR factorization ':-^79}{Col.RES}")
    stop = False
    while not stop:
        ans = input(
            f"\n{Col.QST} Examples:\n"
            "   [1] Linear System;\n"
            "   [2] Population growth;\n"
            "   [3] Planetary orbit;\n"
            "   [4] Rocket velocity\n"
            f"{Col.QST} Which one would you like to run? [1, 2, 3, 4] "
        )
        exs = {"1": example1, "2": example2, "3": example3, "4": example4}

        if ans in exs:
            arg = input(
                f"\n{Col.QST} Please provide the path for the input file\n"
                f"{Col.INF} "
            )
            exs[ans](arg)
        else:
            ans_err = input(
                f"\n{Col.ERR}[*] Unfortunately such example {ans} "
                f"is not available.{Col.RES}\n"
                f"{Col.QST} Would you like to quit? [Y/n] "
            )
            if not ans_err or ans_err in ["y", "Y"]:
                stop = True
            continue

        ans_ex = input(
            f"\n{Col.QST} Would you like to test another example? [Y/n] "
        )
        if ans_ex in ["n", "N"]:
            stop = True


if __name__ == "__main__":
    main()
