import re

import pandas as pd
import sympy

from copul.families.abstract_copula import round_expression

from copul.families.archimedean.nelsen1 import Nelsen1, Clayton
from copul.families.archimedean.nelsen2 import Nelsen2
from copul.families.archimedean.nelsen3 import Nelsen3, AliMikhailHak
from copul.families.archimedean.nelsen4 import Nelsen4, GumbellHougaard
from copul.families.archimedean.nelsen5 import Nelsen5, Frank
from copul.families.archimedean.nelsen6 import Nelsen6, Joe
from copul.families.archimedean.nelsen7 import Nelsen7
from copul.families.archimedean.nelsen8 import Nelsen8
from copul.families.archimedean.nelsen9 import Nelsen9, GumbellBarnett
from copul.families.archimedean.nelsen10 import Nelsen10
from copul.families.archimedean.nelsen11 import Nelsen11
from copul.families.archimedean.nelsen12 import Nelsen12
from copul.families.archimedean.nelsen13 import Nelsen13
from copul.families.archimedean.nelsen14 import Nelsen14
from copul.families.archimedean.nelsen15 import Nelsen15, GenestGhoudi
from copul.families.archimedean.nelsen16 import Nelsen16
from copul.families.archimedean.nelsen17 import Nelsen17
from copul.families.archimedean.nelsen18 import Nelsen18
from copul.families.archimedean.nelsen19 import Nelsen19
from copul.families.archimedean.nelsen20 import Nelsen20
from copul.families.archimedean.nelsen21 import Nelsen21
from copul.families.archimedean.nelsen22 import Nelsen22


def cleanse_latex_str(latex_str):
    def cleanse_this(input_str):
        new_str = re.sub("\{(\\d)\}", "\\1", input_str)
        output_str = re.sub("\^\{(.)\}", "^\\1", new_str)
        return output_str

    if isinstance(latex_str, pd.Series):
        return latex_str.apply(lambda val: cleanse_this(val))
    return cleanse_this(latex_str)


def generate_notes_pdf(my_range):
    cop = "C(u, v)"
    gen = "$\\psi(y)$"
    inv_gen = "$\\psi^{-1}(t)$"
    inv_gen_max = "$\\psi^{-1}(0)$"
    gen_der = "$\\psi'(y)$"
    mustbeconv = "$\\log(-\\psi')(y)$"
    log_der = "$(\\log(-\\psi'))'(y)$"
    log_der2 = "$(\\log(-\\psi'))''(y)$"
    gen_der2 = "$\\psi''(y)$"
    mustbeconv2 = "$\\log(\\psi'')(y)$"
    log2_der = "$(\\log(\\psi''))'(y)$"
    log2_der2 = "$(\\log(\\psi''))''(y)$"
    my_copula = Nelsen17(theta_min=0)
    # conv_func, log_der_val, log_der2_val, local_min_point, local_min_val = my_copula.log2_der()
    df = pd.DataFrame(index=my_range)
    for i in my_range:
        copula_str = f"Nelsen{str(i)}"
        print(copula_str)
        copula = locals()[copula_str](theta_min=0)
        gen_val = copula.generator
        gen_der_val = copula.first_deriv_of_generator
        gen_der2_val = copula.second_deriv_of_gen
        cop_val = copula.cdf
        conv_func, log_der_val, log_der2_val, local_min_point, local_min_val = copula.log_der()
        conv2_func, log2_deriv_val, log2_deriv2_val, local2_min_point, local2_min_val = copula.log2_der()
        df.loc[i, cop] = "$" + sympy.latex(cop_val) + "$"
        df.loc[i, "$\\theta$"] = str(copula.theta_interval)
        df.loc[i, inv_gen] = "$" + sympy.latex(copula.inverse_generator) + "$"
        df.loc[i, inv_gen_max] = str(copula.compute_inv_gen_max())
        df.loc[i, gen] = "$" + sympy.latex(gen_val) + "$"
        df.loc[i, gen_der] = "$" + sympy.latex(gen_der_val) + "$"
        df.loc[i, mustbeconv] = "$" + sympy.latex(conv_func) + "$"
        df.loc[i, log_der] = "$" + sympy.latex(log_der_val) + "$"
        df.loc[i, log_der2] = "$" + sympy.latex(log_der2_val) + "$"
        df.loc[i, f"{log_der2}-min"] = "$" + sympy.latex((local_min_point, local_min_val)) + "$"
        df.loc[i, gen_der2] = "$" + sympy.latex(gen_der2_val) + "$"
        df.loc[i, mustbeconv2] = "$" + sympy.latex(conv2_func) + "$"
        df.loc[i, log2_der] = "$" + sympy.latex(log2_deriv_val) + "$"
        df.loc[i, log2_der2] = "$" + sympy.latex(log2_deriv2_val) + "$"
        df.loc[i, f"{log2_der2}-min"] = (
                "$" + sympy.latex((local2_min_point, local2_min_val)) + "$"
        )
    return df


if __name__ == "__main__":
    cop = Nelsen17()
    gen = cop.generator.subs(cop.theta, 5.5)
    diff2 = round_expression(sympy.diff(gen, cop.y, 2))
    diff3 = round_expression(sympy.diff(gen, cop.y, 3))
    diff4 = round_expression(sympy.diff(gen, cop.y, 4))
    diff5 = round_expression(sympy.diff(gen, cop.y, 5))
    diff6 = round_expression(sympy.diff(gen, cop.y, 6))
    diff7 = round_expression(sympy.diff(gen, cop.y, 7))
    my_gen_plot = sympy.plotting.plot(diff2, (cop.y, 5, 20), show=False, legend=True)
    my_gen_plot.show()
    cdf = cop.cdf().subs(cop.theta, 0.5)
    my_range = list(range(16, 17))
    df = generate_notes_pdf(my_range)
    pd.set_option('display.max_colwidth', None)
    tables = {"Nelsen" + str(i): df.T[[i]].reset_index().rename(columns={i: "Value", "index": "Characteristic"}) for i
              in my_range}
    table_strs = [cleanse_latex_str(v.to_latex(escape=False)) + "\\caption{" + k + "}\\label{tab:" + k + "}" for k, v in
                  tables.items()]


    def table_to_formula(k, v):
        v = v.drop(v.index[[0, 1, 2, 3, 9, 14]])
        return "\item " + k + ": \n\\begin{align}\n" + (v["Characteristic"] + " ~=~ & " + cleanse_latex_str(
            v["Value"]) + ", \\nonumber\\\\").str.replace("$", "").str.cat(
            sep="\n")[:-13] + "\\nonumber" + ".\n\\end{align}\n"

    table_strs2 = {k: table_to_formula(k, v) for k, v in tables.items()}
    start_str = "\\begin{table}[H]\\begin{center}"
    end_str = "\\end{center}\\end{table}"
    full_table = "\n\n".join([start_str + tab + end_str for tab in table_strs])
    full_table2 = "\\begin{itemize}\n" + "\n\n".join([table_strs2[tab] for tab in table_strs2]) + "\\end{itemize}"
    exit()
