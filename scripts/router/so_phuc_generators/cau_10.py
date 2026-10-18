# -*- coding: utf-8 -*-
"""STT10 — Vấn đề 3: Môđun của z biết z̄ là TÍCH hai số phức.
Đề gốc: "Tính môđun của z biết z̄ = (4-3i)(1+i)." → 5√2.
Biến đầu vào: z̄ = (a+bi)(c+di). Vì |z|=|z̄|=|a+bi|·|c+di| = √(a²+b²)·√(c²+d²).
Điều kiện: a,b,c,d ≠ 0. Khoảng số thu hẹp (-6..6) để đáp án gọn.
"""
import sympy as sp
from sp_common import z_string, latex, gen_quads, mc_num

STT = 10


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b, "c": c, "d": d}
            for a, b, c, d in gen_quads(loai_so, n, seed, lo=-6, hi=6)]


def sinh(a, b, c, d):
    m1, m2 = sp.sqrt(a ** 2 + b ** 2), sp.sqrt(c ** 2 + d ** 2)
    modun = sp.sqrt((a ** 2 + b ** 2) * (c ** 2 + d ** 2))
    raw = [(a ** 2 + b ** 2) * (c ** 2 + d ** 2), m1 + m2, 2 * modun]
    stem = f"Tính môđun của số phức $z$ biết $\\overline{{z}} = ({z_string(a, b)})({z_string(c, d)})$."
    block, dap_an = mc_num(modun, raw, (a, b, c, d), fmt=lambda v: f"$|z| = {latex(v)}$.")
    loi_giai = (
        f"Ta có $\\overline{{z}} = ({z_string(a, b)})({z_string(c, d)})$, suy ra "
        f"$|z| = |\\overline{{z}}| = |{z_string(a, b)}|\\cdot|{z_string(c, d)}| "
        f"= {latex(m1)}\\cdot{latex(m2)} = {latex(modun)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
