import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen19(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.exp(ac.theta / ac.t) - sympy.exp(ac.theta)
    theta_interval = sympy.Interval(0, np.inf, left_open=True, right_open=True)
