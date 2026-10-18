# -*- coding: utf-8 -*-
"""Replace the few training questions that have exactly the content of a test question OF THE SAME dạng.

Found by style_gap.content_key (stem maths + set of options, independent of how it is written). Only two dạng were affected:
  Dạng 91  Phần ảo của số phức z = a+bi   (small integers: the space of questions is small, ten collided with test questions)
  Dạng 32  log_B a = log_(B^k)(ab)        (one collided with the test question that has B = 2, k = 3)
The replacement is generated the same way as the original questions, with a new content that is not in the test set.
"""
import random
import re


def new_d91(original, rnd):
    lines = original.split("\n")
    stem = lines[0]
    m = re.match(r"^(Phần ảo của số phức )\$z = .+\$(.*)$", stem)
    if not m:
        return None
    a = rnd.choice([x for x in range(-9, 10) if x != 0])
    b = rnd.choice([x for x in range(-9, 10) if x != 0 and abs(x) != abs(a)])
    z = f"{a}{'+' if b > 0 else '-'}{abs(b)}i"
    opts = [b, -b, a, -a]
    rnd.shuffle(opts)
    blank = "\n\n" in original
    body = f"{m.group(1)}$z = {z}${m.group(2)}" + ("\n\n" if blank else "\n")
    return body + "\n".join(f"{'ABCD'[i]}. ${o}$." for i, o in enumerate(opts))


def new_d32(original, rnd):
    base = rnd.choice(range(2, 31))
    k = rnd.choice([2, 3, 4, 5])
    p = lambda e: "a" if e == 1 else f"a^{{{e}}}"
    q = lambda e: "b" if e == 1 else f"b^{{{e}}}"
    correct = f"{p(k - 1)}=b" if k - 1 > 1 else "a=b"
    pool = [f"{p(k)}=b", f"a={q(k - 1)}" if k - 1 > 1 else "a^{2}=b", "a=b" if k - 1 > 1 else f"a=b^{{{k}}}"]
    pool = [x for x in dict.fromkeys(pool) if x != correct][:3]
    if len(pool) < 3:
        return None
    opts = [correct] + pool
    rnd.shuffle(opts)
    stem = (f"Xét tất cả các số thực dương $a$ và $b$ thỏa mãn $\\log_{{{base}}} a=\\log_{{{base ** k}}}(ab)$.\n"
            "Mệnh đề nào dưới đây đúng?")
    return stem + "\n\n" + "\n".join(f"{'ABCD'[i]}. ${o}$." for i, o in enumerate(opts))


GENERATORS = {91: new_d91, 32: new_d32}
