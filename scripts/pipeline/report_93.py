# -*- coding: utf-8 -*-
"""Report of the 2026-10-16 Kaggle run restricted to the 93-question evaluation set.

The run covered 100 questions. Seven of them were removed afterwards because their ground-truth dạng is a
sub-case of the dạng name rather than an exact match of its template (see ra_soat_nhan_dang_23_cau_phan_sai.csv).
python scripts/pipeline/report_93.py
"""
import os
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                 "data", "results", "pipeline_realworld")
DROP = {"SRC-09", "SRC-02", "SRC-22", "WEB-026", "WEB-044", "BS-008", "CR-9"}

res = pd.read_csv(os.path.join(D, "kaggle_run_20261016", "ket_qua_pipeline_100cau.csv"),
                  encoding="utf-8-sig", keep_default_na=False, dtype=str)
res = res[~res["id"].isin(DROP)].copy()
res["dung_dang"] = res["dang_du_doan"] == res["dang_dung"]
res["nguon"] = ["30 câu đề chính thức (VD/VDC)" if i.startswith("VD-") else "63 câu web / đề thi thử" for i in res["id"]]
lines = []


def out(s=""):
    print(s)
    lines.append(str(s))


def pct(a, b):
    return f"{a}/{b} ({a / b * 100:.1f}%)"


def row(name, g):
    out(f"{name:32s} phân dạng đúng {pct(int(g['dung_dang'].sum()), len(g))} | "
        f"đáp án đúng {pct(int((g['ket_qua'] == 'Đúng').sum()), len(g))}")


n = len(res)
out("=" * 78)
out(f"Phạm vi: {n} câu thực tế, thuộc {res['dang_dung'].nunique()}/142 dạng; "
    + ", ".join(f"{k}: {v}" for k, v in res["topic"].value_counts().items()))
out("Lần chạy Kaggle 2026-10-16 (một lần chạy), đã bỏ 7 câu: " + ", ".join(sorted(DROP)))
out("=" * 78)
row("Cả bộ", res)
out(f"Sai: {int((res['ket_qua'] == 'Sai').sum())} | Không xác định: {int((res['ket_qua'] == 'Không xác định').sum())}")
out()
out("--- Theo nguồn ---")
for k, g in res.groupby("nguon"):
    row(k, g)
out()
out("--- Theo chuyên đề ---")
for k, g in res.groupby("topic"):
    row(k, g)
out()
out("--- Theo cách giải được chọn (theo dạng dự đoán) ---")
for k, g in res.groupby("cach_giai"):
    out(f"{k:32s} đáp án đúng {pct(int((g['ket_qua'] == 'Đúng').sum()), len(g))}")
out()
out("--- Phân dạng x kết quả ---")
out(pd.crosstab(res["dung_dang"].map({True: "đúng dạng", False: "sai dạng"}), res["ket_qua"], margins=True).to_string())
out()
cols = ["id", "topic", "dang_dung", "dang_du_doan", "cach_giai", "dap_an_dung", "model_chon", "ket_qua"]
out("--- Phân dạng đúng nhưng giải sai ---")
out(res[res["dung_dang"] & (res["ket_qua"] == "Sai")][cols + ["so_luot_goi_tool", "ly_do_dung"]].to_string(index=False))
open(os.path.join(D, "bao_cao_93_cau.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
