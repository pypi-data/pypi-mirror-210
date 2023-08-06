import itertools

import numpy as np
import scipy
import sympy
from sympy import log, Subs, Derivative


class ExtremeValueCopula:
    _t_min = 0
    _t_max = 1
    t = sympy.symbols("t", positive=True)
    pickand = sympy.Function("A")(t)
    intervals = None

    def get_free_symbols(self):
        return self.pickand.free_symbols - {self.t}

    def sample_parameters(self, n=1):
        return {k: list(np.random.uniform(max(-10, v.start), min(10, v.end), n)) for k, v in self.intervals.items()}

    @property
    def cdf(self):
        """ Cumulative distribution function of the copula """
        u, v = sympy.symbols("u v")
        cop = (u * v) ** self.pickand.subs(self.t, sympy.ln(v) / sympy.ln(u * v))
        cop = self._get_simplified_solution(cop)
        return cop

    def compute_pdf(self):
        cdf = self.cdf
        pdf = sympy.diff(sympy.diff(cdf, "u"), "v")
        pdf = self._get_simplified_solution(pdf)
        return pdf.doit()

    @property
    def pdf(self):
        """ Probability density function of the copula """
        _xi_1, u, v = sympy.symbols("_xi_1 u v")
        pdf = (u * v) ** self.pickand.subs(self.t, log(v) / log(u * v)) * (-(
                (log(v) - log(u * v)) * Subs(Derivative(self.pickand.subs(self.t, _xi_1), _xi_1), _xi_1,
                                             log(v) / log(u * v)) - self.pickand.subs(self.t, log(v) / log(u * v)) *
                log(u * v)) * (self.pickand.subs(self.t, log(v) / log(u * v)) * log(u * v) - log(v) *
                               Subs(Derivative(self.pickand.subs(self.t, _xi_1), _xi_1), _xi_1, log(v) / log(u * v))) *
                                                                           log(u * v) + (log(v) - log(u * v)) * log(
                v) * Subs(Derivative(self.pickand.subs(self.t, _xi_1), (_xi_1, 2)), _xi_1, log(v) / log(u * v))) / (
                      u * v * log(u * v) ** 3)
        return self._get_simplified_solution(pdf)

    def is_mtp2(self):
        pdf = self.pdf
        log_pdf = sympy.simplify(sympy.ln(pdf))
        x1, x2, y1, y2 = sympy.symbols("x1 x2 y1 y2")
        log_pdf_deriv = sympy.diff(sympy.simplify(sympy.diff(log_pdf, "u")), "v")
        simplified_log_pdf_deriv = sympy.simplify(log_pdf_deriv)
        parameters = list(self.intervals.keys())
        mtp2_lambda = sympy.lambdify([x1, x2, y1, y2] + parameters, simplified_log_pdf_deriv,
                                     modules=['scipy', 'numpy', 'sympy'])
        solution, x0 = self.minimize_func_empirically(mtp2_lambda, parameters)
        mtp2_lambda(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        return solution, x0

    @property
    def spearmans_rho(self):
        integrand = (self.pickand + 1) ** (-2)  # nelsen 5.15
        integral = 12 * sympy.integrate(integrand, (self.t, 0, 1)) - 3
        return sympy.simplify(integral)

    @property
    def kendalls_tau(self):  # nelsen 5.15
        diff_pickand = sympy.simplify(sympy.diff(sympy.simplify(sympy.diff(self.pickand, self.t)), self.t))
        integrand = self.t * (1 - self.t) / self.pickand * diff_pickand
        integral = sympy.integrate(integrand, (self.t, 0, 1))
        return sympy.simplify(integral)

    def minimize_func(self, sympy_func):
        parameters = self.intervals.keys()

        def func(x):
            x1_float, x2_float, y1_float, y2_float = x[:4]
            par_dict = dict(zip(parameters, x[4:]))
            return sympy_func.subs({"x1": x1_float, "x2": x2_float, "y1": y1_float, "y2": y2_float} | par_dict).evalf()

        b = [0, 1]
        bounds = [b, b, b, b]
        parameter_bounds = [[self.intervals[par].inf, self.intervals[par].sup] for par in parameters]
        bounds += parameter_bounds
        start_parameters = [min(self.intervals[par].inf + 0.5, self.intervals[par].sup) for par in parameters]
        i = 0
        x0 = None
        while i < 4:
            x0 = np.concatenate((np.random.rand(4), start_parameters))
            try:
                solution = scipy.optimize.minimize(func, x0, bounds=bounds)
                return solution, x0
            except TypeError:
                i += 1
                print(i)
                continue
        return None, x0

    @staticmethod
    def _get_function_graph(func, par):
        return sympy.plotting.plot(func, show=False, xlim=(0, 1), ylim=(0, 1), label=par, legend=True,
                                   axis_center=(0, 0))

    def plot_pickand(self, sub_dict):
        if sub_dict is None:
            sub_dict = {}
        for key, value in sub_dict.items():
            if not isinstance(value, list):
                sub_dict[key] = [value]
        keys_to_cross_product = [key for key, value in sub_dict.items() if isinstance(value, (str, list))]
        values_to_cross_product = [value if isinstance(value, list) else [value] for value in sub_dict.values()]
        cross_product = list(itertools.product(*values_to_cross_product))
        plot_vals = [dict(zip(keys_to_cross_product, cross_product[i])) for i in range(len(cross_product))]

        plots = []
        for plot_val in plot_vals:
            pickand = self.pickand.subs(plot_val)
            p = self._get_function_graph(pickand, plot_val)
            plots.append(p)
        p1 = plots[0]
        [p1.extend(p) for p in plots[1:]]
        p1.show()
        return None

    def minimize_func_empirically(self, func, parameters):
        b = [0.01, .99]
        bounds = [b, b, b, b]
        parameter_bounds = [[max(self.intervals[par].inf, -10), min(self.intervals[par].sup, 10)] for par in parameters]
        bounds += parameter_bounds
        linspaces = [np.linspace(start=float(bound[0]), stop=float(bound[1]), num=5) for bound in bounds]
        meshgrid = np.meshgrid(*linspaces)
        func_vals = func(*meshgrid)
        return min(func_vals)

    @staticmethod
    def _get_simplified_solution(sol):
        simplified_sol = sympy.simplify(sol)
        if isinstance(simplified_sol, sympy.core.containers.Tuple):
            return simplified_sol[0]
        else:
            return simplified_sol
