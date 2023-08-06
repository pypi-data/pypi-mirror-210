import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Nelsen22(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.asin(1 - ac.t ** ac.theta)
    theta_interval = sympy.Interval(0, 1, left_open=True, right_open=False)

    @property
    def generator(self) -> SymPyFunctionWrapper:
        indicator = sympy.Piecewise((1, self.y <= sympy.pi/2), (0, True))
        gen = (1 - sympy.sin(self.y)) ** (1 / self.theta)*indicator
        return SymPyFunctionWrapper(gen)


    def compute_inv_gen_max(self):
        return np.pi / 2
