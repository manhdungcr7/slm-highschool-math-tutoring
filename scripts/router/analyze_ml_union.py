# -*- coding: utf-8 -*-
"""Union of several sandbox passes: how many really new Mũ-Logarit questions per type?

python analyze_ml_union.py <dir_with_json> [<dir_with_json> ...]   (each dir holds batch_*.json / Dxx_bien_the.json)
"""
import collections
import glob
import os
import sys

from collect_new import load_json_rows, question_key
from common import DROPPED, load_questions

old_names, rows = load_questions()
existing = collections.defaultdict(set)
for r in rows:
    if r["topic"] == "ML":
        existing[r["label"]].add(question_key(r["label"], r["text"]))

pool = collections.defaultdict(dict)       # label -> key -> item
for d in sys.argv[1:]:
    for path in sorted(glob.glob(os.path.join(d, "*.json"))):
        for it in load_json_rows(path):
            label = "ML_" + it["ma_dang"]
            if label in DROPPED or label not in existing:
                continue
            k = question_key(label, it["de_bai"])
            if k not in existing[label] and k not in pool[label]:
                pool[label][k] = it

short = []
for label in sorted(existing, key=lambda c: (int(c[4:].rstrip("ab")), c)):
    n = len(pool[label])
    if n < 90:
        short.append((label, n))
print("passes:", len(sys.argv) - 1, "| types with fewer than 90 new questions:", len(short))
for label, n in short:
    print(f"  {label:9s} {n:3d}")
