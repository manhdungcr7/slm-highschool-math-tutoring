# -*- coding: utf-8 -*-
"""STT16 — Vấn đề 1: Phần ảo của z1+z̄2. Đề gốc: z1=-3+i, z2=1-i → 2.
Biến đầu vào: z1=a+bi, z2=c+di. z̄2=c-di, z1+z̄2=(a+c)+(b-d)i; im=b-d (đáp án).
Điều kiện: im≠0, re=a+c≠0, |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, latex, gen_quads, assemble, neq

STT = 16


def gen_params(loai_so, n, seed):
    def cond(a, b, c, d):
        re, im = a + c, b - d
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = a + c, b - d
    stem = (f"Cho hai số phức $z_1 = {z_string(a, b)}$ và $z_2 = {z_string(c, d)}$. "
            f"Phần ảo của số phức $z_1+\\overline{{z_2}}$ bằng")
    correct = f"${latex(im)}$."
    distractors = [f"${latex(-im)}$.", f"${latex(re)}$.", f"${latex(-re)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, c, d))
    loi_giai = (f"Ta có $\\overline{{z_2}} = {z_string(c, -d)}$ nên $z_1+\\overline{{z_2}} = {z_string(re, im)}$. "
                f"Phần ảo của số phức $z_1+\\overline{{z_2}}$ bằng ${latex(im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
