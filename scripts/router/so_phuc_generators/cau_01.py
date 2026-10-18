# -*- coding: utf-8 -*-
"""STT1 — Vấn đề 1: Phần thực & phần ảo của số phức liên hợp z̄.
Đề gốc: "Cho z = 3-2i. Tìm phần thực và phần ảo của z̄." (z̄ = a-bi).
Biến đầu vào: a,b (z=a+bi). Điều kiện: a,b ≠ 0, |b| ≠ 1 (tránh phương án nhiễu "1i").
Trình bày: hai phương án nhiễu cố tình viết phần ảo KÈM i (bẫy thường gặp).
"""
import sympy as sp
from sp_common import z_string, latex, gen_pairs, assemble

STT = 1


def gen_params(loai_so, n, seed):
    cond = lambda a, b: sp.Abs(b) != 1
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed, cond=cond)]


def sinh(a, b):
    stem = f"Cho số phức $z = {z_string(a, b)}$. Tìm phần thực và phần ảo của số phức $\\overline{{z}}$."
    correct = f"Phần thực bằng ${latex(a)}$ và phần ảo bằng ${latex(-b)}$."
    distractors = [
        f"Phần thực bằng ${latex(-a)}$ và phần ảo bằng ${latex(b)}i$.",
        f"Phần thực bằng ${latex(-a)}$ và phần ảo bằng ${latex(b)}$.",
        f"Phần thực bằng ${latex(a)}$ và phần ảo bằng ${latex(-b)}i$.",
    ]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = (
        f"Từ $z = {z_string(a, b)}$ suy ra $\\overline{{z}} = {z_string(a, -b)}$. "
        f"Nên phần thực của $\\overline{{z}}$ bằng ${latex(a)}$ và phần ảo bằng ${latex(-b)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
