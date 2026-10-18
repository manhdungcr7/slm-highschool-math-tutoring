# -*- coding: utf-8 -*-
"""STT21 — Vấn đề 1: Phần ảo của tích z1·z2. Đề gốc: z1=3-i, z2=-1+i → 4.
Biến đầu vào: z1=a+bi, z2=c+di. z1z2=(ac-bd)+(ad+bc)i; re=ac-bd, im=ad+bc (đáp án).
Điều kiện: re≠0, im≠0, |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, latex, gen_quads, assemble, neq

STT = 21


def gen_params(loai_so, n, seed):
    def cond(a, b, c, d):
        re, im = a * c - b * d, a * d + b * c
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = sp.expand(a * c - b * d), sp.expand(a * d + b * c)
    stem = (f"Cho hai số phức $z_1 = {z_string(a, b)}$ và $z_2 = {z_string(c, d)}$. "
            f"Phần ảo của số phức $z_1z_2$ bằng")
    correct = f"${latex(im)}$."
    distractors = [f"${latex(re)}$.", f"${latex(-re)}$.", f"${latex(-im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, c, d))
    loi_giai = (f"Ta có $z_1z_2 = ({z_string(a, b)})({z_string(c, d)}) = {z_string(re, im)}$. "
                f"Suy ra phần ảo của $z_1z_2$ bằng ${latex(im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
