import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen10(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.log(2 * ac.t ** (-ac.theta) - 1)
    theta_interval = sympy.Interval(0, 1, left_open=True, right_open=False)
