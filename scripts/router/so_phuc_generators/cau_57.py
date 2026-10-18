# -*- coding: utf-8 -*-
"""STT57 — Vấn đề 5: z-w. Đề gốc: z=4+3i, w=1-i → 3+4i.
Biến đầu vào: z=a+bi, w=c+di. z-w=(a-c)+(b-d)i.
Điều kiện: re=a-c≠0, im=b-d≠0, |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, gen_quads, assemble, neq

STT = 57


def gen_params(loai_so, n, seed):
    def cond(a, b, c, d):
        re, im = a - c, b - d
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = a - c, b - d
    stem = (f"Cho hai số phức $z = {z_string(a, b)}$ và $w = {z_string(c, d)}$. "
            f"Số phức $z-w$ bằng")
    correct = f"${z_string(re, im)}$."
    distractors = [f"${z_string(re, -im)}$.", f"${z_string(-re, im)}$.", f"${z_string(im, re)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, c, d))
    loi_giai = f"Ta có $z-w = ({z_string(a, b)})-({z_string(c, d)}) = {z_string(re, im)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
