# -*- coding: utf-8 -*-
"""One fine-tuning experiment for the type router; used to choose the settings (model size, epochs, LoRA rank, learning rate, loss).

python router_sweep.py --name r16_lr2e-4 --model Qwen/Qwen3-0.6B --rank 16 --lr 2e-4 --epochs 2 --per-type 40

It trains a LoRA adapter with a plain PyTorch loop, and after every epoch answers a fixed test sample (172 source questions
+ 5 variants of every type of the EXISTING dataset): the model writes the first tokens of its answer, 'Dạng N' is read from
them and compared with the true type. One JSON line per epoch is appended to sweep_results.jsonl.
"""
import argparse
import json
import math
import os
import random
import re
import time

import numpy as np
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True)
ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
ap.add_argument("--quant", default="none", choices=["none", "4bit"])
ap.add_argument("--rank", type=int, default=16)
ap.add_argument("--alpha-mult", type=float, default=2.0)       # lora_alpha = alpha_mult * rank
ap.add_argument("--lr", type=float, default=2e-4)
ap.add_argument("--epochs", type=int, default=2)
ap.add_argument("--loss", default="completion", choices=["completion", "all"])
ap.add_argument("--per-type", type=int, default=0)            # training pairs per type (0 = all 90)
ap.add_argument("--bs", type=int, default=8)
ap.add_argument("--accum", type=int, default=4)
ap.add_argument("--max-len", type=int, default=768)
ap.add_argument("--no-gc", action="store_true")                # no gradient checkpointing
ap.add_argument("--dropout", type=float, default=0.05)
ap.add_argument("--targets", default="all", choices=["all", "attn"])
ap.add_argument("--eval-per-type", type=int, default=5)
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--skip-eval", action="store_true")
ap.add_argument("--desc-weight", type=float, default=1.0)   # loss weight of the description after "Dạng N:" (1 = same as the number)
ap.add_argument("--bundle", default=r"F:\slm-highschool-math-tutoring\data\router_train\kaggle_bundle")
ap.add_argument("--results", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "sweep_results.jsonl"))
A = ap.parse_args()

random.seed(A.seed); np.random.seed(A.seed); torch.manual_seed(A.seed)
dev = "cuda"
DT = torch.bfloat16
tok = AutoTokenizer.from_pretrained(A.model)
tok.padding_side = "right"
EOS = "<|im_end|>"


def rj(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def prompt_text(user):
    return tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True,
                                   enable_thinking=False)


train = rj(os.path.join(A.bundle, "finetune_router.jsonl"))
by = {}
for r in train:
    by.setdefault(int(re.match(r"Dạng (\d+):", r["completion"]).group(1)), []).append(r)
rng = random.Random(A.seed)
rows = []
for n, rs in sorted(by.items()):
    rs = rs[:]; rng.shuffle(rs)
    rows += rs[:A.per_type] if A.per_type else rs
rng.shuffle(rows)


COLON = tok(":", add_special_tokens=False).input_ids[0]


def enc(user, comp):
    p = tok(prompt_text(user), add_special_tokens=False).input_ids
    c = tok(comp + EOS, add_special_tokens=False).input_ids
    ids = p + c
    lab = ([-100] * len(p) + c) if A.loss == "completion" else list(ids)
    k = c.index(COLON) + 1                                  # tokens of 'Dạng N:' ; the rest is the description
    w = [0.0] * len(p) + [1.0] * k + [A.desc_weight] * (len(c) - k)
    if A.loss == "all":
        w = [1.0] * len(ids)
    return ids[:A.max_len], lab[:A.max_len], w[:A.max_len]


data = [enc(r["prompt"], r["completion"]) for r in rows]
n_tok = sum(len(i) for i, _, _ in data)
print(f"[{A.name}] training pairs {len(data)} | tokens/epoch {n_tok:,}", flush=True)

# ---- fixed test sample from the EXISTING dataset
test_all = rj(os.path.join(A.bundle, "eval_set.jsonl"))
src = [r for r in test_all if r["nguon"] == "Câu gốc"]
var = [r for r in test_all if r["nguon"] != "Câu gốc"]
trng = random.Random(7)
samp = []
for n in range(1, 143):
    vs = [r for r in var if r["so_dang"] == n]
    samp += trng.sample(vs, min(A.eval_per_type, len(vs)))
test = src + samp
print(f"[{A.name}] test sample: {len(src)} source + {len(samp)} variants", flush=True)

# ---- model
quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                           bnb_4bit_compute_dtype=DT) if A.quant == "4bit" else None
model = AutoModelForCausalLM.from_pretrained(A.model, dtype=DT, quantization_config=quant, device_map={"": 0})
model.config.use_cache = False
if A.quant == "4bit":
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=not A.no_gc,
                                            gradient_checkpointing_kwargs={"use_reentrant": False})
elif not A.no_gc:
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
targets = ["q_proj", "k_proj", "v_proj", "o_proj"] + (["gate_proj", "up_proj", "down_proj"] if A.targets == "all" else [])
model = get_peft_model(model, LoraConfig(r=A.rank, lora_alpha=int(A.alpha_mult * A.rank), lora_dropout=A.dropout, bias="none",
                                         task_type="CAUSAL_LM", target_modules=targets))
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
params = [p for p in model.parameters() if p.requires_grad]
for p in params:
    p.data = p.data.float()                       # adapter weights in fp32, compute in bf16
opt = torch.optim.AdamW(params, lr=A.lr, weight_decay=0.0, betas=(0.9, 0.999))
steps_per_epoch = len(data) // (A.bs * A.accum)
total = steps_per_epoch * A.epochs
warm = max(1, int(0.03 * total))


def lr_at(step):
    if step < warm:
        return A.lr * (step + 1) / warm
    return A.lr * 0.5 * (1 + math.cos(math.pi * (step - warm) / max(1, total - warm)))


def batches(order):
    # length-grouped mini-batches: sort inside chunks of 64 sequences to reduce padding
    out = []
    for s in range(0, len(order) - A.bs + 1, A.bs * 8):
        chunk = sorted(order[s:s + A.bs * 8], key=lambda i: len(data[i][0]))
        out += [chunk[j:j + A.bs] for j in range(0, len(chunk) - A.bs + 1, A.bs)]
    random.shuffle(out)
    return out


def collate(idx):
    """Left-padded batch: the answer sits at the end of every row, so only the last K positions need logits."""
    m = max(len(data[i][0]) for i in idx)
    ids = torch.full((len(idx), m), tok.pad_token_id); lab = torch.full((len(idx), m), -100)
    att = torch.zeros((len(idx), m), dtype=torch.long); wt = torch.zeros((len(idx), m))
    for k, i in enumerate(idx):
        a, b, w = data[i]
        ids[k, m - len(a):] = torch.tensor(a); lab[k, m - len(b):] = torch.tensor(b); att[k, m - len(a):] = 1
        wt[k, m - len(w):] = torch.tensor(w)
    pos = (att.cumsum(1) - 1).clamp(min=0)
    keep = int((lab != -100).sum(1).max()) + 1 if A.loss == "completion" else None
    return ids.to(dev), lab.to(dev), att.to(dev), pos.to(dev), wt.to(dev), keep


@torch.no_grad()
def evaluate():
    model.eval(); model.config.use_cache = True
    tok.padding_side = "left"
    order = sorted(range(len(test)), key=lambda i: len(test[i]["prompt"]))
    pred = {}
    for s in range(0, len(order), 32):
        b = [test[i] for i in order[s:s + 32]]
        e = tok([prompt_text(r["prompt"]) for r in b], add_special_tokens=False, return_tensors="pt", padding=True).to(dev)
        with torch.autocast("cuda", dtype=DT):
            out = model.generate(**e, max_new_tokens=9, do_sample=False, pad_token_id=tok.pad_token_id)
        for r, o in zip(b, out):
            m = re.search(r"D[ạa]ng\s*(\d+)", tok.decode(o[e.input_ids.shape[1]:], skip_special_tokens=True))
            pred[r["id"]] = int(m.group(1)) if m else None
    tok.padding_side = "right"; model.config.use_cache = False; model.train()
    ok_s = np.mean([pred[r["id"]] == r["so_dang"] for r in src])
    ok_v = np.mean([pred[r["id"]] == r["so_dang"] for r in samp])
    wrong = sorted({r["so_dang"] for r in test if pred[r["id"]] != r["so_dang"]})
    return float(ok_s), float(ok_v), len(wrong)


model.train()
t_start = time.time()
step, seen_tokens = 0, 0
for ep in range(1, A.epochs + 1):
    t_ep = time.time()
    losses = []
    mb = batches(list(range(len(data))))
    opt.zero_grad()
    for bi, idx in enumerate(mb[:steps_per_epoch * A.accum]):
        ids, lab, att, pos, wt, keep = collate(idx)
        with torch.autocast("cuda", dtype=DT):
            logits = model(input_ids=ids, attention_mask=att, position_ids=pos,
                           **({"logits_to_keep": keep} if keep else {})).logits
        tgt = lab[:, -keep:] if keep else lab
        wk = (wt[:, -keep:] if keep else wt)[:, 1:]
        ce = torch.nn.functional.cross_entropy(logits[:, :-1].float().reshape(-1, logits.size(-1)), tgt[:, 1:].reshape(-1),
                                               ignore_index=-100, reduction="none").view_as(wk)
        loss = (ce * wk).sum() / wk.sum().clamp(min=1e-6)
        (loss / A.accum).backward()
        seen_tokens += int(att.sum())
        losses.append(loss.item())
        if (bi + 1) % A.accum == 0:
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); opt.zero_grad(); step += 1
            if step % 50 == 0:
                print(f"[{A.name}] epoch {ep} step {step}/{total} loss {np.mean(losses[-50 * A.accum:]):.4f} "
                      f"{seen_tokens / (time.time() - t_start):.0f} tok/s", flush=True)
    train_min = (time.time() - t_ep) / 60
    t_ev = time.time()
    ok_s, ok_v, n_wrong_types = (float('nan'), float('nan'), -1) if A.skip_eval else evaluate()
    rec = dict(name=A.name, model=A.model, quant=A.quant, rank=A.rank, lr=A.lr, epochs_total=A.epochs, epoch=ep,
               loss_on=A.loss, per_type=A.per_type or 90, train_pairs=len(data), trainable_params=n_train,
               train_loss=float(np.mean(losses[-100:])), acc_source=ok_s, acc_variants=ok_v,
               types_with_errors=n_wrong_types, epoch_train_min=round(train_min, 2), eval_min=round((time.time() - t_ev) / 60, 2),
               tok_per_s=round(seen_tokens / (time.time() - t_start)), peak_gb=round(torch.cuda.max_memory_allocated() / 1e9, 2),
               targets=A.targets, dropout=A.dropout, desc_weight=A.desc_weight, bs=A.bs, accum=A.accum, seed=A.seed)
    print(f"[{A.name}] RESULT {json.dumps(rec, ensure_ascii=False)}", flush=True)
    with open(A.results, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"[{A.name}] total {(time.time() - t_start) / 60:.1f} min", flush=True)
