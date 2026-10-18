# -*- coding: utf-8 -*-
"""STT13 — Vấn đề 7: (z+pi)(z̄+q) thuần ảo → đường tròn, tìm tâm.
Đề gốc: (z+2i)(z̄+2) thuần ảo → tâm (-1;-1).
Biến đầu vào: p (hệ số ảo trong z+pi), q (hệ số thực trong z̄+q). Đặt z=x+yi,
phần thực của tích = x²+qx+y²+py = 0 ⟺ (x+q/2)²+(y+p/2)²=(p²+q²)/4. Tâm I(-q/2;-p/2).
Điều kiện: p,q≠0, |p|≠|q| (4 phương án tọa độ phân biệt).
"""
import sympy as sp
from sp_common import diem, signed_term, gen_pairs, assemble, neq

STT = 13


def gen_params(loai_so, n, seed):
    cond = lambda p, q: neq(sp.Abs(p), sp.Abs(q))
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(p, q):
    cx = sp.nsimplify(-q / sp.Integer(2))
    cy = sp.nsimplify(-p / sp.Integer(2))
    f1 = f"z{signed_term(p, 'i')}"
    f2 = f"\\overline{{z}}{signed_term(q, '')}"
    stem = (f"Xét các số phức $z$ thỏa mãn $({f1})({f2})$ là số thuần ảo. Biết rằng tập hợp tất cả "
            f"các điểm biểu diễn của $z$ là một đường tròn, tâm của đường tròn đó có tọa độ là")
    correct = f"${diem(cx, cy)}$."
    distractors = [f"${diem(cy, cx)}$.", f"${diem(-cx, cy)}$.", f"${diem(cx, -cy)}$."]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = (f"Đặt $z=x+yi$. Cho phần thực của $({f1})({f2})$ bằng $0$ ta được "
                f"$x^2{signed_term(q, 'x')}+y^2{signed_term(p, 'y')}=0$, tức đường tròn tâm $I{diem(cx, cy)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
