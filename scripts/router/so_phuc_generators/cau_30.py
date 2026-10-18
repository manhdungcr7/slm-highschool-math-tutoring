# -*- coding: utf-8 -*-
"""STT30 — Vấn đề 1: Phần ảo của z=a+bi (hỏi "là"). Đáp án b.
Điều kiện: a,b ≠ 0 và |a| ≠ |b| (4 phương án b, -b, a, -a phân biệt).
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble, neq

STT = 30


def gen_params(loai_so, n, seed):
    cond = lambda a, b: neq(sp.Abs(a), sp.Abs(b))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, b):
    stem = f"Phần ảo của số phức $z = {z_string(a, b)}$ là"
    correct = f"${latex(b)}$."
    distractors = [f"${latex(-b)}$.", f"${latex(a)}$.", f"${latex(-a)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Phần ảo của số phức $z = {z_string(a, b)}$ là ${latex(b)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
