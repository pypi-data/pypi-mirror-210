import numpy as np
import sympy
from sympy import stats

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class HueslerReiss(ExtremeValueCopula):
    lambda_ = sympy.symbols("lambda")

    def __init__(self):
        z = lambda t: 1 / self.lambda_ + self.lambda_ / 2 * sympy.ln(t / (1 - t))
        self.pickand = (1 - self.t) * stats.cdf(stats.Normal("x", 0, 1))(z(1 - self.t)) + self.t * stats.cdf(
            stats.Normal("x", 0, 1))(z(self.t))
        self.intervals = {
            self.lambda_: sympy.Interval(0, np.inf, left_open=False, right_open=True),
        }




if __name__ == '__main__':
    copul = HueslerReiss()
    sub_dict = {copul.lambda_: 0.5}
    copul.plot_pickand(sub_dict)
    exit()
