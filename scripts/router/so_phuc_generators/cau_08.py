# -*- coding: utf-8 -*-
"""STT8 — Vấn đề 6: (a+bi)|z| = k/z + i(a+bi), xác định khoảng chứa |z|.
Đề gốc: (1+2i)|z|=√10/z-2+i → |z|=1, khoảng 1/2<|z|<3/2.
Đặt t=|z|: (a+bi)(t-i)=k/z, lấy môđun: √(a²+b²)·√(t²+1)=k/t
  ⟹ (a²+b²)t⁴+(a²+b²)t²-k²=0 ⟹ t²=u (nghiệm dương) ⟹ t.
Biến đầu vào: a,b (hệ số a+bi), k>0. Đáp án: khoảng (m-½; m+½) với m=round(t).
Điều kiện: t>½ (để m≥1, khoảng dương).
"""
import random
import sympy as sp
from sp_common import z_string, latex, signed_term, rand_val, assemble

STT = 8


def _t(a, b, k):
    s = a ** 2 + b ** 2
    u = (-s + sp.sqrt(s ** 2 + 4 * s * k ** 2)) / (2 * s)  # nghiệm dương của s·u²+s·u-k²=0
    return sp.sqrt(sp.simplify(u))


def gen_params(loai_so, n, seed):
    ra, rk = random.Random(seed), random.Random(seed + 6)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 10000:
        tries += 1
        a, b = rand_val(loai_so, ra), rand_val(loai_so, ra)
        k = sp.Abs(rand_val(loai_so, rk))
        try:
            tv = float(_t(a, b, k))
        except Exception:
            continue
        if tv <= 0.6 or tv > 12:
            continue
        key = (str(a), str(b), str(k))
        if key in seen:
            continue
        seen.add(key)
        out.append({"a": a, "b": b, "k": k})
    return out


def sinh(a, b, k):
    t = _t(a, b, k)
    m = sp.Integer(round(float(t)))
    L, H = m - sp.Rational(1, 2), m + sp.Rational(1, 2)
    stem = (f"Xét số phức $z$ thỏa mãn $({z_string(a, b)})|z| = \\dfrac{{{latex(k)}}}{{z}}"
            f"{signed_term(-b, '')}{signed_term(a, 'i')}$. Mệnh đề nào dưới đây đúng?")
    correct = f"${latex(L)} < |z| < {latex(H)}$."
    distractors = [f"$|z| < {latex(L)}$.", f"$|z| > {latex(H)}$.", f"$|z| = {latex(m)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, k))
    loi_giai = (
        f"Ta có: $({z_string(a, b)})|z| = \\dfrac{{{latex(k)}}}{{z}}{signed_term(-b, '')}{signed_term(a, 'i')} "
        f"\\Leftrightarrow ({z_string(a, b)})|z| = \\dfrac{{{latex(k)}}}{{z}}+i({z_string(a, b)}) "
        f"\\Leftrightarrow ({z_string(a, b)})(|z|-i) = \\dfrac{{{latex(k)}}}{{z}}$.\n"
        f"$\\Rightarrow |({z_string(a, b)})(|z|-i)| = \\left|\\dfrac{{{latex(k)}}}{{z}}\\right| "
        f"\\Rightarrow |{z_string(a, b)}|\\cdot||z|-i| = \\dfrac{{{latex(k)}}}{{|z|}}$ $(*)$.\n"
        f"Đặt $t=|z|>0$. $(*) \\Leftrightarrow \\sqrt{{{latex(a**2+b**2)}}}\\cdot\\sqrt{{t^2+1}}=\\dfrac{{{latex(k)}}}{{t}} "
        f"\\Rightarrow t={latex(t)}$ (do $t>0$). Vậy $|z|=t={latex(t)} \\Rightarrow {latex(L)}<|z|<{latex(H)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
