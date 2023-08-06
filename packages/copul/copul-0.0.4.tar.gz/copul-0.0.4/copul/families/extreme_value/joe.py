import numpy as np
import sympy

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class Joe(ExtremeValueCopula):
    psi1, psi2, delta = sympy.symbols("psi1 psi2 delta")

    def __init__(self):
        self.pickand = 1 - ((self.psi1 * (1 - self.t)) ** (-self.delta) + (self.psi2 * self.t) ** (-self.delta)) ** (
                -1 / self.delta)
        self.intervals = {
            self.psi1: sympy.Interval(0, 1, left_open=False, right_open=False),
            self.psi2: sympy.Interval(0, 1, left_open=False, right_open=False),
            self.delta: sympy.Interval(0, np.inf, left_open=True, right_open=True),
        }


if __name__ == '__main__':
    copul = Joe()
    sub_dict = {copul.delta: [0.1, 0.5, 1, 5, 100], copul.psi1: [0.2, 0.8], copul.psi2: 1}
    copul.plot_pickand(sub_dict)
    exit()
