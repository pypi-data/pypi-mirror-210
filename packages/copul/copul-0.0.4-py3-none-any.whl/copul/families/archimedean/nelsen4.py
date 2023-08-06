import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class GumbellHougaard(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = (-sympy.log(ac.t)) ** ac.theta
    theta_interval = sympy.Interval(1, np.inf, left_open=False, right_open=True)


Nelsen4 = GumbellHougaard
