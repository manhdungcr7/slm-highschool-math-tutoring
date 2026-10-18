# -*- coding: utf-8 -*-
"""STT4 — Vấn đề 7: Quỹ tích của w=(a+bi)z+i khi |z|=R → đường tròn bán kính R·|a+bi|.
Đề gốc: |z|=4, w=(3+4i)z+i → r=20.
Biến đầu vào: a,b (hệ số nhân), R>0 (|z|). Bán kính = R·√(a²+b²). (Số hạng +i không
ảnh hưởng bán kính, chỉ dịch tâm.)
Điều kiện: a,b≠0, R>0.
"""
import random
import sympy as sp
from sp_common import z_string, latex, gen_pairs, rand_val, mc_num

STT = 4


def gen_params(loai_so, n, seed):
    pairs = gen_pairs(loai_so, n, seed)
    rng = random.Random(seed + 5)
    rs = [sp.Abs(rand_val(loai_so, rng)) for _ in pairs]
    return [{"a": a, "b": b, "R": R} for (a, b), R in zip(pairs, rs)]


def sinh(a, b, R):
    radius = sp.simplify(R * sp.sqrt(a ** 2 + b ** 2))
    raw = [R * (a ** 2 + b ** 2), sp.sqrt(a ** 2 + b ** 2), 2 * radius]
    stem = (f"Cho số phức $z$ thỏa mãn $|z| = {latex(R)}$. Biết rằng tập hợp các điểm biểu diễn "
            f"các số phức $w = ({z_string(a, b)})z+i$ là một đường tròn. Tính bán kính $r$ của đường tròn đó.")
    block, dap_an = mc_num(radius, raw, (a, b, R), fmt=lambda v: f"$r = {latex(v)}$.")
    loi_giai = (f"Từ $w = ({z_string(a, b)})z+i$ suy ra $z = \\dfrac{{w-i}}{{{z_string(a, b)}}}$. "
                f"Do $|z|={latex(R)}$ nên $w$ chạy trên đường tròn bán kính "
                f"$r = {latex(R)}\\cdot|{z_string(a, b)}| = {latex(R)}\\cdot{latex(sp.sqrt(a**2+b**2))} = {latex(radius)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
