# -*- coding: utf-8 -*-
"""STT55 — Vấn đề 9: |z|=r1, |w|=r2, khi |z+iw̄+K| nhỏ nhất, tính |z-w| (BĐT tam giác).
Đề gốc: |z|=1,|w|=2, K=6+8i → √29/5.
Chặn dưới |z+iw̄+K|≥|K|-|z|-|w|; dấu bằng khi z=-K·r1/|K|, iw̄=-K·r2/|K|.
Tính z,w rồi suy ra |z-w|. Biến đầu vào: K=p+qi, r1,r2 (>0). Điều kiện: |K|>r1+r2.
"""
import random
import sympy as sp
from sp_common import z_string, latex, join_plus, rand_val, mc_num, neq

STT = 55


def _val(p, q, r1, r2):
    K = p + q * sp.I
    Kmag = sp.sqrt(p ** 2 + q ** 2)
    z = -K * r1 / Kmag
    wbar = sp.I * K * r2 / Kmag
    w = sp.conjugate(wbar)
    diff = sp.expand(z - w)
    return sp.sqrt(sp.simplify(sp.re(diff) ** 2 + sp.im(diff) ** 2)), Kmag


def gen_params(loai_so, n, seed):
    rp, rr = random.Random(seed), random.Random(seed + 6)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 10000:
        tries += 1
        p, q = rand_val(loai_so, rp), rand_val(loai_so, rp)
        r1, r2 = sp.Abs(rand_val(loai_so, rr)), sp.Abs(rand_val(loai_so, rr))
        if not (sp.sqrt(p ** 2 + q ** 2) > r1 + r2):
            continue
        key = (str(p), str(q), str(r1), str(r2))
        if key in seen:
            continue
        seen.add(key)
        out.append({"p": p, "q": q, "r1": r1, "r2": r2})
    return out


def sinh(p, q, r1, r2):
    val, Kmag = _val(p, q, r1, r2)
    raw = [2 * val, sp.simplify(r1 + r2), sp.simplify(Kmag - r1 - r2)]
    stem = (f"Xét các số phức $z, w$ thỏa mãn $|z|={latex(r1)}$ và $|w|={latex(r2)}$. "
            f"Khi $|z+i\\overline{{w}}{join_plus(z_string(p, q))}|$ đạt giá trị nhỏ nhất, $|z-w|$ bằng")
    block, dap_an = mc_num(val, raw, (p, q, r1, r2))
    loi_giai = (
        f"Ta có $|z+i\\overline{{w}}+K|\\ge|K|-|z|-|w|={latex(Kmag)}-{latex(r1)}-{latex(r2)}$ với "
        f"$K={z_string(p, q)}$. Dấu bằng khi $z=-\\dfrac{{K}}{{|K|}}\\cdot{latex(r1)}$ và "
        f"$i\\overline{{w}}=-\\dfrac{{K}}{{|K|}}\\cdot{latex(r2)}$. Tính trực tiếp được $|z-w|={latex(val)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
