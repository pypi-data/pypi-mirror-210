"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 1
Dekker method for finding roots of a given function.
"""
from typing import Callable


def dekker(
    f: Callable[[float], float],
    a: float,
    b: float,
    abs_error: float,
    rel_error: float,
    verbose: bool = True,
) -> float:
    """
    Dekker method for finding approximations of zeros of a given function
    f in the interval [a, b] with an absolute error and relative error of
    abs_error and rel_error, respectively.
    You can toggle the verbose if you don't wish any printing.
    """
    if f(a) * f(b) > 0:
        raise Exception(
            "The function must change sign in the interval"
            "[{}, {}]".format(a, b)
        )

    ant = a                    # Antipode point
    approx = b                 # Current approximation
    last_approx = b            # Last approximation
    fsize = abs(approx - ant)  # Interval size in iteration 0 (mod 4)
    do_dichotomy = False       # Toggle the use of the dichotomy method
    dichotomy_counter = 0      # Counts the number of dichotomy uses

    iteration = 0
    while not (is_approx(approx, ant, abs_error, rel_error) or f(approx) == 0):
        if dichotomy_counter == 3:
            # Stop dichotomy and reset the counter
            do_dichotomy = False
            dichotomy_counter = 0

        # If interval decreased sufficiently in the last 4 iterations
        if iteration != 0 and iteration % 4 == 0:
            last_fsize = fsize
            fsize = abs(approx - ant)
            if abs(approx - ant) > last_fsize / 8:
                # Apply dichotomy 3 times in a row
                do_dichotomy = True

        # Calculates next approximation
        if do_dichotomy:
            next_approx = (approx + ant) / 2
        else:
            next_approx = secant_dichotomy(
                f, approx, ant, last_approx, abs_error, rel_error
            )

        # Calculates the next antipode
        next_ant = approx
        if f(ant) * f(next_approx) < 0:
            next_ant = ant

        # Swaps antipode and approximation if needed
        if abs(f(ant)) < abs(f(approx)):
            aux = ant
            ant = approx
            approx = aux

        # Change of variables to next iteration
        last_approx = approx
        approx = next_approx
        ant = next_ant

        if do_dichotomy:
            dichotomy_counter += 1
        iteration += 1

    if verbose:
        print(
            "{} is the approximation, obtained "
            "in {} iterations".format(approx, iteration)
        )
    return approx


def is_approx(
    approx: float, ant: float, abs_error: float, rel_error: float
) -> bool:
    """
    True if the approximation satisfies the wanted error conditions, false
    otherwise.
    """
    tol = max(abs_error, abs(approx) * rel_error)
    abs_diff = abs(approx - ant)
    if abs_diff / 2 < tol:
        return True
    return False


def secant_dichotomy(
    f: Callable[[float], float],
    approx: float,
    ant: float,
    last_approx: float,
    abs_error: float,
    rel_error: float,
) -> float:
    """
    Implements a mix of the secant and dichotomy methods, returning
    the next approximation for the Dekker method.
    """
    m = (approx + ant) / 2
    s = m
    if f(approx) != f(last_approx):
        delta = (
            f(approx) * (approx - last_approx) / (f(approx) - f(last_approx))
        )
        s = approx - delta

    tol = max(abs_error, abs(approx) * rel_error)
    if abs(s - approx) < tol:
        return approx + tol * (approx - ant) / abs(approx - ant)
    if min(approx, m) < s and s < max(approx, m):
        return s
    return m
