# -*- coding: utf-8 -*-
"""STT19 — Vấn đề 1: Phần thực của z1+z2. Đề gốc: z1=2+i, z2=1+3i → 3.
Biến đầu vào: z1=a+bi, z2=c+di. re=a+c (đáp án), im=b+d.
Điều kiện: re≠0, im≠0, |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, latex, gen_quads, assemble, neq

STT = 19


def gen_params(loai_so, n, seed):
    def cond(a, b, c, d):
        re, im = a + c, b + d
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = a + c, b + d
    stem = (f"Cho hai số phức $z_1 = {z_string(a, b)}$ và $z_2 = {z_string(c, d)}$. "
            f"Phần thực của số phức $z_1+z_2$ bằng")
    correct = f"${latex(re)}$."
    distractors = [f"${latex(-re)}$.", f"${latex(im)}$.", f"${latex(-im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, c, d))
    loi_giai = f"Ta có $z_1+z_2 = {z_string(re, im)}$. Phần thực của số phức $z_1+z_2$ bằng ${latex(re)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
