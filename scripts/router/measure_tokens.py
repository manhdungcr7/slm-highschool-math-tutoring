# -*- coding: utf-8 -*-
"""Token lengths of the router training pairs with the real Qwen3 tokenizer (chat template, thinking off)."""
import json
import os
import statistics

import numpy as np
from transformers import AutoTokenizer

from common import REPO

tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
rows = [json.loads(l) for l in open(os.path.join(REPO, "data", "router_train", "finetune_router.jsonl"), encoding="utf-8")]
P, C = [], []
for r in rows:
    prompt = tok.apply_chat_template([dict(role="user", content=r["prompt"])], tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    P.append(len(tok(prompt, add_special_tokens=False).input_ids))
    C.append(len(tok(r["completion"] + "<|im_end|>", add_special_tokens=False).input_ids))
P, C = np.array(P), np.array(C)
T = P + C
print("pairs:", len(rows))
for name, a in (("prompt", P), ("completion", C), ("total", T)):
    print(f"{name:11s} mean {a.mean():6.1f} median {np.median(a):6.0f} p95 {np.percentile(a, 95):6.0f} p99 {np.percentile(a, 99):6.0f} max {a.max()}")
print("total tokens per epoch:", int(T.sum()), "| loss tokens if completion only:", int(C.sum()))
print("share of completion tokens in the sequence:", round(float(C.sum() / T.sum()), 3))
print("tokens of the example completion 'Dạng 17: …':", tok("Dạng 17: abc", add_special_tokens=False).input_ids[:6],
      [tok.decode([i]) for i in tok("Dạng 17:", add_special_tokens=False).input_ids])
print("sequences longer than 1024:", int((T > 1024).sum()), "| longer than 768:", int((T > 768).sum()), "| longer than 512:", int((T > 512).sum()))
