# -*- coding: utf-8 -*-
"""STT9 — Vấn đề 1: Tìm phần thực, phần ảo của z=a+bi.
Đề gốc: "Kí hiệu a, b lần lượt là phần thực và phần ảo của số phức 3-2√2i. Tìm a, b."
Biến đầu vào: a = phần thực, b = phần ảo (a,b ≠ 0 để 4 phương án ±a,±b phân biệt).
"""
from sp_common import z_string, latex, gen_pairs, assemble

STT = 9


def gen_params(loai_so, n, seed):
    return [{"a": a, "b": b} for a, b in gen_pairs(loai_so, n, seed)]


def sinh(a, b):
    stem = f"Kí hiệu $a, b$ lần lượt là phần thực và phần ảo của số phức ${z_string(a, b)}$. Tìm $a, b$."
    correct = f"$a={latex(a)}, b={latex(b)}$."
    distractors = [
        f"$a={latex(-a)}, b={latex(-b)}$.",
        f"$a={latex(-a)}, b={latex(b)}$.",
        f"$a={latex(a)}, b={latex(-b)}$.",
    ]
    block, dap_an = assemble(correct, distractors, (a, b))
    loi_giai = (
        f"Số phức ${z_string(a, b)}$ có phần thực và phần ảo lần lượt là ${latex(a)}$ và ${latex(b)}$. "
        f"Vậy $a={latex(a)}, b={latex(b)}$."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
