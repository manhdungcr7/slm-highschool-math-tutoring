# -*- coding: utf-8 -*-
"""STT7 — Vấn đề 6: Giải (1+i)z+2z̄=p+qi bằng đồng nhất phần thực/ảo, tính P=a+b.
Đề gốc: (1+i)z+2z̄=3+2i → P=-1.
Biến đầu vào: p,q = phần thực/ảo của VẾ PHẢI (số phức cho trước). Hệ số (1+i), 2
giữ CỐ ĐỊNH (là cấu trúc bài toán). Đặt z=a+bi, đồng nhất → hệ, giải a,b, P=a+b.
Điều kiện: P=a+b ≠ 0 (để phương án P, -P phân biệt) ⟺ p ≠ 2q.
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, mc_num, neq

STT = 7


def _solve(p, q):
    a_, b_ = sp.symbols("a_ b_", real=True)
    z = a_ + b_ * sp.I
    eq = sp.expand((1 + sp.I) * z + 2 * sp.conjugate(z) - (p + q * sp.I))
    sol = sp.solve([sp.re(eq), sp.im(eq)], [a_, b_])
    return sol[a_], sol[b_]


def gen_params(loai_so, n, seed):
    cond = lambda p, q: neq(p, 2 * q)
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(p, q):
    A, B = _solve(p, q)
    P = sp.simplify(A + B)
    raw = [-P, sp.simplify(A - B), 2 * P]
    eq_str = f"(1+i)z+2\\overline{{z}} = {z_string(p, q)}"
    stem = (f"Cho số phức $z = a+bi$ $(a,b \\in \\mathbb{{R}})$ thỏa mãn "
            f"${eq_str}$. Tính $P = a+b$.")
    block, dap_an = mc_num(P, raw, (p, q), fmt=lambda v: f"$P = {latex(v)}$.")
    loi_giai = (
        f"Ta có: ${eq_str}$ $(1)$.\n"
        f"Ta có $z = a+bi \\Rightarrow \\overline{{z}} = a-bi$. Thay vào $(1)$ ta được:\n"
        f"$(1+i)(a+bi)+2(a-bi) = {z_string(p, q)} \\Leftrightarrow "
        f"(a-b)i+(3a-b) = {z_string(p, q)} \\Leftrightarrow "
        f"\\begin{{cases}} 3a-b={latex(p)} \\\\ a-b={latex(q)} \\end{{cases}} \\Leftrightarrow "
        f"\\begin{{cases}} a={latex(A)} \\\\ b={latex(B)} \\end{{cases}} \\Rightarrow P={latex(P)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
