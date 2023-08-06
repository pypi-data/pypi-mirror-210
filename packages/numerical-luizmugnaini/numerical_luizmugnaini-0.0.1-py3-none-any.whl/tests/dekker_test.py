"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 1
Test for Dekker method for finding roots of a given function.
"""
import math
from typing import Callable
from numerical.roots.dekker import dekker


def func1(k: float) -> float:
    """Solution to homework 1"""
    return 10 - math.exp(-2 * k) * (10 - 3 * k) - 20 * k


def func2(x: float) -> float:
    """Solution to homework 2"""
    return x * (math.exp(10 / x) + math.exp(-10 / x) - 2) - 1


def butterfly(theta: float) -> float:
    """Butterfly function"""
    return math.e ** math.sin(theta) - 2 * math.cos(4 * theta)


def card(theta: float) -> float:
    """Cardioid function"""
    return 1 - math.sin(theta)


def clover(theta: float) -> float:
    return math.sin(4 * theta) ** 2 + math.cos(4 * theta)


def curly(theta: float) -> float:
    return 1 + 2 * math.sin(theta / 2)


def there_is_zero(
    f: Callable[[float], float], head: float, tail: float, subint: int
) -> bool:
    """
    Checks if the function has a zero in [head, tail], looking at subint
    subintervals
    """
    length = tail - head
    step = length / subint
    t = head
    a = f(head)
    for i in range(1, subint + 1):
        t += step
        if a * f(t) <= 0:
            return True
    return False


def dekpol(
    f1: Callable[[float], float],
    f2: Callable[[float], float],
    head: float,
    tail: float,
    abs_error: float,
    rel_error: float,
    subint: int = 400
) -> None:
    """
    Finds intersections between two given curves f1 and f2 in the interval
    [head, tail]. The parameter abs_error and rel_error tracks the absolute
    and relative errors. The number of subintervals to look for the
    intersections is specified by subint
    """

    if (there_is_zero(f1, head, tail, subint)
        and there_is_zero(f2, head, tail, subint)):
        print(
            "The curves intersect at the origin and at the following points:"
        )
    else:
        print("The curves intersect at the following points:")

    inter = []  # Array with the computed intersections
    length = tail - head
    step = length / subint
    for i in range(subint):
        h = head + i * step
        t = h + step
        if (f1(h) - f2(h)) * (f1(t) - f2(t)) <= 0:
            theta = dekker(
                lambda x: f1(x) - f2(x), h, t, abs_error, rel_error, False
            )
            r = f1(theta)
            if r < 0:
                r = -r
                theta += math.pi
            inter.append((r, theta % (2 * math.pi)))

    for i in range(subint):
        h = head + i * step
        t = h + step
        if (f1(h) + f2(h + math.pi)) * (f1(t) + f2(t + math.pi)) <= 0:
            theta = dekker(
                lambda x: f1(x) + f2(x + math.pi), h, t,
                abs_error, rel_error, False
            )
            if f1(theta) > 0:
                inter.append((f1(theta), theta % (2 * math.pi)))
        if (f2(h) + f1(h + math.pi)) * (f2(t) + f1(t + math.pi)) <= 0:
            theta = dekker(
                lambda x: f2(x) + f1(x + math.pi), h, t,
                abs_error, rel_error, False
            )
            if f2(theta) > 0:
                inter.append((f2(theta), theta % (2 * math.pi)))

    for i in range(len(inter)):
        print("(r{n}, theta{n}) =".format(n=i), inter[i])


def print_inter(f1, f2, *args):
    """Function for printing intersections"""
    print(f"Intersections between {f1.__name__} and {f2.__name__}")
    print()
    dekpol(f1, f2, *args)
    print()


def main():
    """Solutions to the given homework problems"""
    absl = 0.00001  # Absolute error
    rel = 0.001  # Relative error
    template = f"{' Test for the {} homework ':-^79}\n"

    print(template.format("first"))
    dekker(func1, 0.1, 1, absl, rel)

    print("\n\n" + template.format("second"))
    absl = 0.001
    rel = 0.0001
    dekker(func2, 90, 110, absl, rel)

    print("\n\n" + template.format("third"))
    absl = 0.00001
    rel = 0.00001
    print_inter(butterfly, card, 0, 2 * math.pi, absl, rel)
    print_inter(butterfly, clover, 0, 2 * math.pi, absl, rel)
    print_inter(butterfly, curly, 0, 4 * math.pi, absl, rel)
    print_inter(card, curly, 0, 4 * math.pi, absl, rel)
    print_inter(clover, curly, 0, 4 * math.pi, absl, rel)
    print_inter(card, clover, 0, 2 * math.pi, absl, rel)


if __name__ == "__main__":
    main()
