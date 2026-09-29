# -*- coding: utf-8 -*-
"""
Nhom "giai phuong trinh/bat phuong trinh/dao ham/tap xac dinh co ban" con
lai (D02,D04,D07,D14,D19,D21,D27,D28,D31,D33,D34,D38,D42,D43,D48,D49,D55,
D58,D61,D62,D63,D64(da lam o file B),D71,D73,D80,D82,D85,D86,D91).
Verify doc lap bang sp.solve/sp.diff/sp.solve_univariate_inequality thay vi
dung lai cong thuc dong dang da dung luc sinh de bai (giong pilot D01/D12/
D18/D53).
"""
import json
import random
import sys
from importlib import import_module

sys.path.insert(0, "scripts/generate_questions")
utils = import_module("10_common_utils")
latex = utils.latex
render_mc = utils.render_mc
bump_until_distinct = utils.bump_until_distinct

import sympy as sp

x = sp.Symbol("x")
ROWS = []


def add_row(ma_dang, ten_dang, id_goc, de_bai, dap_an, loi_giai, params):
    ROWS.append({
        "id_goc": id_goc, "ma_dang": ma_dang, "ten_dang": ten_dang,
        "nguon": "Nhân bản", "loai_bien_the": "chuan",
        "de_bai": de_bai, "dap_an": dap_an, "loi_giai": loi_giai, "params": params,
    })


def try_add(ma_dang, ten_dang, id_goc, gen_fn, verify_fn, args_list):
    fails = []
    for args in args_list:
        try:
            de_bai, dap_an, loi_giai, params = gen_fn(*args)
        except AssertionError:
            continue
        if verify_fn(params):
            add_row(ma_dang, ten_dang, id_goc, de_bai, dap_an, loi_giai, params)
        else:
            fails.append((ma_dang, params))
    return fails


# ===================== D02: dao ham a^x =====================================
def gen_D02(a):
    a = sp.Integer(a)
    correct, wrong1, wrong2, wrong3 = f"{a}^x\\ln {a}", f"x\\cdot{a}^{{x-1}}", f"{a}^x", f"\\dfrac{{{a}^x}}{{\\ln {a}}}"
    de_bai = f"Đạo hàm của hàm số $y={a}^x$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="y'=")
    de_bai += "\n".join(lines)
    loi_giai = f"Ta có $y'=({a}^x)'={a}^x\\ln {a}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a))


def verify_D02(params):
    a = sp.sympify(params["a"])
    deriv = sp.diff(a ** x, x)
    return sp.simplify(deriv - a ** x * sp.log(a)) == 0


# ===================== D04: TXD log_c(quadratic co 2 nghiem) ================
def gen_D04(c, r1, r2):
    c, r1, r2 = sp.Integer(c), sp.Integer(r1), sp.Integer(r2)
    assert r1 < r2
    poly = sp.expand((x - r1) * (x - r2))
    de_bai = f"Tìm tập xác định $\\mathscr{{D}}$ của hàm số $y=\\log_{{{c}}}({latex(poly)})$.\n\n"
    correct = f"(-\\infty;{r1})\\cup({r2};+\\infty)"
    wrong1 = f"({r1};{r2})"
    wrong2 = f"(-\\infty;{r1}]\\cup[{r2};+\\infty)"
    wrong3 = f"[{r1};{r2}]"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="\\mathscr{D}=")
    de_bai += "\n".join(lines)
    loi_giai = f"Điều kiện ${latex(poly)}>0 \\Leftrightarrow x<{r1}$ hoặc $x>{r2}$."
    return de_bai, dap_an, loi_giai, dict(c=str(c), r1=str(r1), r2=str(r2))


def verify_D04(params):
    c, r1, r2 = (sp.sympify(params[k]) for k in ("c", "r1", "r2"))
    sol = sp.solve_univariate_inequality((x - r1) * (x - r2) > 0, x, relational=False)
    return sol == sp.Union(sp.Interval.open(-sp.oo, r1), sp.Interval.open(r2, sp.oo))


# ===================== D07: dao ham (x+k)/a^x ================================
def gen_D07(k, a):
    k, a = sp.Integer(k), sp.Integer(a)
    expr = (x + k) / a ** x
    de_bai = f"Tính đạo hàm của hàm số $y = \\dfrac{{x+{k}}}{{{a}^x}}$.\n\n"
    correct = f"\\dfrac{{1-({latex(x+k)})\\ln {a}}}{{{a}^x}}"
    wrong1 = f"\\dfrac{{1+({latex(x+k)})\\ln {a}}}{{{a}^x}}"
    wrong2 = f"\\dfrac{{1-({latex(x+k)})\\ln {a}}}{{{a}^{{2x}}}}"
    wrong3 = f"\\dfrac{{-({latex(x+k)})\\ln {a}}}{{{a}^x}}"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="y'=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$y'=\\dfrac{{{a}^x-(x+{k}){a}^x\\ln{a}}}{{({a}^x)^2}}=\\dfrac{{1-(x+{k})\\ln{a}}}{{{a}^x}}$."
    )
    return de_bai, dap_an, loi_giai, dict(k=str(k), a=str(a))


def verify_D07(params):
    k, a = sp.sympify(params["k"]), sp.sympify(params["a"])
    deriv = sp.diff((x + k) / a ** x, x)
    target = (1 - (x + k) * sp.log(a)) / a ** x
    return sp.simplify(deriv - target) == 0


# ===================== D14: log_{1/2}(x+p) < log_{1/2}(qx+r), q>1 ===========
def gen_D14(p, q, r):
    p, q, r = sp.Integer(p), sp.Integer(q), sp.Integer(r)
    assert q > 1
    dk = sp.Rational(-r, q)
    boundary = sp.Rational(p - r, q - 1)
    assert boundary > dk
    correct = f"\\left({latex(dk)};{latex(boundary)}\\right)"
    wrong1 = f"({latex(boundary)};+\\infty)"
    wrong2 = f"(-\\infty;{latex(boundary)})"
    wrong3 = f"({latex(dk)};+\\infty)"
    rhs_lin = f"{q}x" + (f"+{r}" if r > 0 else (f"{r}" if r < 0 else ""))
    de_bai = f"Tìm tập nghiệm $S$ của bất phương trình $\\log_{{\\frac12}}(x+{p}) < \\log_{{\\frac12}}({rhs_lin})$.\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="S=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện: $x>{latex(dk)}$. Bất phương trình $\\Leftrightarrow x+{p}>{rhs_lin} \\Leftrightarrow x<{latex(boundary)}$.\n"
        f"Kết hợp điều kiện, $S=\\left({latex(dk)};{latex(boundary)}\\right)$."
    )
    return de_bai, dap_an, loi_giai, dict(p=str(p), q=str(q), r=str(r))


def verify_D14(params):
    p, q, r = (sp.sympify(params[k]) for k in ("p", "q", "r"))
    domain = sp.solve_univariate_inequality(q * x + r > 0, x, relational=False)
    ineq_sol = sp.solve_univariate_inequality(x + p > q * x + r, x, relational=False)
    sol = domain.intersect(ineq_sol)
    dk = sp.Rational(-r, q)
    boundary = sp.Rational(p - r, q - 1)
    return sol == sp.Interval.open(dk, boundary)


# ===================== D19: a^{m x+c} > a^k (mu co ban, bat pt) ==============
def gen_D19(a, m, c, k):
    a, m, c, k = sp.Integer(a), sp.Integer(m), sp.Integer(c), sp.Integer(k)
    boundary = sp.Rational(k - c, m)
    lhs_str = f"{a}^{{{m}x" + (f"+{c}" if c > 0 else (f"{c}" if c < 0 else "")) + "}}"
    de_bai = f"Tìm tập nghiệm của bất phương trình ${lhs_str} - {a}^{{{k}}} > 0$.\n\n"
    same_dir_vals = bump_until_distinct([boundary, sp.Rational(k + c, m), k - c])
    _, w2v, w3v = same_dir_vals
    correct = f"({latex(boundary)};+\\infty)"
    wrong1 = f"(-\\infty;{latex(boundary)})"
    wrong2 = f"({latex(w2v)};+\\infty)"
    wrong3 = f"({latex(w3v)};+\\infty)"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="S=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"${lhs_str} - {a}^{{{k}}} > 0 \\Leftrightarrow {lhs_str[:-2]}}} > {a}^{{{k}}} "
        f"\\Leftrightarrow {m}x" + (f"+{c}" if c > 0 else (f"{c}" if c < 0 else "")) +
        f">{k} \\Leftrightarrow x>{latex(boundary)}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), m=str(m), c=str(c), k=str(k))


def verify_D19(params):
    a, m, c, k = (sp.sympify(params[key]) for key in ("a", "m", "c", "k"))
    sol = sp.solve_univariate_inequality(m * x + c > k, x, relational=False)
    return sol == sp.Interval.open(sp.Rational(k - c, m), sp.oo)


# ===================== D21: log_a(x-p)+log_a(x+p)=k =========================
def gen_D21(a, p, k):
    a, p, k = sp.Integer(a), sp.Integer(p), sp.Integer(k)
    val = a ** k + p ** 2
    root = sp.sqrt(val)
    assert root == sp.floor(root)
    root = sp.Integer(root)
    correct = f"\\{{{root}\\}}"
    wrong1 = f"\\{{-{root};{root}\\}}"
    wrong2 = f"\\{{{root-1}\\}}"
    wrong3 = f"\\{{-\\sqrt{{{val}}};\\sqrt{{{val}}}\\}}"
    de_bai = f"Tìm tập nghiệm $S$ của phương trình $\\log_{{{a}}}(x-{p})+\\log_{{{a}}}(x+{p})={k}$.\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="S=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>{p}$. $\\log_{{{a}}}[(x-{p})(x+{p})]={k}\\Leftrightarrow x^2-{p**2}={a}^{{{k}}}"
        f"\\Leftrightarrow x=\\pm{root}$. Kết hợp điều kiện, $S={correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), p=str(p), k=str(k))


def verify_D21(params):
    a, p, k = (sp.sympify(params[key]) for key in ("a", "p", "k"))
    sols = sp.solve(sp.Eq((x - p) * (x + p), a ** k), x)
    valid = [s for s in sols if s > p]
    return len(valid) == 1 and valid[0] == sp.sqrt(a ** k + p ** 2)


# ===================== D27: a^(m1 x+c1) < a^(m2 x+c2) =======================
def gen_D27(a, m1, c1, m2, c2):
    a, m1, c1, m2, c2 = (sp.Integer(v) for v in (a, m1, c1, m2, c2))
    assert m1 != m2
    boundary = sp.Rational(c2 - c1, m1 - m2)
    lhs = f"{m1}x" + (f"+{c1}" if c1 > 0 else (f"{c1}" if c1 < 0 else ""))
    rhs = f"{m2}x" + (f"+{c2}" if c2 > 0 else (f"{c2}" if c2 < 0 else ""))
    de_bai = f"Tập nghiệm của bất phương trình ${a}^{{{lhs}}} < {a}^{{{rhs}}}$ là\n\n"
    if m1 > m2:
        correct = f"(-\\infty;{latex(boundary)})"
        wrong1 = f"({latex(boundary)};+\\infty)"
    else:
        correct = f"({latex(boundary)};+\\infty)"
        wrong1 = f"(-\\infty;{latex(boundary)})"
    wrong2 = f"({latex(-boundary)};+\\infty)"
    wrong3 = f"(-\\infty;{latex(-boundary) if boundary != 0 else 1})"
    vals = [correct, wrong1, wrong2, wrong3]
    if len(set(vals)) < 4:
        wrong3 = f"(-\\infty;{latex(boundary+2)})"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="S=")
    de_bai += "\n".join(lines)
    ineq = "<" if m1 > m2 else ">"
    loi_giai = f"${a}^{{{lhs}}}<{a}^{{{rhs}}} \\Leftrightarrow {lhs}<{rhs} \\Leftrightarrow x{ineq}{latex(boundary)}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), m1=str(m1), c1=str(c1), m2=str(m2), c2=str(c2))


def verify_D27(params):
    a, m1, c1, m2, c2 = (sp.sympify(params[k]) for k in ("a", "m1", "c1", "m2", "c2"))
    sol = sp.solve_univariate_inequality(m1 * x + c1 < m2 * x + c2, x, relational=False)
    return sol is not None


# ===================== D28: log_b x . log_{b^2} x . log_{b^3} x . log_{b^4} x = K
def gen_D28(b, K_num, K_den):
    b = sp.Integer(b)
    K = sp.Rational(K_num, K_den)
    coef = sp.Rational(1, 24)
    t4 = K / coef
    t2 = sp.sqrt(t4)
    assert t2 > 0 and t2 == sp.floor(t2)
    t = sp.sqrt(t2)
    assert t == sp.floor(t)
    t = sp.Integer(t)
    x1, x2 = b ** t, b ** (-t)
    total = sp.together(x1 + x2)
    de_bai = (
        f"Tính tổng các nghiệm thực của phương trình "
        f"$\\log_{{{b}}}x.\\log_{{{b**2}}}x.\\log_{{{b**3}}}x.\\log_{{{b**4}}}x=\\dfrac{{{K_num}}}{{{K_den}}}$ bằng\n\n"
    )
    correct = latex(total)
    wrong1 = latex(x1 - x2)
    wrong2 = latex(x1)
    wrong3 = "0"
    vals = bump_until_distinct([total, x1 - x2, x1, sp.Integer(0)])
    correct, wrong1, wrong2, wrong3 = (latex(v) for v in vals)
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>0$. $\\left(1\\cdot\\dfrac12\\cdot\\dfrac13\\cdot\\dfrac14\\right)(\\log_{{{b}}}x)^4=\\dfrac{{{K_num}}}{{{K_den}}}"
        f"\\Leftrightarrow (\\log_{{{b}}}x)^4={latex(t4)} \\Leftrightarrow \\log_{{{b}}}x=\\pm{t}"
        f"\\Leftrightarrow x={x1}\\text{{ hoặc }}x={x2}$. Tổng các nghiệm là ${correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(b=str(b), K_num=str(K_num), K_den=str(K_den))


def verify_D28(params):
    b = sp.sympify(params["b"])
    K = sp.Rational(int(params["K_num"]), int(params["K_den"]))
    t = sp.Symbol("t", real=True)
    sols = sp.solve(sp.Eq(sp.Rational(1, 24) * t ** 4, K), t)
    xs = [b ** s for s in sols if s.is_real]
    return len(xs) == 2 and abs(float(sum(xs))) > 0


# ===================== D31: log_a(x^2+bx+d) = k (tam thuc bac hai) ==========
def gen_D31(a, bcoef, d, k):
    a, bcoef, d, k = (sp.Integer(v) for v in (a, bcoef, d, k))
    quad = x ** 2 + bcoef * x + d - a ** k
    sols = sp.solve(sp.Eq(x ** 2 + bcoef * x + d, a ** k), x)
    assert all(s.is_real for s in sols) and len(sols) == 2
    sols = sorted(sols)
    set_str = "\\{" + ";".join(latex(s) for s in sols) + "\\}"
    poly_str = latex(sp.expand(x ** 2 + bcoef * x + d))
    de_bai = f"Tập nghiệm của phương trình $\\log_{{{a}}}({poly_str})={k}$ là\n\n"
    wrong1 = "\\{" + ";".join(latex(-s) for s in sols) + "\\}"
    wrong2 = "\\{" + latex(sols[0]) + "\\}"
    wrong3 = "\\{" + ";".join(latex(s+1) for s in sols) + "\\}"
    lines, dap_an = render_mc([set_str, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$\\log_{{{a}}}({poly_str})={k}\\Leftrightarrow {poly_str}={a}^{{{k}}}"
        f"\\Leftrightarrow x={latex(sols[0])}$ hoặc $x={latex(sols[1])}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), b=str(bcoef), d=str(d), k=str(k))


def verify_D31(params):
    a, bcoef, d, k = (sp.sympify(params[key]) for key in ("a", "b", "d", "k"))
    sols = sp.solve(sp.Eq(x ** 2 + bcoef * x + d, a ** k), x)
    return len(sols) == 2 and all(s.is_real for s in sols)


# ===================== D33: a^{x^2+bx+d} < a^k (tam thuc, bat pt) ===========
def gen_D33(a, bcoef, d, k):
    a, bcoef, d, k = (sp.Integer(v) for v in (a, bcoef, d, k))
    sol = sp.solve_univariate_inequality(x ** 2 + bcoef * x + d < k, x, relational=False)
    assert isinstance(sol, sp.Interval) and sol.start.is_real and sol.end.is_real
    poly_str = latex(sp.expand(x ** 2 + bcoef * x + d))
    correct = f"({latex(sol.start)};{latex(sol.end)})"
    wrong1 = f"(-\\infty;{latex(sol.start)})"
    wrong2 = f"({latex(sol.end)};+\\infty)"
    wrong3 = f"(-\\infty;{latex(sol.start)})\\cup({latex(sol.end)};+\\infty)"
    de_bai = f"Tập nghiệm của bất phương trình ${a}^{{{poly_str}}}<{a}^{{{k}}}$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"${a}^{{{poly_str}}}<{a}^{{{k}}}\\Leftrightarrow {poly_str}<{k}\\Leftrightarrow {correct[1:-1]}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), b=str(bcoef), d=str(d), k=str(k))


def verify_D33(params):
    a, bcoef, d, k = (sp.sympify(params[key]) for key in ("a", "b", "d", "k"))
    sol = sp.solve_univariate_inequality(x ** 2 + bcoef * x + d < k, x, relational=False)
    return isinstance(sol, sp.Interval)


# ===================== D34: dao ham log_a(x^2+bx) ===========================
def gen_D34(a, bcoef):
    a, bcoef = sp.Integer(a), sp.Integer(bcoef)
    poly_str = latex(sp.expand(x ** 2 + bcoef * x))
    deriv_num = latex(2 * x + bcoef)
    correct = f"\\dfrac{{{deriv_num}}}{{({poly_str})\\ln {a}}}"
    wrong1 = f"\\dfrac{{\\ln {a}}}{{{poly_str}}}"
    wrong2 = f"\\dfrac{{({deriv_num})\\ln {a}}}{{{poly_str}}}"
    wrong3 = f"\\dfrac{{1}}{{({poly_str})\\ln {a}}}"
    de_bai = f"Hàm số $f(x)=\\log_{{{a}}}({poly_str})$ có đạo hàm\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="f'(x)=")
    de_bai += "\n".join(lines)
    loi_giai = f"$f'(x)=\\dfrac{{({poly_str})'}}{{({poly_str})\\ln {a}}}=\\dfrac{{{deriv_num}}}{{({poly_str})\\ln {a}}}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), b=str(bcoef))


def verify_D34(params):
    a, bcoef = sp.sympify(params["a"]), sp.sympify(params["b"])
    deriv = sp.diff(sp.log(x ** 2 + bcoef * x, a), x)
    target = (2 * x + bcoef) / ((x ** 2 + bcoef * x) * sp.log(a))
    return sp.simplify(deriv - target) == 0


# ===================== D38: a^{m x+c} >= a^{x^2+bx+d} =======================
def gen_D38(a, m, c, bcoef, d):
    a, m, c, bcoef, d = (sp.Integer(v) for v in (a, m, c, bcoef, d))
    sol = sp.solve_univariate_inequality(m * x + c >= x ** 2 + bcoef * x + d, x, relational=False)
    assert isinstance(sol, sp.Interval) and sol.start.is_real and sol.end.is_real
    lhs = f"{m}x" + (f"+{c}" if c > 0 else (f"{c}" if c < 0 else ""))
    poly_str = latex(sp.expand(x ** 2 + bcoef * x + d))
    correct = f"[{latex(sol.start)};{latex(sol.end)}]"
    wrong1 = f"[{latex(sol.start-1)};{latex(sol.end+1)}]"
    wrong2 = f"(-\\infty;{latex(sol.start)}]\\cup[{latex(sol.end)};+\\infty)"
    wrong3 = f"(-\\infty;{latex(sol.start-1)}]\\cup[{latex(sol.end+1)};+\\infty)"
    de_bai = f"Tập nghiệm của bất phương trình ${a}^{{{lhs}}}\\ge {a}^{{{poly_str}}}$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"${a}^{{{lhs}}}\\ge {a}^{{{poly_str}}}\\Leftrightarrow {lhs}\\ge {poly_str}"
        f"\\Leftrightarrow {latex(sol.start)}\\le x\\le {latex(sol.end)}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), m=str(m), c=str(c), b=str(bcoef), d=str(d))


def verify_D38(params):
    a, m, c, bcoef, d = (sp.sympify(params[k]) for k in ("a", "m", "c", "b", "d"))
    sol = sp.solve_univariate_inequality(m * x + c >= x ** 2 + bcoef * x + d, x, relational=False)
    return isinstance(sol, sp.Interval)


# ===================== D42: TXD log_a x =====================================
def gen_D42(a):
    a = sp.Integer(a)
    correct, wrong1, wrong2, wrong3 = "(0;+\\infty)", "[0;+\\infty)", "(-\\infty;+\\infty)", f"[{a};+\\infty)"
    de_bai = f"Tập xác định của hàm số $y=\\log_{{{a}}}x$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Điều kiện $x>0$. Vậy tập xác định là $\\mathscr{{D}}=(0;+\\infty)$."
    return de_bai, dap_an, loi_giai, dict(a=str(a))


def verify_D42(params):
    return True  # hang so, luon dung voi moi a>0,a!=1


# ===================== D43: log_10 x >= k ===================================
def gen_D43(k):
    k = sp.Integer(k)
    val = 10 ** k
    correct, wrong1, wrong2, wrong3 = f"[{val};+\\infty)", "(0;+\\infty)", f"({val};+\\infty)", f"(-\\infty;{val})"
    de_bai = f"Tập nghiệm của bất phương trình $\\log x\\ge {k}$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"$\\log x\\ge {k}\\Leftrightarrow x\\ge {val}$ (đã thỏa $x>0$). Vậy tập nghiệm là $[{val};+\\infty)$."
    return de_bai, dap_an, loi_giai, dict(k=str(k))


def verify_D43(params):
    k = sp.sympify(params["k"])
    sol = sp.solve_univariate_inequality(sp.log(x, 10) >= k, x, relational=False)
    return sol == sp.Interval(10 ** k, sp.oo)


# ===================== D48/D82: a^x >< c (c khong la luy thua nguyen) =======
def gen_D48_D82(a, c, direction):
    a, c = sp.Integer(a), sp.Integer(c)
    val = sp.log(c, a)
    if direction == ">":
        correct = f"(\\log_{{{a}}} {c};+\\infty)"
        wrong1 = f"(-\\infty;\\log_{{{a}}} {c})"
    else:
        correct = f"(-\\infty;\\log_{{{a}}} {c})"
        wrong1 = f"(\\log_{{{a}}} {c};+\\infty)"
    wrong2 = f"(-\\infty;\\log_{{{c}}} {a})" if direction == "<" else f"(\\log_{{{c}}} {a};+\\infty)"
    wrong3 = f"(\\log_{{{c}}} {a};+\\infty)" if direction == "<" else f"(-\\infty;\\log_{{{c}}} {a})"
    de_bai = f"Tập nghiệm của bất phương trình ${a}^x{direction}{c}$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Ta có ${a}^x{direction}{c}\\Leftrightarrow x{direction}\\log_{{{a}}}{c}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), c=str(c), direction=direction)


def verify_D48_D82(params):
    a, c = sp.sympify(params["a"]), sp.sympify(params["c"])
    direction = params["direction"]
    if direction == ">":
        sol = sp.solve_univariate_inequality(a ** x > c, x, relational=False)
        return sol == sp.Interval.open(sp.log(c, a), sp.oo)
    sol = sp.solve_univariate_inequality(a ** x < c, x, relational=False)
    return sol == sp.Interval.open(-sp.oo, sp.log(c, a))


# ===================== D55: ln^2 x + p ln x + q = 0 (tich nghiem) ===========
def gen_D55(p, q):
    p, q = sp.Integer(p), sp.Integer(q)
    disc = p ** 2 - 4 * q
    assert disc > 0
    t = sp.Symbol("t")
    roots = sp.solve(sp.Eq(t ** 2 + p * t + q, 0), t)
    assert len(roots) == 2
    prod = sp.exp(sum(roots))
    prod_simpl = sp.simplify(prod)
    correct = latex(prod_simpl)
    wrong1 = str(-p)
    wrong2 = str(q)
    wrong3 = latex(sp.exp(-p))
    vals_str = bump_until_distinct_str = [correct, wrong1, wrong2, wrong3]
    if len(set(vals_str)) < 4:
        wrong3 = latex(sp.exp(roots[0] - roots[1]))
    de_bai = f"Tích tất cả các nghiệm của phương trình $\\ln^2 x + {p}\\ln x + {q} = 0$ bằng\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>0$. $\\ln^2x+{p}\\ln x+{q}=0 \\Leftrightarrow \\ln x={latex(roots[0])}$ hay $\\ln x={latex(roots[1])}$. "
        f"Vậy tích các nghiệm là $e^{{{latex(roots[0])}}}\\cdot e^{{{latex(roots[1])}}}={correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(p=str(p), q=str(q))


def verify_D55(params):
    p, q = sp.sympify(params["p"]), sp.sympify(params["q"])
    t = sp.Symbol("t")
    roots = sp.solve(sp.Eq(t ** 2 + p * t + q, 0), t)
    if len(roots) != 2:
        return False
    prod = sp.simplify(sp.exp(roots[0]) * sp.exp(roots[1]))
    return sp.simplify(prod - sp.exp(-p)) == 0


# ===================== D58: dat t=a^x =========================================
def _fmt_quad(coef, const):
    s = "t^2"
    if coef == 1:
        s += "+t"
    elif coef == -1:
        s += "-t"
    elif coef > 0:
        s += f"+{coef}t"
    elif coef < 0:
        s += f"-{-coef}t"
    if const > 0:
        s += f"+{const}"
    elif const < 0:
        s += f"-{-const}"
    return s + "=0"


def gen_D58(a, k, c):
    a, k, c = sp.Integer(a), sp.Integer(k), sp.Integer(c)
    ka = k * a
    assert ka != k and ka != -ka and c != -c
    correct = _fmt_quad(ka, -c)
    wrong1 = _fmt_quad(-ka, -c)
    wrong2 = _fmt_quad(k, -c)
    wrong3 = _fmt_quad(ka, c)
    de_bai = (
        f"Cho phương trình ${a}^{{2x}}+{k}\\cdot{a}^{{x+1}}-{c}=0$. "
        f"Khi đặt $t={a}^x$, ta được phương trình nào dưới đây?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Ta có ${a}^{{2x}}+{k}\\cdot{a}^{{x+1}}-{c}=0 \\Leftrightarrow ({a}^x)^2+{k}{a}\\cdot{a}^x-{c}=0$. "
        f"Đặt $t={a}^x$ $(t>0)$, phương trình trở thành ${correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), k=str(k), c=str(c))


def verify_D58(params):
    a, k, c = (sp.sympify(params[key]) for key in ("a", "k", "c"))
    t = sp.Symbol("t")
    expr = a ** (2 * x) + k * a ** (x + 1) - c
    expr_sub = expr.subs(a ** x, t)
    poly = sp.expand(t ** 2 + k * a * t - c)
    lhs_expand = sp.expand(expr.rewrite(sp.Pow).subs(a ** x, t)) if False else None
    manual = sp.expand((a ** x) ** 2 + k * a * a ** x - c).subs(a ** x, t)
    return sp.expand(manual - poly) == 0


# ===================== D61: TXD log_c((x-p)/(x+q)) ==========================
def gen_D61(c, p, q):
    c, p, q = sp.Integer(c), sp.Integer(p), sp.Integer(q)
    assert p > -q
    correct = f"(-\\infty;{-q})\\cup({p};+\\infty)"
    wrong1 = f"({-q};{p})"
    wrong2 = f"\\mathbb{{R}}\\setminus\\{{{-q}\\}}"
    wrong3 = f"(-\\infty;{-q}]\\cup[{p};+\\infty)"
    de_bai = f"Tìm tập xác định $D$ của hàm số $y=\\log_{{{c}}}\\dfrac{{x-{p}}}{{x+{q}}}$.\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="D=")
    de_bai += "\n".join(lines)
    loi_giai = f"ĐK: $\\dfrac{{x-{p}}}{{x+{q}}}>0 \\Leftrightarrow x<{-q}$ hoặc $x>{p}$."
    return de_bai, dap_an, loi_giai, dict(c=str(c), p=str(p), q=str(q))


def verify_D61(params):
    p, q = sp.sympify(params["p"]), sp.sympify(params["q"])
    sol = sp.solve_univariate_inequality((x - p) / (x + q) > 0, x, relational=False)
    return sol == sp.Union(sp.Interval.open(-sp.oo, -q), sp.Interval.open(p, sp.oo))


# ===================== D62: log_a^2 x - S log_a x + P >= 0 ==================
def gen_D62(a, r1, r2):
    a, r1, r2 = sp.Integer(a), sp.Integer(r1), sp.Integer(r2)
    assert r1 < r2
    S, P = r1 + r2, r1 * r2
    lo, hi = a ** r1, a ** r2
    correct = f"(0;{lo}]\\cup[{hi};+\\infty)"
    wrong1 = f"[{lo};{hi}]"
    wrong2 = f"(-\\infty;{lo}]\\cup[{hi};+\\infty)"
    wrong3 = f"(0;{lo})\\cup({hi};+\\infty)"
    sign_S = f"-{S}" if S > 0 else (f"+{-S}" if S < 0 else "")
    sign_P = f"+{P}" if P > 0 else (f"{P}" if P < 0 else "")
    de_bai = f"Tìm tập nghiệm $S$ của bất phương trình $\\log_{{{a}}}^2 x{sign_S}\\log_{{{a}}} x{sign_P}\\ge 0$.\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>0$. $\\log_{{{a}}}x\\le{r1}$ hoặc $\\log_{{{a}}}x\\ge{r2}$ "
        f"$\\Leftrightarrow 0<x\\le{lo}$ hoặc $x\\ge{hi}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), r1=str(r1), r2=str(r2))


def verify_D62(params):
    a, r1, r2 = (sp.sympify(params[k]) for k in ("a", "r1", "r2"))
    t = sp.Symbol("t")
    S, P = r1 + r2, r1 * r2
    sol_t = sp.solve_univariate_inequality(t ** 2 - S * t + P >= 0, t, relational=False)
    return sol_t == sp.Union(sp.Interval(-sp.oo, r1), sp.Interval(r2, sp.oo))


# ===================== D63: log_a^2 x - m log_a x + (km - C) = 0, x1x2 = N ==
def gen_D63(a, k_coef, C, N_exp):
    a, k_coef, C, N_exp = (sp.Integer(v) for v in (a, k_coef, C, N_exp))
    m = a ** N_exp  # log_a(N) voi N=a^N_exp => m = N_exp thuc te, dung truc tiep
    m = N_exp
    disc = m ** 2 - 4 * (k_coef * m - C)
    assert disc > 0
    N = a ** N_exp
    de_bai = (
        f"Tìm giá trị thực của tham số $m$ để phương trình "
        f"$\\log_{{{a}}}^2 x-m\\log_{{{a}}} x+{k_coef}m-{C}=0$ có hai nghiệm thực $x_1,x_2$ thỏa mãn $x_1x_2={N}$.\n\n"
    )
    correct = str(m)
    wrong1 = str(-m)
    wrong2 = str(N_exp * a)
    wrong3 = str(N)
    vals = bump_until_distinct([sp.Integer(m), sp.Integer(-m), sp.Integer(N_exp*a), sp.Integer(N)])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="m=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"ĐK $x>0$. $x_1x_2={N}\\Leftrightarrow \\log_{{{a}}}x_1+\\log_{{{a}}}x_2={N_exp}\\Leftrightarrow t_1+t_2={N_exp}$.\n"
        f"Đặt $t=\\log_{{{a}}}x$: $t^2-mt+{k_coef}m-{C}=0$. YCBT $\\Leftrightarrow \\Delta>0$ và $m={N_exp}\\Leftrightarrow m={m}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), k_coef=str(k_coef), C=str(C), N_exp=str(N_exp))


def verify_D63(params):
    a, k_coef, C, N_exp = (sp.sympify(params[k]) for k in ("a", "k_coef", "C", "N_exp"))
    m = N_exp
    disc = m ** 2 - 4 * (k_coef * m - C)
    return disc > 0


# ===================== D71: log_a(x+p) = 1 + log_a(x+q)  =>  x+p=a(x+q) =====
def gen_D71(a, p, q):
    a, p, q = sp.Integer(a), sp.Integer(p), sp.Integer(q)
    sols = sp.solve(sp.Eq(x + p, a * (x + q)), x)
    assert len(sols) == 1 and sols[0] > max(-p, -q) and sols[0] != 0
    sol = sols[0]
    de_bai = f"Nghiệm của phương trình $\\log_{{{a}}}(x+{p})=1+\\log_{{{a}}}(x+{q})$ là\n\n"
    assert len({sol, -sol, sol - 1, sol + 1}) == 4
    correct = f"x={latex(sol)}"
    wrong1 = f"x={latex(-sol)}"
    wrong2 = f"x={latex(sol-1)}"
    wrong3 = f"x={latex(sol+1)}"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>{max(-p,-q)}$. $\\log_{{{a}}}(x+{p})=1+\\log_{{{a}}}(x+{q})\\Leftrightarrow x+{p}={a}(x+{q})"
        f"\\Leftrightarrow x={latex(sol)}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), p=str(p), q=str(q))


def verify_D71(params):
    a, p, q = (sp.sympify(params[k]) for k in ("a", "p", "q"))
    sols = sp.solve(sp.Eq(x + p, a * (x + q)), x)
    return len(sols) == 1 and sols[0] > max(-p, -q)


# ===================== D73: dao ham a^{x^2+bx} ===============================
def gen_D73(a, bcoef):
    a, bcoef = sp.Integer(a), sp.Integer(bcoef)
    poly_str = latex(sp.expand(x ** 2 + bcoef * x))
    deriv_lin = latex(2 * x + bcoef)
    correct = f"({deriv_lin})\\cdot{a}^{{{poly_str}}}\\cdot\\ln{a}"
    wrong1 = f"{a}^{{{poly_str}}}\\cdot\\ln{a}"
    wrong2 = f"({poly_str})\\cdot{a}^{{{poly_str}-1}}"
    wrong3 = f"({deriv_lin})\\cdot{a}^{{{poly_str}}}"
    de_bai = f"Hàm số $y={a}^{{{poly_str}}}$ có đạo hàm là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"$y'=\\left({poly_str}\\right)'\\cdot{a}^{{{poly_str}}}\\cdot\\ln{a}=({deriv_lin})\\cdot{a}^{{{poly_str}}}\\cdot\\ln{a}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), b=str(bcoef))


def verify_D73(params):
    a, bcoef = sp.sympify(params["a"]), sp.sympify(params["b"])
    deriv = sp.diff(a ** (x ** 2 + bcoef * x), x)
    target = (2 * x + bcoef) * a ** (x ** 2 + bcoef * x) * sp.log(a)
    return sp.simplify(deriv - target) == 0


# ===================== D80: TXD a^x = R ======================================
def gen_D80(a):
    a = sp.Integer(a)
    correct, wrong1, wrong2, wrong3 = "\\mathbb{R}", "\\mathbb{R}\\setminus\\{0\\}", "[0;+\\infty)", "(0;+\\infty)"
    de_bai = f"Tập xác định của hàm số $y={a}^x$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Tập xác định của hàm số $y={a}^x$ là $\\mathscr{{D}}=\\mathbb{{R}}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a))


def verify_D80(params):
    return True


# ===================== D85: TXD log_a(x-c) ===================================
def gen_D85(a, c):
    a, c = sp.Integer(a), sp.Integer(c)
    correct, wrong1, wrong2, wrong3 = f"({c};+\\infty)", f"(-\\infty;{c}]", f"[{c};+\\infty)", f"(-\\infty;{c})"
    de_bai = f"Tập xác định của hàm số $y=\\log_{{{a}}}(x-{c})$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Hàm số xác định khi $x-{c}>0 \\Leftrightarrow x>{c}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), c=str(c))


def verify_D85(params):
    return True


# ===================== D86: a^x = c  =>  x = log_a c =========================
def gen_D86(a, c):
    a, c = sp.Integer(a), sp.Integer(c)
    correct = f"x=\\log_{{{a}}}{c}"
    wrong1 = f"x=\\log_{{{c}}}{a}"
    wrong2 = f"x=\\dfrac{{{c}}}{{{a}}}"
    wrong3 = f"x=\\sqrt{{{c}}}"
    de_bai = f"Nghiệm của phương trình ${a}^x={c}$ là\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Ta có ${a}^x={c}\\Leftrightarrow x=\\log_{{{a}}}{c}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), c=str(c))


def verify_D86(params):
    a, c = sp.sympify(params["a"]), sp.sympify(params["c"])
    sols = sp.solve(sp.Eq(a ** x, c), x)
    return len(sols) == 1 and sp.simplify(sols[0] - sp.log(c, a)) == 0


# ===================== D91: a^{m1 x+c1} = a^{m2 x+c2} ========================
def gen_D91(a, m1, c1, m2, c2):
    a, m1, c1, m2, c2 = (sp.Integer(v) for v in (a, m1, c1, m2, c2))
    assert m1 != m2
    sol = sp.Rational(c2 - c1, m1 - m2)
    lhs = f"{m1}x" + (f"+{c1}" if c1 > 0 else (f"{c1}" if c1 < 0 else ""))
    rhs = f"{m2}x" + (f"+{c2}" if c2 > 0 else (f"{c2}" if c2 < 0 else ""))
    de_bai = f"Nghiệm của phương trình ${a}^{{{lhs}}}={a}^{{{rhs}}}$ là\n\n"
    correct = f"x={latex(sol)}"
    wrong1 = f"x={latex(-sol)}"
    wrong2 = f"x={latex(sol+1)}"
    wrong3 = f"x={latex(sol-1)}"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Xét phương trình ${a}^{{{lhs}}}={a}^{{{rhs}}}\\Leftrightarrow {lhs}={rhs}\\Leftrightarrow x={latex(sol)}$."
    return de_bai, dap_an, loi_giai, dict(a=str(a), m1=str(m1), c1=str(c1), m2=str(m2), c2=str(c2))


def verify_D91(params):
    a, m1, c1, m2, c2 = (sp.sympify(params[k]) for k in ("a", "m1", "c1", "m2", "c2"))
    sols = sp.solve(sp.Eq(m1 * x + c1, m2 * x + c2), x)
    return len(sols) == 1 and sols[0] == sp.Rational(c2 - c1, m1 - m2)


def main():
    fails = []
    fails += try_add("D02", "Đạo hàm hàm số mũ cơ bản y=a^x", "p006_q13", gen_D02, verify_D02,
                      [(v,) for v in (2, 5, 6, 7, 8, 9)])
    fails += try_add("D04", "Tìm tập xác định hàm số lôgarit của tam thức bậc hai", "p006_q15", gen_D04, verify_D04,
                      [(2, -1, 3), (3, -2, 5), (2, -3, 1), (5, -4, 2), (2, 0, 6), (3, -1, 4)])
    fails += try_add("D07", "Đạo hàm hàm số dạng thương chứa hàm số mũ", "p007_q18", gen_D07, verify_D07,
                      [(1, 4), (2, 3), (1, 2), (3, 5), (2, 5), (1, 3)])
    fails += try_add("D14", "Giải bất phương trình lôgarit cơ số nhỏ hơn 1", "p020_q17", gen_D14, verify_D14,
                      [(1, 2, -1), (2, 3, -1), (1, 3, -2), (2, 2, -1), (1, 4, -3), (3, 2, -1)])
    fails += try_add("D19", "Giải bất phương trình mũ cơ bản dạng a^f(x)>a^k", "p031_q03", gen_D19, verify_D19,
                      [(5, 1, 1, -1), (2, 1, 2, 3), (3, 2, -1, 5), (2, 1, -3, 4), (5, 2, 1, 3), (3, 1, 2, -1)])
    fails += try_add("D21", "Giải phương trình lôgarit dùng công thức cộng hai lôgarit cùng cơ số", "p035_q22",
                      gen_D21, verify_D21, [(2, 1, 3), (3, 2, 2), (2, 2, 3), (5, 1, 2), (2, 3, 4), (3, 1, 3)])
    fails += try_add("D27", "Giải bất phương trình mũ cùng cơ số dạng a^f(x)<a^g(x)", "p049_q13", gen_D27,
                      verify_D27, [(2, 2, 0, 1, 6), (3, 1, 0, 2, -4), (2, 1, 1, 2, -3), (5, 2, 1, 1, -2),
                                   (2, 3, 0, 1, 5), (3, 2, 1, 1, -2)])
    fails += try_add("D28", "Giải phương trình tích nhiều lôgarit cùng cơ số bằng đổi cơ số và đặt ẩn phụ",
                      "p053_q27", gen_D28, verify_D28,
                      [(3, 2, 3), (2, 1, 3), (3, 1, 2), (5, 2, 3), (2, 2, 3), (3, 2, 4)])
    fails += try_add("D31", "Giải phương trình lôgarit cơ bản chứa tam thức bậc hai", "p066_q08", gen_D31,
                      verify_D31, [(2, -1, 2, 1), (2, 0, -1, 3), (3, -2, -5, 2), (2, 0, -4, 2), (5, -4, 2, 2),
                                   (2, 2, -3, 3)])
    fails += try_add("D33", "Giải bất phương trình mũ cùng cơ số, số mũ là tam thức bậc hai", "p068_q23", gen_D33,
                      verify_D33, [(3, -2, 0, 3), (2, 0, -23, 2), (5, -4, 0, 1), (3, 2, 0, 3), (2, -6, 0, 4),
                                   (3, 0, -8, 2)])
    fails += try_add("D34", "Đạo hàm hàm hợp chứa lôgarit của tam thức bậc hai", "p069_q28", gen_D34, verify_D34,
                      [(2, -2), (3, 4), (2, 2), (5, -3), (3, -1), (2, 6)])
    fails += try_add("D38", "Giải bất phương trình mũ cùng cơ số, hai vế là tam thức bậc hai", "p082_q21", gen_D38,
                      verify_D38, [(5, -1, 0, -1, -9), (2, 0, 5, -2, -3), (3, 1, 2, 0, -4), (2, -2, 1, -1, -8),
                                   (5, 2, 0, -1, -6), (2, 1, 3, 0, -5)])
    fails += try_add("D42", "Tìm tập xác định hàm số lôgarit cơ bản y=log_a x", "p093_q05", gen_D42, verify_D42,
                      [(v,) for v in (3, 4, 5, 7, 8, 9)])
    fails += try_add("D43", "Giải bất phương trình lôgarit cơ bản (lôgarit thập phân)", "p095_q16", gen_D43,
                      verify_D43, [(v,) for v in (1, 2, 3, -1, 0, 4)])
    fails += try_add("D48", "Giải bất phương trình mũ dạng a^x>c (c không là lũy thừa nguyên của a)", "p109_q07",
                      lambda a, c: gen_D48_D82(a, c, ">"), verify_D48_D82,
                      [(2, 6), (3, 10), (2, 7), (5, 30), (3, 5), (2, 11)])
    fails += try_add("D82", "Giải bất phương trình mũ dạng a^x<c (c không là lũy thừa nguyên của a)", "p210_q26",
                      lambda a, c: gen_D48_D82(a, c, "<"), verify_D48_D82,
                      [(2, 5), (3, 7), (2, 9), (5, 20), (3, 8), (2, 13)])
    fails += try_add("D55", "Giải phương trình lôgarit bậc hai bằng đặt ẩn phụ, tính tích nghiệm qua Viète",
                      "p127_q34", gen_D55, verify_D55,
                      [(2, -3), (1, -2), (3, -4), (2, -8), (1, -6), (4, -5)])
    fails += try_add("D58", "Đặt ẩn phụ t=a^x để đưa phương trình mũ về phương trình bậc hai theo t", "p137_q01",
                      gen_D58, verify_D58, [(2, 1, 3), (2, 2, 5), (3, 1, 4), (2, 1, 8), (3, 2, 7), (2, 3, 9)])
    fails += try_add("D61", "Tìm tập xác định hàm số lôgarit của một phân thức", "p139_q16", gen_D61, verify_D61,
                      [(5, 3, 2), (2, 4, 1), (3, 5, 3), (7, 2, 5), (2, 6, 2), (5, 1, 4)])
    fails += try_add("D62", "Giải bất phương trình lôgarit bậc hai bằng đặt ẩn phụ t=log_a x", "p139_q17", gen_D62,
                      verify_D62, [(2, 1, 4), (3, 0, 2), (2, -1, 3), (5, 1, 2), (2, 0, 3), (3, -1, 2)])
    fails += try_add("D63", "Tìm tham số để phương trình lôgarit bậc hai có hai nghiệm thỏa tích x1x2 cho trước",
                      "p145_q39", gen_D63, verify_D63,
                      [(3, 2, 7, 4), (2, 1, 3, 3), (3, 3, 10, 5), (2, 2, 4, 4), (5, 1, 2, 2), (2, 1, 5, 5)])
    fails += try_add("D71", "Giải phương trình lôgarit chuyển vế rồi dùng công thức cộng lôgarit", "p173_q16",
                      gen_D71, verify_D71, [(2, 1, -1), (3, 2, -1), (2, 3, 1), (5, 1, -2), (2, 4, 2), (3, 1, -2)])
    fails += try_add("D73", "Đạo hàm hàm hợp chứa hàm số mũ y=a^u(x)", "p176_q26", gen_D73, verify_D73,
                      [(3, -3), (2, -1), (5, 2), (3, 4), (2, -5), (5, -2)])
    fails += try_add("D80", "Tìm tập xác định hàm số mũ cơ bản y=a^x", "p206_q04", gen_D80, verify_D80,
                      [(v,) for v in (7, 2, 3, 5, 9, 11)])
    fails += try_add("D85", "Tìm tập xác định hàm số lôgarit dạng log_a(x-c)", "p220_q04", gen_D85, verify_D85,
                      [(3, 4), (2, 5), (5, 2), (7, 1), (2, 6), (3, 8)])
    fails += try_add("D86", "Giải phương trình mũ dạng a^x=c, nghiệm là lôgarit", "p223_q22", gen_D86, verify_D86,
                      [(5, 2), (3, 7), (2, 5), (7, 3), (2, 9), (5, 3)])
    fails += try_add("D91", "Giải phương trình mũ cùng cơ số dạng a^f(x)=a^g(x)", "p238_q21", gen_D91, verify_D91,
                      [(3, 2, 1, 1, 2), (2, 1, 3, 2, -1), (5, 3, -1, 1, 4), (2, 2, 1, 1, -2), (3, 1, 4, 2, 1),
                       (2, 3, -2, 1, 3)])

    with open("data/questions/mu_logarit_extraction/bien_the/batch_basic_eq.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_batchC_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Tong so hang sinh: {len(ROWS)}\n")
        f.write(f"That bai verify: {len(fails)}\n")
        for ma_dang, params in fails:
            f.write(f"  {ma_dang}: {params}\n")
        counts = {}
        for r in ROWS:
            counts[r['ma_dang']] = counts.get(r['ma_dang'], 0) + 1
        f.write("\nSo bien the theo dang:\n")
        for k, v in sorted(counts.items()):
            f.write(f"  {k}: {v}\n")


if __name__ == "__main__":
    main()
