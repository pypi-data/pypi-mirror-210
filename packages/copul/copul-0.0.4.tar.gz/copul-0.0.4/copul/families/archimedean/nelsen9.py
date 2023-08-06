import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class GumbellBarnett(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.log(1 - ac.theta * sympy.log(ac.t))
    theta_interval = sympy.Interval(0, 1, left_open=True, right_open=False)

    @property
    def cdf(self):
        cdf = self.u*self.v*sympy.exp(-self.theta*sympy.log(self.u)*sympy.log(self.v))
        return SymPyFunctionWrapper(cdf)


Nelsen9 = GumbellBarnett