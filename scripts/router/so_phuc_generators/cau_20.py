# -*- coding: utf-8 -*-
"""STT20 — Vấn đề 4: Điểm biểu diễn của z=a+bi. Đề gốc: z=-1+2i → (-1;2).
Biến đầu vào: a,b. Điểm M(a;b). Điều kiện: a,b≠0, |a|≠|b| (4 phương án hoán vị/đổi dấu phân biệt).
"""
import sympy as sp
from sp_common import z_string, diem, gen_pairs, assemble, neq

STT = 20


def gen_params(loai_so, n, seed):
    cond = lambda a, b: neq(sp.Abs(a), sp.Abs(b))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, b):
    stem = f"Trên mặt phẳng tọa độ, điểm biểu diễn số phức $z = {z_string(a, b)}$ là điểm nào dưới đây?"
    correct = f"${diem(a, b)}$."
    distractors = [f"${diem(b, a)}$.", f"${diem(a, -b)}$.", f"${diem(-a, b)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Điểm biểu diễn số phức $z = {z_string(a, b)}$ là điểm có tọa độ ${diem(a, b)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
