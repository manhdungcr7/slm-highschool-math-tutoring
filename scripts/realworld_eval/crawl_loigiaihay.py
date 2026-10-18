# -*- coding: utf-8 -*-
"""Download the "đề thi thử THPT Quốc gia môn Toán" exam pages of loigiaihay.com (questions + answer keys, LaTeX kept).

Two ways to find the exam pages, both save one HTML file per exam in --out:

  python scripts/realworld_eval/crawl_loigiaihay.py --out pages --listing
      Follows the paginated listing of the category (links to exams).
  python scripts/realworld_eval/crawl_loigiaihay.py --out pages --ids 47800 51500
      Scans exam ids c47a<id> (the site answers to https://loigiaihay.com/x-c47a<id>.html); it finds many exams the
      listing does not show, but also pages of other subjects, which parse_exam_pages.py filters out by title.

Be polite to the site: the default is 4 parallel requests; the full id scan of 3,600 ids takes several minutes.
curl must be on PATH (it is on Windows 10+, macOS and Linux).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

BASE = "https://loigiaihay.com"
LISTING = BASE + "/de-thi-thu-thpt-quoc-gia-mon-toan-e10394"


def fetch(url, path, min_size=1000):
    if not (os.path.exists(path) and os.path.getsize(path) > min_size):
        subprocess.run(["curl", "-sL", "-m", "40", "-A", "Mozilla/5.0", url, "-o", path], check=False)
    return open(path, encoding="utf-8", errors="replace").read() if os.path.exists(path) else ""


def crawl_listing(out, workers):
    links = []
    for n in range(1, 60):
        url = LISTING + ".html" if n == 1 else f"{LISTING}/{n}.html"
        html = fetch(url, os.path.join(out, f"list_{n}.html"))
        found = re.findall(r'href="(/[^"]*-c\d+a\d+\.html)"', html)
        new = [f for f in dict.fromkeys(found) if f not in links]
        print(f"listing page {n}: {len(found)} links, {len(new)} new")
        if not found:
            break
        links += new
    json.dump(links, open(os.path.join(out, "listing_links.json"), "w", encoding="utf-8"))

    def get(link):
        name = re.sub(r"[^A-Za-z0-9]+", "_", link) + ".html"
        return len(fetch(BASE + link, os.path.join(out, name))) > 5000

    with ThreadPoolExecutor(workers) as ex:
        ok = list(ex.map(get, links))
    print("exam pages fetched:", sum(ok), "of", len(links))


def crawl_ids(out, lo, hi, workers):
    def get(i):
        path = os.path.join(out, f"c47a{i}.html")
        if os.path.exists(path):
            return i, True
        html = fetch(f"{BASE}/x-c47a{i}.html", path, min_size=40000)
        if len(html) < 40000 or "Câu 1" not in html:     # not an exam page: drop it
            if os.path.exists(path):
                os.remove(path)
            return i, False
        return i, True

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(get, range(lo, hi)))
    print(f"ids {lo}..{hi - 1}: {sum(1 for _, ok in res if ok)} pages with questions kept")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="folder for the downloaded HTML pages")
    ap.add_argument("--listing", action="store_true")
    ap.add_argument("--ids", nargs=2, type=int, metavar=("LOW", "HIGH"))
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.listing:
        crawl_listing(a.out, a.workers)
    if a.ids:
        crawl_ids(a.out, a.ids[0], a.ids[1], a.workers)
    if not (a.listing or a.ids):
        ap.error("choose --listing and/or --ids LOW HIGH")
