# -*- coding: utf-8 -*-
"""Round 5: D22, D24, D39, D75, D93."""
import json
import math
import sys
from importlib import import_module

sys.path.insert(0, "scripts/generate_questions")
utils = import_module("10_common_utils")
latex = utils.latex
render_mc = utils.render_mc
bump_until_distinct = utils.bump_until_distinct

import sympy as sp

x = sp.Symbol("x", positive=True)
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


# ===================== D22: log_a b=C, P=log_{sqrt(b)/a} sqrt(b/a) =========
def gen_D22(C_num, C_is_sqrt):
    if C_is_sqrt:
        C = sp.sqrt(C_num)
        C_str = f"\\sqrt{{{C_num}}}"
    else:
        C = sp.Rational(C_num, 1)
        C_str = str(C_num)
    assert C != 2
    P = sp.simplify((C - 1) / (C - 2))
    correct = latex(P)
    wrong1 = latex(-P)
    wrong2 = latex(P + 1)
    wrong3 = latex(1 - P)
    vals_ok = len({correct, wrong1, wrong2, wrong3}) == 4
    assert vals_ok
    de_bai = (
        f"Cho $a, b$ là các số thực dương thỏa mãn $a\\neq 1, a\\neq\\sqrt{{b}}$ và $\\log_a b={C_str}$. "
        f"Tính $P=\\log_{{\\frac{{\\sqrt{{b}}}}{{a}}}}\\sqrt{{\\dfrac{{b}}{{a}}}}$.\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="P=")
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$P=\\dfrac{{\\log_a\\sqrt{{b/a}}}}{{\\log_a(\\sqrt b/a)}}=\\dfrac{{\\frac12(\\log_a b-1)}}"
        f"{{\\frac12\\log_a b-1}}=\\dfrac{{{C_str}-1}}{{{C_str}-2}}={correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(C_num=str(C_num), C_is_sqrt=str(C_is_sqrt))


def verify_D22(params):
    C_num, C_is_sqrt = int(params["C_num"]), params["C_is_sqrt"] == "True"
    C = sp.sqrt(C_num) if C_is_sqrt else sp.Rational(C_num, 1)
    av = sp.Rational(7, 3)
    bv = av ** C
    P = sp.log(sp.sqrt(bv / av), sp.sqrt(bv) / av)
    target = sp.simplify((C - 1) / (C - 2))
    return abs(complex(P) - complex(target)) < 1e-6


# ===================== D24: y=ln(x)/x^n => x y'' + (n+1) y' = -n/x^(n+1) ===
def gen_D24(n):
    n = sp.Integer(n)
    np1 = n + 1
    xn = "x" if n == 1 else f"x^{{{n}}}"
    xn1 = f"x^{{{n-1}}}" if n != 2 else "x"
    xn1 = "" if n == 1 else (xn1 if n != 2 else "x")
    coef_n = "" if n == 1 else str(n)
    coef_np1 = "" if np1 == 1 else str(np1)
    de_bai = f"Cho hàm số $y=\\dfrac{{\\ln x}}{{{xn}}}$, mệnh đề nào dưới đây đúng?\n\n"
    correct = f"{coef_np1}y'+xy''=-\\dfrac{{{n}}}{{x^{{{np1}}}}}"
    wrong1 = f"{coef_np1}y'+xy''=\\dfrac{{{n}}}{{x^{{{np1}}}}}"
    wrong2 = f"y'+xy''=-\\dfrac{{{n}}}{{x^{{{np1}}}}}"
    wrong3 = f"{coef_n}y'+xy''=-\\dfrac{{{n}}}{{x^{{{np1}}}}}"
    vals_ok = len({correct, wrong1, wrong2, wrong3}) == 4
    assert vals_ok
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    step1_lhs = f"{n}{xn1}y+{xn}y'" if n != 1 else "y+xy'"
    loi_giai = (
        f"Ta có ${xn}y=\\ln x$. Lấy đạo hàm hai vế: ${step1_lhs}=\\dfrac1x$. "
        f"Lấy đạo hàm tiếp rồi rút gọn (thay lại $y$) ta được "
        f"${coef_np1}y'+xy''=-\\dfrac{{{n}}}{{x^{{{np1}}}}}$."
    )
    return de_bai, dap_an, loi_giai, dict(n=str(n))


def verify_D24(params):
    n = sp.sympify(params["n"])
    y = sp.log(x) / x ** n
    yp = sp.diff(y, x)
    ypp = sp.diff(y, x, 2)
    lhs = (n + 1) * yp + x * ypp
    rhs = -n / x ** (n + 1)
    return sp.simplify(lhs - rhs) == 0


# ===================== D39: log_{p^2}x=log_{pq}y=log_{q^2}(cx+y) =>x/y ======
def gen_D39(p, q, c, disc_ok):
    p, q, c = sp.Integer(p), sp.Integer(q), sp.Integer(c)
    assert p != q
    u = sp.Symbol("u", positive=True)
    sols = [s for s in sp.solve(sp.Eq(c * u ** 2 + u - 1, 0), u) if s.is_real and s > 0]
    assert len(sols) == 1
    ratio = sols[0]
    correct = latex(ratio)
    wrong1 = latex(1 / ratio)
    wrong2 = latex(-ratio)
    wrong3 = latex(ratio + 1)
    vals_ok = len({correct, wrong1, wrong2, wrong3}) == 4
    assert vals_ok
    cx_str = f"{c}x+y" if c != 1 else "x+y"
    de_bai = (
        f"Cho $x,y$ là các số thực dương thỏa mãn $\\log_{{{p**2}}}x=\\log_{{{p*q}}}y=\\log_{{{q**2}}}({cx_str})$. "
        f"Giá trị của $\\dfrac{{x}}{{y}}$ bằng\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Đặt $t$ là giá trị chung. $x=({p**2})^t,y=({p*q})^t,{cx_str}=({q**2})^t$. Chia cả hai vế cho "
        f"$({q**2})^t$ và đặt $u=(p/q)^t=x/y$: ${c}u^2+u-1=0\\Rightarrow u={correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(p=str(p), q=str(q), c=str(c))


def verify_D39(params):
    p, q, c = (sp.sympify(params[k]) for k in ("p", "q", "c"))
    u = sp.Symbol("u", positive=True)
    sols = [s for s in sp.solve(sp.Eq(c * u ** 2 + u - 1, 0), u) if s.is_real and s > 0]
    if len(sols) != 1:
        return False
    ratio = sols[0]
    t = sp.log(ratio, sp.Rational(p, q))
    xv = (p ** 2) ** t
    yv = (p * q) ** t
    rhs = (q ** 2) ** t
    return abs(float(c * xv + yv - rhs)) < 1e-6 and abs(float(xv / yv - ratio)) < 1e-9


# ===================== D75 (brute-force count) =============================
def gen_D75(a, c, m_max=250):
    a, c = sp.Integer(a), sp.Integer(c)
    r1, r2 = sp.Integer(2), sp.Rational(-1, 2)  # log_a x = 2 or -1/2, tu 2t^2-3t-2=0
    x1 = a ** r1
    x2 = a ** r2
    x1_f, x2_f, a_f, c_f = float(x1), float(x2), float(a), float(c)
    def has_two_roots(mv):
        # dieu kien mien: nghiem x hop le khi va chi khi c^x >= m (de can bac hai xac dinh)
        roots = set()
        if c_f ** x1_f >= mv:
            roots.add(round(x1_f, 6))
        if c_f ** x2_f >= mv:
            roots.add(round(x2_f, 6))
        xv2 = math.log(mv, c_f)
        if xv2 > 0:
            roots.add(round(xv2, 6))
        return len(roots) == 2
    count = sum(1 for mv in range(1, m_max) if has_two_roots(mv))
    assert count > 5
    correct = str(count)
    vals = bump_until_distinct([sp.Integer(count), count + 1, count - 1, count + 2])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    de_bai = (
        f"Cho phương trình $\\left(2\\log_{{{a}}}^2x-3\\log_{{{a}}}x-2\\right)\\sqrt{{{c}^x-m}}=0$ "
        f"($m$ là tham số thực). Có tất cả bao nhiêu giá trị nguyên dương của $m$ để phương trình đã "
        f"cho có đúng hai nghiệm phân biệt?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>0,{c}^x\\ge m$. Nhân tử đầu có nghiệm $\\log_{{{a}}}x=2$ hay $\\log_{{{a}}}x=-\\dfrac12$, "
        f"tức $x={x1}$ hoặc $x={latex(x2)}$; nhân tử sau có $x=\\log_{{{c}}}m$. Xét các trường hợp theo $m$ "
        f"tương tự bản gốc (đối chiếu điều kiện $\\ge m$ cho từng nghiệm cố định, cộng thêm miền $m$ để "
        f"nghiệm thứ ba xuất hiện đúng một lần) cho tổng cộng ${count}$ giá trị nguyên dương."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), c=str(c), m_max=str(m_max))


def verify_D75_full(params, expected_count):
    a, c, m_max = (sp.sympify(params[k]) for k in ("a", "c", "m_max"))
    a, c, m_max = float(a), float(c), int(m_max)
    # doc lap: giai lai 2t^2-3t-2=0 bang sympy (khong dung lai r1=2,r2=-1/2 co san)
    t = sp.Symbol("t")
    troots = sp.solve(sp.Eq(2 * t ** 2 - 3 * t - 2, 0), t)
    x_roots = [a ** float(r) for r in troots]
    count = 0
    for mv in range(1, m_max):
        roots = set()
        for xr in x_roots:
            # dieu kien mien: can bac hai xac dinh <=> c^x >= m
            if c ** xr >= mv:
                roots.add(round(xr, 6))
        if mv > 0:
            xv2 = math.log(mv, c)
            if xv2 > 0:
                roots.add(round(xv2, 6))
        if len(roots) == 2:
            count += 1
    return count == expected_count


# ===================== D93 (brute-force count) ==============================
def gen_D93(A, B, N, a_max=400, b_range=10):
    A, B, N = sp.Integer(A), sp.Integer(B), sp.Integer(N)
    def count_b(av):
        c = 0
        for b in range(-b_range, b_range):
            f1 = A ** b - A
            f2 = av * B ** b - N
            if f1 * f2 < 0:
                c += 1
        return c
    count = sum(1 for av in range(1, a_max) if count_b(av) == 3)
    assert count > 5
    correct = str(count)
    vals = bump_until_distinct([sp.Integer(count), count + 1, count - 1, count + 2])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    de_bai = (
        f"Có bao nhiêu số nguyên dương $a$ sao cho ứng với mỗi $a$ có đúng ba số nguyên $b$ thỏa mãn "
        f"$({A}^b-{A})({a if False else 'a'}\\cdot{B}^b-{N})<0$?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Xét hai trường hợp $b>1$ và $b<1$ (dấu của ${A}^b-{A}$) rồi tìm khoảng của $a$ tương ứng để "
        f"đúng 3 giá trị nguyên $b$ thỏa mãn ở mỗi trường hợp; gộp lại được tổng cộng ${count}$ giá trị "
        f"nguyên dương $a$."
    )
    return de_bai, dap_an, loi_giai, dict(A=str(A), B=str(B), N=str(N), a_max=str(a_max), b_range=str(b_range))


def verify_D93_full(params, expected_count):
    A, B, N, a_max, b_range = (int(sp.sympify(params[k])) for k in ("A", "B", "N", "a_max", "b_range"))
    count = 0
    for av in range(1, a_max):
        c = 0
        for b in range(-b_range - 5, b_range + 5):
            f1 = A ** b - A
            f2 = av * B ** b - N
            if f1 * f2 < 0:
                c += 1
        if c == 3:
            count += 1
    return count == expected_count


def main():
    fails = []
    for C_num, is_sqrt in [(3, True), (5, True), (2, True), (7, True), (3, False), (5, False), (10, False)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D22(C_num, is_sqrt)
        except AssertionError:
            continue
        if verify_D22(params):
            add_row("D22", "Tính giá trị biểu thức lôgarit phức hợp qua một lôgarit cho trước", "p038_q33",
                     de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D22", params))

    fails += try_add("D24", "Nhận biết tính chất (đạo hàm/đơn điệu) của hàm số chứa lôgarit", "p041_q40",
                      gen_D24, verify_D24, [(v,) for v in (1, 2, 3, 4, 5, 6)])

    for p, q, c in [(3, 2, 2), (2, 3, 2), (5, 2, 2), (4, 3, 2), (3, 5, 2), (5, 3, 2)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D39(p, q, c, True)
        except AssertionError:
            continue
        if verify_D39(params):
            add_row("D39", "Từ dãy đẳng thức lôgarit ba cơ số khác nhau suy ra tỉ lệ giữa các biến", "p087_q41",
                     de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D39", params))

    for a, c in [(2, 3), (2, 2), (3, 2), (2, 5), (3, 5)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D75(a, c)
        except AssertionError:
            continue
        expected = int(dap_an.split("$")[1])
        if verify_D75_full(params, expected):
            add_row("D75", "Đếm giá trị nguyên dương tham số để phương trình tích (lôgarit bậc hai và căn "
                            "chứa tham số) có nghiệm", "p186_q47", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D75", params))

    for A, B, N in [(3, 2, 18), (2, 3, 24), (3, 2, 20), (2, 2, 16), (3, 4, 30)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D93(A, B, N)
        except AssertionError:
            continue
        expected = int(dap_an.split("$")[1])
        if verify_D93_full(params, expected):
            add_row("D93", "Đếm số nguyên dương tham số sao cho có đúng k giá trị nguyên biến kia thỏa "
                            "bất phương trình tích", "p242_q39", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D93", params))

    with open("data/questions/mu_logarit_extraction/bien_the/batch_round5.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_round5_output.txt", "w", encoding="utf-8") as f:
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
