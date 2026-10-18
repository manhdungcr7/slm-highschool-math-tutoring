# -*- coding: utf-8 -*-
"""STT50 — Vấn đề 3: Môđun của z·w̄. Đề gốc: z=2+2i, w=2+i → 2√10.
Biến đầu vào: z=a+bi, w=c+di. |z·w̄| = |z|·|w| = √(a²+b²)·√(c²+d²).
Điều kiện: a,b,c,d ≠ 0. Khoảng số thu hẹp (-6..6) để đáp án gọn.
"""
import sympy as sp
from sp_common import z_string, latex, gen_quads, mc_num

STT = 50


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b, "c": c, "d": d}
            for a, b, c, d in gen_quads(loai_so, n, seed, lo=-6, hi=6)]


def sinh(a, b, c, d):
    m1, m2 = sp.sqrt(a ** 2 + b ** 2), sp.sqrt(c ** 2 + d ** 2)
    modun = sp.sqrt((a ** 2 + b ** 2) * (c ** 2 + d ** 2))
    raw = [(a ** 2 + b ** 2) * (c ** 2 + d ** 2), m1 + m2, 2 * modun]
    stem = (f"Cho hai số phức $z = {z_string(a, b)}$ và $w = {z_string(c, d)}$. "
            f"Mô-đun của số phức $z\\cdot\\overline{{w}}$ bằng")
    block, dap_an = mc_num(modun, raw, (a, b, c, d))
    loi_giai = (
        f"Ta có $|z\\cdot\\overline{{w}}| = |z|\\cdot|\\overline{{w}}| = |z|\\cdot|w| "
        f"= {latex(m1)}\\cdot{latex(m2)} = {latex(modun)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
