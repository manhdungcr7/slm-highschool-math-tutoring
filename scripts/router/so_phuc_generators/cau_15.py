# -*- coding: utf-8 -*-
"""STT15 — Vấn đề 3: Môđun của số phức a+bi (ghi TRỰC TIẾP số phức).
Đề gốc: "Môđun của số phức 1+2i bằng" → √5.
Biến đầu vào: a,b. |z| = √(a²+b²). Phương án nhiễu: a²+b² (quên căn), |a|+|b|, 2√(a²+b²).
"""
import sympy as sp
from sp_common import z_string, latex, latex_sq, gen_pairs, mc_num

STT = 15


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed)]


def sinh(a, b):
    modun = sp.sqrt(a ** 2 + b ** 2)
    raw = [a ** 2 + b ** 2, sp.Abs(a) + sp.Abs(b), 2 * sp.sqrt(a ** 2 + b ** 2)]
    stem = f"Môđun của số phức ${z_string(a, b)}$ bằng"
    block, dap_an = mc_num(modun, raw, (a, b))
    loi_giai = f"Ta có $|{z_string(a, b)}| = \\sqrt{{{latex_sq(a)}^2+{latex_sq(b)}^2}} = {latex(modun)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
