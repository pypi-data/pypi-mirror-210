import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Nelsen12(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = (1 / ac.t - 1) ** ac.theta
    theta_interval = sympy.Interval(1, np.inf, left_open=False, right_open=True)

    @property
    def generator(self):
        gen = 1 / (self.y ** (1 / self.theta) + 1)
        return SymPyFunctionWrapper(gen)
