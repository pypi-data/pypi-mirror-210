import sympy

from copul.families import get_simplified_solution
from copul.families.abstract_copula import AbstractCopula
from copul.sympy_wrapper import SymPyFunctionWrapper


class Plackett(AbstractCopula):
    theta = sympy.symbols("theta", positive=True)

    @property
    def cdf(self):
        cdf = (1 + (self.theta - 1)*(self.u + self.v)
               - sympy.sqrt((1 + (self.theta - 1)*(self.u + self.v))**2
                            - 4*self.u*self.v*self.theta*(self.theta - 1)))\
              /(2*(self.theta - 1))
        simplified_cdf = get_simplified_solution(cdf)
        return SymPyFunctionWrapper(simplified_cdf)

    @property
    def pdf(self):
        pdf = sympy.diff(self.cdf.func, self.u, self.v)
        return SymPyFunctionWrapper(get_simplified_solution(pdf))

    @property
    def spearmans_rho(self):
        return (self.theta+1)/(self.theta-1) - 4*self.theta*sympy.log(self.theta)/(self.theta-1)**2

    def get_density_of_density(self):
        # D_vu(pdf)
        return (-((2*self.u*self.theta - 2*self.u - self.theta + 1)*
                  (self.u**2*self.theta**2 - 2*self.u**2*self.theta + self.u**2
                   - 2*self.u*self.v*self.theta**2 + 2*self.u*self.v + 2*self.u*self.theta
                   - 2*self.u + self.v**2*self.theta**2 - 2*self.v**2*self.theta
                   + self.v**2 + 2*self.v*self.theta - 2*self.v + 1)
                  + 3*(-self.u*self.theta**2 + self.u + self.v*self.theta**2
                       - 2*self.v*self.theta + self.v + self.theta - 1)*
                  (-2*self.u*self.v*self.theta + 2*self.u*self.v + self.u*self.theta
                   - self.u + self.v*self.theta - self.v + 1))
                *(2*self.v*self.theta - 2*self.v - self.theta + 1)
                *(self.u**2*self.theta**2 - 2*self.u**2*self.theta + self.u**2
                  - 2*self.u*self.v*self.theta**2 + 2*self.u*self.v + 2*self.u*self.theta
                  - 2*self.u + self.v**2*self.theta**2 - 2*self.v**2*self.theta + self.v**2
                  + 2*self.v*self.theta - 2*self.v + 1)
                + 2*((2*self.u*self.theta - 2*self.u - self.theta + 1)
                     *(self.u**2*self.theta**2 - 2*self.u**2*self.theta + self.u**2
                       - 2*self.u*self.v*self.theta**2 + 2*self.u*self.v + 2*self.u*self.theta
                       - 2*self.u + self.v**2*self.theta**2 - 2*self.v**2*self.theta + self.v**2
                       + 2*self.v*self.theta - 2*self.v + 1)
                     + 3*(-self.u*self.theta**2 + self.u + self.v*self.theta**2
                          - 2*self.v*self.theta + self.v + self.theta - 1)
                     *(-2*self.u*self.v*self.theta + 2*self.u*self.v + self.u*self.theta
                       - self.u + self.v*self.theta - self.v + 1))
                *(self.u*self.theta**2 - 2*self.u*self.theta + self.u
                  - self.v*self.theta**2 + self.v + self.theta - 1)
                *(-2*self.u*self.v*self.theta + 2*self.u*self.v + self.u*self.theta
                  - self.u + self.v*self.theta - self.v + 1)
                + (-2*(self.theta - 1)
                   *(self.u**2*self.theta**2 - 2*self.u**2*self.theta + self.u**2
                     - 2*self.u*self.v*self.theta**2 + 2*self.u*self.v + 2*self.u*self.theta
                     - 2*self.u + self.v**2*self.theta**2 - 2*self.v**2*self.theta + self.v**2
                     + 2*self.v*self.theta - 2*self.v + 1) + 3*(self.theta**2 - 1)
                   *(-2*self.u*self.v*self.theta + 2*self.u*self.v + self.u*self.theta - self.u
                     + self.v*self.theta - self.v + 1)
                   - 2*(2*self.u*self.theta - 2*self.u - self.theta + 1)
                   *(self.u*self.theta**2 - 2*self.u*self.theta + self.u - self.v*self.theta**2
                     + self.v + self.theta - 1)
                   + 3*(2*self.v*self.theta - 2*self.v - self.theta + 1)
                   *(-self.u*self.theta**2 + self.u + self.v*self.theta**2 - 2*self.v*self.theta
                     + self.v + self.theta - 1))
                *(-2*self.u*self.v*self.theta + 2*self.u*self.v + self.u*self.theta - self.u
                  + self.v*self.theta - self.v + 1)
                *(self.u**2*self.theta**2 - 2*self.u**2*self.theta + self.u**2
                  - 2*self.u*self.v*self.theta**2 + 2*self.u*self.v + 2*self.u*self.theta
                  - 2*self.u + self.v**2*self.theta**2 - 2*self.v**2*self.theta + self.v**2
                  + 2*self.v*self.theta - 2*self.v + 1))/(
                (-2*self.u*self.v*self.theta + 2*self.u*self.v + self.u*self.theta - self.u
                 + self.v*self.theta - self.v + 1)**2
                *(self.u**2*self.theta**2 - 2*self.u**2*self.theta + self.u**2
                  - 2*self.u*self.v*self.theta**2 + 2*self.u*self.v + 2*self.u*self.theta
                  - 2*self.u + self.v**2*self.theta**2 - 2*self.v**2*self.theta + self.v**2
                  + 2*self.v*self.theta - 2*self.v + 1)**2)

    def get_numerator_double_density(self):
        return (-((2 * self.u * self.theta - 2 * self.u - self.theta + 1) *
                 (self.u ** 2 * self.theta ** 2 - 2 * self.u ** 2 * self.theta + self.u ** 2 - 2 * self.u * self.v * self.theta ** 2 + 2 * self.u * self.v + 2 * self.u * self.theta - 2 * self.u + self.v ** 2 * self.theta ** 2 - 2 * self.v ** 2 * self.theta + self.v ** 2 + 2 * self.v * self.theta - 2 * self.v + 1) + 3 * (
                              -self.u * self.theta ** 2 + self.u + self.v * self.theta ** 2 - 2 * self.v * self.theta + self.v + self.theta - 1) * (
                              -2 * self.u * self.v * self.theta + 2 * self.u * self.v + self.u * self.theta - self.u + self.v * self.theta - self.v + 1)) * (
                            2 * self.v * self.theta - 2 * self.v - self.theta + 1) * (
                            self.u ** 2 * self.theta ** 2 - 2 * self.u ** 2 * self.theta + self.u ** 2 - 2 * self.u * self.v * self.theta ** 2 + 2 * self.u * self.v + 2 * self.u * self.theta - 2 * self.u + self.v ** 2 * self.theta ** 2 - 2 * self.v ** 2 * self.theta + self.v ** 2 + 2 * self.v * self.theta - 2 * self.v + 1) + 2 * (
                            (2 * self.u * self.theta - 2 * self.u - self.theta + 1) * (
                                self.u ** 2 * self.theta ** 2 - 2 * self.u ** 2 * self.theta + self.u ** 2 - 2 * self.u * self.v * self.theta ** 2 + 2 * self.u * self.v + 2 * self.u * self.theta - 2 * self.u + self.v ** 2 * self.theta ** 2 - 2 * self.v ** 2 * self.theta + self.v ** 2 + 2 * self.v * self.theta - 2 * self.v + 1) + 3 * (
                                        -self.u * self.theta ** 2 + self.u + self.v * self.theta ** 2 - 2 * self.v * self.theta + self.v + self.theta - 1) * (
                                        -2 * self.u * self.v * self.theta + 2 * self.u * self.v + self.u * self.theta - self.u + self.v * self.theta - self.v + 1)) * (
                            self.u * self.theta ** 2 - 2 * self.u * self.theta + self.u - self.v * self.theta ** 2 + self.v + self.theta - 1) * (
                            -2 * self.u * self.v * self.theta + 2 * self.u * self.v + self.u * self.theta - self.u + self.v * self.theta - self.v + 1) + (
                            -2 * (self.theta - 1) * (
                                self.u ** 2 * self.theta ** 2 - 2 * self.u ** 2 * self.theta + self.u ** 2 - 2 * self.u * self.v * self.theta ** 2 + 2 * self.u * self.v + 2 * self.u * self.theta - 2 * self.u + self.v ** 2 * self.theta ** 2 - 2 * self.v ** 2 * self.theta + self.v ** 2 + 2 * self.v * self.theta - 2 * self.v + 1) + 3 * (
                                        self.theta ** 2 - 1) * (
                                        -2 * self.u * self.v * self.theta + 2 * self.u * self.v + self.u * self.theta - self.u + self.v * self.theta - self.v + 1) - 2 * (
                                        2 * self.u * self.theta - 2 * self.u - self.theta + 1) * (
                                        self.u * self.theta ** 2 - 2 * self.u * self.theta + self.u - self.v * self.theta ** 2 + self.v + self.theta - 1) + 3 * (
                                        2 * self.v * self.theta - 2 * self.v - self.theta + 1) * (
                                        -self.u * self.theta ** 2 + self.u + self.v * self.theta ** 2 - 2 * self.v * self.theta + self.v + self.theta - 1)) * (
                            -2 * self.u * self.v * self.theta + 2 * self.u * self.v + self.u * self.theta - self.u + self.v * self.theta - self.v + 1) * (
                            self.u ** 2 * self.theta ** 2 - 2 * self.u ** 2 * self.theta + self.u ** 2 - 2 * self.u * self.v * self.theta ** 2 + 2 * self.u * self.v + 2 * self.u * self.theta - 2 * self.u + self.v ** 2 * self.theta ** 2 - 2 * self.v ** 2 * self.theta + self.v ** 2 + 2 * self.v * self.theta - 2 * self.v + 1))


if __name__ == "__main__":
    plackett = Plackett()
    cdf = plackett.cdf()
    explicit_num = plackett.get_numerator_double_density()
    print(str(sympy.expand_mul(explicit_num)).replace("**", "^"))
    exit()
