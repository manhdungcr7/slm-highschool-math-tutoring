# -*- coding: utf-8 -*-
"""How a question is WRITTEN (not what it asks): a 'style signature', and which signatures of the test set are absent from the training set.

signature = (line break before the options, opening sentence with the maths and numbers masked, LaTeX brackets, operator spacing,
             '=' spacing, kind of options, logarithm with / without base, right-hand side of the stem)

python style_gap.py                       -> the gap per dạng for the test sources and for the whole test set
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

from common import REPO

BUNDLE = os.path.join(REPO, "data", "router_train", os.environ.get("ROUTER_BUNDLE", "kaggle_bundle_v3"))
TEST_BUNDLE = os.path.join(REPO, "data", "router_train", "kaggle_bundle")
P = "Đề bài:\n"


def body_of(prompt):
    return prompt[prompt.index(P) + len(P):]


def split(body):
    lines = body.split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("A. "))
    return [l for l in lines[:first] if l.strip()], lines[first:]


def math_parts(s):
    return re.findall(r"\$(.+?)\$", s)


def signature(body):
    stem, opts = split(body)
    newline = "blank" if "\n\n" in body.split("\nA. ")[0] + "\n" and re.search(r"\n\n\s*A\. ", body) else "single"
    last = stem[-1]
    opening = re.sub(r"\d+", "#", re.sub(r"\$.+?\$", "$M$", last)).strip()
    mt = " ".join(math_parts("\n".join(stem)))
    ot = " ".join(math_parts("\n".join(opts)))
    allm = mt + " " + ot
    sub_exp = ("braced" if re.search(r"[_^]\{\d\}", allm) else "bare" if re.search(r"[_^]\d", allm) else "-")
    ops = ("spaced" if re.search(r" [-+] ", allm) else "tight" if re.search(r"\w[-+]\w|\)[-+]", allm) else "-")
    eq = "spaced" if re.search(r" = ", mt) else "tight" if "=" in mt else "-"
    o = [re.sub(r"^[A-D]\. ", "", x) for x in opts]
    if all(re.fullmatch(r"-?\d+\.", x) for x in o):
        kind = "plain_int"
    elif all(re.fullmatch(r"\$-?\d+\$\.", x) for x in o):
        kind = "dollar_int"
    elif all(re.fullmatch(r"\$(x [<>] .+|.+ < x < .+)\$\.", x) for x in o):
        kind = "inequality"
    elif all(re.fullmatch(r"\$.*\(.*;.*\).*\$\.", x) for x in o):
        kind = "interval"
    else:
        kind = "expr"
    if "\\log" in allm:
        base = "base" if re.search(r"\\log_", allm) else "no_base"
    else:
        base = "-"
    rhs = "-"
    m = re.search(r"(<|>|\\le|\\ge)\s*(\d+)(\^\{?\d+\}?)?\$", last)
    if m:
        rhs = "pow" if m.group(3) else "num"
    return (newline, opening, sub_exp, ops, eq, kind, base, rhs)


def _canon_math(t):
    t = t.replace(r"\left", "").replace(r"\right", "").replace(r"\dfrac", r"\frac")
    t = t.replace(r"\log_{10}", r"\log").replace(r"\log_10", r"\log")
    t = re.sub(r"\s+", "", t)
    return t.replace("{", "").replace("}", "")


def _canon_option(o):
    o = re.sub(r"^[A-D]\.\s*", "", o).strip().rstrip(".").strip()
    inner = o[1:-1] if o.startswith("$") and o.endswith("$") else o
    t = inner.replace(r"\left", "").replace(r"\right", "").strip()
    m = re.fullmatch(r"x\s*>\s*(.+)", t)                     # an inequality is the same answer as the interval
    if m:
        t = "(" + m.group(1).strip() + r";+\infty)"
    else:
        m = re.fullmatch(r"x\s*<\s*(.+)", t)
        if m:
            t = r"(-\infty;" + m.group(1).strip() + ")"
        else:
            m = re.fullmatch(r"(.+?)\s*<\s*x\s*<\s*(.+)", t)
            if m:
                t = f"({m.group(1).strip()};{m.group(2).strip()})"
    return _canon_math(t)


def content_key(body):
    """What a question ASKS, independent of how it is written: the maths of the stem and the set of options."""
    stem, opts = split(body)
    maths = tuple(_canon_math(m) for l in stem for m in math_parts(l))
    nums = tuple(re.findall(r"\d+", re.sub(r"\$.+?\$", " ", " ".join(stem))))
    return maths, nums, frozenset(_canon_option(o) for o in opts)


def matches(train_sig, test_sig):
    """A training question covers a test style when all features agree; a feature the test question does not have ('-': e.g. no
       exponent, no '+' or '-') puts no requirement on the training question."""
    return all(t == "-" or t == r for r, t in zip(train_sig, test_sig))


def load():
    train = defaultdict(list)
    for l in open(os.path.join(BUNDLE, "finetune_router.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        n = int(re.match(r"Dạng (\d+):", r["completion"]).group(1))
        train[n].append(body_of(r["prompt"]))
    test = defaultdict(list)
    for l in open(os.path.join(TEST_BUNDLE, "eval_set.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        test[r["so_dang"]].append((r["nguon"] == "Câu gốc", body_of(r["prompt"])))
    return train, test


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    train, test = load()
    miss_src, miss_all, total_src_sigs = 0, 0, 0
    report = []
    for n in range(1, 143):
        tr = Counter(signature(b) for b in train[n])
        covered = lambda k: sum(c for sig, c in tr.items() if matches(sig, k))
        te_all = Counter(signature(b) for _, b in test[n])
        te_src = Counter(signature(b) for s, b in test[n] if s)
        gap_src = {k: v for k, v in te_src.items() if covered(k) == 0}
        gap_all = {k: v for k, v in te_all.items() if covered(k) == 0}
        miss_src += sum(gap_src.values()); total_src_sigs += sum(te_src.values()); miss_all += sum(gap_all.values())
        if gap_all:
            report.append((n, len(te_all), len(gap_all), sum(gap_all.values()), len(te_src), sum(gap_src.values())))
    print(f"test questions whose style never occurs in the training set of their dạng: all test {miss_all} / 12951 | source {miss_src} / {total_src_sigs}")
    print("dạng | distinct test styles | not in train | questions | source questions | of them not in train")
    for r in report:
        print("  ", *r)


if __name__ == "__main__":
    main()
