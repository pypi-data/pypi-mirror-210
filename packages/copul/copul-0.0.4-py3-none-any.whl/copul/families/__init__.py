import sympy


def get_simplified_solution(sol):
    try:
        simplified_sol = sympy.simplify(sol)
    except TypeError:
        return sol
    if isinstance(simplified_sol, sympy.core.containers.Tuple):
        return simplified_sol[0]
    else:
        return simplified_sol
