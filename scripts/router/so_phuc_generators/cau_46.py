# -*- coding: utf-8 -*-
"""STT46 — Vấn đề 7: w=(p+iz)/(1+z), |z|=r → đường tròn ảnh, tìm bán kính.
Đề gốc: p=3, |z|=√2 → 2√5. Giữ cố định "1+z", "iz"; tổng quát hóa p và r=|z|.
Cách giải: z=(p-w)/(w-i), |z|=r ⟹ |p-w|=r|w-i|, bình phương → phương trình
đường tròn ẩn (X,Y) của w; đọc bán kính.
Điều kiện: r>0, r≠1 (để chia được cho 1-r²), bán kính² > 0.
"""
import random
import sympy as sp
from sp_common import latex, rand_val, mc_num, neq


STT = 46
X, Y = sp.symbols("X Y", real=True)


def _radius(p, r):
    eq = sp.expand((X - p) ** 2 + Y ** 2 - r ** 2 * (X ** 2 + (Y - 1) ** 2))
    c2 = sp.Poly(eq, X, Y).coeff_monomial(X ** 2)
    eqn = sp.expand(eq / c2)
    poly = sp.Poly(eqn, X, Y)
    D = poly.coeff_monomial(X)
    E = poly.coeff_monomial(Y)
    F = poly.coeff_monomial(1)
    h, k = -D / 2, -E / 2
    R2 = sp.simplify(h ** 2 + k ** 2 - F)
    return R2


def gen_params(loai_so, n, seed):
    rp = random.Random(seed)
    rr = random.Random(seed + 13)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 8000:
        tries += 1
        p = rand_val(loai_so, rp)
        r = sp.Abs(rand_val(loai_so, rr))
        if not (neq(r ** 2, 1) and _radius(p, r) > 0):
            continue
        key = (str(p), str(r))
        if key in seen:
            continue
        seen.add(key)
        out.append({"p": p, "r": r})
    return out


def sinh(p, r):
    R2 = _radius(p, r)
    radius = sp.sqrt(R2)
    raw = [R2, sp.simplify(radius / 2), 2 * radius]
    stem = (f"Xét số phức $z$ thỏa mãn $|z|={latex(r)}$. Trên mặt phẳng tọa độ $Oxy$, tập hợp điểm biểu diễn "
            f"các số phức $w=\\dfrac{{{latex(p)}+iz}}{{1+z}}$ là một đường tròn có bán kính bằng")
    block, dap_an = mc_num(radius, raw, (p, r))
    loi_giai = (
        f"Từ $w=\\dfrac{{{latex(p)}+iz}}{{1+z}}$ suy ra $z=\\dfrac{{{latex(p)}-w}}{{w-i}}$. Lấy môđun và thay "
        f"$|z|={latex(r)}$: $|{latex(p)}-w|={latex(r)}\\,|w-i|$. Bình phương, biến đổi được phương trình đường tròn "
        f"bán kính $R={latex(radius)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
