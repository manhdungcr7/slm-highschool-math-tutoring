# -*- coding: utf-8 -*-
"""STT2 — Vấn đề 3: Môđun của z1+z2. Đề gốc: z1=1+i, z2=2-3i → √13.
Biến đầu vào: z1=a+bi, z2=c+di. Tổng = (a+c)+(b+d)i, |tổng| = √((a+c)²+(b+d)²).
Điều kiện: tổng ≠ 0 (để môđun > 0).
"""
import sympy as sp
from sp_common import z_string, latex, latex_sq, gen_quads, mc_num, neq

STT = 2


def gen_params(loai_so, n, seed):
    cond = lambda a, b, c, d: neq(a + c, 0) or neq(b + d, 0)
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = a + c, b + d
    modun = sp.sqrt(re ** 2 + im ** 2)
    raw = [re ** 2 + im ** 2, sp.Abs(re) + sp.Abs(im), 2 * sp.sqrt(re ** 2 + im ** 2)]
    stem = (f"Cho hai số phức $z_1 = {z_string(a, b)}$ và $z_2 = {z_string(c, d)}$. "
            f"Tính môđun của số phức $z_1+z_2$.")
    block, dap_an = mc_num(modun, raw, (a, b, c, d),
                           fmt=lambda v: f"$|z_1+z_2| = {latex(v)}$.")
    loi_giai = (f"Ta có $z_1+z_2 = {z_string(re, im)} \\Rightarrow "
                f"|z_1+z_2| = \\sqrt{{{latex_sq(re)}^2+{latex_sq(im)}^2}} = {latex(modun)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
