import numpy as np
import sympy

from copul.families.extreme_value.extreme_value_copula import ExtremeValueCopula


class Galambos(ExtremeValueCopula):
    delta = sympy.symbols("delta")

    def __init__(self):
        self.pickand = 1 - (self.t ** (-self.delta) + (1 - self.t) ** (-self.delta)) ** (-1 / self.delta)
        self.intervals = {
            self.delta: sympy.Interval(0, np.inf, left_open=True, right_open=True),
        }


if __name__ == '__main__':
    galambos = Galambos()
    sample_params = galambos.sample_parameters(n=2)
    galambos.plot_pickand(sample_params)
    exit()
