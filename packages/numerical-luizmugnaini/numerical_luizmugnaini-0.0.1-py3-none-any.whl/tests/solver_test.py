"""
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Luan Marc Suquet Camargo      (nUSP: 11809090)
         Francisco Barbosa             (nUSP: 6672901)

Computacao IV (CCM): Chemistry project
"""
from typing import Optional
from numerical.chem.solver import ssa, elmaru
import matplotlib.pyplot as plt
import random as rand
import numpy as np


# Font configuration
font = { "family": "monospace", "size": 15 }
_font = { "family": "monospace", "size": 10 }
sub_font = { "family": "monospace", "size": 10, "weight": "bold" }
title_font = { "family" : "monospace", "size": 20, "weight": "bold" }

# Colors for CLI text
RUN = "\033[1;32m::\033[0m"
QST = "\033[1;35m=>\033[0m"
PLOT = "\033[1;34m->\033[0m"
INF = "\033[1;34m[#]\033[0m"
TITL = "\033[1;35m"
RES = "\033[0m"
ERR = "\033[1;31m"


def dimkin():
    """Dimerisation kinetics: example 1"""
    print(f"\n{TITL}{' Dimerisation kinetics ':-^79}{RES}\n")
    ls = ["$P$", "$P_2$"] # Labels
    x0 = [301, 0] # Initial state
    vol = 1e-15
    tspan = 10
    r = [
        [-2,  1], # Dimerisation
        [ 2, -1]  # Dissociation
    ]

    c1 = 1.66e-3
    def dim(x):
        """Dimerisation propensity"""
        return c1 * x[0] * (x[0] - 1)/2

    c2 = 0.2
    def diss(x):
        """Dissociation propensity"""
        return c2 * x[1]

    print(f"{RUN} Calculating and plotting the evolution over 10s (SSA)\n")
    ssa(x0, r, [dim, diss], tspan=tspan, vol=vol,
        title="Dimerisation kinetics: SSA", labels=ls, conc=True)

    print(f"{RUN} Calculating and plotting the evolution"
          " over 10s (Euler-Maruyama)\n")
    elmaru(x0, r, [dim, diss], vol, tspan=tspan, L=500, labels=ls,
           title="Dimerisation kinetics: Euler-Maruyama")

    print(f"{RUN} Running 20 simulation with SSA...")
    for _ in range(20):
        ts, xs, _ = ssa(x0, r, [dim, diss], tspan=tspan, vol=vol, _plot=False)
        plt.plot(ts, [x[0] for x in xs], color="black")
    print(f"{PLOT} Plotting the overlay of 20 runs for the protein...\n")
    plt.title("Protein evolution: 20 runs", title_font)
    plt.ylim(0, x0[0])
    plt.xlabel("Time", font)
    plt.ylabel("Nr. molecules", font)
    plt.legend(["$P$"], prop=_font)
    plt.show()

    runs = 10_000
    print(f"{RUN} Running {runs} simulations with SSA...")
    ps = []
    for _ in range(runs):
        _, xs, _ = ssa(x0, r, [dim, diss], tspan=10, vol=vol, _plot=False)
        ps.append(xs[-1][0])

    print(f"{PLOT} Plotting the density histogram of the protein"
          " at time t = 10...\n")
    plt.hist(ps, bins=int(185/5), density=True,
             edgecolor="black", color="orange")
    plt.title(f"Density histogram of $P(10)$: SSA, {runs} simulations",
              title_font)
    plt.xlabel("$P(10)$", font)
    plt.ylabel("Density", font)
    plt.show()

    runs = 1000
    print(f"{RUN} Running {runs} Euler-Maruyama simulations...")

    _L = 500          # Number of time-points to be used
    _tspan = 10       # Time span
    tau = _tspan / _L # Fixed time-step

    ts = np.fromiter((n * tau for n in range(_L)), dtype=float)
    pem = np.zeros(_L)         # Records the mean of the simulations
    rec = np.zeros((runs, _L)) # Records the simulations

    for run in range(runs):
        _, xs, _ = elmaru(x0, r, [dim, diss], vol, tspan=_tspan, L=_L,
                          _plot=False)
        xs = np.array(xs)
        pem += xs[:, 0]
        rec[run, :] = xs[:, 0]
    # Calculate the mean
    pem *= 1/runs

    # Calculate standard deviation
    std = np.zeros(_L)
    for t in range(_L):
        std[t] = np.std(rec[:, t])

    print(f"{PLOT} Plotting sample mean for the protein evolution...")
    plt.plot(ts, pem, color="tab:purple")
    plt.plot(ts, pem + 3 * std, color="tab:red")
    plt.plot(ts, pem - 3 * std, color="tab:blue")
    plt.ylim(0, x0[0])
    plt.ylabel("Nr. molecules", font)
    plt.xlabel("Time", font)
    plt.legend(
        ["Mean of $P$",
         f"Mean of $P + 3 \\sigma$",
         f"Mean of $P - 3 \\sigma$"],
        prop=_font
    )
    plt.title("Mean of $P \\pm 3 \\sigma$", title_font)
    plt.show()


def michmen():
    """Michael-Menten: example 2"""
    print(f"\n{TITL}{' Michael-Menten ':-^79}{RES}\n")
    ls = ["Substrate", "Enzyme", "Complex", "Product"]
    x0 = [301, 120, 0, 0] # Initial number of molecules
    r = [
        [-1, -1,  1, 0], # Binding
        [ 1,  1, -1, 0], # Dissociation
        [ 0,  1, -1, 1]  # Conversion
    ]
    vol = 1e-15

    c1 = 1.66e-3
    def b(x):
        """Binding propensity:
        Substrate + Enzime -> Complex
        """
        return c1 * x[0] * x[1]

    c2 = 1e-4
    def d(x):
        """Dissociation propensity:
        Complex -> Substrate + Enzime
        """
        return c2 * x[2]

    c3 = 0.1
    def c(x):
        """Conversion propensity:
        Complex -> Enzime + Product
        """
        return c3 * x[2]

    print(f"{RUN} Calculating SSA simulation and plotting...\n")
    ssa(x0, r, [b, d, c], tspan=50, vol=vol, labels=ls, conc=True,
        title="Michael-Menten: SSA")

    print(f"{RUN} Calculating Euler-Maruyama simulation and plotting...")
    elmaru(x0, r, [b, d, c], vol, tspan=50, labels=ls,
           title="Michael-Menten: Euler-Maruyama")


def argn():
    """Auto-regulatory genetic network"""
    print(f"\n{TITL}{' Auto-regulatory network ':-^79}{RES}\n")
    ls = ["Gene", "$P_2 \\cdot$Gene", "RNA", "$P$", "$P_2$"]
    x0 = [10, 0, 0, 0, 0] # Initial state
    r = [
        [-1,  1,  0,  0, -1], # Repression binding
        [ 1, -1,  0,  0,  1], # Reverse repression binding
        [ 0,  0,  1,  0,  0], # Transcription
        [ 0,  0,  0,  1,  0], # Translation
        [ 0,  0,  0, -2,  1], # Dimerisation
        [ 0,  0,  0,  2, -1], # Dissociation
        [ 0,  0, -1,  0,  0], # RNA degeneration
        [ 0,  0,  0, -1,  0]  # Protein degeneration
    ]

    k1 = 1
    def rb(x):
        """Repression binding:
        Gene + P2 -> P2.Gene
        """
        return k1 * x[0] * x[-1]

    k1r = 10
    def rrb(x):
        """Reverse repression binding:
        P2.Gene -> Gene + P2"""
        return k1r * x[1]

    k2 = 0.01
    def trsc(x):
        """Transcription:
        Gene -> Gene + RNA
        """
        return k2 * x[0]

    k3 = 10
    def trans(x):
        """Translation:
        RNA -> RNA + P
        """
        return k3 * x[2]

    k4 = 1
    def dim(x):
        """Dimerisation:
        P + P -> P2
        """
        return k4 * 0.5 * x[-2] * (x[-2] - 1)

    k4r = 1
    def diss(x):
        """Dissociation:
        P2 -> P + P
        """
        return k4r * x[-1]

    k5 = 0.1
    def rnadeg(x):
        """RNA degeneration:
        RNA -> nothing
        """
        return k5 * x[2]

    k6 = 0.01
    def pdeg(x):
        """Protein degeneration:
        P -> nothing
        """
        return k6 * x[-2]

    def constraint_time(ts: list[float], tfinal: float):
        """Auxiliary function for contraining time arrays:
        Returns the array containing all elments of `ts` less than or equal to
        `tfinal`. Assumes that `ts` is sorted.
        """
        _ts = []
        i = 0
        t = ts[i]
        while t <= tfinal:
            _ts.append(t)
            i += 1
            t = ts[i]
        return _ts

    a = [rb, rrb, trsc, trans, dim, diss, rnadeg, pdeg]

    total_time = 5000
    print(f"{RUN} Calculating evolution of the network through"
          f" a time span of {total_time}s (SSA)...")
    ts, xs, _ = ssa(x0, r, a, tspan=total_time, _plot=False)
    xs = np.array(xs)
    plt.figure()

    print(f"{PLOT} Plotting evolution for time in [0, {total_time}]...")
    plt.subplot(321)
    plt.plot(ts, xs[:, 2], color="orange")
    plt.xlabel("Time", _font)
    plt.ylabel("RNA", _font)

    plt.subplot(323)
    plt.plot(ts, xs[:, 3], color="purple")
    plt.xlabel("Time", _font)
    plt.ylabel("$P$", _font)

    plt.subplot(325)
    plt.plot(ts, xs[:, 4], color="blue")
    plt.xlabel("Time", _font)
    plt.ylabel("$P_2$", _font)

    closeup_time = 250
    print(f"{PLOT} Plotting evolution for time in [0, {closeup_time}]...\n")
    _ts = constraint_time(ts, closeup_time)

    plt.subplot(322)
    plt.plot(_ts, xs[:len(_ts), 2], color="orange")
    plt.xlabel("Time", _font)
    plt.ylabel("RNA", _font)

    plt.subplot(324)
    plt.plot(_ts, xs[:len(_ts), 3], color="purple")
    plt.xlabel("Time", _font)
    plt.ylabel("$P$", _font)

    plt.subplot(326)
    plt.plot(_ts, xs[:len(_ts), 4], color="blue")
    plt.xlabel("Time", _font)
    plt.ylabel("$P_2$", _font)

    plt.suptitle(f"Auto-regulatory genetic network over {total_time}s (SSA)",
                 fontproperties=title_font)
    plt.show()

    time_p = 10
    print(f"{RUN} Calculating evolution of the network through"
        f" a time span of {time_p}s (SSA)...")

    xs, ts = [], []
    while len(xs) < 20 or xs[0][3] * xs[1][3] * xs[2][2] != 0:
        # We try to find an interesting simulation for the evolution of the
        # protein throughout `time_p`, for that, we ensure that at `xs` has at
        # least 20 points, and the first three are non-zero
        ts, xs, _ = ssa(x0, r, a, tspan=time_p, _plot=False)
    xs = np.array(xs)

    print(f"{PLOT} Plotting evolution of P over {time_p}s...\n")
    plt.plot(ts, xs[:, 3], color="purple")
    plt.title(f"Evolution of $P$ over {time_p}s", title_font)
    plt.ylabel("Nr. molecules", font)
    plt.xlabel("Time", font)
    plt.show()

    def density_P10(runs: int, _k2: Optional[float], index: int):
        str_k2 = f"k2 = {_k2}"
        if _k2 == None:
            str_k2 = "k2 uniformly in [0.005, 0.03)"
        print(
            f"{RUN} Running {runs} simulations over 10s (SSA)"
            f" for {str_k2} ..."
        )

        unif = False
        if _k2 == None:
            unif = True

        ps = []
        for _ in range(runs):
            if unif:
                _k2 = rand.uniform(0.005, 0.03)
            def _trsc(x):
                """Transcription with altered constant `k2`
                Gene -> Gene + RNA
                """
                return _k2 * x[0]

            _a = [rb, rrb, _trsc, trans, dim, diss, rnadeg, pdeg]

            _, xs, _ = ssa(x0, r, _a, tspan=10, labels=ls, _plot=False)
            ps.append(xs[-1][-2])

        print(f"{PLOT} Plotting density histogram of P over 10s...\n")
        plt.subplot(3, 1, index)
        plt.hist(ps, bins=int(185/5), density=True,
                edgecolor="black", color="orange")
        plt.xlabel("$P(10)$", _font)
        plt.ylabel("Density", _font)
        if not unif:
            plt.title(f"Density for $k_2 = {_k2}$", sub_font)
        else:
            plt.title(f"$k_2$ uniformly chosen in [0.005, 0.03)", sub_font)

    runs = 1000
    plt.subplots(constrained_layout=True)
    density_P10(runs, 0.01, 1)
    density_P10(runs, 0.02, 2)
    density_P10(runs, _k2=None, index=3)
    plt.suptitle(f"Density histogram of $P(10)$ over {runs} simulation of SSA",
                 fontproperties=title_font)
    plt.show()


def lac():
    """Lac-operon model"""
    print(f"\n{TITL}{' Lac-operon model ':-^79}{RES}\n")
    x0 = [1, 0, 50, 1, 100, 0, 0, 20, 0, 0, 0] # Initial state

    # Available Reactions
    r = [
        # Inhibitor transcription: IDNA -> IDNA + IRNA
        [0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],

        # Inhibitor translation: IRNA -> IRNA + I
        [0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0],

        # Lactose inhibitor binding: I + Lactose -> ILactose
        [0,  0, -1,  0,  0,  0,  0, -1,  1,  0,  0],

        # Lactose inhibitor dissociation: ILactose -> I + Lactose
        [0,  0,  1,  0,  0,  0,  0,  1, -1,  0,  0],

        # Inhibitor binding: I + Op -> IOp
        [0,  0, -1, -1,  0,  0,  0,  0,  0,  1,  0],

        # Inhibitor dissociation: IOp -> I + Op
        [0,  0,  1,  1,  0,  0,  0,  0,  0, -1,  0],

        # RNAp binding: Op + RNAp -> RNApOp
        [0,  0,  0, -1, -1,  0,  0,  0,  0,  0,  1],

        # RNAp dissociation: RNApOp -> Op + RNAp
        [0,  0,  0,  1,  1,  0,  0,  0,  0,  0, -1],

        # Transcription: RNApOp -> Op + RNAp + RNA
        [0,  0,  0,  1,  1,  1,  0,  0,  0,  0, -1],

        # Translation: RNA -> RNA + Z
        [0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0],

        # Conversion: Lactose + Z -> Z
        [0,  0,  0,  0,  0,  0,  0, -1,  0,  0,  0],

        # Inhibitor RNA degradation: IRNA -> nothing
        [0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0],

        # Inhibitor degradation: I -> nothing
        [0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0],

        # Lactose inhibitor degradation: ILactose -> Lactose
        [0,  0,  0,  0,  0,  0,  0,  1, -1,  0,  0],

        # RNA degradation: RNA -> nothing
        [0,  0,  0,  0,  0, -1,  0,  0,  0,  0,  0],

        # Z degradation: Z -> nothing
        [0,  0,  0,  0,  0,  0, -1,  0,  0,  0,  0],
    ]

    c1 = 0.02
    def in_trsc(x):
        """Inhibitor transcription:
        IDNA -> IDNA + IRNA
        """
        return c1 * x[0]

    c2 = 0.1
    def in_trans(x):
        """Inhibitor translation:
        IRNA -> IRNA + I
        """
        return c2 * x[1]

    c3 = 0.005
    def lac_in_bin(x):
        """Lactose inhibitor binding:
        I + Lactose -> ILactose
        """
        return c3 * x[2] * x[7]

    c4 = 0.1
    def lac_in_diss(x):
        """Lactose inhibitor dissociation:
        ILactose -> I + Lactose
        """
        return c4 * x[8]

    c5 = 1
    def in_bin(x):
        """Inhibitor binding:
        I + Op -> IOp
        """
        return c5 * x[2] * x[3]

    c6 = 0.01
    def in_diss(x):
        """Inhibitor dissociation:
        IOp -> I + Op
        """
        return c6 * x[9]

    c7 = 0.1
    def rnap_bin(x):
        """RNAp binding:
        Op + RNAp -> RNApOp
        """
        return c7 * x[3] * x[4]

    c8 = 0.01
    def rnap_diss(x):
        """RNAp dissociation:
        RNApOp -> Op + RNAp
        """
        return c8 * x[10]

    c9 = 0.03
    def trans(x):
        """Transcription:
        RNApOp -> Op + RNAp + RNA
        """
        return c9 * x[10]

    c10 = 0.1
    def transl(x):
        """Translation:
        RNA -> RNA + Z
        """
        return c10 * x[5]

    c11 = 1e-5
    def conv(x):
        """Conversion:
        Lactose + Z -> Z
        """
        return c11 * x[6] * x[7]

    c12 = 0.01
    def in_rna_deg(x):
        """Inhibitor RNA degradation:
        IRNA -> nothing
        """
        return c12 * x[1]

    c13 = 0.002
    def in_deg(x):
        """Inhibitor degradation:
        I -> nothing
        """
        return c13 * x[2]

    def lac_in_deg(x):
        """Lactose inhibitor degradation:
        ILactose -> Lactose
        """
        return c13 * x[8]

    c14 = 0.01
    def rna_deg(x):
        """RNA degradation:
        RNA -> nothing
        """
        return c14 * x[5]

    c15 = 0.001
    def z_deg(x):
        """Z degradation:
        Z -> nothing
        """
        return c15 * x[6]

    # List of propensity functions for each of the reactions in `r`
    a = [
        in_trsc, in_trans,   lac_in_bin, lac_in_diss,
        in_bin,  in_diss,    rnap_bin,   rnap_diss,
        trans,   transl,     conv,       in_rna_deg,
        in_deg,  lac_in_deg, rna_deg,    z_deg,
    ]

    t_event = 20_000
    def intervention(t, x) -> bool:
        """Event intervention at `t == t_event`:
        Adds 10000 lactose molecules to the current state.

        Returns:
        `True` to continue to check for the event;
        `False` when the event occured and we should stop looking for it.
        """
        if t >= t_event:
            x[7] += 10_000
            return False
        return True

    tspan = 50_000
    print(f"{RUN} Running (SSA) simulation of the Lac-operon"
          " model over 50,000s...")
    ts, xs, _ = ssa(x0, r, a, tspan=tspan, _plot=False, event=intervention)
    xs = np.array(xs)

    print(f"{PLOT} Plotting results...")
    plt.subplot(311)
    plt.plot(ts, xs[:, 7], color="orange")
    plt.xlabel("Time", _font)
    plt.ylabel("Lactose", _font)

    plt.subplot(312)
    plt.plot(ts, xs[:, 5], color="purple")
    plt.xlabel("Time", _font)
    plt.ylabel("RNA", _font)

    plt.subplot(313)
    plt.plot(ts, xs[:, 6], color="tab:blue")
    plt.xlabel("Time", _font)
    plt.ylabel("Z", _font)

    plt.suptitle("Lac-Operon model for 50,000s (SSA)", fontproperties=title_font)
    plt.show()


def compare():
    """Comparison of the algorithms SSA and Euler-Maruyama"""
    print(f"\n{TITL}{' Comparison of SSA and Euler Maruyama ':-^79}{RES}\n")
    runs = 10_000 # Number of simulations
    tspan = 10    # Time-span of the simulation
    print(
        f"{INF} In order to compare the algorithms SSA and Euler-Maruyama we'll use\n"
         "    the dimerisation kinetics model --- of which we'll analyse the evolution\n"
        f"    of the protein P throughout a time-span of 10s and {runs} independent\n"
         "    simulations.\n"
    )

    x0 = [301, 0] # Initial state
    vol = 1e-15   # System's volume

    # Reactions
    r = [
        [-2,  1], # Dimerisation
        [ 2, -1]  # Dissociation
    ]

    c1 = 1.66e-3
    def dim(x):
        """Dimerisation:
        P + P -> P2
        """
        return c1 * x[0] * (x[0] - 1)/2

    c2 = 0.2
    def diss(x):
        """Dissociation:
        P2 -> P + P
        """
        return c2 * x[1]

    # Propensity functions associated with each reaction in `r`
    a = [dim, diss]

    print(
        f"{RUN} Running {runs} simulations using both SSA and Euler-Maruyama,\n"
         "   this may take some time..."
    )

    print(
f"""{INF} It should be noted that the stochastic algorithm does not allow us to
    correctly calculate the point-wise mean:

    From its nature, each simulation gets a randomly generated list of
    time-points. In order to calculate the mean and standard deviation of each
    point through the simulations, we randomly choose a standard time-point
    array, by running a single simulation of SSA, that will be used as our basis
    for the record of the results throughout the simulations.
"""
    )

    print(
f"""{INF} In order to have a well behaved mean and standard deviation for SSA,
    we have to take care of two possibilities. In what follows, let `N` be the
    length of the standard time-point array and `M` be the length of the new
    time-point array:
    * If `N < M`, we choose to ignore the last `M - N` protein-states of the new
      array and only store the first `N` points.
    * If `M <= N`, we record the new protein-states as-is and choose to repeat,
      for the last `N - M` elements, the last obtained protein number. This is
      done in order to avoid bad behaviour of the mean and standard deviation.
"""
    )

    # Since the time points vary over the simulations using SSA, I'll determine
    # a standard array of time points `ts_ssa` as a support to calculate the
    # sample mean and standard deviation, this is chosen randomly by running a
    # single simulation of `ssa`
    ts_ssa, xs0_ssa, _ = ssa(x0, r, a, tspan=tspan, _plot=False)
    ts_ssa, xs0_ssa = np.array(ts_ssa), np.array(xs0_ssa)
    L = len(ts_ssa)

    # Record state of the protein for each simulation for SSA
    rec_ssa = np.zeros((runs, L))
    rec_ssa[0] = xs0_ssa[:, 0]

    # `tau` is the fixed time-step used in `elmaru` and `ts_em` represents the
    # array of time-points that will be used by `elmaru` throughout each simulation
    tau = tspan / L
    ts_em = np.array([n * tau for n in range(L)], dtype=float)

    # Record state of the protein for each simulation for Euler-Maruyama
    rec_em = np.zeros((runs, L))

    # In order to use the same simulation-loop as `ssa`, we run a single
    # simulation of `elmaru`
    _, xs0_em, _ = elmaru(x0, r, a, vol, tspan=tspan, L=L, _plot=False)
    xs0_em = np.array(xs0_em)
    rec_em[0] = xs0_em[:, 0]

    for run in range(1, runs):
        # `ssa` simulation: A certain care needs to go with the process of
        # recording the simulation, since the length of the time-points vary
        # through the simulations
        tnew, xs_ssa, _ = ssa(x0, r, a, tspan=tspan, _plot=False)
        xs_ssa, N = np.array(xs_ssa), len(tnew)
        M = min(N, L)
        rec_ssa[run, :M] = xs_ssa[:M, 0]
        if N < L:
            # Repeat the last value obtained in the simulation for the
            # protein. This is determined in order to bring stability to the
            # standard deviation at the end of the simulation, that is, near 10s
            last_value = xs_ssa[-1, 0]
            rec_ssa[run, N:] = np.repeat(last_value, L - N)

        # `elmaru` simulation
        _, xs_em, _ = elmaru(x0, r, a, vol, tspan=tspan, L=L, _plot=False)
        xs_em = np.array(xs_em)
        rec_em[run] = xs_em[:, 0]

    # Record of protein number at 10s
    ps_ssa = rec_ssa[:, -1]
    ps_em = rec_em[:, -1]

    # Point-wise mean
    mean_ssa = np.sum(rec_ssa, axis=0) / runs
    mean_em = np.sum(rec_em, axis=0) / runs

    # Point-wise standard deviation
    std_ssa = np.std(rec_ssa, axis=0)
    std_em = np.std(rec_em, axis=0)

    print(f"{PLOT} Plotting results...\n")
    print(
f"""{INF} The obtained results show that the stability of the Euler-Maruyama algorithm is
    far greater than that of SSA. We should not be deceived by the convergence
    of the SSA mean to the results of Euler-Maruyama near the 10s, since this
    region is where we got the least amount of protein-states throughout the
    simulation by the way we arranged the recording of the SSA simulations and
    therefore is not really reliable.
"""
    )

    plt.plot(ts_ssa, mean_ssa + 3 * std_ssa, color="tab:blue", linestyle=":")
    plt.plot(ts_ssa, mean_ssa, color="tab:blue")
    plt.plot(ts_ssa, mean_ssa - 3 * std_ssa, color="tab:blue", linestyle="-.")

    plt.plot(ts_em, mean_em + 3 * std_em, color="tab:purple", linestyle=":")
    plt.plot(ts_em, mean_em, color="tab:purple")
    plt.plot(ts_em, mean_em - 3 * std_em, color="tab:purple", linestyle="-.")

    plt.ylim(0, x0[0])
    plt.ylabel("Nr. molecules", font)
    plt.xlabel("Time", font)
    plt.legend([
        f"Mean of $P + 3 \\sigma$ (SSA)",
         "Mean of $P$     (SSA)",
        f"Mean of $P - 3 \\sigma$ (SSA)",
        f"Mean of $P + 3 \\sigma$ (Euler-Maruyama)",
         "Mean of $P$     (Euler-Maruyama)",
        f"Mean of $P - 3 \\sigma$ (Euler-Maruyama)"],
        prop=_font)
    plt.title("Comparison of SSA and Euler Maruyama", title_font)
    plt.show()

    print(f"{PLOT} Plotting density histogram for the protein at 10s...\n")

    print(
f"""{INF} Notice that the density histogram of SSA is way sparser when compared to that of
    Euler-Maruyama algorithm. This only reinforces that, if the user wants
    reliability and stability through their simulation, the Euler-Maruyama algorithm
    should be the prefered choice.
"""
    )

    plt.subplot(211)
    plt.hist(ps_ssa, bins=int(185/5), density=True,
             edgecolor="black", color="tab:blue")
    plt.ylabel("Density")
    plt.xlabel("$P(10)$")

    plt.subplot(212)
    plt.hist(ps_em, bins=int(185/5), density=True,
             edgecolor="black", color="tab:orange")
    plt.ylabel("Density")
    plt.xlabel("$P(10)$")

    plt.suptitle("Density histogram of $P(10)$: SSA and Euler-Maruyama",
                 fontproperties=title_font)
    plt.show()


def main():
    print(f"{TITL}{' Simulating Chemical Evironments ':-^79}{RES}\n")
    print(
f"""{INF} We recomend the user to increase their terminal window in order to
    better visualize the displayed text of this program, specially for example
    [5], where we analyse the algorithms.
"""
    )

    stop = False
    while not stop:
        ans = input(
            f"{QST} Availiable examples:\n"
             "   [1] Dimerisation kinetics\n"
             "   [2] Michael-Menten\n"
             "   [3] Auto-regulating genetic network\n"
             "   [4] Lac-operon model\n"
             "   [5] Comparison of the algorithms (SSA and Euler-Maruyama)\n"
            f"{QST} Which one would you like to run? [1, 2, 3, 4, 5] "
        )
        exs = {"1": dimkin, "2": michmen, "3": argn, "4": lac, "5": compare}

        if ans in exs:
            # Run requested example
            exs[ans]()
        else:
            # Deal with degenerate input
            ans_err = input(
                f"\n{ERR}[*] Unfortunately such example {ans} "
                f"is not available.{RES}\n"
                f"{QST} Would you like to quit? [Y/n] "
            )
            if not ans_err or ans_err in ["y", "Y"]:
                stop = True
            continue

        ans_ex = input(
            f"\n{QST} Would you like to test another example? [Y/n] "
        )
        if ans_ex in ["n", "N"]:
            stop = True


if __name__ == "__main__":
    main()
