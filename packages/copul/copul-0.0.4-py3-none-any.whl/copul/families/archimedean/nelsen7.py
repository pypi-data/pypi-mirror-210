import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Nelsen7(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = -sympy.log(ac.theta * ac.t + 1 - ac.theta)
    theta_interval = sympy.Interval(0, 1, left_open=True, right_open=False)

    @property
    def cdf(self):
        cdf = sympy.Max(self.theta*self.u*self.v + (1-self.theta)*(self.u+self.v-1), 0)
        return SymPyFunctionWrapper(cdf)
