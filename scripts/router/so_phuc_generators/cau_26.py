# -*- coding: utf-8 -*-
"""STT26 — Vấn đề 8: z²-2mz+(αm+β)=0, đếm m NGUYÊN để |z1|=|z2|.
Đề gốc: z²-2mz+8m-12=0 → 4 giá trị.
Biến đầu vào: α,β (hệ số αm+β). Δ'=m²-αm-β.
  • Δ'<0 (nghiệm phức liên hợp): luôn |z1|=|z2|.
  • Δ'>0 (nghiệm thực phân biệt): |z1|=|z2| ⟺ z1=-z2 ⟺ m=0 (nếu Δ'(0)>0).
Điều kiện: số giá trị đếm được nằm trong [2;9] (câu hỏi hợp lý).
"""
import sympy as sp
from sp_common import latex, signed_term, gen_pairs, assemble


STT = 26


def _count(alpha, beta):
    cnt = 0
    for mv in range(-200, 201):
        d = mv ** 2 - alpha * mv - beta
        if d < 0:
            cnt += 1
        elif d > 0 and mv == 0:
            cnt += 1
    return cnt


def gen_params(loai_so, n, seed):
    cond = lambda al, be: 2 <= _count(al, be) <= 9
    return [{"alpha": al, "beta": be} for al, be in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(alpha, beta):
    cnt = _count(alpha, beta)
    stem = (f"Trên tập hợp các số phức, xét phương trình $z^2-2mz{signed_term(alpha, 'm')}{signed_term(beta, '')}=0$ "
            f"($m$ là tham số thực). Có bao nhiêu giá trị nguyên của $m$ để phương trình đó có hai nghiệm phân biệt "
            f"$z_1, z_2$ thỏa mãn $|z_1| = |z_2|$?")
    correct = f"${cnt}$."
    distractors = [f"${cnt - 1}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (alpha, beta))
    loi_giai = (
        f"Ta có $\\Delta' = m^2{signed_term(alpha, 'm')}{signed_term(beta, '')}$ "
        f"(dấu đổi so với $\\alpha m+\\beta$). Nếu $\\Delta'<0$ thì hai nghiệm là số phức liên hợp nên luôn "
        f"$|z_1|=|z_2|$; nếu $\\Delta'>0$ thì $|z_1|=|z_2| \\Leftrightarrow z_1+z_2=0 \\Leftrightarrow m=0$ "
        f"(khi $\\Delta'(0)>0$). Đếm các giá trị nguyên $m$ thỏa mãn, được ${cnt}$ giá trị."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
