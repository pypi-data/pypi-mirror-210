#!/usr/bin/env python3
from sympy import (
    IndexedBase,
    log,
    Sum,
    Indexed,
    lambdify,
    gamma,
    simplify,
    hessian,
    symbols,
    Symbol,
    pi,
    diff,
    exp,
    sqrt,
    loggamma,
)


def mc_t():
    """returns functions of the negative log evidence, hessian and jacobian of the y=mx+c model,"""
    # Define symbols
    x = IndexedBase("x")
    y = IndexedBase("y")
    j, N = symbols("j, N")
    # define T's
    T1 = Sum(Indexed(y, j) ** 2 / 2, (j, 0, N - 1))
    T2 = Sum(Indexed(x, j) ** 2 / 2, (j, 0, N - 1))
    T3 = N / 2
    T4 = Sum(Indexed(y, j), (j, 0, N - 1))
    T5 = Sum(Indexed(x, j) * Indexed(y, j), (j, 0, N - 1))
    T6 = Sum(Indexed(x, j), (j, 0, N - 1))
    D = 4 * T2 * T3 - T6**2
    U = T1 - (T2 * T4**2 + T3 * T5**2 - T4 * T5 * T6) / D
    arg_list = (x, y, N)
    d = lambdify(arg_list, D ** (-1 / 2), modules=["numpy", "scipy"])
    u = lambdify(arg_list, U, modules=["numpy", "scipy"])
    return u, d


def mc():
    """returns functions of the negative log evidence of the y=mx+c model assuming known sigma."""
    # Define symbols
    x = IndexedBase("x")
    y = IndexedBase("y")
    sig = IndexedBase("\\sigma")
    j = Symbol("j")
    N = Symbol("N")
    arg_list = (x, y, sig, N)
    # Define T's
    T1 = Sum(Indexed(y, j) ** 2 / 2 / Indexed(sig, j) ** 2, (j, 0, N - 1))
    T2 = Sum(Indexed(x, j) ** 2 / 2 / Indexed(sig, j) ** 2, (j, 0, N - 1))
    T3 = Sum(1 / 2 / Indexed(sig, j) ** 2, (j, 0, N - 1))
    T4 = Sum(Indexed(y, j) / Indexed(sig, j) ** 2, (j, 0, N - 1))
    T5 = Sum(Indexed(x, j) * Indexed(y, j) / Indexed(sig, j) ** 2, (j, 0, N - 1))
    T6 = Sum(Indexed(x, j) / Indexed(sig, j) ** 2, (j, 0, N - 1))
    # Log likelihood
    logl = (
        (1 - N / 2) * log(2 * pi)
        - Sum(log(Indexed(sig, j)), (j, 0, N - 1))
        - 1 / 2 * (log(4 * T2 * T3 - T6**2))
        + (-T1 + (T2 * T4**2 + T3 * T5**2 - T4 * T5 * T6) / (4 * T2 * T3 - T6**2))
    )
    return lambdify(arg_list, logl, modules=["numpy"])
