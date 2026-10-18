# -*- coding: utf-8 -*-
"""STT42 — Vấn đề 6: Đếm z thỏa |z|(z-p-qi)+ki=(c+di)z.
Đề gốc: |z|(z-3-i)+2i=(4-i)z → 3.
Đặt t=|z|: z(t-(c+di)) = t(p+qi)-ki, lấy môđun hai vế:
  t²·((t-c)²+d²) = (tp)² + (tq-k)²  → đa thức bậc 4 theo t. Mỗi t≥0 → một z.
Biến đầu vào: p,q,k,c,d. Số nghiệm t≥0 ∈ [1;4].
"""
import random
import numpy as np
import sympy as sp
from sp_common import z_string, latex, signed_term, rand_val, assemble


STT = 42
_t = sp.symbols("t")


def _count(p, q, k, c, d):
    expr = sp.expand(_t ** 2 * ((_t - c) ** 2 + d ** 2) - ((_t * p) ** 2 + (_t * q - k) ** 2))
    poly = sp.Poly(expr, _t)
    if poly.degree() < 1:
        return 0
    roots = np.roots([complex(x) for x in poly.all_coeffs()])
    uniq = []
    for rt in roots:
        if abs(rt.imag) < 1e-7 and rt.real >= -1e-7:
            x = round(float(rt.real), 6)
            if not any(abs(x - u) < 1e-4 for u in uniq):
                uniq.append(x)
    return len(uniq)


def gen_params(loai_so, n, seed):
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 12000:
        tries += 1
        p, q, k, c, d = (rand_val(loai_so, rng, -6, 6) for _ in range(5))
        try:
            cnt = _count(p, q, k, c, d)
        except Exception:
            continue
        if not (1 <= cnt <= 4):
            continue
        key = tuple(str(x) for x in (p, q, k, c, d))
        if key in seen:
            continue
        seen.add(key)
        out.append({"p": p, "q": q, "k": k, "c": c, "d": d})
    return out


def sinh(p, q, k, c, d):
    stem = (f"Có bao nhiêu số phức $z$ thỏa mãn $|z|(z{signed_term(-p, '')}{signed_term(-q, 'i')})"
            f"{signed_term(k, 'i')}=({z_string(c, d)})z$?")

    expr = sp.expand(_t ** 2 * ((_t - c) ** 2 + d ** 2) - ((_t * p) ** 2 + (_t * q - k) ** 2))
    poly = sp.Poly(expr, _t)
    roots = np.roots([complex(x) for x in poly.all_coeffs()])
    uniq_t = []
    for rt in roots:
        if abs(rt.imag) < 1e-7 and not any(abs(rt.real - u) < 1e-4 for u in uniq_t):
            uniq_t.append(rt.real)
    valid_t = sorted(t for t in uniq_t if t >= -1e-7)
    cnt = len(valid_t)
    correct = f"${cnt}$."
    distractors = [f"${max(cnt - 1, 0)}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (p, q, k, c, d))

    t_list_txt = ", ".join(f"t\\approx{round(t,4)}".replace(".", ",") for t in uniq_t)
    loi_giai = (
        f"Ta có $|z|(z{signed_term(-p, '')}{signed_term(-q, 'i')}){signed_term(k, 'i')}=({z_string(c, d)})z "
        f"\\Leftrightarrow z(|z|{signed_term(-c, '')}{signed_term(-d, 'i')})=|z|({z_string(p, q)}){signed_term(-k, 'i')}$.\n"
        f"Đặt $t=|z|\\ge0,\\ t\\in\\mathbb{{R}}$. Lấy mô-đun hai vế ta được\n"
        f"$t\\cdot|t{signed_term(-c, '')}{signed_term(-d, 'i')}| = |t\\cdot{latex(p)}+(t\\cdot{latex(q)}{signed_term(-k, '')})i|$\n"
        f"$\\Leftrightarrow t\\sqrt{{(t{signed_term(-c, '')})^2+({latex(d)})^2}} = \\sqrt{{(t\\cdot{latex(p)})^2+(t\\cdot{latex(q)}{signed_term(-k, '')})^2}}$\n"
        f"$\\Leftrightarrow {sp.latex(expr)}=0$, giải (bằng số) được: ${t_list_txt}$.\n"
        f"Do đó có ${cnt}$ giá trị $t\\ge0$ thỏa mãn.\n"
        f"Mặt khác, với mỗi $t\\ge0$, ta có $z=\\dfrac{{t({z_string(p, q)}){signed_term(-k, 'i')}}}{{t{signed_term(-c, '')}{signed_term(-d, 'i')}}}$ "
        f"nên có duy nhất một số phức $z$ thỏa mãn. Vậy có ${cnt}$ số phức thỏa mãn yêu cầu bài toán."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
