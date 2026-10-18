# -*- coding: utf-8 -*-
"""STT36 — Vấn đề 8: Viết phương trình bậc hai nhận z=p+qi và p-qi làm nghiệm (Viète đảo).
Đề gốc: z=1+√2 i và 1-√2 i → z²-2z+3=0.
Biến đầu vào: p,q (số phức p+qi và liên hợp). S=z1+z2=2p, P=z1z2=p²+q².
Phương trình: z²-2p·z+(p²+q²)=0.
Điều kiện: p≠0 (để hệ số của z khác 0, 4 phương án đổi dấu phân biệt).
"""
import sympy as sp
from sp_common import latex, z_string, signed_term, gen_pairs, assemble, neq

STT = 36


def gen_params(loai_so, n, seed):
    return [{"p": p, "q": q} for p, q in gen_pairs(loai_so, n, seed, cond=lambda p, q: neq(p, 0))]


def _pt(coef_z, const):
    return f"z^2{signed_term(coef_z, 'z')}{signed_term(const, '')}=0"


def sinh(p, q):
    S, P = 2 * p, sp.expand(p ** 2 + q ** 2)
    stem = (f"Phương trình nào dưới đây nhận hai số phức $z={z_string(p, q)}$ và "
            f"${z_string(p, -q)}$ là nghiệm?")
    correct = f"${_pt(-S, P)}$."
    distractors = [f"${_pt(S, P)}$.", f"${_pt(-S, -P)}$.", f"${_pt(S, -P)}$."]
    block, dap_an = assemble(correct, distractors, (p, q))
    loi_giai = (f"Theo định lý Vi-ét: tổng hai nghiệm bằng ${latex(S)}$, tích hai nghiệm bằng ${latex(P)}$. "
                f"Vậy phương trình cần tìm là ${_pt(-S, P)}$.")
    return stem + "\n\n" + block, dap_an, loi_giai
