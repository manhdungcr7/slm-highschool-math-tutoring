# -*- coding: utf-8 -*-
"""STT65 — Vấn đề 9: |z1|=|z2|=2|z3|=R và c1(z1+z2)z3=c2·z1z2, tính diện tích ΔABC.
Đề gốc: R=2, c1=8, c2=3 → √55/16.
Biến đổi bằng liên hợp về quan hệ vectơ, được hình thoi; đặt K=4c2/c1, diện tích:
  S = (R²/2)·|K/2-1|·√(1-K²/16).
Biến đầu vào: R>0, c1, c2 với |c2|<|c1| (⟺ |K|<4) và K≠2.
"""
import random
import sympy as sp
from sp_common import latex, rand_val, mc_num, neq

STT = 65


def gen_params(loai_so, n, seed):
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 12000:
        tries += 1
        R = sp.Abs(rand_val(loai_so, rng))
        c1 = rand_val(loai_so, rng)
        c2 = rand_val(loai_so, rng)
        if c1 == 0:
            continue
        K = sp.simplify(4 * c2 / c1)
        if not (sp.Abs(K) < 4) or K == 2 or R == 0:
            continue
        key = (str(R), str(c1), str(c2))
        if key in seen:
            continue
        seen.add(key)
        out.append({"R": R, "c1": c1, "c2": c2})
    return out


def _coef(c):
    """Hệ số đứng trước 1 tích/biến: ẩn '1'/'-1' (vd '1z' -> 'z', '-1z' -> '-z')."""
    if c == 1:
        return ""
    if c == -1:
        return "-"
    return latex(c)


def sinh(R, c1, c2):
    K = sp.simplify(4 * c2 / c1)
    S = sp.simplify((R ** 2 / 2) * sp.Abs(K / 2 - 1) * sp.sqrt(1 - K ** 2 / 16))
    raw = [2 * S, sp.simplify(S / 2), sp.simplify(S / 4)]
    stem = (f"Cho các số phức $z_1, z_2, z_3$ thỏa mãn $|z_1|=|z_2|=2|z_3|={latex(R)}$ và "
            f"${_coef(c1)}(z_1+z_2)z_3={_coef(c2)}z_1z_2$. Gọi $A, B, C$ lần lượt là các điểm biểu diễn của "
            f"$z_1, z_2, z_3$ trên mặt phẳng tọa độ. Diện tích tam giác $ABC$ bằng")
    block, dap_an = mc_num(S, raw, (R, c1, c2))
    loi_giai = (
        f"Chia hai vế cho $z_1z_2z_3$ và dùng $\\overline{{z}}=|z|^2/z$, đưa về "
        f"$\\overline{{z_1}}+\\overline{{z_2}}=K\\,\\overline{{z_3}}$ với $K=\\dfrac{{4\\cdot{latex(c2)}}}{{{latex(c1)}}}={latex(K)}$. "
        f"Suy ra cấu hình hình thoi, tính được $S=\\dfrac{{R^2}}{{2}}\\left|\\dfrac{{K}}{{2}}-1\\right|\\sqrt{{1-\\dfrac{{K^2}}{{16}}}}={latex(S)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
