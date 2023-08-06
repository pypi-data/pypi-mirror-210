import sympy

from copul.families.archimedean.archimedean_copula import ArchimedeanCopula


class Nelsen11(ArchimedeanCopula):
    ac = ArchimedeanCopula
    _inv_generator = sympy.log(2 - ac.t ** ac.theta)
    theta_interval = sympy.Interval(0, 0.5, left_open=True, right_open=False)
