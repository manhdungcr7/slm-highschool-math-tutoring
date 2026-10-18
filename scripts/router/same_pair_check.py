# -*- coding: utf-8 -*-
"""Count questions where the two given complex numbers are identical (z1 = z2), old set vs new set."""
import collections
import json
import os
import re

from common import REPO, load_questions

old_names, old = load_questions()
new = [json.loads(l) for l in open(os.path.join(REPO, "data", "router_train", "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]
PAT = re.compile(r"\$(z_1|z)\s*=\s*([^$]+?)\$\s*(?:và|,)\s*\$?(z_2|w)\s*=\s*([^$]+?)\$")


def same(text):
    m = PAT.search(text)
    return bool(m) and re.sub(r"\s+", "", m.group(2)) == re.sub(r"\s+", "", m.group(4))


co, cn = collections.Counter(), collections.Counter()
for r in old:
    if r["topic"] == "SP" and same(r["text"]):
        co[r["label"]] += 1
for r in new:
    if r["ma_cu"].startswith("SP_") and same(r["de_bai"]):
        cn[r["ma_cu"]] += 1
print("old:", sum(co.values()), dict(co))
print("new:", sum(cn.values()), dict(cn))
