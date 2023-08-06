import numpy as np
import sympy

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class Gumbel(ExtremeValueCopula):
    theta = sympy.symbols("theta")

    def __init__(self):
        self.pickand = (self.t ** self.theta + (1 - self.t) ** self.theta) ** (1 / self.theta)
        self.intervals = {
            self.theta: sympy.Interval(1, np.inf, left_open=False, right_open=True),
        }
