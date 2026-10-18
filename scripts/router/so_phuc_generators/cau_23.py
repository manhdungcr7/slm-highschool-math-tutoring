# -*- coding: utf-8 -*-
"""STT23 — Vấn đề 5: Nhân số phức với số thực (k·z). Đề gốc: z=3-2i, 2z → 6-4i.
Biến đầu vào: hệ số nguyên k (|k|≥2) và z=a+bi (a,b theo loại số).
k·z = ka + kb·i. Điều kiện: |a|≠|b| (4 phương án đổi dấu/hoán vị phân biệt).
"""
import random
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble, neq

STT = 23


def gen_params(loai_so, n, seed):
    pairs = gen_pairs(loai_so, n, seed, cond=lambda a, b: neq(sp.Abs(a), sp.Abs(b)))
    rng = random.Random(seed + 7)
    choices = [x for x in range(-12, 13) if abs(x) >= 2]  # hệ số nguyên |k|≥2, cho phép lặp
    return [{"k": sp.Integer(rng.choice(choices)), "a": a, "b": b} for a, b in pairs]


def sinh(k, a, b):
    ra, rb = k * a, k * b
    stem = f"Cho số phức $z = {z_string(a, b)}$, khi đó ${latex(k)}z$ bằng"
    correct = f"${z_string(ra, rb)}$."
    distractors = [f"${z_string(ra, -rb)}$.", f"${z_string(-ra, rb)}$.", f"${z_string(rb, ra)}$."]
    block, dap_an = assemble(correct, distractors, (k, a, b))
    loi_giai = f"Ta có ${latex(k)}z = {latex(k)}({z_string(a, b)}) = {z_string(ra, rb)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
