# -*- coding: utf-8 -*-
"""STT41 — Vấn đề 7: (z̄+pi)(z-q) thuần ảo → đường tròn, tìm bán kính.
Đề gốc: (z̄+3i)(z-3) thuần ảo → R=3√2/2.
Biến đầu vào: p (hệ số ảo trong z̄+pi), q (hệ số thực trong z-q). Phần thực của
tích = x²-qx+y²-py = 0 ⟺ (x-q/2)²+(y-p/2)²=(p²+q²)/4. Bán kính R=√(p²+q²)/2.
Điều kiện: p,q≠0.
"""
import sympy as sp
from sp_common import latex, signed_term, gen_pairs, mc_num

STT = 41


def gen_params(loai_so, n, seed):
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed)]


def sinh(p, q):
    radius = sp.simplify(sp.sqrt(p ** 2 + q ** 2) / 2)
    raw = [sp.sqrt(p ** 2 + q ** 2), sp.simplify((p ** 2 + q ** 2) / 2), 2 * radius]
    f1 = f"\\overline{{z}}{signed_term(p, 'i')}"
    f2 = f"z{signed_term(-q, '')}"
    stem = (f"Xét các số phức $z$ thỏa mãn $({f1})({f2})$ là số thuần ảo. Trên mặt phẳng tọa độ, "
            f"tập hợp tất cả các điểm biểu diễn các số phức $z$ là một đường tròn có bán kính bằng")
    block, dap_an = mc_num(radius, raw, (p, q))
    unreduced = f"\\dfrac{{\\sqrt{{{latex(p**2+q**2)}}}}}{{2}}"
    reduced = latex(radius)
    R_expr = unreduced if unreduced == reduced else f"{unreduced}={reduced}"
    loi_giai = (f"Đặt $z=x+yi$. Cho phần thực của $({f1})({f2})$ bằng $0$ ta được phương trình đường tròn "
                f"bán kính $R={R_expr}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
