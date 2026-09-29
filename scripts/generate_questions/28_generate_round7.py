# -*- coding: utf-8 -*-
"""Round 7: D17 (thiet ke nguoc chon t roi suy k2, giong D68/D94)."""
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


# ===================== D17: P=k1(1+t)^2+k2/t, t=log_{a/b}b, chon t truoc ===
def gen_D17(k1, t_num, t_den):
    k1 = sp.Integer(k1)
    t0 = sp.Rational(t_num, t_den)
    k2 = 2 * k1 * t0 ** 2 * (1 + t0)
    assert k2 == sp.floor(k2) and k2 > 0
    k2 = sp.Integer(k2)
    t = sp.Symbol("t", positive=True)
    P = k1 * (1 + t) ** 2 + k2 / t
    Pmin = P.subs(t, t0)
    assert Pmin == sp.floor(Pmin) and Pmin > 0
    Pmin = sp.Integer(Pmin)
    k1_disp = "" if k1 == 1 else str(k1)
    de_bai = (
        f"Xét các số thực $a, b$ thỏa mãn $a>b>1$. Tìm giá trị nhỏ nhất $P_{{\\min}}$ của biểu thức "
        f"$P = \\log^2_{{\\frac{{a}}{{b}}}}(a^{{{2*k1 if False else 2}}}) + {k2}\\log_b\\left(\\dfrac{{a}}{{b}}\\right)$"
        if k1 == 1 else
        f"Xét các số thực $a, b$ thỏa mãn $a>b>1$. Tìm giá trị nhỏ nhất $P_{{\\min}}$ của biểu thức "
        f"$P = {k1}\\log^2_{{\\frac{{a}}{{b}}}}(a) + {k2}\\log_b\\left(\\dfrac{{a}}{{b}}\\right)$"
    )
    de_bai = (
        f"Xét các số thực $a, b$ thỏa mãn $a>b>1$. Tìm giá trị nhỏ nhất $P_{{\\min}}$ của biểu thức "
        f"$P = {k1_disp}\\log^2_{{\\frac{{a}}{{b}}}}a + {k2}\\log_b\\left(\\dfrac{{a}}{{b}}\\right)$.\n\n"
    )
    correct = f"P_{{\\min}}={Pmin}"
    wrong1 = f"P_{{\\min}}={Pmin+1}"
    wrong2 = f"P_{{\\min}}={Pmin-1}"
    wrong3 = f"P_{{\\min}}={2*Pmin}"
    vals = bump_until_distinct([Pmin, Pmin + 1, Pmin - 1, 2 * Pmin])
    v0, v1, v2, v3 = vals
    correct, wrong1, wrong2, wrong3 = (f"P_{{\\min}}={v}" for v in (v0, v1, v2, v3))
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Đặt $t=\\log_{{a/b}}b>0$. Ta có $\\log_{{a/b}}a=1+t$ và $\\log_b(a/b)=\\dfrac1t$, nên "
        f"$P={k1_disp}(1+t)^2+\\dfrac{{{k2}}}{{t}}=f(t)$. Xét $f'(t)={2*k1}(1+t)-\\dfrac{{{k2}}}{{t^2}}$, "
        f"$f'(t)=0$ tại $t={latex(t0)}$ (nghiệm dương duy nhất). $f\\left({latex(t0)}\\right)={Pmin}$ là giá "
        f"trị nhỏ nhất. Vậy $P_{{\\min}}={Pmin}$."
    )
    return de_bai, dap_an, loi_giai, dict(k1=str(k1), k2=str(k2), t0=str(t0))


def verify_D17(params):
    k1, k2, t0 = (sp.sympify(params[k]) for k in ("k1", "k2", "t0"))
    t = sp.Symbol("t", positive=True)
    P = k1 * (1 + t) ** 2 + k2 / t
    # doc lap: lay mau nhieu diem quanh t0 de xac nhan la cuc tieu (khong dung dao ham)
    Pmin_claimed = float(P.subs(t, t0))
    samples = [P.subs(t, sp.Rational(i, 1000)) for i in range(1, 5000, 5)]
    numeric_min = min(float(s) for s in samples)
    return abs(numeric_min - Pmin_claimed) < 0.05 and Pmin_claimed <= numeric_min + 1e-6


def main():
    fails = []
    candidates = [(1, 1, 1), (2, 1, 1), (3, 1, 1), (4, 1, 2), (5, 1, 1), (6, 1, 1), (7, 1, 1),
                  (1, 2, 1), (2, 2, 1), (3, 2, 1)]
    for k1, t_num, t_den in candidates:
        try:
            de_bai, dap_an, loi_giai, params = gen_D17(k1, t_num, t_den)
        except AssertionError:
            continue
        if verify_D17(params):
            add_row("D17", "Tìm giá trị nhỏ nhất của biểu thức lôgarit bằng đặt ẩn phụ và khảo sát hàm",
                     "p021_q21", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D17", params))

    with open("data/questions/mu_logarit_extraction/bien_the/batch_round7.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_round7_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Tong so hang sinh: {len(ROWS)}\n")
        f.write(f"That bai verify: {len(fails)}\n")
        for ma_dang, params in fails:
            f.write(f"  {ma_dang}: {params}\n")


if __name__ == "__main__":
    main()
