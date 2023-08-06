import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Clayton(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = ((1 / ac.t) ** ac.theta - 1) / ac.theta
    theta_interval = sympy.Interval(0, np.inf, left_open=False, right_open=True)

    @property
    def generator(self):  # ToDo add indicator
        return SymPyFunctionWrapper((self.theta * self.y + 1)**(-1/self.theta))

    @property
    def cdf(self):
        cdf = sympy.Max(
            (self.u ** (-self.theta) + self.v ** (-self.theta) - 1)
            ** (-1 / self.theta),
            0,
        )
        return SymPyFunctionWrapper(cdf)

    @property
    def pdf(self):
        pdf = sympy.Max(
            0,
            (self.u ** (-self.theta) + self.v ** (-self.theta) - 1)
            ** (-2 - 1 / self.theta)
            * self.u ** (-self.theta - 1)
            * self.v ** (-self.theta - 1)
            * (self.theta + 1),
        )
        return SymPyFunctionWrapper(pdf)


Nelsen1 = Clayton
