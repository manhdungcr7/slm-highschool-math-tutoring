# -*- coding: utf-8 -*-
"""How many really new questions does a sandbox pass give for each Mũ-Logarit type?

python analyze_ml_pass.py <sandbox_ml_dir>
"""
import collections
import glob
import os
import sys

from collect_new import load_json_rows, question_key
from common import DROPPED, load_questions

sandbox = sys.argv[1]
old_names, rows = load_questions()
existing = collections.defaultdict(set)
for r in rows:
    if r["topic"] == "ML":
        existing[r["label"]].add(question_key(r["label"], r["text"]))

new_rows = collections.defaultdict(list)
for path in sorted(glob.glob(os.path.join(sandbox, "data", "questions", "mu_logarit_extraction", "bien_the", "*.json"))):
    for it in load_json_rows(path):
        label = "ML_" + it["ma_dang"]
        if label in DROPPED or label not in existing:
            continue
        new_rows[label].append(it)

print(f"{'type':9s} generated  unique_in_pass  new_vs_existing")
short = []
for label in sorted(existing, key=lambda c: (int(c[4:].rstrip('ab')), c)):
    gen = new_rows.get(label, [])
    seen, fresh = set(), []
    for it in gen:
        k = question_key(label, it["de_bai"])
        if k in seen:
            continue
        seen.add(k)
        if k not in existing[label]:
            fresh.append(it)
    flag = "" if len(fresh) >= 90 else "   <-- short"
    if len(fresh) < 90:
        short.append((label, len(gen), len(seen), len(fresh)))
    print(f"{label:9s} {len(gen):9d} {len(seen):15d} {len(fresh):16d}{flag}")
print()
print("types below 90 new questions:", len(short))
