import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Frank(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = -sympy.log((sympy.exp(-ac.theta * ac.t) - 1) / (sympy.exp(-ac.theta) - 1))
    theta_interval = sympy.Interval(0, np.inf, left_open=False, right_open=True)


Nelsen5 = Frank
