# -*- coding: utf-8 -*-
"""STT32 — Vấn đề 9: |z²-C|=k|z|, tính M²+m² của |z| (bất đẳng thức B.C.S).
Đề gốc: |z²-3-4i|=2|z| → 14.
Đặt t=|z|²: t²-(k²+2|C|)t+|C|² ≤ 0, hai biên là m², M². Theo Vi-ét:
  M²+m² = k²+2|C| = k²+2√(c1²+c2²).
Biến đầu vào: C=c1+c2 i, k>0.
"""
import random
import sympy as sp
from sp_common import z_string, latex, latex_sq, signed_term, rand_val, mc_num

STT = 32


def gen_params(loai_so, n, seed):
    rc, rk = random.Random(seed), random.Random(seed + 6)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 8000:
        tries += 1
        c1, c2 = rand_val(loai_so, rc), rand_val(loai_so, rc)
        k = sp.Abs(rand_val(loai_so, rk))
        key = (str(c1), str(c2), str(k))
        if key in seen:
            continue
        seen.add(key)
        out.append({"c1": c1, "c2": c2, "k": k})
    return out


def sinh(c1, c2, k):
    Cmag = sp.sqrt(c1 ** 2 + c2 ** 2)
    ans = sp.simplify(k ** 2 + 2 * Cmag)
    raw = [sp.simplify(Cmag + k ** 2), sp.simplify(2 * Cmag), sp.simplify(4 * Cmag + k ** 2)]
    k_coef = "" if k == 1 else latex(k)
    stem = (f"Xét các số phức $z$ thỏa mãn $|z^2{signed_term(-c1, '')}{signed_term(-c2, 'i')}| = {k_coef}|z|$. "
            f"Gọi $M$ và $m$ lần lượt là giá trị lớn nhất và giá trị nhỏ nhất của $|z|$. Giá trị của $M^2+m^2$ bằng")
    block, dap_an = mc_num(ans, raw, (c1, c2, k))
    loi_giai = (
        f"Đặt $C={z_string(c1, c2)}$, $|C|={latex(Cmag)}$. Theo bất đẳng thức tam giác cho môđun,\n"
        f"$|z|^2-|C| \\le |z^2-C| \\le |z|^2+|C|$, kết hợp $|z^2-C|={k_coef}|z|$ và khảo sát dấu bằng "
        f"(dùng thêm bất đẳng thức B.C.S cho phần thực/ảo của $z^2-C$) dẫn tới, với $t=|z|^2$:\n"
        f"$t^2-({latex_sq(k)}^2+2\\cdot{latex(Cmag)})t+{latex_sq(Cmag)}^2\\le0$,\n"
        f"hai nghiệm biên của bất phương trình này chính là $m^2$ và $M^2$. Theo định lý Vi-ét, "
        f"$M^2+m^2={latex_sq(k)}^2+2\\cdot{latex(Cmag)}={latex(ans)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
