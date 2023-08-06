"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Luan Marc Suquet Camargo      (nUSP: 11809090)
         Francisco Barbosa             (nUSP: 6672901)

Computacao IV (CCM): Chemistry project
"""
from typing import Callable, Optional
import matplotlib.pyplot as plt
from random import random
import numpy as np


def plot(
    ts: list[float],
    _xs: list[list[int]],
    _ys: list[list[float]],
    title: Optional[str],
    labels: Optional[list[str]]
):
    """Visualization of the data:
    `ts`: time points
    `_xs`: record of the number of molecules of the system
    `_ys`: record of the concentration of each molecule
    `title`: title for the final plot
    `labels`: list of labels for each differen species of molecules
    """
    # Font config
    font = { "family": "monospace", "size": 15 }
    _font = { "family": "monospace", "size": 10 }
    title_font = { "family" : "monospace", "size": 20, "weight": "bold" }

    # Collection of colors to be used for each species of molecules
    c = [
        "tab:blue", "tab:orange", "tab:purple", "black",
        "magenta",  "darkorange", "tab:gray",   "forestgreen"
    ]

    xs = np.array(_xs) # Number of molecules
    kinds = len(xs[0]) # Number of different species

    # Concentration
    ys = np.array(_ys)
    if not _ys is None:
        # Only start a subplot if the concentration was specified
        plt.subplot(211)

    # Plot the evolution of each species
    for k in range(kinds):
       plt.plot(ts, xs[:, k], color=c[k])
    plt.xlabel("Time", font)
    plt.ylabel("Nr. molecules", font)
    plt.legend(labels, prop=_font)

    if not _ys is None:
        plt.subplot(212)
        for k in range(kinds):
            plt.plot(ts, ys[:, k], color=c[k])
        plt.xlabel("Time", font)
        plt.ylabel("Concentration (M)", font)
        plt.legend(labels, prop=_font)
        plt.suptitle(title, fontproperties=title_font)
    else:
        plt.title(title, font)
    plt.show()


def ssa(
    x0: list[int],
    r: list[list[int]],
    a: list[Callable[[list[int]], float]],
    tspan: float,
    vol: Optional[float]=None,
    conc: bool=False,
    t0: float=0,
    event: Optional[Callable[[float, list[int]], bool]]=None,
    _plot: bool=True,
    title: Optional[str]=None,
    labels: Optional[list[str]]=None
) -> tuple[list[float], list[list[int]], Optional[list[list[float]]]]:
    """Stochastic simulation algorithm:
    `x0`: initial state (number of molecules) of the system
    `r`: list of state-changing reactions
    `a`: list of callable propensity functions
    `tspan`: time span for the simulation
    `vol`: system's volume (optional, default is `None`)
    `conc`: calculate concentrations (optional, default is `False`)
    `t0`: starting time (optional, defaults to `0`)
    `event`: callable function taking as arguments the time and current state of
        the system, should return a `bool` for whether or not to continue the
        check for the event (`True`: continue check; `False`: stop check)
    `_plot`: whether or not to make a plot (optional, default is `True`)
    `title`: plot title (optional, default is `None`)
    `labels`: labels given to the plot (optional, default is `None`)

    Returns a tuple `(ts, xs, ys)`, where:
    `ts`: 1-dimensional list with each time point
    `xs`: 2-dimensional list of states (number of molecules) of the system
        throughout `ts`
    `ys`: 2-dimensional list of states (concentration of molecules) of the
        system throughout `ts`. If `conc = False` then `ys = None` is returned.
    """
    N = len(x0) # Number of species
    M = len(r)  # Number of possible reactions
    ts = [t0]   # Time recording
    xs = [x0]   # State recording
    t = t0      # Initial time
    check_for_event = True

    C = 0
    if vol != None:
        C = 6.023e23 * vol # Used to convert from #molecules -> concentration

    ys = [] # Records concentrations
    if conc and vol != None:
        ys.append([x0[j]/C for j in range(N)])

    while t - t0 < tspan:
        x = xs[-1]
        if event != None and check_for_event == True:
            check_for_event = event(t, x)

        ax = [_a(x) for _a in a]
        e1, e2 = (random(), random())
        sum_ax = sum(ax)

        # `j0`: index of the occured reaction
        j0, acc = 0, 0
        for j in range(M):
            # Calculates the least index satisfying acc > e1 * sumprop
            acc = acc + ax[j]
            if acc > e1 * sum_ax:
                j0 = j
                break

        # Change system's state after reaction `j0`
        x = [x[j] + r[j0][j] for j in range(N)]
        xs.append(x)

        # Time for reaction `j0` to occur
        tau = np.log(1/e2) / sum_ax
        t = t + tau
        ts.append(t)

        if conc:
            # Calculate concentration only if required
            ys.append([xs[-1][j]/C for j in range(N)])

    if _plot:
        plot(ts, xs, ys, title, labels)

    return ts, xs, ys


def elmaru(
    x0: list[int],
    r: list[list[int]],
    a: list[Callable[[list[int]], float]],
    vol: float,
    tspan: float,
    L: int=250,
    title: Optional[str]=None,
    _plot: bool=True,
    labels: Optional[list[str]]=None,
) -> tuple[list[float], list[list[int]], list[list[float]]]:
    """Euler-Maruyama method for Chemical Langevin Equation
    `x0`: initial state (number of molecules) of the system
    `r`: list of state-changing reactions
    `a`: list of callable propensity functions
    `vol`: volume of the system
    `tspan`: time span for the simulation
    `L`: number of time steps (optional, defaults to `250`)
    `title`: title of the plot (optional, defaults to `None`)
    `_plot`: whether or not to plot (optional, defaults to `True`)
    `labels`: labels given to the plot (optional, default is `None`)

    Returns a tuple `(ts, xs, ys)`, where:
    `ts`: 1-dimensional array with each time point
    `xs`: 2-dimensional array of states (number of molecules) of the system
        throughout `ts`
    `ys`: 2-dimensional array of states (concentration of molecules) of the
        system throughout `ts`.
    """
    C = 6.023e23 * vol # Used to convert from #molecules -> concentration
    N = len(x0)        # Number of species
    M = len(r)         # Number of reactions
    tau = tspan / L    # Fixed time step

    # Initial setup
    xs = [x0]                          # State recording
    ys = [[x0[j]/C for j in range(N)]] # Records concentrations
    ts = [n * tau for n in range(L)]   # Time records

    # Simulations
    for _ in range(L - 1):
        # Propensities for the current realisation
        axs = [_a(xs[-1]) for _a in a]

        # Coefficients for each type of reaction
        d = [
            tau * axs[j] + np.sqrt(abs(tau * axs[j])) * random()
            for j in range(M)
        ]

        rsum = []
        for i in range(N):
            si = 0
            for j in range(M):
                si = si + d[j] * r[j][i]
            rsum.append(si)

        last = xs[-1]
        xs.append([last[j] + rsum[j] for j in range(N)])
        ys.append([xs[-1][j]/C for j in range(N)])

    if _plot:
        plot(ts, xs, ys, title, labels)

    return ts, xs, ys
