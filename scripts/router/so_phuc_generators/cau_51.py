# -*- coding: utf-8 -*-
"""STT51 — Vấn đề 4: Từ điểm biểu diễn M(p;q) tìm số phức z. Đề gốc: M(-3;2) → -3+2i.
Biến đầu vào: p,q. z = p+qi.
Điều kiện: p,q≠0 (4 phương án đổi dấu phân biệt).
"""
from sp_common import diem, z_string, gen_pairs, assemble

STT = 51


def gen_params(loai_so, n, seed):
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed)]


def sinh(p, q):
    stem = f"Trong mặt phẳng tọa độ $Oxy$, điểm $M{diem(p, q)}$ là điểm biểu diễn của số phức nào sau đây?"
    correct = f"${z_string(p, q)}$."
    distractors = [f"${z_string(p, -q)}$.", f"${z_string(-p, q)}$.", f"${z_string(-p, -q)}$."]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = f"Điểm $M{diem(p, q)}$ biểu diễn cho số phức $z = {z_string(p, q)}$."
    return stem + "\n\n" + block, dap_an, loi_giai
