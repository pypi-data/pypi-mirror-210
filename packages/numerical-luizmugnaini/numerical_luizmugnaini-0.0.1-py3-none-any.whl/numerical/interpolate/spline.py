"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 2 Cubic interpolating splines
"""
from numerical.matrix.linear_sys import Tridiagonal, Periodic
import numpy as np


class Spline:
    """Cubic interpolating spline. Real valued twice continuously
    differentiable function. For each interval of consequent knots the spline
    coincides with a polynomial of degree at most 3.
    """

    def __init__(self, knots: list[float], values: list[float]):
        """Base of `Spline` variables:
        `knots`: list of the partition for the interval.
        `values`: list of the values of the spline at the knots.
        """
        if len(knots) != len(values):
            raise Exception("Args must have the same length")
        self.knots = knots
        self.values = values

    def get_knots(self) -> list[float]:
        """Gets the list of knots"""
        return self.knots

    def get_values(self) -> list[float]:
        """Get the list of values for the knots"""
        return self.values

    def which_interval(self, x: float) -> int:
        """Finds the interval that contains `x`.\n
        For instance, if `x` belongs to the interval
        [`knots[i]`, `knots[i+1]`], the method returns `i`.
        """
        if x < self.knots[0] or x > self.knots[-1]:
            raise Exception("Argument not in the interval")

        index = len(self.knots) - 2
        for i in range(len(self.knots) - 2):
            if self.knots[i] <= x <= self.knots[i + 1]:
                index = i
                break
        return index

    def interval_length(self, index: int) -> float:
        """Returns the length of the `index` interval.\n
        Note that `index` should be an int between `0` and `len(knots) - 2`
        """
        if not 0 <= index <= len(self.knots) - 2:
            raise Exception("Index out of bounds")
        return self.knots[index + 1] - self.knots[index]


class NaturalSpline(Spline):
    """Natural cubic interpolating spline.\n
    Characterized by first and last moments being equal to zero.
    """

    def __init__(self, knots: list[float], values: list[float]):
        Spline.__init__(self, knots, values)
        self.moments: list[float] = self.find_moments()

    def find_moments(self) -> list[float]:
        """Finds moments of the spline at the given knots"""
        # Construct matrices
        size = len(self.knots)
        coeff = 2 * np.identity(size, dtype=float)
        res = np.zeros(size, dtype=float)
        for i in range(1, size - 1):
            # Coefficient matrix: tridiagonal
            h_1 = self.interval_length(i - 1)
            h0 = self.interval_length(i)
            upper = h0 / (h0 + h_1)
            coeff[i, i + 1] = upper
            coeff[i, i - 1] = 1 - upper

            # Result matrix
            if i < size - 1:
                diff0 = self.values[i] - self.values[i - 1]
                diff1 = self.values[i + 1] - self.values[i]
                res[i] = 6 / (h_1 + h0) * (diff1 / h0 - diff0 / h_1)

        # Solution to the system `coeff` * `moments` = `res`
        moments = Tridiagonal.solve(coeff, res)
        return moments.tolist()

    def get_moments(self) -> list[float]:
        """Get the moments of the spline"""
        return self.moments

    def value_at(self, x: float) -> float:
        """Returns the value of the spline function at `x`"""
        # Data about the interval of `x`
        i = self.which_interval(x)
        y0, y1 = self.values[i], self.values[i + 1]
        m0, m1 = self.moments[i], self.moments[i + 1]
        h = self.interval_length(i)

        diff = x - self.knots[i]
        beta = (y1 - y0) / h - (2 * m0 + m1) * h / 6
        delta = (m1 - m0) / (6 * h)
        gamma = m0 / 2
        return y0 + beta * diff + gamma * (diff ** 2) + delta * (diff ** 3)


class CompleteSpline(Spline):
    """Complete cubic interpolating spline"""

    def __init__(
        self,
        knots: list[float],
        values: list[float],
        derivatives: tuple[float, float]
    ):
        """Base of `Spline` variables:
        `knots`: list of the partition for the interval.
        `values`: list of the values of the spline at the knots.\n
        The `CompleteSpline` requires additionally:
        `derivatives`: tuple of derivatives of the spline at the end points of
        the knot list.
        """
        Spline.__init__(self, knots, values)
        self.derivatives: tuple[float, float] = derivatives
        self.moments: list[float] = self.find_moments()

    def find_moments(self) -> list[float]:
        """Finds moments of the spline at the given knots"""
        # Construct matrices
        size = len(self.knots)
        coeff = 2 * np.identity(size, dtype=float)
        res = np.zeros(size, dtype=float)
        for i in range(1, size - 1):  # Sets the matrices
            # Coefficient matrix: tridiagonal
            h_1 = self.interval_length(i - 1)
            h0 = self.interval_length(i)
            upper = h0 / (h0 + h_1)
            coeff[i, i + 1] = upper
            coeff[i, i - 1] = 1 - upper

            # Result matrix
            if i < size - 1:
                diff0 = self.values[i] - self.values[i - 1]
                diff1 = self.values[i + 1] - self.values[i]
                res[i] = 6 / (h_1 + h0) * (diff1 / h0 - diff0 / h_1)

        # Complete spline special conditions:
        coeff[0, 1], coeff[-1, -2] = 1, 1
        h0 = self.interval_length(0)
        diff0 = self.values[1] - self.values[0]
        res[0] = 6 / h0 * (diff0 / h0 - self.derivatives[0])
        hn = self.interval_length(size - 2)
        diffn = self.values[-1] - self.values[-2]
        res[-1] = 6 / hn * (self.derivatives[1] - diffn / hn)

        moments = Tridiagonal.solve(coeff, res)
        return moments.tolist()

    def get_moments(self) -> list[float]:
        """Get the moments of the spline"""
        return self.moments

    def value_at(self, x: float) -> float:
        """Returns the value of the spline function at `x`"""
        # Data about the interval of `x`
        i = self.which_interval(x)
        y0, y1 = self.values[i], self.values[i + 1]
        m0, m1 = self.moments[i], self.moments[i + 1]
        h = self.interval_length(i)

        diff = x - self.knots[i]
        beta = (y1 - y0) / h - (2 * m0 + m1) * h / 6
        delta = (m1 - m0) / (6 * h)
        gamma = m0 / 2
        return y0 + beta * diff + gamma * (diff ** 2) + delta * (diff ** 3)


class PeriodicSpline(Spline):
    """Periodic Splines:
    `PeriodicSplines` requires the `k`th derivative (`k` in `[0, 1, 2]`) at the
    end point knots to be equal for the given spline.
    """

    def __init__(self, knots: list[float], values: list[float]):
        Spline.__init__(self, knots, values)
        self.moments: list[float] = self.find_moments()

    def find_moments(self) -> list[float]:
        """Finds moments of the spline at the given knots"""
        # We'll have the two end point moments equal, so we`ll shorten our
        # matrix by one row and column, making it a square `n - 1` matrix,
        # where `n` is the number of knots
        size = len(self.knots)
        coeff = 2 * np.identity(size - 1, dtype=float)
        res = np.zeros(size - 1, dtype=float)
        for i in range(2, size - 1):
            # Since the range starts at 2, we subtract 1 from the actual matrix
            # coordinates in order to maintain the algorithm concise.
            # Coefficient matrix:
            h_1 = self.interval_length(i - 1)
            h0 = self.interval_length(i)
            upper = h0 / (h0 + h_1)
            coeff[i - 1, i] = upper
            coeff[i - 1, i - 2] = 1 - upper

            # Result matrix
            if i < size - 1:
                diff0 = self.values[i] - self.values[i - 1]
                diff1 = self.values[i + 1] - self.values[i]
                res[i - 1] = 6 / (h_1 + h0) * (diff1 / h0 - diff0 / h_1)

        # Complete spline special conditions:
        h0 = self.interval_length(0)
        h1 = self.interval_length(1)
        hn = self.interval_length(size - 2)
        coeff[0, 1] = h1 / (h0 + h1)
        coeff[0, -1] = h0 / (h0 + h1)
        coeff[-1, 0] = h0 / (h0 + hn)
        coeff[-1, -2] = hn / (hn + h1)

        diff1 = self.values[1] - self.values[-1]
        diffn = self.values[-1] - self.values[-2]
        res[0] = 6 / (h0 + h1) * (
            (self.values[2] - self.values[1]) / h1
            - (self.values[1] - self.values[0]) / h0
        )
        res[-1] = (6 / (h0 + hn)) * (diff1 / h0 - diffn / hn)

        moments = Periodic.solve(coeff, res)
        return moments.tolist()

    def get_moments(self) -> list[float]:
        """Get the moments of the spline"""
        return self.moments

    def value_at(self, x: float) -> float:
        """Returns the value of the spline function at `x`"""
        # Data about the interval of `x`
        i = self.which_interval(x)
        y0, y1 = self.values[i], self.values[i + 1]
        m0, m1 = self.moments[i], self.moments[i + 1]
        h = self.interval_length(i)

        diff = x - self.knots[i]
        beta = (y1 - y0) / h - (2 * m0 + m1) * h / 6
        delta = (m1 - m0) / (6 * h)
        gamma = m0 / 2
        return y0 + beta * diff + gamma * (diff ** 2) + delta * (diff ** 3)


class NotKnotSpline(Spline):
    """Not a Knot spline.
    In the intervals `knots[0]` to `knots[2]` and `knots[n - 3]` to `knots[-1]`
    the spline corresponds to a polynomial of degree at most 3.
    """

    def __init__(self, knots: list[float], values: list[float]):
        Spline.__init__(self, knots, values)
        self.moments: list[float] = self.find_moments()

    def find_moments(self) -> list[float]:
        """Finds moments of the spline at the given knots"""
        size = len(self.knots)
        # Construct matrices
        coeff = 2 * np.identity(size - 1, dtype=float)
        res = np.zeros(size - 1, dtype=float)
        for i in range(1, size - 2):  # Sets the matrices
            # Coefficient matrix: tridiagonal
            h_1 = self.interval_length(i - 1)
            h0 = self.interval_length(i)
            if i == 1:
                upper = h_1 / h0
                coeff[i, i + 1] = 1 - upper
                coeff[i, i] = 2 + upper
            if i == (size - 3):
                upper = h_1 / h0
                coeff[i, i] = 2 + upper
                coeff[i, i - 1] = 1 - upper
            else:
                upper = h0 / (h0 + h_1)
                coeff[i, i + 1] = upper
                coeff[i, i - 1] = 1 - upper

            # Result matrix
            if i < size - 2:
                diff0 = self.values[i] - self.values[i - 1]
                diff1 = self.values[i + 1] - self.values[i]
                res[i] = 6 / (h_1 + h0) * (diff1 / h0 - diff0 / h_1)

        # Calculate inner moments
        moments = Tridiagonal.solve(coeff, res)

        # First moment
        h1 = self.interval_length(0)
        h2 = self.interval_length(1)
        m0 = ((h1 + h2) / h2) * moments[0] - (h1 / h2) * moments[1]

        # Last moment
        h_n = self.interval_length(size - 2)
        h_n_1 = self.interval_length(size - 3)
        m_n = (
            ((h_n + h_n_1) / h_n_1) * moments[size - 2]
            - (h_n / h_n_1) * moments[size - 3]
        )

        return np.insert(moments, (0, len(moments)), (m0, m_n)).tolist()


    def get_moments(self) -> list[float]:
        """Get the moments of the spline"""
        return self.moments

    def value_at(self, x: float) -> float:
        """Returns the value of the spline function at `x`"""
        # Data about the interval of `x`
        i = self.which_interval(x)
        y0, y1 = self.values[i], self.values[i + 1]
        m0, m1 = self.moments[i], self.moments[i + 1]
        h = self.interval_length(i)

        diff = x - self.knots[i]
        beta = (y1 - y0) / h - (2 * m0 + m1) * h / 6
        delta = (m1 - m0) / (6 * h)
        gamma = m0 / 2
        return y0 + beta * diff + gamma * (diff ** 2) + delta * (diff ** 3)
