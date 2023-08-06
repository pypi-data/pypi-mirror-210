import numpy as np
import sympy

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class BB5(ExtremeValueCopula):
    theta, delta = sympy.symbols("theta delta")

    def __init__(self):
        def pickand(t, th, d):
            return (t ** th + (1 - t) ** th - ((1 - t) ** (-th * d) + t ** (-th * d)) ** (-1 / d)) ** (1 / th)

        self.pickand = pickand(self.t, self.theta, self.delta)
        self.intervals = {
            self.theta: sympy.Interval(1, np.inf, left_open=False, right_open=True),
            self.delta: sympy.Interval(0, np.inf, left_open=True, right_open=True),
        }
