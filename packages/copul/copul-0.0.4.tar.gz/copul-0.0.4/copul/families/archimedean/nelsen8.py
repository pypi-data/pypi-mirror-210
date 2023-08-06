import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Nelsen8(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = (1 - ac.t) / (1 + (ac.theta - 1) * ac.t)
    theta_interval = sympy.Interval(1, np.inf, left_open=False, right_open=True)

    @property
    def cdf(self):
        num = self.theta**2*self.u*self.v - (1-self.u)*(1-self.v)
        den = self.theta**2 - (self.theta - 1)**2*(1-self.u)*(1-self.v)
        return SymPyFunctionWrapper(sympy.Max(num/den, 0))
