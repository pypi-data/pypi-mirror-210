import numpy as np
import sympy
from scipy import optimize

from copul.families import get_simplified_solution
from copul.families.abstract_copula import AbstractCopula, concrete_expand_log
from copul.sympy_wrapper import SymPyFunctionWrapper


class ArchimedeanCopula(AbstractCopula):
    _t_min = 0
    _t_max = 1
    y, t, theta = sympy.symbols("y t theta", positive=True)
    theta_interval = None
    _inv_generator = None

    def __init__(self, theta_min=None, theta_max=None):
        if theta_min is not None:
            self.theta_interval = sympy.Interval(theta_min, self.theta_max, left_open=self.theta_interval.left_open,
                                                 right_open=self.theta_interval.right_open)
        if theta_max is not None:
            self.theta_interval = sympy.Interval(self.theta_min, theta_max, left_open=self.theta_interval.left_open,
                                                 right_open=self.theta_interval.right_open)

    @property
    def inverse_generator(self):
        return SymPyFunctionWrapper(self._inv_generator)

    @property
    def theta_max(self):
        return self.theta_interval.closure.end

    @property
    def theta_min(self):
        return self.theta_interval.closure.inf

    @property
    def cdf(self):
        """ Cumulative distribution function of the copula """
        gen = self.generator
        inv_gen_at_u = self._inv_generator.subs(self.t, self.u)
        inv_gen_at_v = self._inv_generator.subs(self.t, self.v)
        cdf = gen.subs(self.y, inv_gen_at_u + inv_gen_at_v)
        return SymPyFunctionWrapper(get_simplified_solution(cdf.func))

    @property
    def pdf(self):
        """ Probability density function of the copula """
        cdf = self.cdf
        first_diff = sympy.diff(cdf, self.u)
        pdf = sympy.diff(first_diff, self.v)
        simplified_pdf = get_simplified_solution(pdf.func)
        return SymPyFunctionWrapper(simplified_pdf)

    @property
    def generator(self) -> SymPyFunctionWrapper:
        eq = sympy.Eq(self.y, self._inv_generator)
        sol = sympy.solve([eq, self.theta > 0, self.y > 0], self.t)
        my_sol = sol[self.t] if isinstance(sol, dict) else sol[0]
        my_simplified_sol = get_simplified_solution(my_sol)
        return SymPyFunctionWrapper(my_simplified_sol)

    @property
    def first_deriv_of_generator(self):
        diff = sympy.diff(self.generator.func, self.y)
        return sympy.simplify(diff)

    @property
    def second_deriv_of_gen(self):
        first_diff = self.first_deriv_of_generator
        second_diff = sympy.diff(first_diff, self.y)
        return sympy.simplify(second_diff)

    @property
    def ci_char(self):
        minus_gen_deriv = - self.first_deriv_of_generator
        beauty_deriv = concrete_expand_log(sympy.simplify(sympy.log(minus_gen_deriv)))
        return SymPyFunctionWrapper(beauty_deriv)

    @property
    def first_deriv_of_ci_char(self):
        chi_char_func = self.ci_char()
        return sympy.simplify(sympy.diff(chi_char_func, self.y))

    @property
    def second_deriv_of_ci_char(self):
        chi_char_func_deriv = self.first_deriv_of_ci_char()
        return sympy.simplify(sympy.diff(chi_char_func_deriv, self.y))

    @property
    def mtp2_char(self):
        second_deriv = self.second_deriv_of_gen
        beauty_2deriv = concrete_expand_log(sympy.simplify(sympy.log(second_deriv)))
        return SymPyFunctionWrapper(beauty_2deriv)

    @property
    def first_deriv_of_mtp2_char(self):
        mtp2_char = self.mtp2_char()
        return sympy.simplify(sympy.diff(mtp2_char, self.y))

    @property
    def second_deriv_of_mtp2_char(self):
        mtp2_char_deriv = self.first_deriv_of_mtp2_char()
        return sympy.simplify(sympy.diff(mtp2_char_deriv, self.y))

    @property
    def log_der(self):
        minus_log_derivative = self.ci_char()
        first_deriv = self.first_deriv_of_ci_char()
        second_deriv = self.second_deriv_of_ci_char()
        return self._compute_log2_der_of(first_deriv, minus_log_derivative, second_deriv)

    @property
    def log2_der(self):
        log_second_derivative = self.mtp2_char()
        first_deriv = self.first_deriv_of_mtp2_char()
        second_deriv = self.second_deriv_of_mtp2_char()
        return self._compute_log2_der_of(first_deriv, log_second_derivative, second_deriv)

    def _compute_log2_der_of(self, first_deriv, log_second_derivative, second_deriv):
        log_der_lambda = sympy.lambdify([(self.y, self.theta)], second_deriv)
        bounds = [(self._t_min, self._t_max), (self.theta_min, self.theta_max)]
        starting_point = np.array([min(self._t_min + 0.5, self._t_max), min(self.theta_min + 0.5, self.theta_max)])
        min_val = optimize.minimize(log_der_lambda, starting_point, bounds=bounds)
        return log_second_derivative, first_deriv, second_deriv, [round(val, 2) for val in min_val.x], round(
            log_der_lambda(min_val.x), 2)

    def compute_inv_gen_max(self):
        try:
            limit = sympy.limit(self._inv_generator, self.t, 0)
        except TypeError:
            limit = sympy.limit(self._inv_generator.subs(self.theta, (self.theta_max - self.theta_min) / 2), self.t, 0)
        return sympy.simplify(limit)
