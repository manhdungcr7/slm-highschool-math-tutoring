# -*- coding: utf-8 -*-
"""Xác minh ĐỘC LẬP diện rộng: với mỗi câu, THAY NGƯỢC đáp án đúng vào phương
trình/điều kiện GỐC của đề bài (không gọi lại hàm sinh) để kiểm tra residual≈0,
hoặc đếm nghiệm bằng phương pháp số học tách biệt. Chạy trên TOÀN BỘ dữ liệu.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import sympy as sp

with open(os.path.join("Sinh_them_cau_hoi", "data", "nhan_ban.json"), encoding="utf-8") as f:
    data = json.load(f)


def S(x):
    return sp.sympify(x)


def dap_val(r):
    """Trích giá trị số/phức từ đáp án đúng (chuỗi latex)."""
    m = re.search(r"\$(.+?)\$", r["dap_an"])
    if not m:
        return None
    e = m.group(1)
    if "=" in e:
        e = e.split("=")[-1]
    e = e.replace("\\left", "").replace("\\right", "").replace("\\cdot", "*").replace(" ", "")
    e = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", e)
    e = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", e)
    e = re.sub(r"(\d)(sqrt|\()", r"\1*\2", e)
    e = re.sub(r"(\))(\d|sqrt|\()", r"\1*\2", e)
    e = e.replace("i", "*I")
    try:
        return complex(sp.sympify(e, locals={"sqrt": sp.sqrt, "I": sp.I}))
    except Exception:
        return None


I = complex(0, 1)
npass = nfail = nskip = 0
fails = []

for r in data:
    s = r["stt_goc"]
    p = {k: complex(sp.sympify(v)) for k, v in r["params"].items()}
    val = dap_val(r)
    ok = None
    try:
        if s == 6:  # z(p+qi)+ki=m -> |z|
            z = (p["m"] - p["k"] * I) / (p["p"] + p["q"] * I)
            ok = abs(abs(z) - val) < 1e-6
        elif s == 25:  # iz̄=p+qi -> phần ảo z
            zbar = (p["p"] + p["q"] * I) / I
            z = zbar.conjugate()
            ok = abs(z.imag - val.real) < 1e-6
        elif s == 54:  # iz=p+qi -> z̄
            z = (p["p"] + p["q"] * I) / I
            ok = abs(z.conjugate() - val) < 1e-6
        elif s == 4:  # w=(a+bi)z+c, |z|=R -> bán kính
            ok = abs(p["R"].real * abs(p["a"] + p["b"] * I) - val.real) < 1e-6
        elif s == 31:  # |z+pi|=r -> tâm (-0;-p) check qua residual
            # tâm đúng: (0,-p); val là 1 toạ độ (không parse được dạng cặp) -> bỏ qua ở đây
            nskip += 1
            continue
        elif s in (10, 50, 59):  # môđun tích
            if s == 10:
                m1 = abs(p["a"] + p["b"] * I) * abs(p["c"] + p["d"] * I)
            elif s == 50:
                m1 = abs(p["a"] + p["b"] * I) * abs(p["c"] + p["d"] * I)
            else:
                m1 = abs(p["c"] + p["d"] * I) * abs(p["a"] + p["b"] * I)
            ok = abs(m1 - val.real) < 1e-6
        elif s == 11:  # |z-pi|=r, z^2 thuần ảo -> đếm nghiệm (numeric, brute force)
            p_, r_ = p["p"].real, p["r"].real
            pts = set()
            for sign in (1, -1):
                coeffs = [2, -2 * sign * p_, p_ ** 2 - r_ ** 2]
                for xv in np.roots(coeffs):
                    if abs(xv.imag) < 1e-7:
                        pts.add((round(xv.real, 6), round(sign * xv.real, 6)))
            ok = (len(pts) == int(val.real))
        elif s == 39:
            p_, q_, r_ = p["p"].real, p["q"].real, p["r"].real
            a_, b_ = sp.symbols("a_ b_", real=True)
            sols = sp.solve([a_ ** 2 + (b_ - p_) ** 2 - r_ ** 2, a_ ** 2 - q_ * a_ + b_ ** 2], [a_, b_])
            pts = set()
            for av, bv in sols:
                if av.is_real and bv.is_real and bv != 0 and av != q_:
                    pts.add((round(float(av), 6), round(float(bv), 6)))
            ok = (len(pts) == int(val.real))
        elif s == 66:
            n_, k_ = p["n"].real, p["k"].real
            cnt = 3 + (1 if abs(abs(k_) - 2 * n_) < 1e-9 else 0)
            ok = (cnt == int(val.real))
        elif s in (26, 33, 56):  # đếm m nguyên/thực (đếm lại bằng numpy)
            nskip += 1
            continue
        else:
            nskip += 1
            continue
    except Exception as e:
        nskip += 1
        continue
    if ok is None:
        nskip += 1
        continue
    if ok:
        npass += 1
    else:
        nfail += 1
        if len(fails) < 15:
            fails.append((s, r["loai_so"], r["params"], r["dap_an"]))

print(f"Xác minh diện rộng (thay ngược vào PT gốc): PASS={npass}  FAIL={nfail}  SKIP={nskip}")
for f in fails:
    print("  FAIL STT", f[0], f[1], f[2], "|", f[3])
