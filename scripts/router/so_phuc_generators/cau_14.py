# -*- coding: utf-8 -*-
"""STT14 — Vấn đề 6: Đếm z thỏa |z|²=k|z+z̄|+c và |z-A|=|z-B|.
Đề gốc: |z|²=2|z+z̄|+4 và |z-1-i|=|z-3+3i| → 3.
Đặt z=x+yi: |z|²=x²+y², |z+z̄|=2|x| ⟹ x²+y²∓2kx-c=0 (x≥0 / x<0);
|z-A|=|z-B| là đường trung trực, rút gọn x=my+n rồi thế vào từng nhánh (giống
cách làm của lời giải gốc). Lọc nhanh bằng số học (numpy) để đếm nghiệm, sau đó
trình bày lại bằng sympy chính xác; nếu biểu thức quá dài thì loại bộ số đó.
Biến đầu vào: k>0, c, A=(ax,ay), B=(bx,by). Số nghiệm ∈ [1;4].
"""
import random
import numpy as np
import sympy as sp
from sp_common import latex, signed_term, rand_val, assemble

STT = 14
_x, _y = sp.symbols("x y", real=True)
_MAX_LEN = 150


def _count_fast(k, c, ax, ay, bx, by):
    A2 = float(2 * (bx - ax))
    B2 = float(2 * (by - ay))
    E2 = float(bx ** 2 + by ** 2 - ax ** 2 - ay ** 2)
    kf, cf = float(k), float(c)
    pts = set()
    for coef, ok in ((-2 * kf, lambda xv: xv >= -1e-9), (2 * kf, lambda xv: xv < 1e-9)):
        aa = 1 + (A2 / B2) ** 2
        bb = coef - 2 * A2 * E2 / B2 ** 2
        cc = (E2 / B2) ** 2 - cf
        for xv in np.roots([aa, bb, cc]):
            if abs(xv.imag) < 1e-7:
                xr = xv.real
                if ok(xr):
                    pts.add((round(xr, 5), round((E2 - A2 * xr) / B2, 5)))
    return len(pts)


def _solve_exact(k, c, ax, ay, bx, by):
    lin = sp.expand((_x - ax) ** 2 + (_y - ay) ** 2 - (_x - bx) ** 2 - (_y - by) ** 2)
    x_expr = sp.solve(sp.Eq(lin, 0), _x)[0]
    branches = []
    for coef, cond_txt, ok in ((-2 * k, "x\\ge0", lambda xv: xv >= 0), (2 * k, "x<0", lambda xv: xv < 0)):
        eq = sp.expand(x_expr ** 2 + _y ** 2 + coef * x_expr - c)
        ys = [yv for yv in sp.solve(sp.Eq(eq, 0), _y) if yv.is_real]
        if any(len(str(yv)) > _MAX_LEN for yv in ys):
            raise ValueError("bieu thuc qua dai")
        branches.append((coef, cond_txt, ys, ok))
    return x_expr, branches


def gen_params(loai_so, n, seed):
    rng = random.Random(seed)
    # A,B (toa do tham chieu duong trung truc) luon la so nguyen nho, giu vai
    # tro nhu A(1,1), B(3,-3) o de goc - tranh dai so no qua lon; k,c (hai so
    # "dau bai" chinh) moi thuc su doi theo loai_so.
    rng_ab = random.Random(seed + 1000)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < 15000:
        tries += 1
        k = sp.Abs(rand_val(loai_so, rng, -5, 5))
        c = rand_val(loai_so, rng, -5, 5)
        ax, ay, bx, by = (rand_val("Số nguyên", rng_ab, -4, 4) for _ in range(4))
        if ax == bx:
            continue
        try:
            if not (1 <= _count_fast(k, c, ax, ay, bx, by) <= 4):
                continue
            _solve_exact(k, c, ax, ay, bx, by)  # chỉ để kiểm tra độ dài, bỏ nếu quá dài
        except Exception:
            continue
        key = tuple(str(v) for v in (k, c, ax, ay, bx, by))
        if key in seen:
            continue
        seen.add(key)
        out.append({"k": k, "c": c, "ax": ax, "ay": ay, "bx": bx, "by": by})
    return out


def sinh(k, c, ax, ay, bx, by):
    x_expr, branches = _solve_exact(k, c, ax, ay, bx, by)
    A = f"z{signed_term(-ax, '')}{signed_term(-ay, 'i')}"
    B = f"z{signed_term(-bx, '')}{signed_term(-by, 'i')}"

    parts_by_branch = []
    cnt = 0
    for coef, cond_txt, ys, ok in branches:
        parts = []
        for yv in ys:
            xv = sp.simplify(x_expr.subs(_y, yv))
            nhan = ok(float(xv))
            cnt += 1 if nhan else 0
            parts.append(f"y={latex(yv)} \\Rightarrow x={latex(xv)}\\ \\text{{({'nhận' if nhan else 'loại'})}}")
        parts_by_branch.append((coef, cond_txt, parts))

    k_coef = "" if k == 1 else latex(k)
    stem = (f"Có bao nhiêu số phức $z$ thỏa mãn $|z|^2={k_coef}|z+\\overline{{z}}|{signed_term(c, '')}$ và "
            f"$|{A}|=|{B}|$?")
    correct = f"${cnt}$."
    distractors = [f"${max(cnt - 1, 0)}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (k, c, ax, ay, bx, by))

    (c1, t1, p1), (c2, t2, p2) = parts_by_branch
    loi_giai = (
        f"Gọi $z=x+yi$ $(x;y\\in\\mathbb{{R}})$.\n"
        f"$|z|^2={k_coef}|z+\\overline{{z}}|{signed_term(c, '')} \\Leftrightarrow x^2+y^2={latex(2*k)}|x|{signed_term(c, '')} "
        f"\\Leftrightarrow x^2+y^2{signed_term(c1, '')}=0,\\ {t1}\\ (1)$ hoặc $x^2+y^2{signed_term(c2, '')}=0,\\ {t2}\\ (2)$.\n"
        f"$|{A}|=|{B}| \\Leftrightarrow x={latex(x_expr)}$ $(3)$.\n"
        f"+ Thay $(3)$ vào $(1)$: {' hoặc '.join(p1) if p1 else 'vô nghiệm'}.\n"
        f"+ Thay $(3)$ vào $(2)$: {' hoặc '.join(p2) if p2 else 'vô nghiệm'}.\n"
        f"Vậy có ${cnt}$ số phức $z$ thỏa mãn điều kiện."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
