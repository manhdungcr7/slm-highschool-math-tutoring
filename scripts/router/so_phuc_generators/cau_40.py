# -*- coding: utf-8 -*-
"""STT40 — Vấn đề 1: Viết số phức khi biết phần thực và phần ảo.
Đề gốc: "Số phức có phần thực bằng 3 và phần ảo bằng 4 là" → 3+4i.
Biến đầu vào: a = phần thực, b = phần ảo. Điều kiện: a,b ≠ 0, |a| ≠ |b|.
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble, neq

STT = 40


def gen_params(loai_so, n, seed):
    cond = lambda a, b: neq(sp.Abs(a), sp.Abs(b))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, b):
    stem = f"Số phức có phần thực bằng ${latex(a)}$ và phần ảo bằng ${latex(b)}$ là"
    correct = f"${z_string(a, b)}$."
    distractors = [f"${z_string(b, -a)}$.", f"${z_string(a, -b)}$.", f"${z_string(b, a)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Số phức có phần thực bằng ${latex(a)}$ và phần ảo bằng ${latex(b)}$ là $z = {z_string(a, b)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
