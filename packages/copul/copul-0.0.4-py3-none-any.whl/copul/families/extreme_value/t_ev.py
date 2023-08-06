import numpy as np
import sympy
from sympy import stats

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


# noinspection PyPep8Naming
class tEV(ExtremeValueCopula):
    nu, rho = sympy.symbols("nu rho")

    def __init__(self):
        def z(t):
            return (1 + self.nu) ** (1 / 2) * ((t / (1 - t)) ** (1 / self.nu) - self.rho) * (1 - self.rho ** 2) ** (
                    -1 / 2)

        self.pickand = (1 - self.t) * stats.cdf(stats.StudentT("x", self.nu + 1))(z(1 - self.t)) + self.t * stats.cdf(
            stats.StudentT("x", self.nu + 1))(z(self.t))
        self.intervals = {
            self.nu: sympy.Interval(0, np.inf, left_open=True, right_open=True),
            self.rho: sympy.Interval(-1, 1, left_open=True, right_open=True),
        }
