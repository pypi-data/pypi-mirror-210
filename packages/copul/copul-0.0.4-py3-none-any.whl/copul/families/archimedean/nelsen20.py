import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen20(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.exp(ac.t ** (-ac.theta)) - sympy.exp(1)
    theta_interval = sympy.Interval(0, np.inf, left_open=True, right_open=True)
