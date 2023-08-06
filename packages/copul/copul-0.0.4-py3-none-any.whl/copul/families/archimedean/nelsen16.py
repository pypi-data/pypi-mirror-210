import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Nelsen16(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = (ac.theta / ac.t + 1) * (1 - ac.t)
    theta_interval = sympy.Interval(0, np.inf, left_open=True, right_open=True)

    @property
    def generator(self):
        gen = (
            -self.theta / 2
            - self.y / 2
            + 1 / 2
            + 1 / 2 * sympy.sqrt((self.theta + self.y - 1) ** 2 + 4 * self.theta)
        )
        return SymPyFunctionWrapper(gen)

    @property
    def first_deriv_of_generator(self):
        return (self.theta + self.y - 1) / (
            2 * ((self.theta + self.y - 1) ** 2 + 4 * self.theta)
        ) - 1 / 2

    @property
    def ci_char(self):
        ci_char = sympy.log(
            1 / 2
            - (self.theta + self.y - 1) / (8 * self.theta + 2 * (self.theta + self.y - 1) ** 2)
        )
        return SymPyFunctionWrapper(ci_char)
