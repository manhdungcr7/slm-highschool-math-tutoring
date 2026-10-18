# -*- coding: utf-8 -*-
"""STT54 — Vấn đề 6: Giải iz=p+qi rồi tìm liên hợp của z. Đề gốc: iz=6+5i → z̄=5+6i.
Biến đầu vào: p,q. z = (p+qi)/i = q - p·i ⟹ z̄ = q + p·i.
Điều kiện: p,q≠0 (4 phương án đổi dấu phân biệt).
"""
import sympy as sp
from sp_common import z_string, gen_pairs, assemble

STT = 54


def gen_params(loai_so, n, seed):
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed)]


def sinh(p, q):
    z = sp.expand((p + q * sp.I) / sp.I)  # = q - p i
    re_z, im_z = sp.re(z), sp.im(z)       # re=q, im=-p
    zb_re, zb_im = re_z, -im_z            # z̄ = q + p i
    stem = f"Cho số phức $z$ thỏa mãn $iz = {z_string(p, q)}$. Số phức liên hợp của $z$ là"
    correct = f"$\\overline{{z}} = {z_string(zb_re, zb_im)}$."
    distractors = [
        f"$\\overline{{z}} = {z_string(zb_re, -zb_im)}$.",
        f"$\\overline{{z}} = {z_string(-zb_re, zb_im)}$.",
        f"$\\overline{{z}} = {z_string(-zb_re, -zb_im)}$.",
    ]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = (f"Ta có $iz = {z_string(p, q)} \\Leftrightarrow z = \\dfrac{{{z_string(p, q)}}}{{i}} = "
                f"{z_string(re_z, im_z)}$. Vậy $\\overline{{z}} = {z_string(zb_re, zb_im)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
