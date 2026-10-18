# -*- coding: utf-8 -*-
"""STT12 — Vấn đề 9: z thuộc đoạn AB (|z-A|+|z-B|=AB), min/max |z-C|, tính P=m+M.
Đề gốc: A(-2;1),B(4;7),C(1;-1) → P=(5√2+2√73)/2.
Tham số hóa z=A+t(B-A), t∈[0;1]; |z-C|² là hàm bậc hai theo t; khảo sát trên đoạn.
Biến đầu vào: A,B,C (tọa độ). Điều kiện: A≠B, kết quả không quá cồng kềnh.
"""
import random
import sympy as sp
from sp_common import latex, signed_term, rand_val, mc_num

STT = 12
_t = sp.symbols("t", real=True)


def _mM(ax, ay, bx, by, cx, cy):
    x = ax + _t * (bx - ax)
    y = ay + _t * (by - ay)
    f = sp.expand((x - cx) ** 2 + (y - cy) ** 2)
    cand = [f.subs(_t, 0), f.subs(_t, 1)]
    for tt in sp.solve(sp.diff(f, _t), _t):
        if tt.is_real and 0 <= tt <= 1:
            cand.append(f.subs(_t, tt))
    fmin = min(cand, key=lambda e: float(e))
    fmax = max(cand, key=lambda e: float(e))
    return sp.sqrt(sp.simplify(fmin)), sp.sqrt(sp.simplify(fmax))


def gen_params(loai_so, n, seed):
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 15000:
        tries += 1
        ax, ay, bx, by, cx, cy = (rand_val(loai_so, rng, -6, 6) for _ in range(6))
        if (ax, ay) == (bx, by):
            continue
        try:
            m, M = _mM(ax, ay, bx, by, cx, cy)
        except Exception:
            continue
        if m == M or len(str(m)) > 40 or len(str(M)) > 40:
            continue
        key = tuple(str(x) for x in (ax, ay, bx, by, cx, cy))
        if key in seen:
            continue
        seen.add(key)
        out.append({"ax": ax, "ay": ay, "bx": bx, "by": by, "cx": cx, "cy": cy})
    return out


def sinh(ax, ay, bx, by, cx, cy):
    m, M = _mM(ax, ay, bx, by, cx, cy)
    P = sp.simplify(m + M)
    AB = sp.sqrt(sp.simplify((bx - ax) ** 2 + (by - ay) ** 2))
    raw = [sp.simplify(M - m), sp.simplify(2 * M), sp.simplify(m * M)]
    zA = f"z{signed_term(-ax, '')}{signed_term(-ay, 'i')}"
    zB = f"z{signed_term(-bx, '')}{signed_term(-by, 'i')}"
    zC = f"z{signed_term(-cx, '')}{signed_term(-cy, 'i')}"
    stem = (f"Xét các số phức $z$ thỏa mãn $|{zA}|+|{zB}| = {latex(AB)}$. Gọi $m, M$ lần lượt là giá trị nhỏ nhất, "
            f"giá trị lớn nhất của $|{zC}|$. Tính $P = m+M$.")
    block, dap_an = mc_num(P, raw, (ax, ay, bx, by, cx, cy), fmt=lambda v: f"$P = {latex(v)}$.")
    loi_giai = (
        f"Vì $|{zA}|+|{zB}|=AB$ nên điểm biểu diễn $z$ thuộc đoạn thẳng $AB$. Tham số hóa và đưa $|{zC}|^2$ về "
        f"hàm bậc hai trên đoạn, tìm được $m={latex(m)}$, $M={latex(M)}$. Vậy $P=m+M={latex(P)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
