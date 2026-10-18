# -*- coding: utf-8 -*-
"""Recompute, from the files in this repository, the numbers quoted in data/results/pipeline_realworld/PHAN_TICH_LOI.md.

python scripts/pipeline/analyze_pipeline_errors.py [--run kaggle_run_20261016]

Reads  data/results/pipeline_realworld/<run>/ket_qua_pipeline_100cau.csv  (+ raw/*.csv for the Calculator logs)
       data/router_train/finetune_router.jsonl                             (the router's training data)
and prints, for the 93 questions of the evaluation (the 100 of the run minus 7 with uncertain labels):
  1. accuracy of the router and of the answers, and how a wrong dạng changed the prompt that was used;
  2. router: how many distinct question templates each dạng has in the training data, whether the wrong cases are
     templates seen in training, the router's confidence on right/wrong cases, the true dạng in its top 3;
  3. ReAct: which answers are backed by a Calculator result ("supported") and which are not;
  4. zero-shot: length of the reasoning and amount of hesitation.
Part 2 needs scikit-learn only for the optional similarity line.
"""
import argparse
import collections
import csv
import glob
import json
import os
import re
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DROP = {"SRC-09", "SRC-02", "SRC-22", "WEB-026", "WEB-044", "BS-008", "CR-9"}      # labels judged uncertain, see README


def stem(t):
    return re.split(r"(?:^|\n)A\.\s", t.strip(), maxsplit=1)[0].strip()


def skeleton(t):
    """Question stem with numbers masked and LaTeX noise removed: two questions of one template have the same skeleton."""
    t = stem(t).lower()
    t = re.sub(r"\\(left|right|dfrac|tfrac|displaystyle|,|;|!)", "", t).replace("\\frac", "frac")
    t = re.sub(r"[\s$\\{}()\[\]]", "", t)
    return re.sub(r"\d+(?:[.,]\d+)?", "#", t)


def load(run):
    d = os.path.join(REPO, "data", "results", "pipeline_realworld", run)
    r = pd.read_csv(os.path.join(d, "ket_qua_pipeline_100cau.csv"), encoding="utf-8-sig", keep_default_na=False, dtype=str)
    r = r[~r["id"].isin(DROP)].copy()
    raw = {}
    for f in glob.glob(os.path.join(d, "raw", "*.csv")):
        if os.path.basename(f).startswith("ZS_"):
            continue
        x = pd.read_csv(f, encoding="utf-8-sig", keep_default_na=False, dtype=str)
        log = "tool_log" if "tool_log" in x else "nhat_ky_tool"
        err = "syntax_errors" if "syntax_errors" in x else "so_loi_cu_phap"
        for _, row in x.iterrows():
            raw[int(row["STT"])] = (row[log], int(row[err]))
    r["STT"] = r["STT"].astype(int)
    r["token"] = r["token"].astype(int)
    r["calls"] = r["so_luot_goi_tool"].astype(int)
    r["tool_log"] = r["STT"].map(lambda s: raw.get(s, ("", 0))[0])
    r["n_err"] = r["STT"].map(lambda s: raw.get(s, ("", 0))[1])
    r["react"] = r["cach_giai"] == "ReAct+Calculator"
    r["dung_dang"] = r["dang_dung"] == r["dang_du_doan"]
    r["dung"] = r["ket_qua"] == "Đúng"
    return r


def pct(a, b):
    return f"{a}/{b} ({a / b * 100:.1f}%)"


def part1(r):
    print("=" * 78, "\n1. ACCURACY\n" + "=" * 78)
    print("router (right dạng):", pct(int(r.dung_dang.sum()), len(r)), "| answers:", pct(int(r.dung.sum()), len(r)))
    bad = r[~r.dung_dang]
    print("\nwrong dạng x prompt actually used x result:")
    print(pd.crosstab([bad["cach_giai_dang_dung"], bad["cach_giai"]], bad["ket_qua"], margins=True))
    print("\nright dạng but wrong answer:")
    print(r[r.dung_dang & ~r.dung][["id", "dang_dung", "cach_giai", "dap_an_dung", "model_chon", "calls", "ly_do_dung"]].to_string(index=False))


def part2(r):
    print("\n" + "=" * 78, "\n2. ROUTER vs ITS TRAINING DATA\n" + "=" * 78)
    train = []
    for l in open(os.path.join(REPO, "data", "router_train", "finetune_router.jsonl"), encoding="utf-8"):
        d = json.loads(l)
        train.append((int(re.match(r"Dạng (\d+):", d["completion"]).group(1)), d["prompt"].split("Đề bài:\n")[-1]))
    sk = collections.defaultdict(set)
    for n, q in train:
        sk[n].add(skeleton(q))
    cnt = np.array([len(sk[n]) for n in range(1, 143)])
    print(f"training pairs {len(train)}; distinct question templates per dạng: min {cnt.min()}, median {int(np.median(cnt))}, "
          f"max {cnt.max()}; dạng with <= 3 templates: {(cnt <= 3).sum()}/142")
    r = r.copy()
    r["seen"] = [skeleton(q) in sk[int(t)] for q, t in zip(r["de_bai_mcq"], r["dang_dung"])]
    ok, bad = r[r.dung_dang], r[~r.dung_dang]
    print(f"template of the TRUE dạng seen in training: right routes {int(ok.seen.sum())}/{len(ok)} | wrong routes {int(bad.seen.sum())}/{len(bad)}")
    unseen = r[~r.seen]
    print(f"accuracy when the template was not in training: {pct(int(unseen.dung_dang.sum()), len(unseen))}")
    conf = r["do_tin_cay"].astype(float)
    print(f"router confidence: right {conf[r.dung_dang].mean():.2f} | wrong {conf[~r.dung_dang].mean():.2f}; wrong with >= 0.9: "
          f"{int((conf[~r.dung_dang] >= 0.9).sum())}/{len(bad)}")
    top3 = r["top3"].map(lambda s: [int(x) for x in s.split(";")])
    print("true dạng in the router's top 3 among the wrong cases:",
          sum(int(t) in tt for t, tt in zip(bad["dang_dung"], top3[bad.index])), "of", len(bad))
    # opening words
    def opening(t, k=3):
        return " ".join(re.sub(r"[\$\\{}]", " ", stem(t)).lower().split()[:k])
    op = collections.defaultdict(set)
    for n, q in train:
        op[n].add(opening(q))
    w = r[~r["id"].str.startswith("VD-")]
    wb = w[~w.dung_dang]
    print(f"web questions, wrong routes whose first 3 words occur in the PREDICTED dạng's training data: "
          f"{sum(opening(q) in op[int(p)] for q, p in zip(wb['de_bai_mcq'], wb['dang_du_doan']))}/{len(wb)}; "
          f"in the TRUE dạng's: {sum(opening(q) in op[int(t)] for q, t in zip(wb['de_bai_mcq'], wb['dang_dung']))}/{len(wb)}")
    print("\nwrong routes:")
    print(bad[["id", "dang_dung", "dang_du_doan", "do_tin_cay"]].assign(template_seen=r.loc[bad.index, "seen"]).to_string(index=False))


def supported(x):
    """A ReAct answer is backed when the Calculator result of the chosen option is True (and the loop was not cut)."""
    log = x.tool_log.split(" | ")
    forced = x.ly_do_dung in ("tool_limit_reached", "het_han_muc_tool")
    tests = dict(re.findall(r"test_([A-D]) = (True|False)", x.tool_log))
    if tests:
        return [k for k, v in tests.items() if v == "True"] == [x.model_chon]
    cmp_true = [e for e in log if re.match(r"\s*Eq\(", e) and e.rstrip().endswith("True")]
    return (not forced) and bool(cmp_true) and not log[-1].strip().startswith("ERROR")


def part3(r):
    print("\n" + "=" * 78, "\n3. REACT: IS THE ANSWER BACKED BY A CALCULATOR RESULT?\n" + "=" * 78)
    a = r[r.react].copy()
    a["supported"] = a.apply(supported, axis=1)
    print(pd.crosstab(a["supported"], a["ket_qua"], margins=True))
    print("\nnot backed:")
    print(a[~a.supported][["id", "dang_dung", "unit", "calls", "n_err", "ly_do_dung", "model_chon", "dap_an_dung", "ket_qua"]].to_string(index=False))


def part4(r):
    print("\n" + "=" * 78, "\n4. ZERO-SHOT: LENGTH AND HESITATION\n" + "=" * 78)
    z = r[~r.react].copy()
    hes = z["loi_giai"].map(lambda t: len(re.findall(r"\b(Wait|Hmm|But wait|Alternatively|Let me check|Actually)\b", t.split("</think>")[0])))
    z["do_du"] = hes
    print(f"{len(z)} questions: tokens mean {z.token.mean():.0f}, median {z.token.median():.0f}, max {z.token.max()} (budget 9216); "
          f"> 3000 tokens: {(z.token > 3000).sum()}; answers extracted: {int((z.model_chon != '').sum())}/{len(z)}")
    print(z.sort_values("token", ascending=False)[["id", "dang_dung", "token", "do_du", "ket_qua"]].head(8).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="kaggle_run_20261016")
    res = load(ap.parse_args().run)
    print(len(res), "questions (the 7 with uncertain labels are removed:", ", ".join(sorted(DROP)) + ")")
    part1(res)
    part2(res)
    part3(res)
    part4(res)
