# -*- coding: utf-8 -*-
"""STT33 — Vấn đề 8: z²-2(m+a)z+m²=0, đếm m để |z1|+|z2|=S.
Đề gốc: a=1, S=2 → 2 giá trị. Δ'=(m+a)²-m²=2am+a².
  • Δ'<0: z1=z̄2 ⟹ 2|z1|=S ⟹ |z1|=S/2 ⟹ m²=|z1|²=S²/4 ⟹ m=±S/2 (nếu Δ'<0).
  • Δ'>0: (|z1|+|z2|)²=4(m+a)² ⟹ |m+a|=S/2 ⟹ m=-a±S/2 (nếu Δ'>0).
Biến đầu vào: a (hệ số), S>0 (tổng môđun). Đếm được trong [1;4].
"""
import sympy as sp
from sp_common import latex, latex_sq, signed_term, gen_pairs, assemble, neq


STT = 33


def _count(a, S):
    valid = set()
    for mv in [S / 2, -S / 2]:
        if 2 * a * mv + a ** 2 < 0:
            valid.add(sp.nsimplify(mv))
    for mv in [-a + S / 2, -a - S / 2]:
        if 2 * a * mv + a ** 2 > 0:
            valid.add(sp.nsimplify(mv))
    return len(valid)


def gen_params(loai_so, n, seed):
    cond = lambda a, S: S > 0 and 1 <= _count(a, S) <= 4
    return [{"a": a, "S": S} for a, S in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, S):
    half = sp.nsimplify(S / 2)
    stem = (f"Trên tập hợp số phức, xét phương trình $z^2-2(m{signed_term(a, '')})z+m^2=0$ ($m$ là tham số thực). "
            f"Có bao nhiêu giá trị của $m$ để phương trình đó có hai nghiệm phân biệt $z_1, z_2$ thỏa mãn "
            f"$|z_1|+|z_2|={latex(S)}$?")

    th1_cands = [half, -half]
    th1_ok = [mv for mv in th1_cands if 2 * a * mv + a ** 2 < 0]
    th2_cands = [-a + half, -a - half]
    th2_ok = [mv for mv in th2_cands if 2 * a * mv + a ** 2 > 0]
    valid = set(th1_ok) | set(th2_ok)
    cnt = len(valid)
    correct = f"${cnt}$."
    distractors = [f"${cnt - 1}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (a, S))

    th1_txt = " hoặc ".join(f"$m={latex(mv)}$ ({'nhận' if mv in th1_ok else 'loại'})" for mv in th1_cands)
    th2_txt = " hoặc ".join(f"$m={latex(mv)}$ ({'nhận' if mv in th2_ok else 'loại'})" for mv in th2_cands)
    valid_txt = ", ".join(f"$m={latex(v)}$" for v in sorted(valid, key=lambda v: float(v)))
    loi_giai = (
        f"Ta có $\\Delta'=(m{signed_term(a, '')})^2-m^2=2({latex(a)})m+({latex(a)})^2$.\n"
        f"- TH1: $\\Delta'<0$. Khi đó $z_1=\\overline{{z_2}}$, suy ra $2|z_1|=|z_1|+|z_2|={latex(S)} "
        f"\\Rightarrow |z_1|={latex(half)} \\Rightarrow m^2=z_1z_2=|z_1|^2={latex_sq(half)}^2 \\Rightarrow m=\\pm{latex(half)}$: {th1_txt}.\n"
        f"- TH2: $\\Delta'\\ge0$. Khi đó $z_1+z_2=2(m{signed_term(a, '')})$, $z_1z_2=m^2$. Do đó\n"
        f"${latex_sq(S)}^2=(|z_1|+|z_2|)^2=(z_1+z_2)^2-2z_1z_2+2|z_1z_2|=4(m{signed_term(a, '')})^2 "
        f"\\Leftrightarrow |m{signed_term(a, '')}|={latex(half)} \\Rightarrow m=-({latex(a)})\\pm{latex(half)}$: {th2_txt}.\n"
        f"Vậy có ${cnt}$ giá trị $m$" + (f" là {valid_txt}" if cnt <= 3 else "") + " thỏa mãn bài toán."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
