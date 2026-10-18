# -*- coding: utf-8 -*-
"""STT27 — Vấn đề 9: Re(1/(|z|-z))=1/c → đường tròn (O;c/2); max của
P=|z1-Ki|²-|z2-Ki|² khi |z1-z2|=d.
Đề gốc: 1/8, K=5, d=2 → 20.
Quỹ tích |z|=c/2=R (đường tròn tâm O). P=AI²-BI²=2·OI·AB ≤ 2·OI·d = 2·K·d
(với I(0;K), OI=K). max P = 2·K·d.
Biến đầu vào: c>0 (Re=1/c), K>0, d>0 với d≤c (=2R).
"""
import random
import sympy as sp
from sp_common import latex, rand_val, mc_num

STT = 27


def gen_params(loai_so, n, seed):
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 10000:
        tries += 1
        c = sp.Abs(rand_val(loai_so, rng))
        K = sp.Abs(rand_val(loai_so, rng))
        d = sp.Abs(rand_val(loai_so, rng))
        if c == 0 or not (d <= c):
            continue
        key = (str(c), str(K), str(d))
        if key in seen:
            continue
        seen.add(key)
        out.append({"c": c, "K": K, "d": d})
    return out


def sinh(c, K, d):
    R = sp.simplify(c / 2)
    ans = sp.simplify(2 * K * d)
    raw = [sp.simplify(K * d), sp.simplify(4 * K * d), sp.simplify(K * R)]
    K_i = "i" if K == 1 else f"{latex(K)}i"  # K luôn dương: bỏ hệ số 1 trước i, không hiện dấu
    stem = (f"Gọi $S$ là tập hợp tất cả các số phức $z$ sao cho số phức $w=\\dfrac{{1}}{{|z|-z}}$ có phần thực bằng "
            f"$\\dfrac{{1}}{{{latex(c)}}}$. Xét các số phức $z_1, z_2 \\in S$ thỏa mãn $|z_1-z_2|={latex(d)}$, "
            f"giá trị lớn nhất của $P = |z_1-{K_i}|^2 - |z_2-{K_i}|^2$ bằng")
    block, dap_an = mc_num(ans, raw, (c, K, d))
    loi_giai = (
        f"Biến đổi phần thực của $w$ bằng $\\dfrac{{1}}{{{latex(c)}}}$ được $|z|={latex(R)}$ (đường tròn tâm $O$). "
        f"Gọi $A,B$ biểu diễn $z_1,z_2$, $I(0;{latex(K)})$. Khi đó "
        f"$P=AI^2-BI^2=2\\overrightarrow{{OI}}\\cdot\\overrightarrow{{AB}}\\le2\\cdot OI\\cdot AB=2\\cdot{latex(K)}\\cdot{latex(d)}={latex(ans)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
