"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Tests: module numerical.interpolate.matrix
"""
import numpy as np
from numerical.matrix.linear_sys import Tridiagonal, SquareMatrix, Qr


def decomposition(mat, vec):
    """Tests LU decomposition algorithm"""
    print("initial matrix =\n{}\n".format(mat))
    SquareMatrix.gaussian_elim(mat, vec, True)
    print("Resulting mixed matrix =\n{}\n".format(mat))

    lower = np.tril(mat)
    np.fill_diagonal(lower, 1)
    upper = np.triu(mat)

    print("upper =\n{}\nlower =\n{}\n".format(upper, lower))
    prod = np.matmul(lower, upper)
    print("product = lower * upper =\n{}\n".format(prod))


def linear_sys_test():
    print(">>> Testing tridiagonal gaussian elimination:\n")
    coeff = np.array([
            [4.0, 1, 0, 0, 0, 0],
            [-3, 10, -1, 0, 0, 0],
            [0, 7, 30, 1, 0, 0],
            [0, 0, -6, 90, 2, 0],
            [0, 0, 0, 2, 5, 15],
            [0, 0, 0, 0, 3.0, 40],
    ])
    vec = np.array([5.0, 7, 9, 10, 7, 8])
    sol = Tridiagonal.solve(coeff, vec)
    print(
        "The solution for the system coeff * sol = vec, where\ncoeff "
        "=\n{}\nvec =\n{}\nis given by\nsol =\n{}\n".format(coeff, vec, sol)
    )

    print("\n\n>>> Testing Gaussian elimination:\n")
    y = np.array([
            [7.0, 8.0, 9.0, 19.0, 6],
            [6, 3, 2, 20, 9],
            [10, 7, 11, 22, 8],
            [3, 7, 8, 33, 2],
            [4, 5, 6, 8, 3],
    ])
    t = np.array([5.0, 7.0, 8.0, 8, 10])
    print("Given a matrix\n{}\nand a vector\n{}\n".format(y, t))
    SquareMatrix.gaussian_elim(y, t)
    print(
        "The gaussian elimination yield matrix\n{}\nand"
        "vector\n{}\n".format(y, t)
    )

    print("\n\n>>> Testing LU decomposition:\n")
    y = np.array([
            [7.0, 8.0, 9.0, 19.0, 6],
            [6, 3, 2, 20, 9],
            [10, 7, 11, 22, 8],
            [3, 7, 8, 33, 2],
            [4, 5, 6, 8, 3],
    ])
    t = np.array([5.0, 7.0, 8.0, 8, 10])
    decomposition(y, t)


def linear_space_test(verbose=True):
    for row, col in [(6, 4), (4, 4), (4, 6)]:
        print("---> Case shape = ({}, {})".format(row, col))

        mat = np.random.rand(row, col)
        if verbose:
            print("Given the random matrix =\n", mat)

        q, r = Qr.factorization(mat)
        res = np.matmul(q, r)
        if verbose:
            print("\n\n\n>>> our test\n")
            print("we get q =\n{}\nand r =\n{}".format(q, r))
            print("the product of q and r is\n", res)

        print("Checking if the answer is correct...")
        np.testing.assert_allclose(res, mat, 0.000001, 0.000001)


def main():
    """Tests"""
    linear_space_test(False)


if __name__ == "__main__":
    main()
