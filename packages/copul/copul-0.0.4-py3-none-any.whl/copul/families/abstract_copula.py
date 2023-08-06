import sympy
from spb import plot3d


class AbstractCopula:
    u, v = sympy.symbols("u v", positive=True)

    def __call__(self, **kwargs):
        self._are_class_vars(kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def _are_class_vars(self, kwargs):
        class_vars = set(dir(self))
        assert set(kwargs).issubset(class_vars), f"keys: {set(kwargs)}, free symbols: {class_vars}"

    @property
    def cdf(self):
        return None

    @property
    def pdf(self):
        return sympy.simplify(sympy.diff(self.cdf, self.u, self.v))

    @property
    def log_pdf(self, expand_log=False):
        log_pdf = sympy.simplify(sympy.log(self.pdf))
        return concrete_expand_log(log_pdf) if expand_log else log_pdf

    def plot_cdf(self):
        free_symbols = set(self.cdf.func.free_symbols) - {self.u, self.v}
        free_symbol_dict = {str(s): getattr(self, str(s)) for s in free_symbols}
        cdf = self.cdf(**free_symbol_dict).func
        return plot3d(cdf, (self.u, 0, 1), (self.v, 0, 1),
                      title=f"{type(self).__name__} Copula",
                      xlabel="u", ylabel="v", zlabel="CDF", zlim=(0, 1))

    def plot_pdf(self):
        free_symbols = set(self.pdf.func.free_symbols) - {self.u, self.v}
        free_symbol_dict = {str(s): getattr(self, str(s)) for s in free_symbols}
        pdf = self.pdf(**free_symbol_dict).func
        return plot3d(pdf, (self.u, 0, 1), (self.v, 0, 1),
                      title=f"{type(self).__name__} Copula",
                      xlabel="u", ylabel="v", zlabel="PDF")


def round_expression(expr, n=2):
    expr = sympy.simplify(expr)
    for a in sympy.preorder_traversal(expr):
        if isinstance(a, sympy.Float):
            expr = expr.subs(a, round(a, n))
    return expr


def concrete_expand_log(expr, first_call=True):
    import sympy as sp
    if first_call:
        expr = sp.expand_log(expr, force=True)
    func = expr.func
    args = expr.args
    if args == ():
        return expr
    if func == sp.log and args[0].func == sp.concrete.products.Product:
        prod = args[0]
        term = prod.args[0]
        indices = prod.args[1:]
        return sp.Sum(sp.log(term), *indices)
    return func(*map(lambda x: concrete_expand_log(x, False), args))
