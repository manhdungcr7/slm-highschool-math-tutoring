# -*- coding: utf-8 -*-
"""Second, independent answer check for the 32 Mũ-Logarit types that have a ReAct method.

The Calculator program of each type (scripts/experiments/react/dang_Dxx.py) is replayed on every NEW question; the option it
finds true must be the letter the generator marked as correct. This path shares no code with the question generators.

python verify_replay.py
"""
import collections
import importlib
import json
import os
import re
import sys

from common import REPO

REACT_DIR = os.path.join(REPO, "scripts", "experiments", "react")
sys.path.insert(0, REACT_DIR)
os.chdir(REACT_DIR)
bm = importlib.import_module("build_multi_notebook")

data = [json.loads(l) for l in open(os.path.join(REPO, "data", "router_train", "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]
by = collections.defaultdict(list)
for r in data:
    if r["ma_cu"].startswith("ML_"):
        by[r["ma_cu"][3:]].append(r)

ok_total = bad_total = err_total = 0
problems = []
for path in sorted(os.listdir(REACT_DIR)):
    m = re.match(r"dang_(D\d+)\.py$", path)
    if not m:
        continue
    code = m.group(1)
    if code not in by:
        continue
    dang = importlib.import_module(f"dang_{code}")
    ok = bad = err = 0
    for r in by[code]:
        letter = re.match(r"\s*([ABCD])\.", r["dap_an_dung"]).group(1)
        try:
            matched, _ = bm.replay(dang, r["de_bai"])
        except Exception as e:                      # the question has a shape the replay program does not parse
            err += 1
            if len(problems) < 12:
                problems.append((code, r["stt"], "error", type(e).__name__, str(e)[:100]))
            continue
        if matched == [letter]:
            ok += 1
        else:
            bad += 1
            if len(problems) < 12:
                problems.append((code, r["stt"], "mismatch", matched, letter))
    ok_total += ok
    bad_total += bad
    err_total += err
    print(f"{code}: replay agrees {ok}/{len(by[code])}  disagrees {bad}  could not parse {err}")
print(f"TOTAL agree {ok_total}  disagree {bad_total}  could not parse {err_total}")
for p in problems:
    print("  ", p)
