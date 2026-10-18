# -*- coding: utf-8 -*-
"""Generate NEW Số phức variants for the router training set.

Same question generators as the existing dataset (so_phuc_generators/cau_XX.py), new random seeds, and every question is
checked against the existing dataset: only questions whose key is not already in the project are kept.
For every source question and number kind (integer / rational / irrational) the number kept is the same as in the
existing dataset (for example 30, 15, 10 or 7-8), so each type again ends with exactly 90 questions.

python gen_sp_new.py [attempts_per_slot]
Output: data/router_train/_work/so_phuc_candidates.json
"""
import collections
import glob
import importlib.util
import json
import os
import sys
import zlib

from collect_new import question_key
from common import REPO, load_questions

GEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "so_phuc_generators")
sys.path.insert(0, GEN_DIR)
OUT_DIR = os.path.join(REPO, "data", "router_train", "_work")
SP_FILE = os.path.join(REPO, "so_phuc", "data", "questions", "So_phuc_day_du.csv")
LOAI = ["Số nguyên", "Số hữu tỉ", "Số vô tỉ"]


def load_modules():
    mods = {}
    for path in sorted(glob.glob(os.path.join(GEN_DIR, "cau_*.py"))):
        name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mods[mod.STT] = mod
    return mods


def existing_structure():
    """stt -> (type code, per-number-kind count in the existing data); and the set of existing keys per type."""
    import csv
    info, count = {}, collections.Counter()
    for r in csv.DictReader(open(SP_FILE, encoding="utf-8-sig")):
        stt = int(r["STT câu gốc"])
        info[stt] = r["Mã dạng"]
        if r["Nguồn"] == "Nhân bản":
            count[(stt, r["Loại số"])] += 1
    return info, count


def main(attempts=12, only=None, salt="", spare=0):
    info, count = existing_structure()
    _, rows = load_questions()
    existing = collections.defaultdict(set)
    for r in rows:
        if r["topic"] == "SP":
            existing[r["label"]].add(question_key(r["label"], r["text"]))
    mods = load_modules()
    out, shortage = [], []
    for stt in sorted(mods):
        if stt not in info:                       # a source question that is not part of the 54 retained types
            continue
        mod = mods[stt]
        ma = info[stt]
        label = "SP_" + ma
        if only and ma not in only:
            continue
        for loai in LOAI:
            need = count[(stt, loai)] + spare
            got, seen = [], set()
            for attempt in range(attempts):
                seed = zlib.crc32(f"router_train{salt}|{stt}|{loai}|{attempt}".encode()) % (2 ** 31)
                params = None
                for n_try in (max(3 * need, 30), max(2 * need, 20), max(need, 10)):
                    try:
                        params = mod.gen_params(loai, n_try, seed)
                        break
                    except Exception:
                        continue
                if not params:
                    continue
                for p in params:
                    try:
                        de_bai, dap_an, loi_giai = mod.sinh(**p)
                    except Exception:
                        continue
                    k = question_key(label, de_bai)
                    if k in seen or k in existing[label]:
                        continue
                    seen.add(k)
                    got.append(dict(ma_dang=ma, stt_goc=stt, loai_so=loai, de_bai=de_bai, dap_an=dap_an,
                                    loi_giai=loi_giai, params={a: str(b) for a, b in p.items()}))
                    if len(got) >= need:
                        break
                if len(got) >= need:
                    break
            if len(got) < need:
                shortage.append((label, stt, loai, need, len(got)))
            out.extend(got[:need])
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"so_phuc_candidates{salt}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    per = collections.Counter("SP_" + r["ma_dang"] for r in out)
    print("candidates:", len(out), "| types:", len(per), "| per type min/max:", min(per.values()), max(per.values()))
    print("slots short of the existing count:", len(shortage))
    for s in shortage:
        print("   ", s)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        main(int(args[0]), only=set(args[2:]), salt=args[1], spare=3)
    else:
        main(int(args[0]) if args else 12)
