# -*- coding: utf-8 -*-
"""STT43 — Vấn đề 2: Số phức liên hợp của a+bi (phương án ghi TRỰC TIẾP số phức).
Đề gốc: "Số phức liên hợp của số phức 5-3i là" → 5+3i.
Biến đầu vào: a,b. z̄ = a-bi. Điều kiện: a,b ≠ 0.
"""
from sp_common import z_string, gen_pairs, assemble

STT = 43


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed)]


def sinh(a, b):
    stem = f"Số phức liên hợp của số phức ${z_string(a, b)}$ là"
    correct = f"${z_string(a, -b)}$."
    distractors = [f"${z_string(-a, b)}$.", f"${z_string(-a, -b)}$.", f"${z_string(a, b)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = f"Số phức liên hợp của số phức ${z_string(a, b)}$ là ${z_string(a, -b)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
