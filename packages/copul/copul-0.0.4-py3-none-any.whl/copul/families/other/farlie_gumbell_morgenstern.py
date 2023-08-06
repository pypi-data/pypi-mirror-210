import sympy

from copul.families import abstract_copula
from copul.families.abstract_copula import AbstractCopula


class FarlieGumbellMorgenstern(AbstractCopula):
    theta = sympy.symbols("theta", positive=True)

    def cdf(self):
        return self.u*self.v + self.theta*self.u*self.v*(1 - self.u)*(1 - self.v)

    @property
    def spearmans_rho(self):
        return self.theta/3

    @property
    def kendalls_tau(self):
        return 2*self.theta/9


if __name__ == "__main__":
    farlie = FarlieGumbellMorgenstern()
    cdf = farlie.cdf
    pdf = farlie.log_pdf
    diff = sympy.simplify(sympy.diff(cdf, farlie.v))
    diff2 = sympy.simplify(sympy.diff(diff, farlie.v))
    print(sympy.latex(diff2))
    special_diff = abstract_copula.round_expression(diff.subs(farlie.u, 0.5))
    sympy.plot(special_diff.subs(farlie.theta, 2))
    exit()
