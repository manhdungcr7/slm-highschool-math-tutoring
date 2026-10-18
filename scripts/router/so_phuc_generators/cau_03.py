# -*- coding: utf-8 -*-
"""STT3 — Vấn đề 5: Tính w = iz + z̄. Đề gốc: z=2+5i → w=-3-3i.
Biến đầu vào: z=a+bi. iz = -b+ai, z̄ = a-bi ⟹ w = (a-b)+(a-b)i.
Điều kiện: a≠b (để w≠0 và 4 phương án đổi dấu phân biệt).
"""
import sympy as sp
from sp_common import z_string, gen_pairs, assemble, neq

STT = 3


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=lambda a, b: neq(a, b))]


def sinh(a, b):
    w = sp.expand(sp.I * (a + b * sp.I) + (a - b * sp.I))
    re, im = sp.re(w), sp.im(w)  # re = im = a-b
    stem = f"Cho số phức $z = {z_string(a, b)}$. Tìm số phức $w = iz+\\overline{{z}}$."
    correct = f"$w = {z_string(re, im)}$."
    distractors = [f"$w = {z_string(re, -im)}$.", f"$w = {z_string(-re, im)}$.", f"$w = {z_string(-re, -im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = (f"Ta có $w = i({z_string(a, b)})+({z_string(a, -b)}) = {z_string(re, im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
