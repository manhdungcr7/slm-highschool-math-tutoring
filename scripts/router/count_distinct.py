# -*- coding: utf-8 -*-
"""How many different questions does each type really have? (distinct stem, distinct stem+options)"""
import collections
import re

from common import load_questions, stem

old, rows = load_questions()
by_stem = collections.defaultdict(set)
by_full = collections.defaultdict(set)
cnt = collections.Counter()
for r in rows:
    if r["source"] == "Câu gốc":
        continue
    s = re.sub(r"\s+", " ", stem(r["text"])).strip()
    f = re.sub(r"\s+", " ", r["text"]).strip()
    by_stem[r["label"]].add(s)
    by_full[r["label"]].add(f)
    cnt[r["label"]] += 1

low = sorted(cnt, key=lambda c: len(by_stem[c]))
print("types:", len(cnt), "| variants per type:", sorted(set(cnt.values())))
print("distinct stems per type: min", len(by_stem[low[0]]), "median", len(by_stem[low[len(low) // 2]]))
hist = collections.Counter()
for c in cnt:
    n = len(by_stem[c])
    hist["<=20" if n <= 20 else "21-50" if n <= 50 else "51-80" if n <= 80 else "81-89" if n < 90 else "90"] += 1
print(dict(hist))
print("lowest 30 (code, distinct stems, distinct full questions):")
for c in low[:30]:
    print(f"  {c}: {len(by_stem[c])} / {len(by_full[c])} of {cnt[c]}")
