# -*- coding: utf-8 -*-
"""STT38 — Vấn đề 6: Giải z+p+qi-|z|i=0 (chứa |z|), tính S=a+m·b.
Đề gốc: z+1+3i-|z|i=0, S=a+3b → -5.
Biến đầu vào: p,q (số phức cho trước p+qi); hệ số m (nguyên) trong S=a+m·b.
Đặt z=a+bi: a+p=0 ⟹ a=-p; b+q-√(a²+b²)=0 ⟹ b=(p²-q²)/(2q).
Điều kiện: q>0 (để b+q=√(a²+b²) ≥ 0, nghiệm hợp lệ).
"""
import random
import sympy as sp
from sp_common import z_string, latex, join_plus, signed_term, gen_pairs, mc_num

STT = 38


def gen_params(loai_so, n, seed):
    pairs = gen_pairs(loai_so, n, seed, cond=lambda p, q: q > 0)
    rng = random.Random(seed + 11)
    ms = [sp.Integer(rng.choice([x for x in range(-6, 7) if abs(x) >= 2])) for _ in pairs]
    return [{"p": p, "q": q, "m": m} for (p, q), m in zip(pairs, ms)]


def sinh(p, q, m):
    a = -p
    b = sp.simplify((p ** 2 - q ** 2) / (2 * q))
    S = sp.simplify(a + m * b)
    raw = [-S, sp.simplify(a - b), sp.simplify(a + b)]
    stem = (f"Cho số phức $z = a+bi$ $(a,b \\in \\mathbb{{R}})$ thỏa mãn "
            f"$z{join_plus(z_string(p, q))}-|z|i = 0$. Tính $S = a{('+' + latex(m)) if m > 0 else latex(m)}b$.")
    block, dap_an = mc_num(S, raw, (p, q, m), fmt=lambda v: f"$S = {latex(v)}$.")
    m_str = ('+' + latex(m)) if m > 0 else latex(m)
    loi_giai = (
        f"$z{join_plus(z_string(p, q))}-|z|i=0 \\Leftrightarrow a+bi{join_plus(z_string(p, q))}-\\sqrt{{a^2+b^2}}\\,i=0 "
        f"\\Leftrightarrow (a{signed_term(p, '')})+(b{signed_term(q, '')}-\\sqrt{{a^2+b^2}})i=0$\n"
        f"$\\Leftrightarrow \\begin{{cases}} a{signed_term(p, '')}=0 \\\\ b{signed_term(q, '')}-\\sqrt{{a^2+b^2}}=0 \\end{{cases}} "
        f"\\Leftrightarrow \\begin{{cases}} a={latex(a)} \\\\ \\sqrt{{b^2{signed_term(a**2,'')}}}=b{signed_term(q, '')} \\end{{cases}} "
        f"\\Leftrightarrow \\begin{{cases}} a={latex(a)} \\\\ b={latex(b)} \\end{{cases}}$.\n"
        f"$S=a{m_str}b={latex(S)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
