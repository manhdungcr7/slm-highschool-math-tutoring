# -*- coding: utf-8 -*-
"""STT53 — Vấn đề 1: Phần thực của z=a+bi (hỏi "bằng"). Đáp án a.
Điều kiện: a,b ≠ 0 và |a| ≠ |b|.
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble, neq

STT = 53


def gen_params(loai_so, n, seed):
    cond = lambda a, b: neq(sp.Abs(a), sp.Abs(b))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, b):
    stem = f"Phần thực của số phức $z = {z_string(a, b)}$ bằng"
    correct = f"${latex(a)}$."
    distractors = [f"${latex(-a)}$.", f"${latex(b)}$.", f"${latex(-b)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Phần thực của số phức $z = {z_string(a, b)}$ bằng ${latex(a)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
