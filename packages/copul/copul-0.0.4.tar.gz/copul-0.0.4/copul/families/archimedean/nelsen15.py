import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class GenestGhoudi(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = (1 - ac.t ** (1 / ac.theta)) ** ac.theta
    theta_interval = sympy.Interval(1, np.inf, left_open=False, right_open=True)


Nelsen15 = GenestGhoudi