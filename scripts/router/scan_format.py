# -*- coding: utf-8 -*-
"""Scan the new training questions for presentation problems (signs, empty braces, odd dollar signs, stray text...)."""
import collections
import json
import os
import re

from common import REPO

rows = [json.loads(l) for l in open(os.path.join(REPO, "data", "router_train", "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]

CHECKS = {
    "dấu + rồi - (+-)": r"\+\s*-(?!\d*\\?[a-z]*\s*\))",
    "hai dấu trừ liền (--)": r"(?<![\-\\])--(?!-)",
    "dấu trừ rồi cộng (-+)": r"-\s*\+",
    "ngoặc nhọn rỗng {}": r"\{\s*\}",
    "số mũ rỗng ^{}": r"\^\{\s*\}",
    "hệ số 1 thừa (1x, 1i, 1\\log...)": r"(?<![\d.,/\\])1\s*(x\b|i\b|\\ln|\\log|y\b|m\b)",
    "hệ số 0 thừa (0x, 0i)": r"(?<![\d.,])0\s*(x|i|y|m)\b",
    "số mũ ^{1}": r"\^\{1\}(?!\d)",
    "ký tự lạ (None, nan, inf)": r"\bNone\b|\bnan\b|\binf\b|\bzoo\b",
    "hai dấu cách liền": r"[^\s]  +[^\s]",
    "dấu chấm câu lặp (.. hoặc ,,)": r"\.\.|,,",
    "dấu ngoặc trống ()": r"\(\s*\)",
    "ký hiệu sympy (Rational, sqrt( , log( ...)": r"Rational|\bsqrt\(|\blog\(|\bI\b\*|\*\*|\bsp\.",
    "dấu * (nhân) lộ ra": r"(?<!\\cdot)\*",
    "lệnh LaTeX lạ (\\text{ lỗi...)": r"\\\\[a-zA-Z]",
    "ký tự điều khiển": r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
    "thiếu dấu cách sau 'Có bao nhiêu'/'Cho' dính chữ": r"[a-zà-ỹ]\$[A-Za-z]",
}
LOOSE = {}
count = collections.Counter()
examples = collections.defaultdict(list)
for r in rows:
    txt = r["de_bai"]
    if txt.count("$") % 2:
        count["số dấu $ lẻ"] += 1
        examples["số dấu $ lẻ"].append((r["stt"], txt[:150]))
    for name, pat in CHECKS.items():
        m = re.search(pat, txt)
        if m:
            count[name] += 1
            if len(examples[name]) < 5:
                s = max(0, m.start() - 50)
                examples[name].append((r["stt"], txt[s:m.end() + 50].replace("\n", " | ")))
    if re.search(r"\$\s*\$", txt):
        count["cặp $ trống"] += 1
    if "\n\n" not in txt:
        count["thiếu dòng trống giữa đề và phương án"] += 1
        if len(examples["thiếu dòng trống giữa đề và phương án"]) < 5:
            examples["thiếu dòng trống giữa đề và phương án"].append((r["stt"], txt[:120].replace("\n", " | ")))
    if not re.search(r"\n\s*A\.", txt) or not re.search(r"\n\s*D\.", txt):
        count["thiếu phương án"] += 1
    if txt != txt.strip():
        count["khoảng trắng đầu/cuối"] += 1
    if not txt.rstrip().endswith((".", "$.", "?", "là", "bằng", "đạo hàm", "$")) and not re.search(r"[\.\?]$", txt.splitlines()[-1].strip()):
        pass

print("questions scanned:", len(rows))
for name, n in count.most_common():
    print(f"{n:6d}  {name}")
    for st, ex in examples[name][:4]:
        print(f"          [{st}] {ex}")
