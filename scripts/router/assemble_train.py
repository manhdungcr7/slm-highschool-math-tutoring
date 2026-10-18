# -*- coding: utf-8 -*-
"""Assemble the new router training set: exactly 90 new, checked questions for each of the 142 types.

Sources of candidates
  Mũ-Logarit: the sandbox passes of the original generators (new seeds) + gen_ml_extra.py (wider parameter ranges)
  Số phức   : gen_sp_new.py (same generators, new seeds)

Every chosen question must
  * be new for the whole project (key not in the 90 existing variants nor the source question) and unique in the new set,
  * have four distinct options A-D and a correct answer that is one of them,
  * contain no mojibake,
  * match the signature of its own type in the catalogue and of no other type (the catalogue's identification test).

python assemble_train.py <sandbox_ml>/passes
Output (data/router_train/): bien_the_moi_142_dang.csv/.jsonl, finetune_router.jsonl, finetune_router.csv, README.md
"""
import collections
import csv
import glob
import json
import os
import random
import re
import sys

from collect_new import load_json_rows, question_key
from common import DROPPED, REPO, has_identical_pair, load_questions, norm, options, stem

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalogue_ml
import catalogue_sp

OUT = os.path.join(REPO, "data", "router_train")
WORK = os.path.join(OUT, "_work")
PER_TYPE = 90
SEED = 20261007

MOJIBAKE = re.compile(r"Ã|Â|Ä[-¿]|á[º»]|â€|�|\?\?")

PROMPT = ("Hãy xác định dạng bài của đề bài sau. Chỉ trả lời đúng một dòng theo mẫu "
          "\"Dạng N: mô tả dạng bài\", trong đó N là số thứ tự của dạng.\n\nĐề bài:\n")


def catalogue():
    from build_catalogue import numbering
    num = numbering()
    entries = catalogue_sp.ENTRIES + catalogue_ml.ENTRIES
    by_code = {e["code"]: e for e in entries}
    return num, by_code


def option_ok(de_bai, dap_an):
    opts = options(de_bai)
    if set(opts) != set("ABCD"):
        return False, "options"
    flat = [re.sub(r"[\s$.,]", "", v) for v in opts.values()]
    if len(set(flat)) != 4:
        return False, "duplicate options"
    m = re.match(r"\s*([ABCD])\.", dap_an)
    if not m:
        return False, "answer letter"
    want = re.sub(r"[\s$.,]", "", re.sub(r"^\s*[ABCD]\.", "", dap_an))
    if re.sub(r"[\s$.,]", "", opts[m.group(1)]) != want:
        return False, "answer text differs from option"
    return True, ""


def gather_ml(passes_dir):
    pool = collections.defaultdict(list)
    for d in sorted(glob.glob(os.path.join(passes_dir, "offset_*"))):
        for path in sorted(glob.glob(os.path.join(d, "*.json"))):
            for it in load_json_rows(path):
                pool[it["ma_dang"]].append(("pass", it))
    for path in sorted(glob.glob(os.path.join(WORK, "ml_extra_*.json"))):
        for it in load_json_rows(path):
            pool[it["ma_dang"]].append(("extra", it))
    return pool


def main(passes_dir):
    num, by_code = catalogue()
    sig = {c: re.compile(e["pattern"]) for c, e in by_code.items()}
    _, old_rows = load_questions()
    existing = collections.defaultdict(set)
    source_id = {}
    for r in old_rows:
        existing[r["label"]].add(question_key(r["label"], r["text"]))
    rnd = random.Random(SEED)

    ml_pool = gather_ml(passes_dir)
    sp_rows = []
    for sp_path in sorted(glob.glob(os.path.join(WORK, "so_phuc_candidates*.json"))):
        sp_rows += load_json_rows(sp_path)

    chosen, report = [], []
    for code in sorted(by_code, key=lambda c: num[c]):
        label = code
        topic = code[:2]
        cands = []
        if topic == "ML":
            items = ml_pool.get(code[3:], [])
            for origin, it in items:
                cands.append((origin, it["de_bai"], it["dap_an"], it.get("loi_giai", ""), it.get("id_goc", ""),
                              it.get("params", {})))
        else:
            for it in sp_rows:
                if "SP_" + it["ma_dang"] == code:
                    cands.append(("sp", it["de_bai"], it["dap_an"], it.get("loi_giai", ""),
                                  f"STT{it['stt_goc']}|{it['loai_so']}", it.get("params", {})))
        seen, good, rejected = set(), [], collections.Counter()
        for origin, de_bai, dap_an, loi_giai, idg, params in cands:
            k = question_key(label, de_bai)
            if k in existing[label]:
                rejected["trùng bộ hiện có"] += 1
                continue
            if k in seen:
                rejected["trùng trong bộ mới"] += 1
                continue
            ok, why = option_ok(de_bai, dap_an)
            if not ok:
                rejected[why] += 1
                continue
            if MOJIBAKE.search(de_bai) or MOJIBAKE.search(dap_an):
                rejected["lỗi mã hóa"] += 1
                continue
            if has_identical_pair(de_bai):
                rejected["hai số phức đầu vào giống hệt"] += 1
                continue
            t = norm(de_bai)
            hits = [c for c, p in sig.items() if p.search(t)]
            if hits != [code]:
                rejected["không khớp dấu hiệu nhận dạng"] += 1
                continue
            seen.add(k)
            good.append((origin, de_bai, dap_an, loi_giai, idg, params))
        # keep the generator's own passes first, extras only to fill up; random but reproducible choice
        first = [g for g in good if g[0] in ("pass", "sp")]
        extra = [g for g in good if g[0] == "extra"]
        rnd.shuffle(first)
        rnd.shuffle(extra)
        pick = (first + extra)[:PER_TYPE]
        report.append((code, len(cands), len(good), len(pick), dict(rejected)))
        for g in pick:
            chosen.append((code, g))
    short = [r for r in report if r[3] < PER_TYPE]
    print("types:", len(report), "| total chosen:", len(chosen), "| types below", PER_TYPE, ":", len(short))
    for r in short:
        print("   SHORT", r)
    rej = collections.Counter()
    for r in report:
        rej.update(r[4])
    print("rejected candidates by reason:", dict(rej))
    if short:
        json.dump(report, open(os.path.join(WORK, "assemble_report.json"), "w", encoding="utf-8"), ensure_ascii=False,
                  indent=1)
        return 1

    # ---------------------------------------------------------------- write the dataset
    os.makedirs(OUT, exist_ok=True)
    desc = {e["code"]: e["name"] for e in by_code.values()}
    ids = collections.Counter()
    rows_out = []
    for code, (origin, de_bai, dap_an, loi_giai, idg, params) in chosen:
        ids[code] += 1
        rows_out.append(dict(
            ten_goi=f"Dạng {num[code]}", so_dang=num[code], ma_cu=code,
            chu_de="Mũ-Logarit" if code.startswith("ML_") else "Số phức",
            stt=f"{num[code]}-{ids[code]:02d}", nguon_sinh=origin, id_goc=idg,
            de_bai=de_bai, dap_an_dung=dap_an, loi_giai=loi_giai, mo_ta_dang=desc[code]))
    with open(os.path.join(OUT, "bien_the_moi_142_dang.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0]))
        w.writeheader()
        w.writerows(rows_out)
    with open(os.path.join(OUT, "bien_the_moi_142_dang.jsonl"), "w", encoding="utf-8") as f:
        for r in rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # fine-tuning pairs: input = instruction + question, output = "Dạng N: mô tả"
    ft = []
    for r in rows_out:
        answer = f"{r['ten_goi']}: {r['mo_ta_dang']}"
        ft.append(dict(stt=r["stt"], prompt=PROMPT + r["de_bai"], completion=answer,
                       messages=[dict(role="user", content=PROMPT + r["de_bai"]),
                                 dict(role="assistant", content=answer)]))
    rnd.shuffle(ft)
    with open(os.path.join(OUT, "finetune_router.jsonl"), "w", encoding="utf-8") as f:
        for r in ft:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(OUT, "finetune_router.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stt", "input", "output"])
        for r in ft:
            w.writerow([r["stt"], r["prompt"], r["completion"]])
    json.dump(report, open(os.path.join(WORK, "assemble_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written:", OUT, "| rows:", len(rows_out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
