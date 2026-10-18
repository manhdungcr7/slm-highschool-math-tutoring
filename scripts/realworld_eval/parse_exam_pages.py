# -*- coding: utf-8 -*-
"""Turn downloaded loigiaihay exam pages into a pool of multiple-choice questions with their answer keys.

python scripts/realworld_eval/parse_exam_pages.py <pages_folder> <pool.json>

Keeps only pages whose title is a Toán THPT Quốc gia exam (not a school test, not another subject). A question is kept
when it has the four options A-D; "ans" is empty if the page has no readable answer key (such questions are unusable).
Each record: num (question number in the exam, 1-50; the last ones are the application / advanced level), stem,
opts {A..D}, ans, url, title. The text is the page text with formulas as $...$; nothing is rewritten.
"""
import glob
import html
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


def to_text(h):
    h = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", h)
    h = re.sub(r"(?i)</p>|<br\s*/?>|</div>|</tr>|</li>", "\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h).replace("\xa0", " ")
    h = re.sub(r"\\\((.+?)\\\)", lambda m: "$" + m.group(1).strip() + "$", h, flags=re.S)
    h = re.sub(r"\\\[(.+?)\\\]", lambda m: "$" + m.group(1).strip() + "$", h, flags=re.S)
    return h


def parse(h, url):
    t = to_text(h)
    k = t.find("Lời giải chi tiết")
    body, key = (t[:k], t[k:k + 6000]) if k > 0 else (t, "")
    ans = {}
    for n, L in re.findall(r"(?<!\d)(\d{1,2})\s*[\.\:\-]?\s*([A-D])(?![A-Za-zÀ-ỹ])", key):
        ans.setdefault(int(n), L)
    out = []
    parts = re.split(r"(?m)^\s*Câu\s*(\d+)\s*[\.\:]\s*", body)
    for i in range(1, len(parts) - 1, 2):
        n, blk = int(parts[i]), parts[i + 1]
        m = re.search(r"(?m)^\s*A[\.\)]\s", blk)
        if not m:
            continue
        stem = re.sub(r"\s+", " ", blk[:m.start()]).strip()
        opts = {}
        for mm in re.finditer(r"(?ms)^\s*([A-D])[\.\)]\s*(.*?)(?=^\s*[A-D][\.\)]\s|\Z)", blk[m.start():]):
            opts.setdefault(mm.group(1), re.sub(r"\s+", " ", mm.group(2)).strip())
        if set(opts) != {"A", "B", "C", "D"} or not stem or any(len(v) > 400 for v in opts.values()):
            continue
        out.append(dict(num=n, stem=stem, opts=opts, ans=ans.get(n, ""), url=url))
    return out


def is_math_thpt_exam(title):
    return ("Toán" in title and re.search(r"THPT|Quốc [gG]ia", title)
            and not re.search(r"học kì|lớp 1[01]|vào 10|lớp 9|lớp 6", title, re.I))


if __name__ == "__main__":
    folder, out_path = sys.argv[1], sys.argv[2]
    pool, pages = [], 0
    for p in sorted(glob.glob(os.path.join(folder, "*.html"))):
        h = open(p, encoding="utf-8", errors="replace").read()
        m = re.search(r"<title>(.*?)</title>", h, re.S)
        title = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip() if m else ""
        if not is_math_thpt_exam(title):
            continue
        mu = re.search(r'https://loigiaihay\.com/[^"\s]*c47a\d+\.html', h)
        mi = re.search(r"c47a(\d+)", os.path.basename(p))
        url = mu.group(0) if mu else (f"https://loigiaihay.com/x-c47a{mi.group(1)}.html" if mi else os.path.basename(p))
        got = parse(h, url)
        for q in got:
            q["title"] = title.split("|")[0].strip()
        pool += got
        pages += 1
    json.dump(pool, open(out_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{pages} exam pages -> {len(pool)} questions ({sum(1 for q in pool if q['ans'])} with an answer key) -> {out_path}")
