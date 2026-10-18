# -*- coding: utf-8 -*-
"""STT56 — Vấn đề 8: z²-2(m+a)z+m²=0, đếm m để TỒN TẠI nghiệm z0 với |z0|=R.
Đề gốc: a=1, R=5 → 3 giá trị. Δ'=2am+a².
  • Δ'=0: nghiệm kép z0=m+a=a/2, kiểm tra |a/2|=R.
  • Δ'<0: z0 phức, |z0|=|m|=R ⟹ m=±R (nếu Δ'<0).
  • Δ'>0: z0=±R thực, thế vào phương trình giải m (nếu Δ'>0).
Biến đầu vào: a (hệ số), R>0. Đếm được trong [1;4].
"""
import sympy as sp
from sp_common import latex, signed_term, gen_pairs, assemble


STT = 56


def _count(a, R):
    valid = set()
    m = sp.symbols("m", real=True)
    if sp.simplify(sp.Abs(a / 2) - R) == 0:
        valid.add(sp.nsimplify(-a / 2))
    for mv in [R, -R]:
        if 2 * a * mv + a ** 2 < 0:
            valid.add(sp.nsimplify(mv))
    for z0 in [R, -R]:
        for mv in sp.solve(z0 ** 2 - 2 * (m + a) * z0 + m ** 2, m):
            if mv.is_real and (2 * a * mv + a ** 2 > 0):
                valid.add(sp.nsimplify(mv))
    return len(valid)


def gen_params(loai_so, n, seed):
    cond = lambda a, R: R > 0 and 1 <= _count(a, R) <= 4
    return [{"a": a, "R": R} for a, R in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, R):
    m = sp.symbols("m", real=True)
    stem = (f"Trên tập hợp các số phức, xét phương trình $z^2-2(m{signed_term(a, '')})z+m^2=0$ ($m$ là tham số thực). "
            f"Có bao nhiêu giá trị của $m$ để phương trình đó có nghiệm $z_0$ thỏa mãn $|z_0|={latex(R)}$?")

    th1 = th2 = th3 = None
    m_edge = sp.nsimplify(-a / 2)
    if sp.simplify(sp.Abs(a / 2) - R) == 0:
        th1 = m_edge
    th2_vals = [sp.nsimplify(mv) for mv in [R, -R] if 2 * a * mv + a ** 2 < 0]
    th3_vals = []
    for z0 in [R, -R]:
        for mv in sp.solve(z0 ** 2 - 2 * (m + a) * z0 + m ** 2, m):
            if mv.is_real and (2 * a * mv + a ** 2 > 0):
                th3_vals.append(sp.nsimplify(mv))

    valid = set(([th1] if th1 is not None else []) + th2_vals + th3_vals)
    cnt = len(valid)
    correct = f"${cnt}$."
    distractors = [f"${cnt - 1}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (a, R))

    th1_txt = (f"$\\Delta'=0 \\Leftrightarrow m={latex(m_edge)}$ thì $z_0=m{signed_term(a,'')}={latex(m_edge+a)}$, "
               f"suy ra $m={latex(m_edge)}$ ({'nhận' if th1 is not None else 'loại'})")
    th2_txt = (f"$\\Delta'<0 \\Leftrightarrow$ $z_0$ phức, $|z_0|=|m|={latex(R)} \\Rightarrow m=\\pm{latex(R)}$" +
               (f", nhận $m={' \\text{ hoặc } m='.join(latex(v) for v in th2_vals)}$" if th2_vals else " (không thỏa điều kiện $\\Delta'<0$)"))
    th3_txt = (f"$\\Delta'>0 \\Leftrightarrow$ phương trình có hai nghiệm thực; khi $z_0=\\pm{latex(R)}$, thế vào phương trình "
               f"giải $m$" + (f", nhận $m={' \\text{ hoặc } m='.join(latex(v) for v in th3_vals)}$" if th3_vals else " (không có nghiệm thỏa $\\Delta'>0$)"))
    loi_giai = (
        f"Ta có $\\Delta'=(m{signed_term(a, '')})^2-m^2=2({latex(a)})m+({latex(a)})^2$.\n"
        f"- TH1: {th1_txt}.\n"
        f"- TH2: {th2_txt}.\n"
        f"- TH3: {th3_txt}.\n"
        f"Vậy có ${cnt}$ giá trị của $m$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
