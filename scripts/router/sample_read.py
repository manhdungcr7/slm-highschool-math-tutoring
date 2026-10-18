# -*- coding: utf-8 -*-
"""Print 4 random new questions of each type (reproducible) for reading.

python sample_read.py <first_dang> <last_dang> [per_type] [seed]
"""
import collections
import json
import os
import random
import sys

from common import REPO

lo, hi = int(sys.argv[1]), int(sys.argv[2])
per = int(sys.argv[3]) if len(sys.argv) > 3 else 4
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
rows = [json.loads(l) for l in open(os.path.join(REPO, "data", "router_train", "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]
by = collections.defaultdict(list)
for r in rows:
    by[r["so_dang"]].append(r)
for n in range(lo, hi + 1):
    rs = by[n]
    pick = random.Random(f"{seed}|{n}").sample(rs, per)
    print(f"##### Dạng {n} ({rs[0]['ma_cu']})")
    for r in pick:
        print(f"[{r['stt']}] " + r["de_bai"].replace("\n\n", " || ").replace("\n", " | "))
        print(f"      ĐÁP ÁN: {r['dap_an_dung']}")
