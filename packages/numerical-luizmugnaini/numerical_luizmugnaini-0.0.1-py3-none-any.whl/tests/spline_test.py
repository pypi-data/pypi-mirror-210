"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Tests: module numerical.interpolate.spline
"""
import math
import matplotlib.pyplot as plt
from numerical.interpolate.spline import (
    NaturalSpline,
    CompleteSpline,
    NotKnotSpline,
    PeriodicSpline,
)
from scipy.interpolate import CubicSpline, CubicHermiteSpline


class Curves:
    """Bidimensional smooth curves"""

    def __init__(self, coord1: list[float], coord2: list[float], _range: int):
        if len(coord1) != len(coord2):
            raise Exception("Coordinates must have the same length")
        self.coord1 = coord1
        self.coord2 = coord2
        self.param = [self.calc_param(i) for i in range(len(coord1))]
        self.spline1 = PeriodicSpline(self.param, coord1)
        self.spline2 = PeriodicSpline(self.param, coord2)
        self.points = self.calc_points(_range)

    def calc_param(self, index: int) -> float:
        """Calculates the parameter at `index`"""
        if index == 0:
            return 0
        return self.calc_param(index - 1) + math.sqrt(
            (self.coord1[index] - self.coord1[index - 1]) ** 2
            + (self.coord2[index] - self.coord2[index - 1]) ** 2
        )

    def get_param_at(self, index: int) -> float:
        """Returns the parameter at `index`"""
        return self.param[index]

    def get_param(self) -> list[float]:
        """Returns the list of parameters"""
        return self.param

    def calc_points(self, _range: int) -> list[tuple[float, float]]:
        """Calculates a list of length `_range` of curve points"""
        points = []
        for i in range(_range):
            epsilon = i / _range
            t = (1 - epsilon) * self.param[0] + self.param[-1] * epsilon
            x = self.spline1.value_at(t)
            y = self.spline2.value_at(t)
            points.append((x, y))
        return points

    def get_points(self) -> list[tuple[float, float]]:
        """Return the list of curve points"""
        return self.points

    def plot_curve(self):
        """Plots the curve"""
        plt.plot(*zip(*self.points))
        font = { "family": "monospace", "size": 22 }
        plt.title("Cubic spline interpolation", font)
        plt.xlabel("x axis", font)
        plt.ylabel("y axis", font)


def ep_test(cls, func, deriv=None, verbose=True):
    for n in [10, 20, 30, 40, 80, 160]:
        # Spline construction
        knots = [i / n for i in range(n)]
        values = [func(k) for k in knots]

        spline = None
        if cls.__name__ == "CompleteSpline":
            # The complete spline requires derivative values
            derivatives = (deriv(knots[0]), deriv(knots[-1]))
            spline = cls(knots, values, derivatives)
        else:
            spline = cls(knots, values)

        if verbose:
            print(
                "-> {} constructed for {} for {} "
                "knots...".format(cls.__name__, func.__name__, n)
            )

        # Error estimate
        error = 0
        _range = 1000
        for i in range(_range):
            point = i / _range
            if point <= knots[-1]:
                oscillation = abs(func(point) - spline.value_at(point))
                error = max(error, oscillation)
            else:
                break

        print(
            "The error for the {} of {} for {} knots is "
            "{:e}\n\n".format(cls.__name__, func.__name__, n, error)
        )


def scipy_plot(x, y, n):
    def calc_param(x, y, index):
        if index == 0:
            return 0
        return calc_param(x, y, index - 1) + math.sqrt(
            (x[index] - x[index - 1]) ** 2
            + (y[index] - y[index - 1]) ** 2
        )

    param = [calc_param(x, y, i) for i in range(len(x))]

    spline_x = CubicSpline(param, x, bc_type="periodic")
    spline_y = CubicSpline(param, y, bc_type="periodic")

    interval = []
    for i in range(n):
        epsilon = i / n
        interval.append((1 - epsilon) * param[0] + param[-1] * epsilon)

    xs = spline_x(interval)[:]
    ys = spline_y(interval)[:]
    plt.plot(xs, ys, color="green")


def scipy_test(name: str, func, deriv=None, verbose=True):
    for n in [10, 20, 30, 40, 80, 160]:
        # Spline construction
        knots = [i / n for i in range(n)]
        values = [func(k) for k in knots]

        spline = None
        if name == "complete":
            # The complete spline requires derivative values
            derivatives = [deriv(k) for k in knots]
            spline = CubicHermiteSpline(knots, values, derivatives)
        else:
            spline = CubicSpline(x=knots, y=values, bc_type=name)

        if verbose:
            print(
                "-> {} constructed for {} for {} "
                "knots...".format(name, func.__name__, n)
            )

        # Error estimate
        error = 0
        _range = 1000
        points = [i / _range for i in range(1000)]
        spline_vec = spline(points)
        for i in range(len(points)):
            if points[i] <= knots[-1]:
                oscillation = abs(func(points[i]) - spline_vec[i])
                error = max(error, oscillation)
            else:
                break

        print(
            "The error for the {} of {} for {} knots is "
            "{:e}\n\n".format(name, func.__name__, n, error)
        )


def main():
    """Tests"""
    def func(x: float) -> float:
        return 1 / (2 - x)

    def func_derivative(x: float) -> float:
        return 1 / (2 - x) ** 2

    print(">>> Error tests:\n")

    print("NATURAL SPLINE:\n")
    ep_test(NaturalSpline, func)

    print("scipy NATURAL SPLINE:\n")
    scipy_test("natural", func)

    print("-" * 80)

    print("\n\nCOMPLETE SPLINE:\n")
    ep_test(CompleteSpline, func, func_derivative)

    print("\nscipy COMPLETE SPLINE:\n")
    scipy_test("complete", func, func_derivative)

    print("-" * 80)

    print("\n\nNOT A KNOT\n")
    ep_test(NotKnotSpline, func)

    print("\nscipy NOT A KNOT\n")
    scipy_test("not-a-knot", func)

    print("\n\n>>> Curves test:\n")
    coord1 = [25.0, 19.0, 13.0, 9.0, 5.0, 2.2, 1.0, 3.0, 8.0, 13.0, 18.0, 25.0]
    coord2 = [5.0, 7.5, 9.1, 9.4, 9.0, 7.5, 5.0, 2.1, 2.0, 3.5, 4.5, 5.0]
    curve = Curves(coord1, coord2, 400)
    plt.scatter(coord1, coord2)
    curve.plot_curve()
    scipy_plot(coord1, coord2, 400)
    plt.show()


if __name__ == "__main__":
    main()
