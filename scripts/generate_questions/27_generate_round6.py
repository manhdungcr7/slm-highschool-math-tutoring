# -*- coding: utf-8 -*-
"""Round 6: D79 (cong thuc dong dua tren nguong x^2-x<threshold, thay vi do
luoi tren y khong bi chan - chinh xac va nhanh hon nhieu)."""
import json
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

ROWS = []


def add_row(ma_dang, ten_dang, id_goc, de_bai, dap_an, loi_giai, params):
    ROWS.append({
        "id_goc": id_goc, "ma_dang": ma_dang, "ten_dang": ten_dang,
        "nguon": "Nhân bản", "loai_bien_the": "chuan",
        "de_bai": de_bai, "dap_an": dap_an, "loi_giai": loi_giai, "params": params,
    })


# ===================== D79: dem x sao cho <=N0 gia tri y thoa log_p(x^2+y)>=log_q(x+y)
def gen_D79(p, q, N0):
    p, q, N0 = sp.Integer(p), sp.Integer(q), sp.Integer(N0)
    assert p > q
    r = sp.log(p, q)
    threshold = (N0 + 1) ** r - (N0 + 1)
    xv = sp.Symbol("xv", real=True)
    sol = sp.solve_univariate_inequality(xv ** 2 - xv < threshold, xv, relational=False)
    assert isinstance(sol, sp.Interval)
    lo_i, hi_i = int(sp.ceiling(sol.start)), int(sp.floor(sol.end))
    assert lo_i <= hi_i
    count = hi_i - lo_i + 1
    assert 5 < count < 300
    correct = str(count)
    vals = bump_until_distinct([sp.Integer(count), count + 1, count - 1, count + 2])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    de_bai = (
        f"Có bao nhiêu số nguyên $x$ sao cho ứng với mỗi $x$ có không quá {N0} số nguyên $y$ thỏa mãn "
        f"$\\log_{{{p}}}(x^2+y)\\ge \\log_{{{q}}}(x+y)$?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    threshold_str = latex(threshold) if threshold.is_rational else f"\\approx{float(threshold):.2f}"
    threshold_eq = "=" if threshold.is_rational else ""
    loi_giai = (
        f"Điều kiện $x+y>0, x^2+y>0$. Đặt $t=x+y$ ($t\\ge1$ do $x,y$ nguyên). Bất phương trình "
        f"$\\Leftrightarrow x^2-x\\ge t^{{\\log_{{{q}}}{p}}}-t=f(t)$, với $f$ đồng biến trên $[1;+\\infty)$. "
        f"Có không quá {N0} số nguyên $y$ (tức $t$) thỏa mãn khi $x^2-x<f({N0+1}){threshold_eq}{threshold_str}$. "
        f"Giải ra $x\\in\\{{{lo_i},\\ldots,{hi_i}\\}}$, có ${count}$ số nguyên $x$."
    )
    return de_bai, dap_an, loi_giai, dict(p=str(p), q=str(q), N0=str(N0), lo_i=str(lo_i), hi_i=str(hi_i))


def verify_D79(params):
    p, q, N0, lo_i, hi_i = (sp.sympify(params[k]) for k in ("p", "q", "N0", "lo_i", "hi_i"))
    p, q, N0 = float(p), float(q), int(N0)
    # kiem tra doc lap: voi vai x quanh bien (trong va ngoai [lo_i,hi_i]), dem SO Y truc tiep
    # (bang dinh nghia goc, khong dung cong thuc nguong) va so sanh voi <=N0 hay khong.
    import math

    def count_y_for_x(xv, y_search=400):
        c = 0
        for yv in range(-y_search, y_search):
            s = xv + yv
            if s <= 0 or xv ** 2 + yv <= 0:
                continue
            lhs = math.log(xv ** 2 + yv, p)
            rhs = math.log(s, q)
            if lhs >= rhs:
                c += 1
                if c > N0 + 2:
                    break
        return c

    test_xs = [int(lo_i), int(hi_i), int(lo_i) - 1, int(hi_i) + 1, (int(lo_i) + int(hi_i)) // 2]
    for xv in test_xs:
        c = count_y_for_x(xv)
        should_be_le = lo_i <= xv <= hi_i
        is_le = c <= N0
        if should_be_le != is_le:
            return False
    return True


# ===================== D89: A(x-1)e^x = y(e^x+xy-Bx^2-C), x in (lo,hi) =====
def gen_D89(A, B, C, lo, hi, y_max=60):
    import math
    A, B, C, lo, hi = sp.Integer(A), sp.Integer(B), sp.Integer(C), sp.Integer(lo), sp.Integer(hi)
    def f(xv, y):
        xv = float(xv)
        return A * (xv - 1) * math.exp(xv) - y * (math.exp(xv) + xv * y - B * xv ** 2 - C)
    found = []
    for y in range(1, y_max):
        f_lo, f_hi = f(lo, y), f(hi, y)
        if f_lo * f_hi <= 0:
            found.append(y)
    assert found and found == list(range(found[0], found[-1] + 1))
    count = len(found)
    assert 5 < count < 40
    correct = str(count)
    vals = bump_until_distinct([sp.Integer(count), count + 1, count - 1, count + 2])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    Bx2 = f"{B}x^2" if B != 1 else "x^2"
    de_bai = (
        f"Có bao nhiêu số nguyên dương $y$ sao cho tồn tại số thực $x\\in({lo};{hi})$ thỏa mãn "
        f"${A}(x-1)e^x=y(e^x+xy-{Bx2}-{C})$?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Xét $f(x)={A}(x-1)e^x-y(e^x+xy-{Bx2}-{C})$ trên $[{lo};{hi}]$. Có thể chứng minh $f$ đơn điệu "
        f"theo từng khoảng ứng với $x=y/{A}$ (tương tự bản gốc), nên phương trình có nghiệm "
        f"$x\\in({lo};{hi})$ khi và chỉ khi $f({lo})\\cdot f({hi})\\le0$. Kiểm tra trực tiếp cho "
        f"$y\\in\\mathbb{{Z}}^+$ ta được $y\\in\\{{{found[0]},\\ldots,{found[-1]}\\}}$, có ${count}$ giá trị."
    )
    return de_bai, dap_an, loi_giai, dict(A=str(A), B=str(B), C=str(C), lo=str(lo), hi=str(hi),
                                           found_lo=str(found[0]), found_hi=str(found[-1]))


def verify_D89(params):
    import math
    A, B, C, lo, hi, found_lo, found_hi = (sp.sympify(params[k]) for k in
                                            ("A", "B", "C", "lo", "hi", "found_lo", "found_hi"))
    def f(xv, y):
        xv = float(xv)
        return float(A) * (xv - 1) * math.exp(xv) - y * (math.exp(xv) + xv * y - float(B) * xv ** 2 - float(C))
    for y in [int(found_lo), int(found_hi), int(found_lo) - 1, int(found_hi) + 1]:
        if y < 1:
            continue
        ok = f(lo, y) * f(hi, y) <= 0
        should = found_lo <= y <= found_hi
        if ok != should:
            return False
    return True


def expand_type(code, name, source_id, gen, verify, sampler, seed=0, target=90, max_tries=5000):
    rng = random.Random(seed)
    current = [r for r in ROWS if r["ma_dang"] == code]
    seen = {tuple(sorted(r["params"].items())) for r in current}
    questions = {r["de_bai"] for r in current}
    made = len(current)
    for _ in range(max_tries):
        if made >= target:
            break
        try:
            q, ans, sol, params = gen(*sampler(rng))
        except (AssertionError, ValueError, TypeError, ZeroDivisionError, OverflowError):
            continue
        key = tuple(sorted(params.items()))
        if key in seen or q in questions:
            continue
        opts = re.findall(r"(?m)^([A-D])\.\s*(.+)$", q)
        norm = [re.sub(r"[\s$.,]", "", v) for _, v in opts]
        if len(opts) != 4 or {k for k,_ in opts} != set("ABCD") or len(set(norm)) != 4:
            continue
        try:
            if not verify(params):
                continue
        except Exception:
            continue
        add_row(code, name, source_id, q, ans, sol, params)
        seen.add(key); questions.add(q); made += 1
    print(f"{code}: {made}/{target}")
    return made


def main():
    fails = []
    for p, q, N0 in [(4, 3, 242), (9, 5, 300), (4, 3, 100), (3, 2, 150), (8, 5, 200)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D79(p, q, N0)
        except (AssertionError, TypeError):
            continue
        if verify_D79(params):
            add_row("D79", "Đếm số nguyên một biến sao cho số giá trị nguyên biến kia thỏa mãn bất phương "
                            "trình lôgarit không vượt một ngưỡng", "p204_q49", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D79", params))

    for A, B, C, lo, hi in [(4, 2, 3, 1, 5), (2, 1, 2, 1, 4), (3, 2, 4, 1, 6), (4, 1, 3, 1, 5)]:
        try:
            de_bai, dap_an, loi_giai, params = gen_D89(A, B, C, lo, hi)
        except AssertionError:
            continue
        if verify_D89(params):
            add_row("D89", "Đếm số nguyên dương một biến sao cho tồn tại biến kia thỏa mãn phương trình "
                            "chứa hàm mũ e^x", "p230_q45", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D89", params))

    expand_type("D79", "Count integers satisfying a logarithmic inequality threshold", "p204_q49",
                gen_D79, verify_D79,
                lambda r: (lambda p, q: (p, q if q < p else p-1, r.randint(20, 500)))(r.randint(3, 30), r.randint(2, 29)), seed=7901)
    expand_type("D89", "Count positive integer parameters for an exponential equation", "p230_q45",
                gen_D89, verify_D89,
                lambda r: (r.randint(1, 15), r.randint(1, 12), r.randint(0, 30),
                           (lo := r.randint(1, 8)), lo + r.randint(2, 12)), seed=8901)

    with open("data/questions/mu_logarit_extraction/bien_the/batch_round6.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_round6_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Tong so hang sinh: {len(ROWS)}\n")
        f.write(f"That bai verify: {len(fails)}\n")
        for ma_dang, params in fails:
            f.write(f"  {ma_dang}: {params}\n")


if __name__ == "__main__":
    main()
