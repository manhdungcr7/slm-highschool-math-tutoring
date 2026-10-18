# -*- coding: utf-8 -*-
"""Check the facts that a name states but that the stem alone does not show (they sit in the options or in constants).

Each claim is (code, description, regex on the normalised text of stem + options, expected fraction = 'all').
"""
import re

from common import load_questions, norm, options, stem

CLAIMS = [
    ("ML_D13", "mọi phương án chứa log_p(q·a^k/b)", "opts_all", r"\\log_\d+\(\\frac\{\d*a\^\d+\}\{b\}\)="),
    ("ML_D06", "mọi phương án chứa log_{a^k}(ab)", "opts_all", r"\\log_a\^\d+\(ab\)="),
    ("SP_D54", "|z₁| = |z₂| = 2|z₃| ở mọi câu", "stem", r"\|z_1\|=\|z_2\|=2\|z_3\|="),
    ("SP_D54", "có hệ thức k(z₁+z₂)z₃ = l·z₁z₂ ở mọi câu", "stem", r"\(z_1\+z_2\)z_3=.*z_1z_2"),
    ("SP_D31", "phương trình (1+i)z+2z̄ cố định", "stem", r"\(1\+i\)z\+2\\overline\{z\}="),
    ("SP_D32", "phương trình 3(z̄−i)−(2+3i)z cố định", "stem", r"3\(\\overline\{z\}-i\)-\(2\+3i\)z="),
    ("SP_D27", "w = iz + z̄ cố định", "stem", r"w=iz\+\\overline\{z\}"),
    ("SP_D48", "z²+4az+b²+2=0 cố định", "stem", r"z\^2\+4az\+b\^2\+2=0"),
    ("SP_D44", "w = (c+iz)/(1+z) có mẫu 1+z", "stem", r"w=\\frac\{.*\+iz\}\{1\+z\}"),
    ("SP_D53", "biểu thức |z + i·w̄ + c|", "stem", r"\|z\+i\\overline\{w\}"),
    ("ML_D17", "log²_{a/b}(…) + c·log_b(a/b)", "stem", r"\\log\^2_\{?\\frac\{a\}\{b\}\}?.*\\log_b\(\\frac\{a\}\{b\}\)"),
    ("ML_D28", "bốn cơ số là b, b², b³, b⁴", "bases4", r""),
    ("ML_D41", "cơ số của lôgarit bằng hệ số trong (px+p) và mũ là (p²)^y", "d41", r""),
    ("ML_D36a", "phương án là đẳng thức của log(a^k) hoặc log(ka), lôgarit thập phân không ghi cơ số", "opts_all", r"\\log\((a\^\d+|\d+a)\)="),
    ("ML_D36b", "phương án là biểu thức theo log_c a (log_c a có mặt trong ít nhất ba phương án)", "opts_min3", r"\\log_\d+a"),
    ("ML_D76", "phương án theo log_a b", "opts_min3", r"\\log_ab"),
    ("ML_D14", "cơ số của lôgarit là phân số 1/p với p nguyên dương", "stem", r"\\log_(?:\{\\frac\{1\}\{\d+\}\}|\\frac1\d+)"),
    ("ML_D17", "biểu thức P có hạng tử log_b(a/b)", "stem", r"\\log_b\(\\frac\{a\}\{b\}\)"),
    ("ML_D31_none", "(không dùng)", "stem", r""),
]


def run():
    old, rows = load_questions()
    bad = 0
    for code, desc, where, pat in CLAIMS:
        if code.endswith("_none"):
            continue
        qs = [r for r in rows if r["label"] == code]
        ok = 0
        for r in qs:
            if where == "stem":
                txt = norm(r["text"])
                hit = re.search(pat, txt) is not None
            elif where == "bases4":
                m = re.search(r"\\log_(\d+)x\.\\log_(\d+)x\.\\log_(\d+)x\.\\log_(\d+)x=", norm(r["text"]))
                hit = bool(m) and all(int(m.group(i)) == int(m.group(1)) ** i for i in range(1, 5))
            elif where == "d41":
                m = re.search(r"\\log_(\d+)\((\d+)x\+(\d+)\)\+x=\d*y\+(\d+)\^y", norm(r["text"]))
                hit = bool(m) and int(m.group(1)) == int(m.group(2)) == int(m.group(3)) and int(m.group(4)) == int(m.group(1)) ** 2
            else:
                opts = options(r["text"])
                texts = [norm(v) for v in opts.values()]          # one option has no 'A.' marker, so norm keeps all of it
                n = sum(1 for t in texts if re.search(pat, t))
                hit = (n == len(texts) and len(texts) == 4) if where == "opts_all" else n >= 3
            ok += hit
        flag = "OK " if ok == len(qs) else "XX "
        bad += ok != len(qs)
        print(f"{flag}{code}: {ok}/{len(qs)}  {desc}")
    return bad


if __name__ == "__main__":
    run()
