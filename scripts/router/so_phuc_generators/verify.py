# -*- coding: utf-8 -*-
"""Xác minh ĐỘC LẬP: với các câu cơ bản, tính lại đáp án bằng cách khác rồi so
với phương án được đánh đúng trong dữ liệu (bắt lỗi công thức nếu có)."""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import sympy as sp

with open(os.path.join("Sinh_them_cau_hoi", "data", "nhan_ban.json"), encoding="utf-8") as f:
    data = json.load(f)


def S(x):
    return sp.sympify(x)


def dap_letter(r):
    return r["dap_an"][0]


def opt_of_letter(de, letter):
    m = re.search(rf"^{letter}\.\s*(.+)$", de, re.M)
    return m.group(1) if m else None


def eq_latex(val, opt_text):
    """opt_text là chuỗi latex trong '$...$.'; so khớp với latex(val)."""
    m = re.search(r"\$(.+?)\$", opt_text)
    if not m:
        return False
    inner = m.group(1)
    if "=" in inner:            # bỏ tiền tố kiểu "|z_1+z_2| ="
        inner = inner.split("=")[-1]
    # chuyển latex về biểu thức sympy rồi so sánh BẰNG SỐ
    expr = inner
    expr = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", expr)
    expr = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", expr)
    expr = expr.replace("\\left", "").replace("\\right", "").replace("\\cdot", "*").replace(" ", "")
    expr = re.sub(r"(\d)(sqrt|\()", r"\1*\2", expr)   # nhân ẩn: 2sqrt(2)->2*sqrt(2)
    expr = re.sub(r"(\))(\d|sqrt|\()", r"\1*\2", expr)
    try:
        opt_val = sp.sympify(expr, locals={"sqrt": sp.sqrt})
        return abs(float(opt_val) - float(val)) < 1e-6
    except Exception:
        return False


npass = nfail = nskip = 0
fails = []
for r in data:
    s = r["stt_goc"]
    p = {k: S(v) for k, v in r["params"].items()}
    expect = None  # giá trị đúng (tính độc lập)
    try:
        if s in (53,):        # phần thực của z=a+bi
            expect = p["a"]
        elif s in (30, 58):   # phần ảo
            expect = p["b"]
        elif s in (15, 22, 62):  # môđun
            expect = sp.sqrt(p["a"] ** 2 + p["b"] ** 2)
        elif s == 2:          # |z1+z2|
            expect = sp.sqrt((p["a"] + p["c"]) ** 2 + (p["b"] + p["d"]) ** 2)
        elif s == 19:         # phần thực z1+z2
            expect = p["a"] + p["c"]
        elif s == 21:         # phần ảo z1z2
            expect = sp.expand(p["a"] * p["d"] + p["b"] * p["c"])
        elif s == 29:         # phần thực z²
            expect = p["a"] ** 2 - p["b"] ** 2
        else:
            nskip += 1
            continue
    except Exception:
        nskip += 1
        continue
    opt = opt_of_letter(r["de_bai"], dap_letter(r))
    if opt and eq_latex(expect, opt):
        npass += 1
    else:
        nfail += 1
        if len(fails) < 10:
            fails.append((s, r["loai_so"], r["params"], r["dap_an"], sp.latex(sp.nsimplify(expect))))

print(f"Xác minh độc lập: PASS={npass}  FAIL={nfail}  (bỏ qua {nskip} câu phức tạp)")
for f in fails:
    print("  FAIL STT", f[0], f[1], f[2], "| đáp:", f[3], "| tính lại:", f[4])
