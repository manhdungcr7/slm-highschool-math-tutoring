# -*- coding: utf-8 -*-
"""STT39 — Vấn đề 6: Đếm z thỏa |z-pi|=r và z/(z-q) thuần ảo.
Đề gốc: |z-3i|=5 và z/(z-4) thuần ảo → 1.
Biến đầu vào: p (tâm ảo), q (số thực trong z-q), r>0. Đặt z=a+bi:
  đường tròn a²+(b-p)²=r²; z/(z-q) thuần ảo ⟺ a²-qa+b²=0 (a≠q, b≠0).
Giải hệ, đếm nghiệm. Điều kiện: số nghiệm trong [1;3].
"""
import random
import sympy as sp
from sp_common import latex, latex_sq, signed_term, rand_val, assemble, neq


STT = 39


def _count(p, q, r):
    a, b = sp.symbols("a b", real=True)
    sols = sp.solve([a ** 2 + (b - p) ** 2 - r ** 2, a ** 2 - q * a + b ** 2], [a, b])
    cnt = 0
    for av, bv in sols:
        if av.is_real and bv.is_real and bv != 0 and av != q:
            cnt += 1
    return cnt


def gen_params(loai_so, n, seed):
    rp, rq, rr = random.Random(seed), random.Random(seed + 2), random.Random(seed + 3)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 12000:
        tries += 1
        p = rand_val(loai_so, rp)
        q = rand_val(loai_so, rq)
        r = sp.Abs(rand_val(loai_so, rr))
        if not (1 <= _count(p, q, r) <= 3):
            continue
        key = (str(p), str(q), str(r))
        if key in seen:
            continue
        seen.add(key)
        out.append({"p": p, "q": q, "r": r})
    return out


def sinh(p, q, r):
    a, b = sp.symbols("a b", real=True)
    cnt = _count(p, q, r)
    stem = (f"Có bao nhiêu số phức $z$ thỏa mãn $|z{signed_term(-p, 'i')}| = {latex(r)}$ và "
            f"$\\dfrac{{z}}{{z{signed_term(-q, '')}}}$ là số thuần ảo?")
    correct = f"${cnt}$."
    distractors = [f"${max(cnt - 1, 0)}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (p, q, r))

    eq1 = sp.expand(a ** 2 + b ** 2 - 2 * p * b - (r ** 2 - p ** 2))   # tu duong tron, da khai trien
    eq2 = sp.expand(a ** 2 - q * a + b ** 2)                          # tu dieu kien thuan ao
    lin = sp.expand(eq1 - eq2)  # khu a^2+b^2, con lai phuong trinh bac nhat
    b_of_a = sp.solve(sp.Eq(lin, 0), b)[0]
    quad_in_a = sp.expand(eq2.subs(b, b_of_a))
    sols = sp.solve([a ** 2 + (b - p) ** 2 - r ** 2, a ** 2 - q * a + b ** 2], [a, b])
    valid_sols = [(av, bv) for av, bv in sols if av.is_real and bv.is_real and bv != 0 and av != q]
    sol_txt = " hoặc ".join(f"\\begin{{cases}} a={latex(av)} \\\\ b={latex(bv)} \\end{{cases}}" for av, bv in valid_sols) or "vô nghiệm"

    loi_giai = (
        f"$\\begin{{cases}} |z{signed_term(-p, 'i')}| = {latex(r)} \\\\ \\dfrac{{z}}{{z{signed_term(-q, '')}}} \\text{{ là số thuần ảo}} \\end{{cases}}$\n"
        f"$\\Leftrightarrow \\begin{{cases}} a^2+(b{signed_term(-p, '')})^2={latex_sq(r)}^2 \\\\ a^2{signed_term(-q, 'a')}+b^2=0,\\ a\\ne{latex(q)},\\ b\\ne0 \\end{{cases}}$\n"
        f"Lấy phương trình đầu trừ phương trình sau (khử $a^2+b^2$), được phương trình bậc nhất, suy ra $b={latex(b_of_a)}$.\n"
        f"Thế vào phương trình thuần ảo, được: ${latex(quad_in_a)}=0$, giải ra: {sol_txt}.\n"
        f"Vậy có ${cnt}$ số phức thỏa mãn yêu cầu bài toán."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
