# -*- coding: utf-8 -*-
"""STT17 — Vấn đề 4: Điểm biểu diễn của z=(a+bi)². Đề gốc: z=(1+2i)² → (-3;4).
Biến đầu vào: a,b. z²=(a²-b²)+2ab·i; điểm (re;im) với re=a²-b², im=2ab.
Điều kiện: |a|≠|b| (re≠0), a,b≠0 (im≠0), |re|≠|im|.
"""
import sympy as sp
from sp_common import z_string, diem, gen_pairs, assemble, neq

STT = 17


def gen_params(loai_so, n, seed):
    def cond(a, b):
        re, im = a ** 2 - b ** 2, 2 * a * b
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond)]


def sinh(a, b):
    val = sp.expand((a + b * sp.I) ** 2)
    re, im = sp.re(val), sp.im(val)
    stem = f"Trên mặt phẳng tọa độ, điểm biểu diễn số phức $z = ({z_string(a, b)})^2$ là điểm nào dưới đây?"
    correct = f"${diem(re, im)}$."
    distractors = [f"${diem(im, re)}$.", f"${diem(re, -im)}$.", f"${diem(-re, im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = (f"Ta có $z = ({z_string(a, b)})^2 = {z_string(re, im)}$. "
                f"Vậy điểm biểu diễn của $z$ có tọa độ ${diem(re, im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
