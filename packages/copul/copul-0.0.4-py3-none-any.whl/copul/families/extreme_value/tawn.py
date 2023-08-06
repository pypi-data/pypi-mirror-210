import numpy as np
import sympy

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class Tawn(ExtremeValueCopula):
    psi1, psi2, theta = sympy.symbols("psi1 psi2 theta")

    def __init__(self):
        self.pickand = (1 - self.psi1) * (1 - self.t) + (1 - self.psi2) * self.t \
                       + ((self.psi1 * (1 - self.t)) ** self.theta + (self.psi2 * self.t) ** self.theta) ** (
                               1 / self.theta)
        self.intervals = {
            self.psi1: sympy.Interval(0, 1, left_open=False, right_open=False),
            self.psi2: sympy.Interval(0, 1, left_open=False, right_open=False),
            self.theta: sympy.Interval(1, np.inf, left_open=False, right_open=True),
        }
