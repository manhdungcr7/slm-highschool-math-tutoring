# -*- coding: utf-8 -*-
"""D49 (tach hieu) va D20 (luy thua cua luy thua) - 2 dang don gian con sot."""
import json
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


# ===================== D49: log_c(a/k) = log_c a - log_c k ==================
def gen_D49(c, k):
    c, k = sp.Integer(c), sp.Integer(k)
    logk = sp.log(k, c)
    is_clean = logk.is_Integer
    logk_str = str(logk) if is_clean else latex(logk)
    correct = f"\\log_{{{c}}} a-{logk_str}"
    wrong1 = f"\\log_{{{c}}} a+{logk_str}"
    wrong2 = f"{logk_str}-\\log_{{{c}}} a"
    wrong3 = f"\\log_{{{c}}} a-{k}"
    de_bai = f"Với mọi số thực $a$ dương, $\\log_{{{c}}}\\dfrac{{a}}{{{k}}}$ bằng\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = f"Ta có $\\log_{{{c}}}\\dfrac{{a}}{{{k}}}=\\log_{{{c}}} a-\\log_{{{c}}}{k}=\\log_{{{c}}} a-{logk_str}$."
    return de_bai, dap_an, loi_giai, dict(c=str(c), k=str(k))


def verify_D49(params):
    c, k = sp.sympify(params["c"]), sp.sympify(params["k"])
    av = sp.Rational(11, 3)
    lhs = sp.log(av / k, c)
    rhs = sp.log(av, c) - sp.log(k, c)
    return abs(float(lhs - rhs)) < 1e-9


# ===================== D20: log_{a^(1/m)} a^n = n*m =========================
def gen_D20(m, n):
    m, n = sp.Integer(m), sp.Integer(n)
    val = n * m
    root = "\\sqrt{a}" if m == 2 else f"\\sqrt[{m}]{{a}}"
    vals = bump_until_distinct([val, sp.Rational(n, m), m + n, n - m if n != m else n + m + 1])
    correct, wrong1, wrong2, wrong3 = (latex(v) for v in vals)
    de_bai = (
        f"Cho $a$ là số thực dương, $a\\neq 1$ và $P=\\log_{{{root}}} a^{{{n}}}$. "
        f"Mệnh đề nào dưới đây là đúng?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0, prefix="P=")
    de_bai += "\n".join(lines)
    loi_giai = f"Ta có $P=\\log_{{a^{{1/{m}}}}}a^{{{n}}}=\\dfrac{{{n}}}{{1/{m}}}\\log_a a={val}$."
    return de_bai, dap_an, loi_giai, dict(m=str(m), n=str(n))


def verify_D20(params):
    m, n = sp.sympify(params["m"]), sp.sympify(params["n"])
    av = sp.Rational(13, 5)
    lhs = sp.log(av ** n, av ** (sp.Rational(1, m)))
    return abs(float(lhs - n * m)) < 1e-9


def main():
    fails = []
    for c, k in [(2, 2), (3, 3), (5, 5), (2, 4), (3, 9), (2, 8)]:
        de_bai, dap_an, loi_giai, params = gen_D49(c, k)
        if verify_D49(params):
            add_row("D49", "Tách lôgarit của một thương thành hiệu hai lôgarit", "p110_q17",
                     de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D49", params))

    for m, n in [(3, 3), (2, 4), (4, 2), (3, 6), (2, 5), (5, 2)]:
        de_bai, dap_an, loi_giai, params = gen_D20(m, n)
        if verify_D20(params):
            add_row("D20", "Tính giá trị lôgarit có cơ số và biểu thức đều là lũy thừa của một số", "p033_q13",
                     de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D20", params))

    with open("data/questions/mu_logarit_extraction/bien_the/batch_identities_C.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_batchE_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Tong so hang sinh: {len(ROWS)}\n")
        f.write(f"That bai verify: {len(fails)}\n")
        for ma_dang, params in fails:
            f.write(f"  {ma_dang}: {params}\n")


if __name__ == "__main__":
    main()
