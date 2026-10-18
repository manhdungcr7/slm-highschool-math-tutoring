# -*- coding: utf-8 -*-
"""STT29 — Vấn đề 1: Phần thực của z². Đề gốc: z=2+9i → -77.
Biến đầu vào: z=a+bi. z²=(a²-b²)+2ab·i; re=a²-b² (đáp án), im=2ab.
Điều kiện: a²≠b² (re≠0), a,b≠0 (im≠0), |a²-b²|≠|2ab|.
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble, neq

STT = 29


def gen_params(loai_so, n, seed):
    def cond(a, b):
        re, im = a ** 2 - b ** 2, 2 * a * b
        return neq(re, 0) and neq(im, 0) and neq(sp.Abs(re), sp.Abs(im))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond)]


def sinh(a, b):
    val = sp.expand((a + b * sp.I) ** 2)
    re, im = sp.re(val), sp.im(val)
    stem = f"Cho số phức $z = {z_string(a, b)}$, phần thực của số phức $z^2$ bằng"
    correct = f"${latex(re)}$."
    distractors = [f"${latex(im)}$.", f"${latex(-re)}$.", f"${latex(-im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = (f"Ta có $z^2 = ({z_string(a, b)})^2 = {z_string(re, im)}$ "
                f"nên phần thực của số phức $z^2$ bằng ${latex(re)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
