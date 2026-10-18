# -*- coding: utf-8 -*-
"""STT47 — Vấn đề 4: Từ điểm biểu diễn M(p;q) tìm phần thực của z. Đề gốc: M(-1;3) → -1.
Biến đầu vào: p,q. z=p+qi, phần thực = p.
Điều kiện: p,q≠0, |p|≠|q|.
"""
import sympy as sp
from sp_common import diem, latex, z_string, gen_pairs, assemble, neq

STT = 47


def gen_params(loai_so, n, seed):
    cond = lambda p, q: neq(sp.Abs(p), sp.Abs(q))
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(p, q):
    stem = f"Trên mặt phẳng tọa độ, biết $M{diem(p, q)}$ là điểm biểu diễn số phức $z$. Phần thực của $z$ bằng"
    correct = f"${latex(p)}$."
    distractors = [f"${latex(q)}$.", f"${latex(-p)}$.", f"${latex(-q)}$."]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = f"Ta có $M{diem(p, q)}$ là điểm biểu diễn số phức $z = {z_string(p, q)}$. Do đó phần thực của $z$ là ${latex(p)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
