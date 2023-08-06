import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Nelsen21(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = 1 - (1 - (1 - ac.t) ** ac.theta) ** (1 / ac.theta)
    theta_interval = sympy.Interval(1, np.inf, left_open=False, right_open=True)

    @property
    def generator(self) -> SymPyFunctionWrapper:
        indicator = sympy.Piecewise((1, self.y <= sympy.pi/2), (0, True))
        gen = (1 - (1 - (1 - self.y) ** self.theta) ** (1 / self.theta))*indicator
        return SymPyFunctionWrapper(gen)
