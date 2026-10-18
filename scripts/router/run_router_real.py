# -*- coding: utf-8 -*-
"""Run the fine-tuned router on the real-world questions (no ground-truth dạng): predicted dạng, confidence, top 3.

python run_router_real.py <questions.csv> <adapter_dir> <out.csv>
Same two-stage scoring as the training notebook: the part 'Dạng N:' of all 142 candidates, then the whole text of the best 5.
"""
import copy
import csv
import json
import os
import re
import sys
import time

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

Q, ADAPTER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
BUNDLE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "router_train", "kaggle_bundle")
PROMPT = ("Hãy xác định dạng bài của đề bài sau. Chỉ trả lời đúng một dòng theo mẫu "
          "\"Dạng N: mô tả dạng bài\", trong đó N là số thứ tự của dạng.\n\nĐề bài:\n")
EOS = "<|im_end|>"
CHUNK = int(os.environ.get("ROUTER_CHUNK", "24"))
sys.stdout.reconfigure(encoding="utf-8")

CANDS = json.load(open(os.path.join(BUNDLE, "candidates.json"), encoding="utf-8"))
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float16, device_map={"": 0})
model = PeftModel.from_pretrained(model, ADAPTER).merge_and_unload().eval()
DEV = next(model.parameters()).device
CAND_IDS = [tok(c + EOS, add_special_tokens=False).input_ids for c in CANDS]
COLON = tok(":", add_special_tokens=False).input_ids[0]
LABEL_LEN = [ids.index(COLON) + 1 for ids in CAND_IDS]


def to_training_layout(q):
    """Real questions have the options inline ('stem A. .. B. .. C. .. D. ..'); the training questions have the stem, a blank line, then one option per line."""
    parts = re.split(r"(?:^|\n|\s)(?=[A-D]\.\s)", q.strip())
    stem, opts = parts[0].strip(), [p.strip() for p in parts[1:]]
    if len(opts) != 4:
        return q.strip()
    fixed = []
    for o in opts:
        o = o.rstrip(";").rstrip()
        fixed.append(o if o.endswith(".") else o + ".")
    return stem + "\n\n" + "\n".join(fixed)


def prompt_text(user):
    return tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True, enable_thinking=False)


@torch.no_grad()
def prompt_state(user):
    p_ids = tok(prompt_text(user), add_special_tokens=False, return_tensors="pt").input_ids.to(DEV)
    out = model(input_ids=p_ids, use_cache=True)
    return out.past_key_values, p_ids.shape[1], torch.log_softmax(out.logits[0, -1].float(), -1)


@torch.no_grad()
def sum_logprob(state, token_lists, chunk):
    cache, L, first = state
    res = torch.zeros(len(token_lists))
    for s in range(0, len(token_lists), chunk):
        part = token_lists[s:s + chunk]
        n = len(part)
        m = max(len(x) for x in part)
        ids = torch.full((n, m), tok.pad_token_id, dtype=torch.long)
        msk = torch.zeros((n, m), dtype=torch.long)
        for i, x in enumerate(part):
            ids[i, :len(x)] = torch.tensor(x)
            msk[i, :len(x)] = 1
        c = copy.deepcopy(cache)
        c.batch_repeat_interleave(n)
        attn = torch.cat([torch.ones((n, L), dtype=torch.long), msk], 1).to(DEV)
        o = model(input_ids=ids.to(DEV), attention_mask=attn, past_key_values=c, use_cache=True)
        logp = torch.log_softmax(o.logits.float(), -1)
        tgt = ids[:, 1:].to(DEV)
        tok_lp = logp[:, :-1].gather(2, tgt.unsqueeze(-1)).squeeze(-1) * msk[:, 1:].to(DEV)
        tok_lp = torch.cat([first[ids[:, 0].to(DEV)].unsqueeze(1), tok_lp], 1)
        cum = tok_lp.cumsum(1)
        for i in range(n):
            res[s + i] = cum[i, len(part[i]) - 1].item()
        del o, logp, c
    return res


@torch.no_grad()
def score_candidates(user, top=5):
    state = prompt_state(user)
    label = sum_logprob(state, [ids[:LABEL_LEN[i]] for i, ids in enumerate(CAND_IDS)], CHUNK)
    best = torch.topk(label, top).indices.tolist()
    full = sum_logprob(state, [CAND_IDS[i] for i in best], top)
    return label, best, full


rows = list(csv.DictReader(open(Q, encoding="utf-8-sig", newline="")))
out_rows = []
t0 = time.time()
for i, r in enumerate(rows):
    user = PROMPT + to_training_layout(r["question_markdown_latex"])
    label, best, full = score_candidates(user)
    order = [best[j] for j in torch.argsort(full, descending=True).tolist()]
    pred = order[0] + 1
    conf = float(torch.softmax(label, 0).max())
    out_rows.append(dict(id=r["id"], topic=r["topic"], du_doan_dang=pred, do_tin_cay=round(conf, 4),
                         top3="; ".join(str(k + 1) for k in order[:3]), mo_ta_du_doan=CANDS[order[0]].split(": ", 1)[1][:200],
                         cau_hoi=r["question_markdown_latex"].replace("\n", " ")[:300]))
    if i % 10 == 0:
        el = time.time() - t0
        print(f"{i + 1}/{len(rows)} | {el / 60:.1f} min | about {el / (i + 1) * (len(rows) - i - 1) / 60:.0f} min left", flush=True)
        with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
            w.writeheader(); w.writerows(out_rows)
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
    w.writeheader(); w.writerows(out_rows)
print("done", len(out_rows), "rows in", round((time.time() - t0) / 60, 1), "min", flush=True)
