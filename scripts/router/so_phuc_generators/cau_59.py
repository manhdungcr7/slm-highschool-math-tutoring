# -*- coding: utf-8 -*-
"""STT59 — Vấn đề 3: Môđun của (c+di)·z. Đề gốc: z=4-2i, (1+i)z → 2√10.
Biến đầu vào: z=a+bi và số phức nhân (c+di). |(c+di)z| = √(c²+d²)·√(a²+b²).
Điều kiện: a,b,c,d ≠ 0. Khoảng số thu hẹp (-6..6) để đáp án gọn.
"""
import sympy as sp
from sp_common import z_string, latex, gen_quads, mc_num

STT = 59


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b, "c": c, "d": d}
            for a, b, c, d in gen_quads(loai_so, n, seed, lo=-6, hi=6)]


def sinh(a, b, c, d):
    m1, m2 = sp.sqrt(c ** 2 + d ** 2), sp.sqrt(a ** 2 + b ** 2)
    modun = sp.sqrt((a ** 2 + b ** 2) * (c ** 2 + d ** 2))
    raw = [(a ** 2 + b ** 2) * (c ** 2 + d ** 2), m1 + m2, 2 * modun]
    stem = f"Cho số phức $z = {z_string(a, b)}$, mô-đun của số phức $({z_string(c, d)})z$ bằng"
    block, dap_an = mc_num(modun, raw, (a, b, c, d))
    loi_giai = (
        f"Ta có $|({z_string(c, d)})z| = |{z_string(c, d)}|\\cdot|z| "
        f"= {latex(m1)}\\cdot{latex(m2)} = {latex(modun)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
