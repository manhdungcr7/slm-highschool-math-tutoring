# -*- coding: utf-8 -*-
"""STT64 — Vấn đề 5: z1+z2. Đề gốc: z1=2+3i, z2=1-i → 3+2i.
Biến đầu vào: z1=a+bi, z2=c+di. Điều kiện: re=a+c≠0, im=b+d≠0, |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, join_plus, gen_quads, assemble, neq

STT = 64


def gen_params(loai_so, n, seed):
    def cond(a, b, c, d):
        re, im = a + c, b + d
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = a + c, b + d
    stem = (f"Cho hai số phức $z_1 = {z_string(a, b)}$ và $z_2 = {z_string(c, d)}$. "
            f"Số phức $z_1+z_2$ bằng")
    correct = f"${z_string(re, im)}$."
    distractors = [f"${z_string(re, -im)}$.", f"${z_string(-re, im)}$.", f"${z_string(im, re)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, c, d))
    loi_giai = f"Ta có $z_1+z_2 = {z_string(a, b)}{join_plus(z_string(c, d))} = {z_string(re, im)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
