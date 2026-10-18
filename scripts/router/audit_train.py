# -*- coding: utf-8 -*-
"""Final audit of the router training set written by assemble_train.py.

Checks, on the files as written:
  1. every one of the 142 types has exactly 90 questions;
  2. no question of the new set equals a question of the existing dataset (test set), by key and by exact text;
  3. no repeated question inside the new set;
  4. each question has four distinct options A-D and its answer is one of them; no mojibake;
  5. each question matches the signature of its own type and of no other type;
  6. every fine-tuning pair has the output 'Dạng N: mô tả' that belongs to the question's type;
  7. the distribution of the correct letter.
"""
import collections
import json
import os
import re
import sys

from assemble_train import MOJIBAKE, PROMPT, catalogue, option_ok
from collect_new import question_key
from common import REPO, has_identical_pair, load_questions, norm

OUT = os.path.join(REPO, "data", "router_train")
rows = [json.loads(l) for l in open(os.path.join(OUT, "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]
ft = [json.loads(l) for l in open(os.path.join(OUT, "finetune_router.jsonl"), encoding="utf-8")]
num, by_code = catalogue()
sig = {c: re.compile(e["pattern"]) for c, e in by_code.items()}
_, old = load_questions()
old_keys = {(r["label"], question_key(r["label"], r["text"])) for r in old}
old_text = {re.sub(r"\s+", "", r["text"]) for r in old}

problems = collections.Counter()
per = collections.Counter(r["ma_cu"] for r in rows)
if len(per) != 142 or set(per.values()) != {90}:
    problems["not 90 per type"] += 1
    print("per-type counts:", sorted(set(per.values())), len(per))
seen = set()
letters = collections.Counter()
for r in rows:
    code = r["ma_cu"]
    k = question_key(code, r["de_bai"])
    if (code, k) in old_keys or re.sub(r"\s+", "", r["de_bai"]) in old_text:
        problems["same as an existing question"] += 1
    if (code, k) in seen:
        problems["repeated in the new set"] += 1
    seen.add((code, k))
    ok, why = option_ok(r["de_bai"], r["dap_an_dung"])
    if not ok:
        problems["options: " + why] += 1
    if MOJIBAKE.search(r["de_bai"]) or MOJIBAKE.search(r["dap_an_dung"]):
        problems["mojibake"] += 1
    if has_identical_pair(r["de_bai"]):
        problems["identical z1 = z2"] += 1
    hits = [c for c, p in sig.items() if p.search(norm(r["de_bai"]))]
    if hits != [code]:
        problems["signature"] += 1
    letters[r["dap_an_dung"][0]] += 1
    if r["ten_goi"] != f"Dạng {num[code]}":
        problems["name/number mismatch"] += 1

by_stt = {r["stt"]: r for r in rows}
for p in ft:
    r = by_stt[p["stt"]]
    want = f"{r['ten_goi']}: {by_code[r['ma_cu']]['name']}"
    if p["completion"] != want or p["messages"][1]["content"] != want:
        problems["fine-tune output wrong"] += 1
    if p["prompt"] != PROMPT + r["de_bai"] or p["messages"][0]["content"] != p["prompt"]:
        problems["fine-tune input wrong"] += 1
if len(ft) != len(rows) or len({p["stt"] for p in ft}) != len(rows):
    problems["fine-tune count"] += 1

print("questions:", len(rows), "| types:", len(per), "| fine-tune pairs:", len(ft))
print("correct letter distribution:", dict(sorted(letters.items())))
print("problems:", dict(problems) if problems else "none")
sys.exit(1 if problems else 0)
