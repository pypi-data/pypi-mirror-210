import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen13(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = (1 - sympy.log(ac.t)) ** ac.theta - 1
    theta_interval = sympy.Interval(0, np.inf, left_open=True, right_open=True)
