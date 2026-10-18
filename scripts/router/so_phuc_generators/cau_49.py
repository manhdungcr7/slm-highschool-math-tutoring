# -*- coding: utf-8 -*-
"""STT49 — Vấn đề 2: Số phức liên hợp của z=a+bi (phương án ghi "\\overline{z}=...").
Đề gốc: "Số phức liên hợp của số phức z=-2+5i là" → -2-5i.
Biến đầu vào: a,b. z̄ = a-bi. Điều kiện: a,b ≠ 0.
"""
from sp_common import z_string, gen_pairs, assemble

STT = 49


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed)]


def sinh(a, b):
    stem = f"Số phức liên hợp của số phức $z = {z_string(a, b)}$ là"
    correct = f"$\\overline{{z}}={z_string(a, -b)}$."
    distractors = [
        f"$\\overline{{z}}={z_string(-a, -b)}$.",
        f"$\\overline{{z}}={z_string(-a, b)}$.",
        f"$\\overline{{z}}={z_string(a, b)}$.",
    ]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Ta có số phức liên hợp của số phức $z = {z_string(a, b)}$ là $\\overline{{z}}={z_string(a, -b)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
