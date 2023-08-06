import numpy as np
import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen17(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = -sympy.log(((1 + ac.t) ** (-ac.theta) - 1) / (2 ** (-ac.theta) - 1))
    theta_interval = sympy.Interval(-np.inf, np.inf, left_open=False, right_open=True)

    @property
    def first_deriv_of_generator(self):
        return sympy.simplify(
            (
                2**self.theta
                * sympy.exp(self.y)
                / (2**self.theta * sympy.exp(self.y) - 2**self.theta + 1)
            )
            ** (1 / self.theta)
            * (2**self.theta * (-(2**self.theta) + 1))
            / (
                2**self.theta
                * self.theta
                * (2**self.theta * sympy.exp(self.y) - 2**self.theta + 1)
            )
        )

    @property
    def second_deriv_of_gen(self):
        return sympy.simplify(
            (
                2**self.theta
                * sympy.exp(self.y)
                / (2**self.theta * sympy.exp(self.y) - 2**self.theta + 1)
            )
            ** (1 / self.theta)
            * (
                2**self.theta * self.theta * (-(2**self.theta) + 1) * sympy.exp(self.y)
                - 2 ** (self.theta + 1) * self.theta * (-(2**self.theta) + 1) * sympy.exp(self.y)
                + (2**self.theta - 1) ** 2
            )
            / (self.theta**2 * (2**self.theta * sympy.exp(self.y) - 2**self.theta + 1) ** 2)
        )

    @property
    def first_deriv_of_ci_char(self):
        return sympy.simplify(
            (
                2**self.theta * (-(2**self.theta) + 1)
                - 4**self.theta * self.theta * sympy.exp(self.y)
            )
            / (
                2**self.theta
                * self.theta
                * (2**self.theta * sympy.exp(self.y) - 2**self.theta + 1)
            )
        )

    def first_deriv_of_mtp2_char(self):
        return 1 / self.theta + 2**self.theta * sympy.exp(self.y) * (
            1 / (2**self.theta * sympy.exp(self.y) - 2**self.theta + 1)
            + self.theta / (2**self.theta * self.theta * sympy.exp(self.y) + 2**self.theta + 1)
            - 1
            / (
                2**self.theta * self.theta * sympy.exp(self.y)
                - 2**self.theta * self.theta
                + self.theta
            )
        )
