# -*- coding: utf-8 -*-
"""STT60 — Vấn đề 9: |z|=|w|=R, |z-w|=R√2, min P=|z-A|+|w-B|.
Đề gốc: R=4, A=1+i, B=-3+4i → √13.
Từ |z|=|w|, |z-w|=R√2 suy ra z=±iw. Xét hai trường hợp, dùng BĐT tam giác:
  z=iw → P≥|-iA-B|;  z=-iw → P≥|iA-B|.  minP = min hai giá trị đó.
Biến đầu vào: R>0, A=(ax,ay), B=(bx,by).
"""
import random
import sympy as sp
from sp_common import latex, signed_term, rand_val, mc_num, neq

STT = 60


def _cmod(e):
    e = sp.expand(e)
    return sp.sqrt(sp.simplify(sp.re(e) ** 2 + sp.im(e) ** 2))


def _bounds(ax, ay, bx, by):
    A, B = ax + ay * sp.I, bx + by * sp.I
    return _cmod(-sp.I * A - B), _cmod(sp.I * A - B)


def gen_params(loai_so, n, seed):
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 12000:
        tries += 1
        R = sp.Abs(rand_val(loai_so, rng))
        ax, ay, bx, by = (rand_val(loai_so, rng, -6, 6) for _ in range(4))
        b1, b2 = _bounds(ax, ay, bx, by)
        if not neq(b1, b2):
            continue
        key = (str(R), str(ax), str(ay), str(bx), str(by))
        if key in seen:
            continue
        seen.add(key)
        out.append({"R": R, "ax": ax, "ay": ay, "bx": bx, "by": by})
    return out


def sinh(R, ax, ay, bx, by):
    b1, b2 = _bounds(ax, ay, bx, by)
    ans = b1 if float(b1) <= float(b2) else b2
    other = b2 if float(b1) <= float(b2) else b1
    raw = [other, sp.simplify(other / 2), 2 * ans]
    Rs = latex(sp.simplify(R * sp.sqrt(2)))
    A = f"z{signed_term(-ax, '')}{signed_term(-ay, 'i')}"
    Bp = f"w{signed_term(-bx, '')}{signed_term(-by, 'i')}"
    stem = (f"Xét các số phức $z$ và $w$ thay đổi thỏa mãn $|z|=|w|={latex(R)}$ và $|z-w|={Rs}$. "
            f"Giá trị nhỏ nhất của $P=|{A}|+|{Bp}|$ bằng")
    block, dap_an = mc_num(ans, raw, (R, ax, ay, bx, by))
    loi_giai = (
        f"Từ $|z|=|w|$ và $|z-w|={Rs}$ suy ra $z=iw$ hoặc $z=-iw$. Với mỗi trường hợp dùng bất đẳng thức "
        f"tam giác $|w-C_1|+|w-C_2|\\ge|C_1-C_2|$, được hai chặn dưới ${latex(b1)}$ và ${latex(b2)}$. "
        f"Vậy $\\min P={latex(ans)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
