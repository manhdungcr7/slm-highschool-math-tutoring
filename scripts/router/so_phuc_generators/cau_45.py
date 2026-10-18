# -*- coding: utf-8 -*-
"""STT45 — Vấn đề 6: Giải 3(z̄-i)-(2+3i)z=p+qi bằng đồng nhất phần thực/ảo, tính |z|.
Đề gốc: 3(z̄-i)-(2+3i)z=7-16i → √5.
Biến đầu vào: p,q = phần thực/ảo của VẾ PHẢI. Hệ số 3, (2+3i), -i giữ CỐ ĐỊNH.
Điều kiện: nghiệm z ≠ 0 (để môđun > 0).
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, mc_num, neq

STT = 45


def _solve(p, q):
    a_, b_ = sp.symbols("a_ b_", real=True)
    z = a_ + b_ * sp.I
    eq = sp.expand(3 * (sp.conjugate(z) - sp.I) - (2 + 3 * sp.I) * z - (p + q * sp.I))
    sol = sp.solve([sp.re(eq), sp.im(eq)], [a_, b_])
    return sol[a_], sol[b_]


def gen_params(loai_so, n, seed):
    def cond(p, q):
        A, B = _solve(p, q)
        return neq(A, 0) or neq(B, 0)
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(p, q):
    A, B = _solve(p, q)
    modun = sp.sqrt(sp.simplify(A ** 2 + B ** 2))
    raw = [sp.simplify(modun ** 2), sp.Abs(A) + sp.Abs(B), 2 * modun]
    stem = (f"Cho số phức $z$ thoả mãn $3(\\overline{{z}}-i)-(2+3i)z = {z_string(p, q)}$. "
            f"Mô-đun của $z$ bằng")
    block, dap_an = mc_num(modun, raw, (p, q))
    loi_giai = (
        f"Đặt $z=a+bi$. Đồng nhất phần thực, phần ảo ta được $a = {latex(A)}$, $b = {latex(B)}$. "
        f"Vậy $|z| = {latex(modun)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
