# -*- coding: utf-8 -*-
"""STT25 — Vấn đề 6: Giải iz̄=p+qi rồi tìm phần ảo của z. Đề gốc: iz̄=5+2i → phần ảo 5.
Biến đầu vào: p,q. z̄ = (p+qi)/i = q - p·i ⟹ z = q + p·i, phần ảo của z = p.
Điều kiện: p,q≠0, |p|≠|q| (4 phương án p, -p, q, -q phân biệt).
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble, neq

STT = 25


def gen_params(loai_so, n, seed):
    cond = lambda p, q: neq(sp.Abs(p), sp.Abs(q))
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(p, q):
    zbar = sp.expand((p + q * sp.I) / sp.I)  # = q - p i
    z = sp.conjugate(zbar)                   # = q + p i
    im_z = sp.im(z)                          # = p
    stem = f"Cho số phức $z$ thỏa mãn $i\\overline{{z}} = {z_string(p, q)}$. Phần ảo của $z$ bằng"
    correct = f"${latex(im_z)}$."
    distractors = [f"${latex(-im_z)}$.", f"${latex(q)}$.", f"${latex(-q)}$."]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = (f"Ta có $\\overline{{z}} = \\dfrac{{{z_string(p, q)}}}{{i}} = {z_string(sp.re(zbar), sp.im(zbar))}$, "
                f"suy ra $z = {z_string(sp.re(z), sp.im(z))}$. Phần ảo của $z$ bằng ${latex(im_z)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
