# -*- coding: utf-8 -*-
"""STT66 — Vấn đề 6: Đếm z thỏa |z²|=n|z-z̄| và |(z-k)(z̄-ki)|=|z+ki|².
Đề gốc: n=2, k=4 → 4.
Vì z̄-ki = conj(z+ki) nên điều kiện 2 ⟺ |z-k|=|z+ki| (hoặc z=-ki).
  • |z-k|=|z+ki| ⟹ b=-a; thay vào |z²|=n|z-z̄| (2a²=2n|a|) ⟹ a=0 hoặc |a|=n
    ⟹ z=0, z=n-ni, z=-n+ni (3 nghiệm).
  • z=-ki thỏa điều kiện 1 khi |k|=2n (thêm 1 nghiệm).
Biến đầu vào: n>0, k. Số nghiệm ∈ {3,4}.
"""
import random
import sympy as sp
from sp_common import latex, num_bare, signed_term, rand_val, assemble

STT = 66


def _count(n, k):
    return 3 + (1 if sp.simplify(sp.Abs(k) - 2 * n) == 0 else 0)


def gen_params(loai_so, n_needed, seed):
    rn, rk = random.Random(seed), random.Random(seed + 4)
    out, seen, tries = [], set(), 0
    # Một nửa số câu ép |k|=2n (đáp án 4), nửa còn lại k tự do (đáp án 3)
    while len(out) < n_needed and tries < 12000:
        tries += 1
        nn = sp.Abs(rand_val(loai_so, rn))
        if tries % 2 == 0:
            k = 2 * nn  # ép |k|=2n
        else:
            k = rand_val(loai_so, rk)
        key = (str(nn), str(k))
        if key in seen or nn == 0:
            continue
        seen.add(key)
        out.append({"n": nn, "k": k})
    return out


def sinh(n, k):
    cnt = _count(n, k)
    z_sub_k = f"z{signed_term(-k, '')}"        # z - k
    zbar_sub_ki = f"\\overline{{z}}{signed_term(-k, 'i')}"  # z̄ - ki
    z_add_ki = f"z{signed_term(k, 'i')}"        # z + ki
    neg_ki = signed_term(-k, "i")               # -ki (đứng riêng, có dấu)
    n_coef = "" if n == 1 else latex(n)
    stem = (f"Có bao nhiêu số phức $z$ thỏa mãn $|z^2|={n_coef}|z-\\overline{{z}}|$ và "
            f"$|({z_sub_k})({zbar_sub_ki})|=|{z_add_ki}|^2$?")
    correct = f"${cnt}$."
    distractors = [f"${cnt - 1}$.", f"${cnt + 1}$.", f"${cnt + 2}$."]
    block, dap_an = assemble(correct, distractors, (n, k))
    loi_giai = (
        f"Vì $\\overline{{z}}{signed_term(-k, 'i')}=\\overline{{{z_add_ki}}}$ nên điều kiện thứ hai "
        f"$\\Leftrightarrow |{z_sub_k}|=|{z_add_ki}|$ (hoặc ${z_add_ki}=0$). "
        f"Từ $|{z_sub_k}|=|{z_add_ki}|$ suy ra $b=-a$; thay vào $|z^2|={n_coef}|z-\\overline{{z}}|$ "
        f"được $z=0$, $z={num_bare(n)}{signed_term(-n, 'i')}$, $z={signed_term(-n, '')}{signed_term(n, 'i')}$. Ngoài ra ${z_add_ki}=0$ thỏa mãn khi "
        f"$|{latex(k)}|=2\\cdot{latex(n)}$. Tổng cộng ${cnt}$ số phức."
    )
    return stem + "\n\n" + block, dap_an, loi_giai
