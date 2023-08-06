import sympy


class SymPyFunctionWrapper:
    def __init__(self, sympy_func):
        allowed = (
            sympy.Pow,
            sympy.Mul,
            sympy.Add,
            sympy.Max,
            sympy.log,
            sympy.exp,
            sympy.core.numbers.Zero,
        )
        assert isinstance(
            sympy_func, allowed
        ), f"Function must be from sympy, but is {type(sympy_func)}"
        self._func = sympy_func

    def __str__(self):
        return str(self._func)

    def __repr__(self):
        return repr(self._func)

    def __call__(self, **kwargs):
        free_symbols = {str(f) for f in self._func.free_symbols}
        assert set(kwargs).issubset(
            free_symbols
        ), f"keys: {set(kwargs)}, free symbols: {self._func.free_symbols}"
        vars_ = {f: kwargs[str(f)] for f in self._func.free_symbols if str(f) in kwargs}
        self._func = self._func.subs(vars_)
        return self

    @property
    def func(self):
        return self._func

    def subs(self, *args, **kwargs):
        self._func = self._func.subs(*args, **kwargs)
        return self

    def diff(self, *args, **kwargs):
        self._func = self._func.diff(*args, **kwargs)
        return self
