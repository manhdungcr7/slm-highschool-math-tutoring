"""
Sinh bien the D53 - Giai bat phuong trinh logarit co ban dang
log_a(f(x))>k, f(x) bac nhat. 4 cau goc: p006_q14, p124_q21, p221_q08,
p236_q12 (p006_q14 vốn bị gán nhầm ma dang rieng D03; da gop lai vao D53
vi cung dang: log_a(bac nhat)>k).

Cong thuc: log_a(m*x + c) > k  (a>1, m>0)  =>  x > (a^k - c) / m
"""
import json
import random
import sys
from importlib import import_module

sys.path.insert(0, "scripts/generate_questions")
utils = import_module("10_common_utils")
latex = utils.latex
linear_expr_str = utils.linear_expr_str
bump_until_distinct = utils.bump_until_distinct

import sympy as sp

MA_DANG = "D53"
TEN_DANG = "Giai bat phuong trinh logarit co ban dang log_a(f(x))>k, f(x) bac nhat"
SOURCE_IDS = ["p006_q14", "p124_q21", "p221_q08", "p236_q12"]


def mau_D53(a, m, c, k):
    a, m, c, k = sp.Integer(a), sp.Integer(m), sp.Integer(c), sp.Integer(k)
    boundary = sp.Rational(a ** k - c, m)
    wrong_boundary1 = a ** k - c
    wrong_boundary2 = sp.Rational(a * k - c, m)
    vals = bump_until_distinct([boundary, wrong_boundary1, wrong_boundary2, boundary])
    boundary, wrong_boundary1, wrong_boundary2, _ = vals

    correct = f"\\left({latex(boundary)};+\\infty\\right)"
    wrong1 = f"\\left(-\\infty;{latex(boundary)}\\right)"
    wrong2 = f"\\left({latex(wrong_boundary1)};+\\infty\\right)"
    wrong3 = f"\\left({latex(wrong_boundary2)};+\\infty\\right)"

    expr = linear_expr_str(m, c)
    de_bai = f"Tập nghiệm của bất phương trình $\\log_{{{a}}}({expr})>{k}$ là\n\n"
    opts = [correct, wrong1, wrong2, wrong3]
    letters = ["A", "B", "C", "D"]
    order = [0, 1, 2, 3]
    random.shuffle(order)
    lines = []
    correct_letter = None
    for pos, idx in enumerate(order):
        letter = letters[pos]
        if idx == 0:
            correct_letter = letter
        lines.append(f"{letter}. ${opts[idx]}$.")
    de_bai += "\n".join(lines)
    dap_an = f"{correct_letter}. ${correct}$."
    loi_giai = (
        f"Điều kiện: ${expr}>0$. Vì $a={a}>1$ nên "
        f"$\\log_{{{a}}}({expr})>{k} \\Leftrightarrow {expr}>{a}^{{{k}}}={latex(a**k)} "
        f"\\Leftrightarrow x>{latex(boundary)}$. Vậy tập nghiệm là ${correct}$."
    )
    return de_bai, dap_an, loi_giai, dict(a=str(a), m=str(m), c=str(c), k=str(k))


BUCKETS = {
    "he_so_x_bang_1": dict(m_choices=[1], c_range=(-6, 6)),
    "he_so_x_lon_hon_1": dict(m_choices=[2, 3], c_range=(-6, 6)),
    "dap_so_phan_so": dict(m_choices=[2, 3], c_range=(-6, 6)),
}
SO_BAN_MOI_BUCKET = 2


def gen_variants(id_goc, seed_base):
    rows = []
    rnd = random.Random(seed_base)
    for bucket_name, spec in BUCKETS.items():
        made = 0
        tries = 0
        seen = set()
        while made < SO_BAN_MOI_BUCKET and tries < 500:
            tries += 1
            a = rnd.choice([2, 3, 4, 5, 6, 7])
            m = rnd.choice(spec["m_choices"])
            c = utils.rrange(*spec["c_range"], exclude=set(), rnd=rnd)
            k = rnd.choice([0, 1, 2, 3])
            if bucket_name == "dap_so_phan_so":
                if (a ** k - c) % m == 0:
                    continue
            else:
                if (a ** k - c) % m != 0:
                    continue
            key = (a, m, c, k)
            if key in seen:
                continue
            seen.add(key)
            de_bai, dap_an, loi_giai, params = mau_D53(a, m, c, k)
            rows.append({
                "id_goc": id_goc,
                "ma_dang": MA_DANG,
                "ten_dang": TEN_DANG,
                "nguon": "Nhân bản",
                "loai_bien_the": bucket_name,
                "de_bai": de_bai,
                "dap_an": dap_an,
                "loi_giai": loi_giai,
                "params": params,
            })
            made += 1
    return rows


if __name__ == "__main__":
    all_rows = []
    for i, id_goc in enumerate(SOURCE_IDS):
        all_rows.extend(gen_variants(id_goc, seed_base=5300 + i))
    print("Tong so bien the D53:", len(all_rows))
    with open("data/questions/mu_logarit_extraction/bien_the/D53_bien_the.json", "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=2)
