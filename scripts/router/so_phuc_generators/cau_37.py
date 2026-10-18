# -*- coding: utf-8 -*-
"""STT37 — Vấn đề 4: Điểm biểu diễn của w=iz. Đề gốc: z=1-2i → w=iz=2+i → (2;1).
Biến đầu vào: z=a+bi. w=iz = -b + a·i; điểm (-b; a).
Điều kiện: a,b≠0, |a|≠|b| (4 phương án hoán vị/đổi dấu phân biệt).
"""
import sympy as sp
from sp_common import z_string, diem, gen_pairs, assemble, neq

STT = 37


def gen_params(loai_so, n, seed):
    cond = lambda a, b: neq(sp.Abs(a), sp.Abs(b))
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, b):
    w = sp.expand(sp.I * (a + b * sp.I))
    re, im = sp.re(w), sp.im(w)  # re=-b, im=a
    stem = (f"Cho số phức $z = {z_string(a, b)}$. Điểm nào dưới đây là điểm biểu diễn của số phức "
            f"$w = iz$ trên mặt phẳng tọa độ?")
    correct = f"${diem(re, im)}$."
    distractors = [f"${diem(im, re)}$.", f"${diem(re, -im)}$.", f"${diem(-re, im)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Ta có $w = iz = {z_string(re, im)}$. Điểm biểu diễn của $w$ có tọa độ ${diem(re, im)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
