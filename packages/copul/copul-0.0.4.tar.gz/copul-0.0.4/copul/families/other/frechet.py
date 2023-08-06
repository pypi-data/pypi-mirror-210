import sympy

from copul.families.abstract_copula import AbstractCopula


class Frechet(AbstractCopula):
    alpha, beta = sympy.symbols("alpha beta", positive=True)

    @property
    def cdf(self):
        frechet_upper_bound = sympy.Min(self.u, self.v)
        frechet_lower_bound = sympy.Max(self.u + self.v - 1, 0)
        return self.alpha*frechet_upper_bound + (1-self.alpha-self.beta)*self.u*self.v +self.beta*frechet_lower_bound

    @property
    def pdf(self):
        raise NotImplementedError("PDF does not exist for Frechet copula")

    @property
    def spearmans_rho(self):
        return self.alpha - self.beta

    @property
    def kendalls_tau(self):
        return (self.alpha - self.beta)*(2 + self.alpha + self.beta)/3


LowerFrechetBound = Frechet()(alpha=0, beta=1)


UpperFrechetBound = Frechet()(alpha=1, beta=0)


if __name__ == "__main__":
    frechet = Frechet()
    cdf = frechet.spearmans_rho()
    exit()
