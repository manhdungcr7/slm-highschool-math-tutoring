# -*- coding: utf-8 -*-
"""Compare presentation quirks and number sizes between the existing dataset (test) and the new training set."""
import collections
import json
import os
import re

from common import REPO, load_questions

old_names, old = load_questions()
new = [json.loads(l) for l in open(os.path.join(REPO, "data", "router_train", "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]

QUIRKS = {
    "chữ 'Vô số' nằm trong $...$ (không có \\text)": r"\$Vô số\$",
    "hệ số 1 hiện ra: '+1\\cdot', '1\\ln', '+1y'": r"[+-]\s*1\\cdot\d|[+-]\s*1\\ln|[+-]\s*1\\log|[+-]1y\b",
    "số mũ ^{1}": r"\^\{1\}(?!\d)",
    "dấu cách sau dấu trừ ('- \\dfrac', '- 3')": r"-\s\\dfrac|-\s\d|-\s\\sqrt",
    "dấu cách trong tích hệ số ('3 x', '2 x')": r"\d\sx\b",
    "phân số lồng '\\dfrac{\\dfrac'": r"\\dfrac\{\\dfrac",
    "hai số phức z1 = z2 giống hệt": None,
}
cnt_old, cnt_new = collections.Counter(), collections.Counter()
for name, pat in QUIRKS.items():
    if pat is None:
        continue
    cnt_old[name] = sum(bool(re.search(pat, r["text"])) for r in old)
    cnt_new[name] = sum(bool(re.search(pat, r["de_bai"])) for r in new)


def same_z(text):
    m = re.search(r"z_1 = (.*?) và z_2 = (.*?)\.", text)
    return bool(m) and m.group(1).strip() == m.group(2).strip()


cnt_old["hai số phức z1 = z2 giống hệt"] = sum(same_z(r["text"]) for r in old)
cnt_new["hai số phức z1 = z2 giống hệt"] = sum(same_z(r["de_bai"]) for r in new)
print(f"{'hiện tượng':55s} {'bộ cũ':>8s} {'bộ mới':>8s}   (trên {len(old)} / {len(new)} đề)")
for name in QUIRKS:
    print(f"{name:55s} {cnt_old[name]:8d} {cnt_new[name]:8d}")


def max_digits(text):
    nums = re.findall(r"\d+", re.sub(r"\\[a-zA-Z]+", " ", text.split("\n\n")[0] if "\n\n" in text else text))
    return max((len(n) for n in nums), default=0)


mo, mn = collections.defaultdict(list), collections.defaultdict(list)
for r in old:
    if r["source"] != "Câu gốc":
        mo[r["label"]].append(max_digits(r["text"]))
for r in new:
    mn[r["ma_cu"]].append(max_digits(r["de_bai"]))
print("\nDạng mà đề mới có số dài hơn hẳn bộ cũ (độ dài chữ số lớn nhất trong phần đề, không tính phương án):")
rows = []
for code in mo:
    a, b = max(mo[code]), max(mn[code])
    if b >= a + 3:
        rows.append((code, a, b, sum(x > a for x in mn[code])))
for code, a, b, k in sorted(rows, key=lambda r: -(r[2] - r[1])):
    print(f"  {code:8s} bộ cũ tối đa {a:2d} chữ số, bộ mới tối đa {b:2d}; {k}/90 đề mới dài hơn mức tối đa của bộ cũ")
