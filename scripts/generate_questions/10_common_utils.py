"""Ham tien ich dung chung cho cac script sinh bien the Mu-Logarit."""
import random

import sympy as sp


def latex(expr):
    expr = sp.sympify(expr)
    s = sp.latex(sp.nsimplify(expr))
    s = s.replace(r"\frac", r"\dfrac")
    return s


def assert_distinct(*vals):
    """Bao dam 4 phuong an A/B/C/D khong trung nhau."""
    seen = []
    for v in vals:
        for s in seen:
            if sp.simplify(v - s) == 0:
                raise ValueError(f"Trung phuong an: {v} == {s}")
        seen.append(v)


def bump_until_distinct(vals):
    """vals[0] la dap an dung, giu nguyen. Cong dan 1 vao vals[1:] neu trung
    voi bat ky gia tri nao truoc do, cho den khi tat ca phan biet."""
    vals = list(vals)
    for i in range(1, len(vals)):
        tries = 0
        while any(sp.simplify(vals[i] - vals[j]) == 0 for j in range(i)) and tries < 50:
            vals[i] = vals[i] + 1
            tries += 1
    return vals


def linear_expr_str(m, c, var="x"):
    """Chuoi latex cho m*var + c, vd '2x-1', 'x+4', '3x'."""
    m = sp.sympify(m)
    c = sp.sympify(c)
    coef = "" if m == 1 else (f"{latex(m)}" if m != -1 else "-")
    s = f"{coef}{var}" if m != 0 else ""
    if c != 0:
        sign = "+" if c > 0 else "-"
        s += f"{sign}{latex(sp.Abs(c))}"
    return s


def rrange(lo, hi, exclude=(0,), rnd=None):
    rnd = rnd or random
    while True:
        v = rnd.randint(lo, hi)
        if v not in exclude:
            return v
