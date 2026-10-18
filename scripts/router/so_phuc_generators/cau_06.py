# -*- coding: utf-8 -*-
"""STT6 — Vấn đề 6: Giải z(p+qi)+ki=m (bậc nhất), tính môđun. Đề gốc: z(2-i)+13i=1 → √34.
Biến đầu vào: p,q (số nhân, không đồng thời 0), k, m. Phương trình:
  z(p+qi) + k·i = m  ⟺  z = (m - k·i)/(p+qi),  |z| = √(m²+k²)/√(p²+q²).
Điều kiện: (p,q)≠(0,0), k,m≠0 (bảo đảm bởi bộ sinh số). Khoảng số -6..6 cho gọn.
"""
import sympy as sp
from sp_common import z_string, latex, latex_sq, signed_term, gen_quads, mc_num

STT = 6


def gen_params(loai_so, n, seed):
    return [{"p": p, "q": q, "k": k, "m": m}
            for p, q, k, m in gen_quads(loai_so, n, seed, lo=-6, hi=6)]


def sinh(p, q, k, m):
    conj = p - q * sp.I
    num = sp.expand((m - k * sp.I) * conj)
    den = sp.expand((p + q * sp.I) * conj)  # = p²+q² (số thực)
    z = sp.simplify((m - k * sp.I) / (p + q * sp.I))
    re, im = sp.re(z), sp.im(z)
    modun = sp.sqrt(sp.simplify(re ** 2 + im ** 2))
    raw = [sp.simplify(modun ** 2), sp.Abs(re) + sp.Abs(im), 2 * modun]
    stem = f"Tính môđun của số phức $z$ thỏa mãn $z({z_string(p, q)}){signed_term(k)} = {latex(m)}$."
    block, dap_an = mc_num(modun, raw, (p, q, k, m), fmt=lambda v: f"$|z| = {latex(v)}$.")
    loi_giai = (
        f"Ta có: $z({z_string(p, q)}){signed_term(k)} = {latex(m)} \\Leftrightarrow "
        f"z = \\dfrac{{{z_string(m, -k)}}}{{{z_string(p, q)}}} \\Leftrightarrow "
        f"z = \\dfrac{{({z_string(m, -k)})({z_string(p, -q)})}}{{({z_string(p, q)})({z_string(p, -q)})}} = {z_string(re, im)}$. "
        f"$|z| = \\sqrt{{{latex_sq(re)}^2+{latex_sq(im)}^2}} = {latex(modun)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
