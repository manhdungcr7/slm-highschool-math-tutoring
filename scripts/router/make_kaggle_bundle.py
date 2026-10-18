# -*- coding: utf-8 -*-
"""Build the folder to upload as a Kaggle Dataset for the router fine-tuning notebook.

  finetune_router.jsonl   training pairs (copy)
  eval_set.jsonl          the EXISTING dataset (the test set) with its 'Dạng N' label, same prompt as in training
  candidates.json         the 142 strings 'Dạng N: mô tả' (the possible outputs), in order of N

python make_kaggle_bundle.py
"""
import json
import os
import shutil

from assemble_train import PROMPT, catalogue
from common import REPO, load_questions

OUT = os.path.join(REPO, "data", "router_train", "kaggle_bundle")
os.makedirs(OUT, exist_ok=True)
num, by_code = catalogue()

# 1) candidates, in order of N
cands = sorted(((num[c], f"Dạng {num[c]}: {e['name']}") for c, e in by_code.items()))
assert [n for n, _ in cands] == list(range(1, 143))
json.dump([s for _, s in cands], open(os.path.join(OUT, "candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
cand_by_n = dict(cands)

# 2) training pairs: every completion must be one of the candidates
shutil.copy(os.path.join(REPO, "data", "router_train", "finetune_router.jsonl"), os.path.join(OUT, "finetune_router.jsonl"))
train = [json.loads(l) for l in open(os.path.join(OUT, "finetune_router.jsonl"), encoding="utf-8")]
assert all(r["completion"] in set(cand_by_n.values()) for r in train)

# 3) the existing dataset as the test set
_, rows = load_questions()
n = 0
with open(os.path.join(OUT, "eval_set.jsonl"), "w", encoding="utf-8") as f:
    for i, r in enumerate(rows, start=1):
        code = r["label"]
        rec = dict(id=i, so_dang=num[code], ten_goi=f"Dạng {num[code]}", ma_cu=code,
                   nguon="Câu gốc" if r["source"] == "Câu gốc" else "Biến thể",
                   chu_de="Mũ-Logarit" if code.startswith("ML_") else "Số phức",
                   de_bai=r["text"], prompt=PROMPT + r["text"])
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n += 1
print("candidates:", len(cands), "| training pairs:", len(train), "| test questions:", n)
for name in sorted(os.listdir(OUT)):
    print(f"  {name:24s} {os.path.getsize(os.path.join(OUT, name)) / 1e6:6.1f} MB")
