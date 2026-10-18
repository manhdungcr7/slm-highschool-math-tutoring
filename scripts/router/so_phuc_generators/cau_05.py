# -*- coding: utf-8 -*-
"""STT5 — Vấn đề 2: Liên hợp của số phức cho dưới dạng biểu thức z=i(p+qi).
Đề gốc: "Tìm số phức liên hợp của z = i(3i+1)." → z=-3+i, z̄=-3-i.
Biến đầu vào: p,q. z = i(p+qi) = -q + p·i, nên z̄ = -q - p·i.
Điều kiện: p,q ≠ 0 (phần thực -q ≠ 0, phần ảo p ≠ 0 → 4 phương án ±dấu phân biệt).
"""
import sympy as sp
from sp_common import z_string, gen_pairs, assemble

STT = 5


def gen_params(loai_so, n, seed):
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed)]


def sinh(p, q):
    z = sp.expand(sp.I * (p + q * sp.I))
    re, im = sp.re(z), sp.im(z)  # re=-q, im=p
    stem = f"Tìm số phức liên hợp của số phức $z = i({z_string(p, q)})$."
    correct = f"$\\overline{{z}} = {z_string(re, -im)}$."
    distractors = [
        f"$\\overline{{z}} = {z_string(-re, im)}$.",
        f"$\\overline{{z}} = {z_string(re, im)}$.",
        f"$\\overline{{z}} = {z_string(-re, -im)}$.",
    ]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = (f"Ta có $z = i({z_string(p, q)}) = {z_string(re, im)}$ "
                f"$\\Rightarrow \\overline{{z}} = {z_string(re, -im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
