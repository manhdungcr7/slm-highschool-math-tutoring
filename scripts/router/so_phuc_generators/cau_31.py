# -*- coding: utf-8 -*-
"""STT31 — Vấn đề 7: Quỹ tích |z+(a+bi)|=r → đường tròn, tìm tâm.
Đề gốc: |z+2i|=1 → tâm (0;-2).
Biến đầu vào: a,b (số phức cộng vào z), r>0 (bán kính). Tâm I(-a;-b).
Điều kiện: a,b≠0, |a|≠|b| (4 phương án tọa độ phân biệt).
"""
import random
import sympy as sp
from sp_common import diem, latex, latex_sq, signed_term, gen_pairs, rand_val, assemble, neq

STT = 31


def gen_params(loai_so, n, seed):
    pairs = gen_pairs(loai_so, n, seed, cond=lambda a, b: neq(sp.Abs(a), sp.Abs(b)))
    rng = random.Random(seed + 3)
    rs = [sp.Abs(rand_val(loai_so, rng)) for _ in pairs]
    return [{"a": a, "b": b, "r": r} for (a, b), r in zip(pairs, rs)]


def sinh(a, b, r):
    inside = f"z{signed_term(a, '')}{signed_term(b, 'i')}"
    stem = (f"Trên mặt phẳng tọa độ, biết tập hợp điểm biểu diễn các số phức $z$ thỏa mãn "
            f"$|{inside}|={latex(r)}$ là một đường tròn. Tâm của đường tròn đó có tọa độ là")
    correct = f"${diem(-a, -b)}$."
    distractors = [f"${diem(a, b)}$.", f"${diem(-a, b)}$.", f"${diem(a, -b)}$."]
    block, dap_an = assemble(correct, distractors, (a, b, r))
    loi_giai = (f"Gọi $z=x+yi$. Ta có $|{inside}|={latex(r)} \\Leftrightarrow "
                f"(x{signed_term(a, '')})^2+(y{signed_term(b, '')})^2={latex_sq(r)}^2$. "
                f"Vậy tâm $I{diem(-a, -b)}$, bán kính $R={latex(r)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
