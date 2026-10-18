# -*- coding: utf-8 -*-
"""Replace, in place, the new questions that fail a quality gate by spare candidates of the same type, source question and
number kind. Currently the gate is: the two given complex numbers must not be identical (z1 = z2).

python replace_bad_rows.py
Needs data/router_train/_work/so_phuc_candidates_spare*.json (made by gen_sp_new.py 12 _spareN <types>).
"""
import csv
import glob
import json
import os
import re

from assemble_train import MOJIBAKE, PROMPT, catalogue, option_ok
from collect_new import question_key
from common import REPO, has_identical_pair, load_questions, norm

OUT = os.path.join(REPO, "data", "router_train")
rows = [json.loads(l) for l in open(os.path.join(OUT, "bien_the_moi_142_dang.jsonl"), encoding="utf-8")]
num, by_code = catalogue()
sig = {c: re.compile(e["pattern"]) for c, e in by_code.items()}
_, old = load_questions()
taken = {(r["label"], question_key(r["label"], r["text"])) for r in old}
taken |= {(r["ma_cu"], question_key(r["ma_cu"], r["de_bai"])) for r in rows}

spares = []
for p in sorted(glob.glob(os.path.join(OUT, "_work", "so_phuc_candidates_spare*.json"))):
    spares += json.load(open(p, encoding="utf-8"))

changed = []
for r in rows:
    if not has_identical_pair(r["de_bai"]):
        continue
    code = r["ma_cu"]
    stt, loai = r["id_goc"].replace("STT", "").split("|")
    for c in spares:
        if "SP_" + c["ma_dang"] != code or str(c["stt_goc"]) != stt or c["loai_so"] != loai:
            continue
        k = question_key(code, c["de_bai"])
        if (code, k) in taken or has_identical_pair(c["de_bai"]):
            continue
        if not option_ok(c["de_bai"], c["dap_an"])[0] or MOJIBAKE.search(c["de_bai"]):
            continue
        if [x for x, p in sig.items() if p.search(norm(c["de_bai"]))] != [code]:
            continue
        taken.add((code, k))
        changed.append((r["stt"], r["de_bai"][:70].replace("\n", " "), c["de_bai"][:70].replace("\n", " ")))
        r["de_bai"], r["dap_an_dung"], r["loi_giai"] = c["de_bai"], c["dap_an"], c.get("loi_giai", "")
        break
    else:
        raise SystemExit(f"no spare for {r['stt']}")
for c in changed:
    print("replaced", c)

with open(os.path.join(OUT, "bien_the_moi_142_dang.jsonl"), "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(os.path.join(OUT, "bien_the_moi_142_dang.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
by_stt = {r["stt"]: r for r in rows}
ft = [json.loads(l) for l in open(os.path.join(OUT, "finetune_router.jsonl"), encoding="utf-8")]
for p in ft:
    r = by_stt[p["stt"]]
    p["prompt"] = PROMPT + r["de_bai"]
    p["messages"][0]["content"] = p["prompt"]
with open(os.path.join(OUT, "finetune_router.jsonl"), "w", encoding="utf-8") as f:
    for p in ft:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")
with open(os.path.join(OUT, "finetune_router.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["stt", "input", "output"])
    for p in ft:
        w.writerow([p["stt"], p["prompt"], p["completion"]])
print("replaced rows:", len(changed))
