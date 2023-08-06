import sympy

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class MarshallOlkin(ExtremeValueCopula):
    alpha1, alpha2 = sympy.symbols("alpha1 alpha2")

    def __init__(self):
        self.pickand = sympy.Max(1 - self.alpha1 * (1 - self.t), 1 - self.alpha2 * (1 - self.t))
        self.intervals = {
            self.alpha1: sympy.Interval(0, 1, left_open=False, right_open=False),
            self.alpha2: sympy.Interval(0, 1, left_open=False, right_open=False),
        }
