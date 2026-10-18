# -*- coding: utf-8 -*-
"""Pick candidate evaluation questions from a pool: Mũ-Logarit or Số phức, new, and (optionally) application level.

python scripts/realworld_eval/filter_candidates.py <pool.json> <out_prefix> [--min-num 36] [--exclude a.csv b.csv ...]

Steps (each only removes questions, nothing is edited):
  1. keep questions with an answer key and exam number >= --min-num (default 30; use 36+ for application / advanced level);
  2. drop geometry, integrals, probability, graphs, applied word problems ... (regex GEO) - they belong to no dạng;
  3. keep those that look like Mũ-Logarit or Số phức (regexes ML / SP);
  4. drop any question whose stem is already in --exclude files (CSV with a question_markdown_latex column) or is a source
     question of the router evaluation set (so the new set does not repeat the old one).
Output: <out_prefix>.json (full records) and <out_prefix>.csv (id, topic, question_markdown_latex, answer_letter, url),
the CSV is the input format of scripts/router/run_router_real.py. THE LABEL (which of the 142 dạng) STILL HAS TO BE
DECIDED BY HAND against data/catalogue/danh_muc_dang_bai.csv: most application-level questions are outside the 142 dạng.
"""
import argparse
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GEO = (r"Oxyz|mặt cầu|mặt phẳng|đường thẳng|vectơ|véc|hình chóp|hình lăng|thể tích|diện tích hình|khối|nguyên hàm|tích phân|"
       r"cấp số|xác suất|tổ hợp|chỉnh hợp|hình vẽ|đồ thị|bảng biến thiên|\\int|\\sum|\\lim|tiệm cận|cực trị|góc|hình trụ|hình nón|"
       r"hình học|parabol|đường tròn|elip|hình vuông|hình chữ nhật|đoạn thẳng|khoảng cách|sân bay|kho hàng|vận tốc|chuyển động")
ML = r"log|\\ln|\bln\b|\^\{?x|\^\{?\d*x|mũ|lũy thừa|e\^"
SP = r"số phức|\bz\b|z_1|z_2|\\overline|\\bar|phần thực|phần ảo|mô\s?-?đun|môđun"


def canon(s):
    s = s.lower()
    for w in (r"\left", r"\right", r"\dfrac", r"\frac", r"\tfrac", r"\,", r"\;", r"\!", r"\mathbb", r"\rm", r"\cdot",
              r"\overline", r"\bar", r"\displaystyle", r"\text"):
        s = s.replace(w, "")
    return re.sub(r"[\s$\\{}()\[\].,;:?|]", "", s)


def stem_of(t):
    return re.split(r"(?:^|\n|\s)A\.\s", t, maxsplit=1)[0]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pool")
    ap.add_argument("out_prefix")
    ap.add_argument("--min-num", type=int, default=30)
    ap.add_argument("--exclude", nargs="*", default=[])
    a = ap.parse_args()

    used = set()
    for f in a.exclude:
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            used.add(canon(stem_of(r["question_markdown_latex"])))
    ev = os.path.join(REPO, "data", "router_train", "kaggle_bundle", "eval_set.jsonl")
    for l in open(ev, encoding="utf-8"):
        r = json.loads(l)
        if r.get("nguon") == "Câu gốc":
            used.add(canon(stem_of(r["prompt"].split("Đề bài:\n")[1])))

    rows = []
    for i, q in enumerate(json.load(open(a.pool, encoding="utf-8"))):
        if not q["ans"] or q["num"] < a.min_num:
            continue
        t = q["stem"] + " " + " ".join(q["opts"].values())
        if re.search(GEO, t, re.I):
            continue
        topic = "Số phức" if re.search(SP, t, re.I) and not re.search(r"\\log|\\ln", t) else ("Mũ–Logarit" if re.search(ML, t, re.I) else "")
        k = canon(q["stem"])
        if not topic or k in used:
            continue
        used.add(k)
        rows.append(dict(id=f"P{i:05d}", topic=topic, num=q["num"], stem=q["stem"], opts=q["opts"], ans=q["ans"], url=q["url"],
                         title=q.get("title", "")))
    json.dump(rows, open(a.out_prefix + ".json", "w", encoding="utf-8"), ensure_ascii=False)
    with open(a.out_prefix + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "topic", "question_markdown_latex", "answer_letter", "url"])
        w.writeheader()
        for r in rows:
            w.writerow(dict(id=r["id"], topic=r["topic"], answer_letter=r["ans"], url=r["url"],
                            question_markdown_latex=r["stem"] + " " + " ".join(f"{L}. {r['opts'][L]}" for L in "ABCD")))
    print(f"{len(rows)} candidates -> {a.out_prefix}.json / .csv")
