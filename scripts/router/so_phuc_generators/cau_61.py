# -*- coding: utf-8 -*-
"""STT61 — Vấn đề 8: z²+4az+b²+2=0, đếm cặp (a;b) để z1+2iz2=p+qi.
Đề gốc: p=3, q=3 → 3 cặp. Giữ cố định hệ số 4, +2, 2i; tổng quát hóa VẾ PHẢI p+qi.
  • TH nghiệm thực: z1=p, z2=q/2 ⟹ b²=pq/2-2 (2 cặp nếu b²>0, 1 nếu =0, 0 nếu <0).
  • TH nghiệm phức liên hợp z1=x+yi, z2=x-yi: x+2y=p, 2x+y=q ⟹ x,y; nếu y≠0 thì
    b²=x²+y²-2 (số cặp theo dấu b²).
Điều kiện: tổng số cặp trong [1;4].
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble


STT = 61


def _pairs_from_b2(b2):
    if b2 > 0:
        return 2
    if b2 == 0:
        return 1
    return 0


def _count(p, q):
    total = 0
    # TH nghiệm thực
    total += _pairs_from_b2(sp.simplify(p * q / 2 - 2))
    # TH nghiệm phức liên hợp
    x = sp.simplify((2 * q - p) / 3)
    y = sp.simplify((2 * p - q) / 3)
    if y != 0:
        total += _pairs_from_b2(sp.simplify(x ** 2 + y ** 2 - 2))
    return total


def gen_params(loai_so, n, seed):
    cond = lambda p, q: 1 <= _count(p, q) <= 4
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(p, q):
    cnt = _count(p, q)
    stem = (f"Trên tập hợp các số phức, xét phương trình $z^2+4az+b^2+2=0$ ($a, b$ là các tham số thực). "
            f"Có bao nhiêu cặp số thực $(a;b)$ sao cho phương trình đó có hai nghiệm $z_1, z_2$ thỏa mãn "
            f"$z_1+2iz_2={z_string(p, q)}$?")
    correct = f"${cnt}$."
    distractors = [f"${cnt - 1}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = (
        f"TH nghiệm thực: $z_1={latex(p)}$, $z_2={latex(sp.nsimplify(q/2))}$, từ Vi-ét $b^2=z_1z_2-2$. "
        f"TH nghiệm phức liên hợp $z_1=x+yi$: cân bằng phần thực/ảo được $x,y$, rồi $b^2=x^2+y^2-2$. "
        f"Đếm số cặp $(a;b)$ hợp lệ, được ${cnt}$ cặp."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
