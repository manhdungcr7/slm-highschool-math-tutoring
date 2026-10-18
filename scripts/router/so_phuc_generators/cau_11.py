# -*- coding: utf-8 -*-
"""STT11 — Vấn đề 6: Đếm z thỏa |z-pi|=r và z² thuần ảo.
Đề gốc: |z-i|=5 và z² thuần ảo → 4.
Biến đầu vào: p (tâm ảo), r>0 (bán kính). Đặt z=x+yi: đường tròn x²+(y-p)²=r²;
z² thuần ảo ⟺ x²-y²=0 ⟺ x=±y. Giải hệ, đếm nghiệm.
Điều kiện: số nghiệm trong [1;4].
"""
import random
import sympy as sp
from sp_common import latex, latex_sq, signed_term, rand_val, assemble, neq


STT = 11


def _count(p, r):
    y = sp.symbols("y", real=True)
    pts = set()
    for sign in (1, -1):
        for yv in sp.solve(y ** 2 + (y - p) ** 2 - r ** 2, y):
            if yv.is_real:
                pts.add((sp.nsimplify(sign * yv), sp.nsimplify(yv)))
    return len(pts)


def gen_params(loai_so, n, seed):
    rp, rr = random.Random(seed), random.Random(seed + 3)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 8000:
        tries += 1
        p = rand_val(loai_so, rp)
        r = sp.Abs(rand_val(loai_so, rr))
        if not (1 <= _count(p, r) <= 4):
            continue
        key = (str(p), str(r))
        if key in seen:
            continue
        seen.add(key)
        out.append({"p": p, "r": r})
    return out


def sinh(p, r):
    y = sp.symbols("y", real=True)
    branch_txt = []
    all_pts = []
    for sign, sign_str in ((1, "x=y"), (-1, "x=-y")):
        ys = sorted(sp.solve(y ** 2 + (y - p) ** 2 - r ** 2, y), key=lambda v: float(v))
        pts = [(sp.nsimplify(sign * yv), sp.nsimplify(yv)) for yv in ys if yv.is_real]
        all_pts.extend(pts)
        sols_txt = " hoặc ".join(f"\\begin{{cases}} y={latex(yv)} \\\\ x={latex(sign*yv)} \\end{{cases}}" for yv in ys)
        branch_txt.append(sols_txt)
    seen = set()
    uniq_pts = []
    for xv, yv in all_pts:
        key = (str(xv), str(yv))
        if key not in seen:
            seen.add(key)
            uniq_pts.append((xv, yv))
    cnt = len(uniq_pts)
    stem = (f"Hỏi có bao nhiêu số phức $z$ thỏa mãn đồng thời các điều kiện: $|z{signed_term(-p, 'i')}| = {latex(r)}$ "
            f"và $z^2$ là số thuần ảo?")
    correct = f"${cnt}$."
    distractors = [f"${max(cnt - 1, 0)}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (p, r))
    loi_giai = (
        f"Đặt $z=x+yi$ với $x,y\\in\\mathbb{{R}}$.\n"
        f"$|z{signed_term(-p, 'i')}|={latex(r)} \\Leftrightarrow x^2+(y{signed_term(-p, '')})^2={latex_sq(r)}^2$.\n"
        f"$z^2$ là số thuần ảo $\\Leftrightarrow x^2-y^2=0 \\Leftrightarrow x=\\pm y$.\n"
        f"Vậy ta có hệ: $\\begin{{cases}} x^2+(y{signed_term(-p, '')})^2={latex_sq(r)}^2 \\\\ x=y \\end{{cases}}$ hoặc "
        f"$\\begin{{cases}} x^2+(y{signed_term(-p, '')})^2={latex_sq(r)}^2 \\\\ x=-y \\end{{cases}}$\n"
        f"$\\Leftrightarrow$ {branch_txt[0]} hoặc {branch_txt[1]}.\n"
        f"Vậy có ${cnt}$ số phức $z$ thỏa mãn điều kiện."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
