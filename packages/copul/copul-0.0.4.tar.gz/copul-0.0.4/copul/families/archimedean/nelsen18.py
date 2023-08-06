import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen18(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.exp(ac.theta / (ac.t - 1))
    theta_interval = sympy.Interval(2, np.inf, left_open=False, right_open=True)
