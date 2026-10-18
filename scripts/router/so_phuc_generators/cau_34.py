# -*- coding: utf-8 -*-
"""STT34 — Vấn đề 1: Nhận biết số thuần ảo.
Đề gốc: "Số phức nào dưới đây là số thuần ảo?" (đáp án 3i).
Biến đầu vào: a,b ≠ 0. Đáp án đúng là số thuần ảo b·i; 3 phương án nhiễu KHÔNG
thuần ảo: a+bi, số thực a, a-bi.
"""
from sp_common import z_string, latex, gen_pairs, assemble

STT = 34


def _imag_only(c):
    if c == 1:
        return "i"
    if c == -1:
        return "-i"
    return f"{latex(c)}i"


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed)]


def sinh(a, b):
    stem = "Số phức nào dưới đây là số thuần ảo?"
    correct = f"$z = {_imag_only(b)}$."
    distractors = [f"$z = {z_string(a, b)}$.", f"$z = {latex(a)}$.", f"$z = {z_string(a, -b)}$."]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = (
        f"Số phức là số thuần ảo khi và chỉ khi phần thực bằng $0$. "
        f"Trong các phương án, chỉ ${_imag_only(b)}$ có phần thực bằng $0$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
