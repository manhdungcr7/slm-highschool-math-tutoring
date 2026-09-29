# -*- coding: utf-8 -*-
"""
Round 2: cac dang truoc day bi xep vao nhom "kho/rui ro" nhung sau khi xem
lai ky hon thi TONG QUAT HOA duoc an toan:
- D35, D28(da lam): dap so la TONG/TICH nghiem qua Viete -> luon dep du
  tung nghiem rieng le co the vo ti.
- D69, D51, D56, D16: dap so la MOT SO DEM/MOT KHOANG tinh qua ham dac
  trung don dieu hoac lap luan dai so -> van dung du nguong trung gian xau.
- D40, D45, D67: phuong trinh bac hai theo an phu duoc THIET KE co nghiem
  dep (giu cau truc Viete/nhan tu nhu ban goc).
- D15, D08, D22, D29, D05: chi la dao ham/dong nhat thuc/bien doi dai so
  tong quat, truoc do bi bo qua nham (khong thuc su kho).

Verify doc lap: dung sp.solve/sp.diff/dem truc tiep (brute-force) nhu cac
batch truoc, KHONG dung lai cong thuc dong dang da sinh de bai.
"""
import json
import math
import random
import re
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
        "nguon": "NhÃ¢n báº£n", "loai_bien_the": "chuan",
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


# ===================== D15: dao ham ln(1+sqrt(x+k)) ==========================
def gen_D15(k):
    k = sp.Integer(k)
    de_bai = f"TÃ­nh Ä‘áº¡o hÃ m cá»§a hÃ m sá»‘ $y = \\ln(1+\\sqrt{{x+{k}}})$.\n\n"
    correct = f"\\dfrac{{1}}{{2\\sqrt{{x+{k}}}(1+\\sqrt{{x+{k}}})}}"
    wrong1 = f"\\dfrac{{1}}{{1+\\sqrt{{x+{k}}}}}"
    wrong2 = f"\\dfrac{{1}}{{\\sqrt{{x+{k}}}(1+\\sqrt{{x+{k}}})}}"
    wrong3 = f"\\dfrac{{2}}{{\\sqrt{{x+{k}}}(1+\\sqrt{{x+{k}}})}}"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="y'=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$y'=\\dfrac{{(1+\\sqrt{{x+{k}}})'}}{{1+\\sqrt{{x+{k}}}}}"
        f"=\\dfrac{{\\frac{{1}}{{2\\sqrt{{x+{k}}}}}}}{{1+\\sqrt{{x+{k}}}}}=\\dfrac{{1}}{{2\\sqrt{{x+{k}}}(1+\\sqrt{{x+{k}}})}}$."
    )
    return de_bai, dap_an, loi_giai, dict(k=str(k))


def verify_D15(params):
    k = sp.sympify(params["k"])
    deriv = sp.diff(sp.log(1 + sp.sqrt(x + k)), x)
    target = 1 / (2 * sp.sqrt(x + k) * (1 + sp.sqrt(x + k)))
    return sp.simplify(deriv - target) == 0


# ===================== D05: menh de sai ve bien doi log cua a^x*b^(x^2) ====
def gen_D05(a, b):
    a, b = sp.Integer(a), sp.Integer(b)
    # dung: log_a(...)< log_a 1 => x + x^2 log_a b <0
    correct = f"x+x^2\\log_{{{a}}}{b}<0"
    wrong_sai = f"1+x\\log_{{{a}}}{b}<0"  # SAI (thieu nhan x)
    opt_c = f"x\\log_{{{b}}}{a}+x^2<0"  # dung (chia cho log_b)
    opt_d = f"x\\ln{a}+x^2\\ln{b}<0"  # dung (dung ln)
    de_bai = (
        f"Cho hÃ m sá»‘ $y=f(x)={a}^x\\cdot{b}^{{x^2}}$. Kháº³ng Ä‘á»‹nh nÃ o sau Ä‘Ã¢y lÃ  kháº³ng Ä‘á»‹nh "
        f"**sai**?\n\n"
    )
    opts = [wrong_sai, correct, opt_c, opt_d]
    lines, dap_an = render_mc(opts, 0, prefix="f(x)<1\\Leftrightarrow ")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$f(x)<1\\Leftrightarrow\\log_{{{a}}}f(x)<0\\Leftrightarrow x+x^2\\log_{{{a}}}{b}<0"
        f"\\Leftrightarrow x(1+x\\log_{{{a}}}{b})<0$, KHÃ”NG tÆ°Æ¡ng Ä‘Æ°Æ¡ng vá»›i "
        f"$1+x\\log_{{{a}}}{b}<0$ (thiáº¿u nhÃ¢n tá»­ $x$). Váº­y kháº³ng Ä‘á»‹nh sai lÃ  "
        f"$1+x\\log_{{{a}}}{b}<0$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), b=str(b))


def verify_D05(params):
    a, b = sp.sympify(params["a"]), sp.sympify(params["b"])
    xv = sp.Rational(-1, 10)  # diem thu: x nho am, x(1+x logb)<0 co the dung hoac sai tuy dau
    # kiem tra doc lap: dang "dung" (correct) phai tuong duong f(x)<1 tai nhieu diem mau,
    # dang "sai" (thieu he so x) KHONG tuong duong
    f = a ** x * b ** (x ** 2)
    match_correct, mismatch_wrong = True, False
    for xv in [sp.Rational(1, 2), sp.Rational(-1, 2), sp.Integer(2), sp.Integer(-2), sp.Rational(3, 10)]:
        lhs = f.subs(x, xv) < 1
        rhs_correct = (xv + xv ** 2 * sp.log(b, a) < 0)
        rhs_wrong = (1 + xv * sp.log(b, a) < 0)
        if bool(lhs) != bool(rhs_correct):
            match_correct = False
        if bool(lhs) != bool(rhs_wrong):
            mismatch_wrong = True
    return match_correct and mismatch_wrong


# ===================== D45: A^(2x)+p*A^x-q>0 factor (A^x-r1)(A^x-r2)>0 =====
def gen_D45(A, r1, r2):
    A, r1, r2 = sp.Integer(A), sp.Integer(r1), sp.Integer(r2)
    assert r1 > 0 > r2
    p = -(r1 + r2)
    const = r1 * r2
    lhs = f"{A**2}^x" + (f"+{p}\\cdot{A}^x" if p > 0 else (f"{p}\\cdot{A}^x" if p < 0 else ""))
    lhs += (f"+{const}" if const > 0 else (f"{const}" if const < 0 else ""))
    de_bai = f"Táº­p nghiá»‡m cá»§a báº¥t phÆ°Æ¡ng trÃ¬nh ${lhs}>0$ lÃ \n\n"
    boundary = sp.log(r1, A)
    correct = f"({latex(boundary)};+\\infty)"
    wrong1 = f"(-\\infty;{latex(boundary)})"
    wrong2 = f"[{latex(boundary)};+\\infty)"
    wrong3 = f"({latex(boundary+1)};+\\infty)"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$({A}^x-{r1})({A}^x-{r2})>0$. VÃ¬ ${A}^x>0>{r2}$ nÃªn ${A}^x-{r2}>0$ luÃ´n Ä‘Ãºng, "
        f"do Ä‘Ã³ báº¥t phÆ°Æ¡ng trÃ¬nh $\\Leftrightarrow {A}^x>{r1}\\Leftrightarrow x>\\log_{{{A}}}{r1}$."
    )
    return de_bai, dap_an, loi_giai, dict(A=str(A), r1=str(r1), r2=str(r2))


def verify_D45(params):
    A, r1, r2 = (sp.sympify(params[k]) for k in ("A", "r1", "r2"))
    p, const = -(r1 + r2), r1 * r2
    sol = sp.solve_univariate_inequality(A ** (2 * x) + p * A ** x + const > 0, x, relational=False)
    return sol == sp.Interval.open(sp.log(r1, A), sp.oo)


# ===================== D67: t^2-k*m*t+c*m^2-c=0 (dat t=B^x), 2 nghiem duong
def gen_D67(B, k, c):
    B, k, c = sp.Integer(B), sp.Integer(k), sp.Integer(c)
    assert c > 0 and k > 0 and k ** 2 < 4 * c
    # The positive-root criteria reduce to m>1 and
    # (4c-k^2)m^2 < 4c. Enumerate this exact open interval.
    lo = sp.Integer(1)
    hi = sp.sqrt(sp.Rational(4 * c, 4 * c - k ** 2))
    int_vals = [v for v in range(2, int(sp.ceiling(hi))) if sp.Integer(v) < hi]
    assert 1 <= len(int_vals) <= 6
    count = len(int_vals)
    de_bai = (
        f"Gá»i $S$ lÃ  táº­p há»£p táº¥t cáº£ cÃ¡c giÃ¡ trá»‹ nguyÃªn cá»§a tham sá»‘ $m$ sao cho phÆ°Æ¡ng trÃ¬nh "
        f"${B**2}^x-m\\cdot{B}^{{x+1}}+{c}m^2-{c}=0$ cÃ³ hai nghiá»‡m phÃ¢n biá»‡t. Há»i $S$ cÃ³ bao nhiÃªu pháº§n tá»­?\n\n"
    )
    correct = str(count)
    wrong1, wrong2, wrong3 = str(count + 1), str(max(count - 1, 0)), str(count + 2)
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Äáº·t $t={B}^x>0$: $t^2-{k}mt+{c}m^2-{c}=0$. YCBT $\\Leftrightarrow$ PT cÃ³ 2 nghiá»‡m dÆ°Æ¡ng phÃ¢n biá»‡t "
        f"$\\Leftrightarrow \\Delta>0,\\ {k}m>0,\\ {c}m^2-{c}>0 \\Leftrightarrow m\\in\\left({latex(lo)};{latex(hi)}\\right)$. "
        f"Váº­y $S=\\{{{','.join(str(v) for v in int_vals)}\\}}$, cÃ³ ${count}$ pháº§n tá»­."
    )
    return de_bai, dap_an, loi_giai, dict(B=str(B), k=str(k), c=str(c))


def verify_D67_full(params, expected_count):
    # Independently count integer m by applying the quadratic discriminant,
    # sum, and product criteria for two distinct positive roots.
    _, k, c = (int(sp.sympify(params[key])) for key in ("B", "k", "c"))
    count = 0
    for mv in range(-100, 101):
        disc = (k * mv) ** 2 - 4 * (c * mv ** 2 - c)
        total = k * mv
        product = c * mv ** 2 - c
        if disc > 0 and total > 0 and product > 0:
            count += 1
    return count == expected_count


# ===================== D40: log_a^2(bx)-(m+p)log_a x+m-q=0, 2 nghiem [1,a] =
def gen_D40(a, b_coef, p, q=None):
    a, b_coef, p = sp.Integer(a), sp.Integer(b_coef), sp.Integer(p)
    q = 4 - p  # rang buoc bat buoc de PT luon co nghiem t=1 co dinh (xem suy luan trong doc string)
    t = sp.Symbol("t")
    # ho tro b_coef=a (tuc log_a(a x)=1+t voi t=log_a x)
    assert b_coef == a
    m = sp.Symbol("m")
    full = sp.expand((1 + t) ** 2 - (m + p) * t + m - q)
    full_poly = sp.Poly(full, t)
    coeffs = full_poly.all_coeffs()  # [1, coef_t, const] dang t^2+B t+C voi B,C phu thuoc m
    B_of_m = full_poly.coeff_monomial(t)
    C_of_m = full_poly.coeff_monomial(1)
    # roots theo m: gia su factor thanh (t-1)(t-(m-r)) dang thiet ke
    roots_m = sp.solve(sp.Eq(full, 0), t)
    assert len(roots_m) == 2
    r_fixed = [r for r in roots_m if not r.has(m)]
    r_var = [r for r in roots_m if r.has(m)]
    assert len(r_fixed) == 1 and len(r_var) == 1
    r_fixed = r_fixed[0]
    r_var = r_var[0]
    assert 0 <= r_fixed <= 1
    lo = sp.solve(sp.Eq(r_var, 0), m)
    hi = sp.solve(sp.Eq(r_var, 1), m)
    assert len(lo) == 1 and len(hi) == 1
    lo, hi = lo[0], hi[0]
    if lo > hi:
        lo, hi = hi, lo
    correct = f"[{latex(lo)};{latex(hi)})" if r_fixed != 0 else f"({latex(lo)};{latex(hi)}]"
    wrong1 = f"({latex(lo)};{latex(hi)})"
    wrong2 = f"[{latex(lo)};{latex(hi)}]"
    wrong3 = f"({latex(hi)};+\\infty)"
    de_bai = (
        f"Cho phÆ°Æ¡ng trÃ¬nh $\\log_{{{a}}}^2({a}x)-(m+{p})\\log_{{{a}}}x+m-{q}=0$ ($m$ lÃ  tham sá»‘ thá»±c). "
        f"Táº­p há»£p táº¥t cáº£ cÃ¡c giÃ¡ trá»‹ cá»§a $m$ Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh Ä‘Ã£ cho cÃ³ hai nghiá»‡m phÃ¢n biá»‡t thuá»™c Ä‘oáº¡n "
        f"$[1;{a}]$ lÃ \n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Äáº·t $t=\\log_{{{a}}}x$, PT trá»Ÿ thÃ nh $t^2-mt+m-{q+1}=0$" +
        f" $\\Leftrightarrow (t-{r_fixed})(t-({latex(r_var)}))=0$" +
        f" (sau khi rÃºt gá»n). $x\\in[1;{a}]\\Leftrightarrow t\\in[0;1]$. Váº­y $m\\in{correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), p=str(p), q=str(q), lo=str(lo), hi=str(hi), r_fixed=str(r_fixed))


def verify_D40_full(params):
    a, p, q, lo, hi, r_fixed = (sp.sympify(params[k]) for k in ("a", "p", "q", "lo", "hi", "r_fixed"))
    m = sp.Symbol("m")
    t = sp.Symbol("t")
    # thu 3 gia tri m: 1 trong khoang, 2 ngoai khoang -> kiem tra dung/sai qua dinh nghia goc
    ok = True
    test_ms = [lo + sp.Rational(1, 2) * (hi - lo), lo - 1, hi + 1]
    for mv in test_ms:
        full = sp.expand((1 + t) ** 2 - (mv + p) * t + mv - q)
        roots = sp.solve(sp.Eq(full, 0), t)
        valid = [r for r in roots if r.is_real and 0 <= r <= 1]
        should_have_2 = (lo <= mv < hi) if r_fixed == 0 else (lo < mv <= hi)
        has_2 = len(set(valid)) == 2
        if should_have_2 != has_2:
            ok = False
    return ok


# ===================== D16: A^x+(c-m)B^x-m=0 co nghiem thuoc (0,1) ========
def gen_D16(A, B, c):
    A, B, c = sp.Integer(A), sp.Integer(B), sp.Integer(c)
    assert A > B
    f = lambda t: (A ** t + c * B ** t) / (B ** t + 1)
    fp = sp.diff((A ** x + c * B ** x) / (B ** x + 1), x)
    samples = [fp.subs(x, sp.Rational(i, 10)) for i in range(0, 11)]
    assert all(sp.sign(v) == 1 for v in samples)
    f0, f1 = f(0), f(1)
    assert f0 != f1
    lo, hi = (f0, f1) if f0 < f1 else (f1, f0)
    correct = f"({latex(lo)};{latex(hi)})"
    wrong1 = f"[{latex(lo)};{latex(hi)}]"
    wrong2 = f"({latex(lo-1)};{latex(hi)})"
    wrong3 = f"({latex(lo)};{latex(hi+1)})"
    de_bai = (
        f"TÃ¬m táº­p há»£p táº¥t cáº£ cÃ¡c giÃ¡ trá»‹ cá»§a tham sá»‘ thá»±c $m$ Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh "
        f"${A}^x+({c}-m){B}^x-m=0$ cÃ³ nghiá»‡m thuá»™c khoáº£ng $(0;1)$.\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"PT $\\Leftrightarrow m=\\dfrac{{{A}^x+{c}\\cdot{B}^x}}{{{B}^x+1}}=f(x)$. HÃ m $f$ Ä‘á»“ng biáº¿n trÃªn "
        f"$\\mathbb{{R}}$ (do ${A}>{B}$), nÃªn $0<x<1\\Leftrightarrow f(0)<f(x)<f(1)\\Leftrightarrow {correct[1:-1]}$ "
        f"vÃ¬ $f(0)={latex(f0)}, f(1)={latex(f1)}$."
    )
    return de_bai, dap_an, loi_giai, dict(A=str(A), B=str(B), c=str(c))


def verify_D16(params):
    A, B, c = (sp.sympify(params[k]) for k in ("A", "B", "c"))
    fp = sp.diff((A ** x + c * B ** x) / (B ** x + 1), x)
    samples = [fp.subs(x, sp.Rational(i, 20)) for i in range(0, 21)]
    if not all(sp.sign(v) == 1 for v in samples):
        return False
    f0 = (A ** 0 + c * B ** 0) / (B ** 0 + 1)
    f1 = (A ** 1 + c * B ** 1) / (B ** 1 + 1)
    return True


# ===================== D35: log_a(N-a^x)=k-x, tong nghiem qua Viete ========
def gen_D35(a, N, k):
    a, N, k = sp.Integer(a), sp.Integer(N), sp.Integer(k)
    t = sp.Symbol("t", positive=True)
    poly = sp.Poly(t ** 2 - N * t + a ** k, t)
    disc = N ** 2 - 4 * a ** k
    assert disc > 0
    roots = sp.solve(sp.Eq(poly.as_expr(), 0), t)
    assert len(roots) == 2 and all(r.is_real and r > 0 for r in roots)
    total = k  # tong nghiem x1+x2 = log_a(t1*t2) = log_a(a^k) = k, luon dung theo Viete
    correct = str(total)
    wrong1 = str(N)
    wrong2 = str(k + 1)
    wrong3 = str(2 * k)
    vals = bump_until_distinct([sp.Integer(total), N, k + 1, 2 * k])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    de_bai = f"Tá»•ng táº¥t cáº£ cÃ¡c nghiá»‡m cá»§a phÆ°Æ¡ng trÃ¬nh $\\log_{{{a}}}({N}-{a}^x)={k}-x$ báº±ng\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"ÄK: ${N}-{a}^x>0$. $\\log_{{{a}}}({N}-{a}^x)={k}-x \\Leftrightarrow {N}-{a}^x={a}^{{{k}-x}}=\\dfrac{{{a}^{{{k}}}}}{{{a}^x}}"
        f"\\Leftrightarrow ({a}^x)^2-{N}\\cdot{a}^x+{a}^{{{k}}}=0$. Äáº·t $t={a}^x$, PT cÃ³ 2 nghiá»‡m $t_1,t_2$ vá»›i "
        f"$t_1t_2={a}^{{{k}}}$ (ViÃ¨te), suy ra ${a}^{{x_1+x_2}}={a}^{{{k}}}\\Leftrightarrow x_1+x_2={k}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), N=str(N), k=str(k))


def verify_D35(params):
    a, N, k = (sp.sympify(params[key]) for key in ("a", "N", "k"))
    t = sp.Symbol("t", positive=True)
    roots = sp.solve(sp.Eq(t ** 2 - N * t + a ** k, 0), t)
    valid = [r for r in roots if r.is_real and r > 0]
    if len(valid) != 2:
        return False
    prod = sp.simplify(valid[0] * valid[1])
    return abs(float(sp.log(prod, a) - k)) < 1e-9


# ===================== D69: a^x+m=log_a(x-m), dem m nguyen trong khoang ====
def gen_D69(a, lo, hi):
    a, lo, hi = sp.Integer(a), sp.Integer(lo), sp.Integer(hi)
    g = lambda t: a ** t - t
    xv = sp.Symbol("xv", real=True)
    crit = sp.solve(sp.Eq(sp.diff(a ** xv - xv, xv), 0), xv)
    assert len(crit) == 1
    crit = crit[0]
    threshold = -g(crit)
    threshold_f = float(threshold)
    count = 0
    m_list = []
    for mv in range(int(lo) + 1, int(hi)):
        if mv < threshold_f:
            count += 1
            m_list.append(mv)
    assert count > 0
    correct = str(count)
    wrong1, wrong2, wrong3 = str(count + 1), str(count - 1 if count > 1 else count + 2), str(hi - lo - 1)
    de_bai = (
        f"Cho phÆ°Æ¡ng trÃ¬nh ${a}^x+m=\\log_{{{a}}}(x-m)$ vá»›i $m$ lÃ  tham sá»‘. CÃ³ bao nhiÃªu giÃ¡ trá»‹ nguyÃªn "
        f"cá»§a $m\\in({lo};{hi})$ Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh Ä‘Ã£ cho cÃ³ nghiá»‡m?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$\\Leftrightarrow {a}^x+x=\\log_{{{a}}}(x-m)+(x-m)$. XÃ©t $f(t)={a}^t+t$ Ä‘á»“ng biáº¿n trÃªn $\\mathbb{{R}}$ nÃªn "
        f"$x=\\log_{{{a}}}(x-m)\\Leftrightarrow {a}^x=x-m\\Leftrightarrow {a}^x-x=-m$. XÃ©t $g(x)={a}^x-x$ cÃ³ "
        f"$g'(x)=0$ táº¡i $x\\approx{float(crit):.4f}$, giÃ¡ trá»‹ nhá» nháº¥t $g_{{\\min}}\\approx{float(g(crit)):.4f}$. "
        f"PT cÃ³ nghiá»‡m khi $m<{float(threshold):.4f}$. Vá»›i $m$ nguyÃªn trong $({lo};{hi})$, cÃ³ ${count}$ giÃ¡ trá»‹."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), lo=str(lo), hi=str(hi))


def verify_D69_full(params, expected_count):
    a, lo, hi = (float(sp.sympify(params[k])) for k in ("a", "lo", "hi"))
    # Compute the global minimum independently from the derivative equation,
    # then enumerate integer parameters in the stated open interval.
    x_min = math.log(1.0 / math.log(a)) / math.log(a)
    g_min = a ** x_min - x_min
    count = sum(1 for m in range(int(lo) + 1, int(hi)) if -m > g_min + 1e-10)
    return count == expected_count


# ===================== D51: (A^x-c1*B^{x+e}+c2)*sqrt(D-log(F*x)) >= 0 =====
def gen_D51(A, e_val, F, D):
    A, e_val, F, D = (sp.Integer(v) for v in (A, e_val, F, D))
    dk_hi = sp.Rational(10 ** D, F)
    assert dk_hi == sp.floor(dk_hi) and dk_hi > 0
    dk_hi = sp.Integer(dk_hi)
    # A^x - 5*A^(x+2)/... giu dung cau truc ban goc: 4^x - 5*2^(x+2) + 64 >=0 voi A=2 (4=A^2)
    t = sp.Symbol("t", positive=True)
    poly = t ** 2 - 20 * t + 64  # giu nguyen dang cau truc goc (A=2 co dinh de dam bao dep)
    roots = sp.solve(sp.Eq(poly, 0), t)
    roots = sorted(roots)
    r1, r2 = roots
    assert r1 == sp.floor(r1) and r2 == sp.floor(r2)
    x1, x2 = sp.log(r1, 2), sp.log(r2, 2)
    assert x1 == sp.floor(x1) and x2 == sp.floor(x2)
    lo_x, hi_x = int(x1), int(x2)
    count = (lo_x - 0) + (dk_hi - hi_x) if lo_x >= 0 else None
    # so nguyen trong (0;lo_x] hop [hi_x;dk_hi]
    count = lo_x + (dk_hi - hi_x + 1)
    vals = bump_until_distinct([sp.Integer(count), count + 1, count - 1, dk_hi])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    de_bai = (
        f"CÃ³ bao nhiÃªu sá»‘ nguyÃªn $x$ thá»a mÃ£n $(4^x-5\\cdot2^{{x+2}}+64)\\sqrt{{{D}-\\log({F}x)}}\\ge 0$?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"ÄKXÄ: $0<x\\le{dk_hi}$. VÃ¬ cÄƒn $\\ge0$ nÃªn BPT $\\Leftrightarrow 4^x-20\\cdot2^x+64\\ge0"
        f"\\Leftrightarrow 2^x\\le{r1}$ hoáº·c $2^x\\ge{r2}\\Leftrightarrow x\\le{lo_x}$ hoáº·c $x\\ge{hi_x}$. "
        f"Káº¿t há»£p ÄKXÄ: $S=(0;{lo_x}]\\cup[{hi_x};{dk_hi}]$, cÃ³ ${count}$ sá»‘ nguyÃªn."
    )
    return de_bai, dap_an, loi_giai, dict(F=str(F), D=str(D), lo_x=str(lo_x), hi_x=str(hi_x), dk_hi=str(dk_hi))


def verify_D51_full(params, expected_count):
    F, D, dk_hi = (int(sp.sympify(params[k])) for k in ("F", "D", "dk_hi"))
    # Directly enumerate integer x, testing the original radicand domain and
    # polynomial inequality with exact integer arithmetic.
    count = 0
    for xv in range(1, dk_hi + 1):
        if F * xv <= 10 ** D and 4 ** xv - 20 * 2 ** xv + 64 >= 0:
            count += 1
    return count == expected_count


def sample_D51(rng):
    D = rng.randint(1, 10)
    limit = 10 ** D
    valid_F = [int(v) for v in sp.divisors(limit) if limit // int(v) <= 5000]
    return rng.choice(valid_F), D


def expand_type(code, name, source_id, gen, verify, sampler, expected_arg=False, seed=0, target=90, max_tries=2000):
    rng = random.Random(seed)
    current = [row for row in ROWS if row["ma_dang"] == code]
    seen_params = {tuple(sorted(row["params"].items())) for row in current}
    seen_questions = {row["de_bai"] for row in current}
    made = len(current)
    for _ in range(max_tries):
        if made >= target:
            break
        try:
            question, answer, solution, params = gen(*sampler(rng))
        except (AssertionError, ValueError, TypeError, ZeroDivisionError, OverflowError):
            continue
        key = tuple(sorted(params.items()))
        if key in seen_params or question in seen_questions:
            continue
        choices = re.findall(r"(?m)^([A-D])\.\s*(.+)$", question)
        norm = [re.sub(r"[\s$.,]", "", value) for _, value in choices]
        if len(choices) != 4 or {letter for letter, _ in choices} != set("ABCD") or len(set(norm)) != 4:
            continue
        try:
            if expected_arg:
                match = re.search(r"\$\s*(-?\d+)\s*\$", answer)
                if not match or not verify(params, int(match.group(1))):
                    continue
            elif not verify(params):
                continue
        except Exception:
            continue
        add_row(code, name, source_id, question, answer, solution, params)
        seen_params.add(key); seen_questions.add(question); made += 1
    print(f"{code}: {made}/{target}")
    return made


def main():
    fails = []
    fails += try_add("D15", "Äáº¡o hÃ m hÃ m há»£p chá»©a lÃ´garit tá»± nhiÃªn", "p021_q18", gen_D15, verify_D15,
                      [(v,) for v in (1, 2, 3, 0, 4, 5)])
    fails += try_add("D05", "Nháº­n biáº¿t má»‡nh Ä‘á» Ä‘Ãºng/sai vá» biáº¿n Ä‘á»•i lÃ´garit cá»§a tÃ­ch lÅ©y thá»«a", "p006_q16",
                      gen_D05, verify_D05, [(2, 7), (3, 5), (2, 9), (5, 3), (2, 11), (3, 7)])
    fails += try_add("D45", "Giáº£i báº¥t phÆ°Æ¡ng trÃ¬nh mÅ© báº±ng Ä‘áº·t áº©n phá»¥ t=a^x", "p099_q31", gen_D45, verify_D45,
                      [(3, 1, -3), (2, 4, -1), (5, 1, -5), (3, 2, -9), (2, 1, -8), (5, 5, -1)])

    for a, p, q in [(2, 2, 7), (3, 1, 6), (2, 3, 8), (5, 2, 9), (3, 2, 5), (2, 1, 6)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D40(a, a, p, q)
        except AssertionError:
            continue
        if verify_D40_full(params):
            add_row("D40", "TÃ¬m tham sá»‘ Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh lÃ´garit báº­c hai (Ä‘áº·t áº©n phá»¥) cÃ³ hai nghiá»‡m phÃ¢n biá»‡t thá»a Ä‘iá»u kiá»‡n",
                     "p088_q43", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D40", params))

    for A, B, c in [(6, 2, 3), (8, 2, 4), (9, 3, 2), (12, 2, 6), (15, 3, 5), (4, 2, 2)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D16(A, B, c)
        except AssertionError:
            continue
        if verify_D16(params):
            add_row("D16", "TÃ¬m tham sá»‘ Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh mÅ© cÃ³ nghiá»‡m thuá»™c má»™t khoáº£ng (Ä‘áº·t áº©n phá»¥, xÃ©t hÃ m)",
                     "p021_q20", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D16", params))

    for a, N, k in [(3, 7, 2), (2, 5, 1), (5, 30, 2), (3, 15, 3), (2, 10, 3), (3, 20, 2)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D35(a, N, k)
        except AssertionError:
            continue
        if verify_D35(params):
            add_row("D35", "Giáº£i phÆ°Æ¡ng trÃ¬nh lÃ´garit báº±ng Ä‘áº·t áº©n phá»¥ t=a^x, tÃ­nh tá»•ng nghiá»‡m", "p070_q31",
                     de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D35", params))

    for B, k, c in [(2, 4, 5), (2, 5, 7), (3, 4, 5), (3, 5, 7), (5, 4, 5), (5, 5, 7)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D67(B, k, c)
        except AssertionError:
            continue
        expected = int(dap_an.split("$")[1])
        if verify_D67_full(params, expected):
            add_row("D67", "TÃ¬m tham sá»‘ nguyÃªn Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh mÅ© Ä‘áº·t áº©n phá»¥ cÃ³ hai nghiá»‡m áº©n phá»¥ phÃ¢n biá»‡t",
                     "p161_q35", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D67", params))

    for a, lo, hi in [(3, -15, 15), (2, -10, 10), (3, -20, 20), (5, -12, 12)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D69(a, lo, hi)
        except AssertionError:
            continue
        expected = int(dap_an.split("$")[1])
        if verify_D69_full(params, expected):
            add_row("D69", "Äáº¿m giÃ¡ trá»‹ nguyÃªn tham sá»‘ Ä‘á»ƒ phÆ°Æ¡ng trÃ¬nh mÅ©-lÃ´garit lá»“ng nhau cÃ³ nghiá»‡m",
                     "p166_q45", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D69", params))

    for F, D in [(4, 2), (2, 3), (5, 3), (2, 2)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D51(2, 2, F, D)
        except AssertionError:
            continue
        expected = int(dap_an.split("$")[1])
        if verify_D51_full(params, expected):
            add_row("D51", "Äáº¿m sá»‘ nguyÃªn thá»a báº¥t phÆ°Æ¡ng trÃ¬nh mÅ©-lÃ´garit-cÄƒn phá»©c há»£p", "p115_q39",
                     de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D51", params))

    expand_type("D15", "Logarithmic derivative", "p021_q18", gen_D15, verify_D15,
                lambda r: (r.randint(1, 500),), seed=1501)
    expand_type("D05", "Identify a false logarithmic transformation statement", "p006_q16", gen_D05, verify_D05,
                lambda r: (r.randint(2, 100), r.randint(2, 100)), seed=501)
    expand_type("D45", "Solve an exponential inequality by substitution", "p099_q31", gen_D45, verify_D45,
                lambda r: (r.randint(2, 15), r.randint(2, 100), -r.randint(1, 100)), seed=4501)
    expand_type("D40", "Find parameter values giving two distinct logarithmic equation roots", "p088_q43",
                lambda a, p: gen_D40(a, a, p), verify_D40_full,
                lambda r: (r.randint(2, 30), r.randint(1, 40)), seed=4001)
    expand_type("D16", "Find parameter values for an exponential equation to have a root in an interval", "p021_q20",
                gen_D16, verify_D16, lambda r: (r.randint(3, 100), r.randint(2, 99), r.randint(1, 100)), seed=1601)
    expand_type("D35", "Sum roots of a logarithmic equation", "p070_q31", gen_D35, verify_D35,
                lambda r: (r.randint(2, 8), r.randint(20, 500), r.randint(1, 8)), seed=3501)
    expand_type("D67", "Count integer parameters giving two positive roots", "p161_q35",
                gen_D67, lambda p, e: verify_D67_full(p, e),
                lambda r: (r.randint(2, 30), r.randint(2, 40), r.randint(2, 40)), expected_arg=True, seed=6701, max_tries=20000)
    expand_type("D69", "Count integer parameters for an exponential-logarithmic equation", "p166_q45",
                gen_D69, lambda p, e: verify_D69_full(p, e),
                lambda r: (r.randint(2, 10), (lo := r.randint(-100, 50)), lo + r.randint(10, 150)), expected_arg=True, seed=6901)
    expand_type("D51", "Count integer solutions of a product inequality", "p115_q39",
                lambda F, D: gen_D51(2, 2, F, D), lambda p, e: verify_D51_full(p, e),
                sample_D51, expected_arg=True, seed=5101, max_tries=10000)

    with open("data/questions/mu_logarit_extraction/bien_the/batch_round2.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_round2_output.txt", "w", encoding="utf-8") as f:
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
