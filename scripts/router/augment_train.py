# -*- coding: utf-8 -*-
"""Surface augmentation of the router training questions (the number of questions per dạng stays 90).

Why: the generated questions of a dạng share one or a few fixed templates, so the fine-tuned model can answer by
recognising the template instead of the maths. Real questions are typed by hand (single line break, compact LaTeX,
"Giải bất phương trình ..." instead of "Tập nghiệm của ...", plain numbers as options, base-10 logarithm without a base ...)
and a few of them were answered wrongly for that reason.

Every transform changes only how the question is WRITTEN. The mathematics, the options and the label are untouched.
A row keeps its original form with probability KEEP, so the generator's own style (the style of the test variants) is still seen.
No question of the test set is copied: after every change the question is compared with all test questions.

python augment_train.py            -> data/router_train/kaggle_bundle_v3/
"""
import json
import os
import random
import re
import shutil
import sys
from collections import Counter

from common import REPO
from style_gap import content_key

SRC = os.path.join(REPO, "data", "router_train", "kaggle_bundle")
OUT = os.path.join(REPO, "data", "router_train", "kaggle_bundle_v3")
PROMPT = ("Hãy xác định dạng bài của đề bài sau. Chỉ trả lời đúng một dòng theo mẫu "
          "\"Dạng N: mô tả dạng bài\", trong đó N là số thứ tự của dạng.\n\nĐề bài:\n")
KEEP = 0.35                                    # share of rows left exactly as generated


def math_only(f):
    """Apply f to the inside of every $...$ of a text."""
    return lambda s: re.sub(r"\$(.+?)\$", lambda m: "$" + f(m.group(1)) + "$", s)


def compact(m):
    m = re.sub(r"_\{(\d)\}", r"_\1", m)                      # \log_{2} -> \log_2
    m = re.sub(r"\^\{(\d)\}", r"^\1", m)                     # x^{2}   -> x^2
    m = re.sub(r"(\d) ([a-z\\])", r"\1\2", m)                # 2 x -> 2x ; 2 \sqrt -> 2\sqrt
    m = m.replace(" - ", "-").replace(" + ", "+")
    return m


def spaced_equals(m):
    return re.sub(r"\s*=\s*", " = ", m, count=1)


def split_body(body):
    """-> (stem lines, option lines). Options are the lines that start with 'A. ' ... 'D. '."""
    lines = body.split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("A. "))
    return [l for l in lines[:first] if l.strip()], lines[first:]


def join_body(stem, opts, blank):
    return "\n".join(stem) + ("\n\n" if blank else "\n") + "\n".join(opts)


def t_opening(stem, rnd, stats):
    """'Tập nghiệm của (bất) phương trình X là' -> 'Giải (bất) phương trình X.' / 'Tìm tập nghiệm của ... .'
       'Trên khoảng (0;+oo), đạo hàm của hàm số X là' -> 'Tìm đạo hàm của hàm số X.'"""
    s = stem[-1]
    m = re.match(r"^Tập nghiệm của (bất phương trình|phương trình) (\$.+\$) là$", s)
    if m:
        if rnd.random() < 0.6:
            stem[-1] = f"Giải {m.group(1)} {m.group(2)}."; stats["opening_giai"] += 1
        else:
            stem[-1] = f"Tìm tập nghiệm của {m.group(1)} {m.group(2)}."; stats["opening_tim"] += 1
        return
    m = re.match(r"^Trên khoảng \$\(0;\+\\infty\)\$, đạo hàm của hàm số (\$.+\$) là$", s)
    if m:
        stem[-1] = f"Tìm đạo hàm của hàm số {m.group(1)}."; stats["opening_derivative"] += 1


def t_strip_end(stem, stats):
    s = stem[-1]
    for w in (" bằng",):
        if s.endswith(w):
            stem[-1] = s[: -len(w)]; stats["strip_end"] += 1
            return


def t_plain_options(opts, stats):
    ok = all(re.match(r"^[A-D]\. \$-?\d+\$\.$", o) for o in opts)
    if ok:
        for i, o in enumerate(opts):
            opts[i] = re.sub(r"\$(-?\d+)\$", r"\1", o)
        stats["plain_options"] += 1


def interval_to_inequality(inner):
    """(a;+oo) -> x > a ; (-oo;b) -> x < b ; (a;b) -> a < x < b. Anything else (unions, closed ends) -> None."""
    t = inner.replace(r"\left", "").replace(r"\right", "").strip()
    if r"\cup" in t or not (t.startswith("(") and t.endswith(")")):
        return None
    parts = t[1:-1].split(";")
    if len(parts) != 2:
        return None
    a, b = parts[0].strip(), parts[1].strip()
    if b == r"+\infty" and a != r"-\infty":
        return f"x > {a}"
    if a == r"-\infty" and b != r"+\infty":
        return f"x < {b}"
    if "infty" not in a and "infty" not in b:
        return f"{a} < x < {b}"
    return None


def t_inequality_options(opts, stats):
    r"""A. $(3;+\infty)$. -> A. $x > 3$.   (only when all four options are simple intervals)"""
    new = []
    for o in opts:
        m = re.match(r"^([A-D])\. \$(.+)\$\.$", o)
        conv = interval_to_inequality(m.group(2)) if m else None
        if conv is None:
            return
        new.append(f"{m.group(1)}. ${conv}$.")
    opts[:] = new
    stats["inequality_options"] += 1


def t_rhs_number(stem, stats):
    """... < 5^{3}$  ->  ... < 125$  (only the right-hand side of the last comparison, when the value is small)."""
    s = stem[-1]
    m = re.search(r"(<|>|\\le|\\ge|=)\s*(\d+)\^\{(\d+)\}\$", s)
    if m:
        v = int(m.group(2)) ** int(m.group(3))
        if v <= 10 ** 6:
            stem[-1] = s[: m.start()] + f"{m.group(1)}{v}$" + s[m.end():]; stats["rhs_number"] += 1


def widen_small_base_d15(body, rnd, stats):
    """Dạng 15 was generated with bases 94..597 only, the test questions use 2..91: draw the base from the small range too,
       and write the base-10 logarithm without its base."""
    m = re.search(r"\\log_\{(\d+)\} x", body)
    if not m:
        return body
    old = m.group(1)
    new = rnd.choice(["2", "3", "4", "5", "6", "7", "8", "9", "10", "10", "10", "10", "11", "12"])
    body = re.sub(r"(?<!\d)" + old + r"(?!\d)", new, body)
    stats["d15_small_base"] += 1
    if new == "10" and rnd.random() < 0.8:
        body = body.replace("\\log_{10} x", "\\log x"); stats["d15_decimal_log"] += 1
    return body


def drop_base_d26(body, rnd, stats):
    """Dạng 26: 'log_{B}(ab^{n})' - the base plays no role. Sometimes write the decimal logarithm without a base."""
    if re.search(r"\\log_\{\d+\}\(ab", body) and rnd.random() < 0.3:
        stats["d26_no_base"] += 1
        return re.sub(r"\\log_\{\d+\}", r"\\log", body)
    return body


def augment(row, number, rnd, stats):
    body = row["prompt"][len(PROMPT):]
    # parameter range / base fixes belong to the generator, so they are drawn independently of the style choice
    if number == 15 and re.search(r"\\log_\{(9\d|[1-9]\d\d)\} x", body):
        if rnd.random() < 0.7:
            body = widen_small_base_d15(body, rnd, stats)
    if number == 26:
        body = drop_base_d26(body, rnd, stats)
    if rnd.random() < KEEP:
        stats["kept"] += 1
        return body
    stem, opts = split_body(body)
    blank = rnd.random() < 0.4                                # the generators put a blank line before the options
    if not blank:
        stats["single_newline"] += 1
    if rnd.random() < 0.5:
        t_opening(stem, rnd, stats)
    if rnd.random() < 0.4:
        t_strip_end(stem, stats)
    if rnd.random() < 0.6:
        t_rhs_number(stem, stats)
    if rnd.random() < 0.5:
        stem = [math_only(compact)(l) for l in stem]
        opts = [math_only(compact)(o) for o in opts]
        stats["compact_latex"] += 1
    if rnd.random() < 0.3:
        stem = [math_only(spaced_equals)(l) for l in stem]; stats["spaced_equals"] += 1
    if rnd.random() < 0.4:
        t_plain_options(opts, stats)
    if rnd.random() < 0.4:
        t_inequality_options(opts, stats)
    return join_body(stem, opts, blank)


def norm(s):
    return re.sub(r"\s+", "", s)


def main():
    rows = [json.loads(l) for l in open(os.path.join(SRC, "finetune_router.jsonl"), encoding="utf-8")]
    test = [json.loads(l) for l in open(os.path.join(SRC, "eval_set.jsonl"), encoding="utf-8")]
    test_keys = {content_key(r["prompt"][len(PROMPT):]) for r in test}       # what a question asks, not how it is written
    rnd = random.Random(20261009)
    stats = Counter()
    seen, out, changed = set(), [], 0
    shown = {}
    for r in rows:
        number = int(re.match(r"Dạng (\d+):", r["completion"]).group(1))
        original = r["prompt"][len(PROMPT):]
        for attempt in range(20):
            local = Counter()
            body = augment(r, number, rnd, local)
            key = content_key(body)
            if key not in test_keys and key not in seen:
                break
        else:
            body, local, key = original, Counter(), content_key(original)         # could not find a free form: keep the original
        stats.update(local)
        seen.add(key)
        changed += body != original
        new = dict(r)
        new["prompt"] = PROMPT + body
        new["messages"] = [dict(role="user", content=PROMPT + body), dict(role="assistant", content=r["completion"])]
        out.append(new)
        if body != original and shown.get(number, 0) < 1 and number in (15, 26, 27, 28, 29, 49):
            shown[number] = 1
            print(f"--- Dạng {number}\n{original}\n=>\n{body}")
    # every way of writing that occurs in the test questions of a dạng must also occur in its training questions
    from style_match import match_styles
    originals = [r["prompt"][len(PROMPT):] for r in rows]
    bodies = [r["prompt"][len(PROMPT):] for r in out]
    numbers = [int(re.match(r"Dạng (\d+):", r["completion"]).group(1)) for r in out]
    test_by_number = {}
    for t in test:
        test_by_number.setdefault(t["so_dang"], []).append(t["prompt"][len(PROMPT):])
    forbidden = set(test_keys) | {content_key(b) for b in bodies}
    # training questions with exactly the content of a test question of the same dạng are replaced by new ones
    from fix_overlaps import GENERATORS
    test_by_dang = {(t["so_dang"], content_key(t["prompt"][len(PROMPT):])) for t in test}
    replaced = Counter()
    for i, n in enumerate(numbers):
        if (n, content_key(originals[i])) in test_by_dang:
            gen = GENERATORS[n]                       # a dạng without a generator would raise: it must be handled explicitly
            for _ in range(500):
                nb = gen(originals[i], rnd)
                if nb and content_key(nb) not in forbidden:
                    break
            else:
                raise SystemExit(f"cannot replace the overlapping question of Dạng {n}")
            forbidden.discard(content_key(bodies[i]))
            forbidden.add(content_key(nb))
            bodies[i] = originals[i] = nb
            replaced[n] += 1
    print("overlapping training questions replaced:", dict(replaced))
    # Dạng 49: the base-10 logarithm without a base never occurred in the generator's questions: 12 of its 90 questions are replaced
    from gen_d49_decimal import make as make_decimal
    d49 = [i for i, x in enumerate(numbers) if x == 49]
    for i in rnd.sample(d49, 12):
        for _ in range(50):
            nb = make_decimal(rnd, blank=rnd.random() < 0.4)
            if content_key(nb) not in forbidden:
                break
        forbidden.discard(content_key(bodies[i]))
        forbidden.add(content_key(nb))
        bodies[i] = originals[i] = nb
    unreachable = match_styles(bodies, originals, numbers, test_by_number, forbidden, rnd)
    for r, b in zip(out, bodies):
        r["prompt"] = PROMPT + b
        r["messages"] = [dict(role="user", content=PROMPT + b), dict(role="assistant", content=r["completion"])]
    print("styles of the test set that could not be reproduced without changing the mathematics:", len(unreachable))
    for n, sig, need in unreachable[:40]:
        print("   Dạng", n, "| need", need, "|", sig)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "finetune_router.jsonl"), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    for name in ("candidates.json", "eval_set.jsonl"):
        shutil.copy(os.path.join(SRC, name), os.path.join(OUT, name))
    per = Counter(re.match(r"Dạng (\d+):", r["completion"]).group(1) for r in out)
    assert len(out) == len(rows) and set(per.values()) == {90} and len(per) == 142
    print("rows:", len(out), "| changed:", changed, "| dạng:", len(per), "| 90 each")
    print(dict(stats))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
