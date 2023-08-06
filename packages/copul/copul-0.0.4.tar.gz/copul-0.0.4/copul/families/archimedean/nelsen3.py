import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class AliMikhailHak(ArchimedeanCopula):
    """
        Ali-Mikhail-Hak copula (Nelsen 3)
    """
    ac = ArchimedeanCopula
    _inv_generator = sympy.log((1 - ac.theta * (1 - ac.t)) / ac.t)
    theta_interval = sympy.Interval(-1, 1, left_open=False, right_open=True)

    @property
    def cdf(self):
        cdf = (self.u * self.v) / (1 - self.theta * (1 - self.u) * (1 - self.v))
        return SymPyFunctionWrapper(cdf)


Nelsen3 = AliMikhailHak