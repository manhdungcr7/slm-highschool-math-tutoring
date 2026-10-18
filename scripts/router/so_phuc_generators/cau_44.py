# -*- coding: utf-8 -*-
"""STT44 — Vấn đề 4: Điểm biểu diễn của 2z1+z2. Đề gốc: z1=-2+i, z2=1+i → (-3;3).
Biến đầu vào: z1=a+bi, z2=c+di. 2z1+z2 = (2a+c)+(2b+d)i; điểm (re;im).
Điều kiện: re≠0, im≠0, |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, diem, gen_quads, assemble, neq

STT = 44


def gen_params(loai_so, n, seed):
    def cond(a, b, c, d):
        re, im = 2 * a + c, 2 * b + d
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b, "c": c, "d": d} for a, b, c, d in gen_quads(loai_so, n, seed, cond)]


def sinh(a, b, c, d):
    re, im = 2 * a + c, 2 * b + d
    stem = (f"Cho hai số phức $z_1 = {z_string(a, b)}$ và $z_2 = {z_string(c, d)}$. "
            f"Trên mặt phẳng tọa độ $Oxy$, điểm biểu diễn số phức $2z_1+z_2$ có tọa độ là")
    correct = f"${diem(re, im)}$."
    distractors = [f"${diem(im, re)}$.", f"${diem(re, -im)}$.", f"${diem(-re, im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, c, d))
    loi_giai = (f"Ta có $2z_1+z_2 = {z_string(re, im)}$. "
                f"Vậy điểm biểu diễn số phức $2z_1+z_2$ có tọa độ là ${diem(re, im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
