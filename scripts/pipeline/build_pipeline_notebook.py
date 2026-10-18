# -*- coding: utf-8 -*-
"""Build the end-to-end pipeline notebook of the AI tutor (đề bài -> router -> prompt of that dạng -> Qwen3-4B -> đáp án).

python scripts/pipeline/build_pipeline_notebook.py [router_adapter_dir]     (default: models/router_lora, the 100% router)

Every dạng keeps exactly what it had in its final experiment: the code of the notebook that produced its reported
result is copied verbatim (prompt, Calculator backend, ReAct loop, generation parameters, answer extraction). The only
lines left out are the ones that load that notebook's 90 questions and create the tokenizer/LLM; the pipeline gives the
code the routed questions, one shared tokenizer and one shared vLLM engine instead.

Outputs:
  data/pipeline_bundle/            Kaggle Dataset: pipeline_units.json, the 100 questions, router candidates and adapter
  data/pipeline_bundle/bang_dang_prompt.csv   which prompt / setting each of the 142 dạng uses
  experiments/Pipeline/KLTN_Pipeline_GiaSu_100cau.ipynb
"""
import csv
import glob
import hashlib
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ML_DIR = os.path.join(REPO, "experiments", "ReAct-Calculator")
ML_ZS_NB = os.path.join(REPO, "experiments", "Qwen3-4B", "KLTN_mulogarit_zeroshot_full90_Qwen3-4B.ipynb")
SP_DIR = os.path.join(REPO, "so_phuc", "experiments", "Qwen3-4B")
SP_ZS_NB = os.path.join(REPO, "experiments", "Qwen3-4B", "qwen_eval_kaggle_sophuc_zeroshot.ipynb")
CATALOGUE = os.path.join(REPO, "data", "catalogue", "danh_muc_dang_bai.csv")
# The question set the notebook evaluates. To evaluate another set, replace this file (same name, same columns:
# id, topic, question_markdown_latex, answer_letter, dang_dung) and rebuild.
QUESTIONS = os.path.join(REPO, "data", "results", "pipeline_realworld", "questions", "cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv")
CANDIDATES = os.path.join(REPO, "data", "router_train", "kaggle_bundle", "candidates.json")
BUNDLE = os.path.join(REPO, "data", "pipeline_bundle")
NB_OUT = os.path.join(REPO, "experiments", "Pipeline", "KLTN_Pipeline_GiaSu_100cau.ipynb")
ADAPTER = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "models", "router_lora")

# Final notebook of each Mũ-Logarit ReAct dạng (checked: it holds the latest prompt_Dxx*.txt and its result is 90/90).
ML_FINAL = {"D08": "G10", "D10": "H01", "D16": "G06", "D17": "H02", "D22": "G09", "D23": "H02", "D24": "G07",
            "D25": "H05", "D28": "G05", "D29": "H03", "D40": "R04", "D41": "G06", "D45": "H01", "D46": "G05",
            "D47": "G01", "D51": "G09", "D52": "H04", "D56": "G04", "D57": "H04", "D65": "G03", "D68": "R01",
            "D69": "G02", "D71": "H05", "D75": "H02", "D78": "G04", "D79": "D79", "D83": "H03", "D84": "G01",
            "D88": "G06", "D89": "H03", "D93": "G03", "D94": "G07"}
# Số phức ReAct dạng (codes of the data/notebooks; data D55 is D54 in the paper and the catalogue).
SP_SINGLE = ["D35", "D36", "D37", "D38", "D39", "D44", "D45", "D46", "D47", "D48", "D50", "D51", "D52", "D53", "D55"]
# D04 uses the Nhom1 version (the author confirmed it; the stand-alone D04 notebook is an older prompt, md5 ff72a99c).
SP_GROUP = {"Nhom1": ["D04", "D14", "D28", "D32", "D33"], "Nhom2": ["D34", "D40", "D42", "D49"]}
SP_GROUP_NB = {"Nhom1": "KLTN_Nhom1_D04_D14_D28_D32_D33_full90.ipynb", "Nhom2": "KLTN_Nhom2_D34_D40_D42_D45_D46_D49_full90.ipynb"}


def cells(path):
    return ["".join(c["source"]) for c in json.load(open(path, encoding="utf-8"))["cells"]]


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def cut(text, pattern, flags=re.S | re.M):
    """Remove the one place that matches; fail loudly if it is not there exactly once."""
    found = list(re.finditer(pattern, text, flags))
    assert len(found) == 1, (pattern, len(found))
    m = found[0]
    return text[:m.start()] + text[m.end():]


def grab(text, pattern, flags=re.S | re.M):
    found = list(re.finditer(pattern, text, flags))
    assert len(found) == 1, (pattern, len(found))
    return found[0].group(0)


units = {}

# ---------------- Mũ-Logarit ReAct: G/H/R group notebooks ----------------
for name in sorted(set(ML_FINAL.values()) - {"D79"}):
    c = cells(os.path.join(ML_DIR, f"KLTN_{name}_ReAct_Calculator.ipynb"))
    setup = cut(c[2], r"^DATA_FILENAME = .*?^DATA_PATH = _matches\[0\]\n")
    setup = cut(setup, r"^with open\(DATA_PATH.*\Z")
    loop = cut(c[5], r"\n# =+\n# RUN EVERY TYPE OF THIS NOTEBOOK.*\Z")
    assert "out_path = f'/kaggle/working/{ma_dang.lower()}_react_calculator_full90.csv'" in loop
    ns = {}
    exec(c[3], ns)
    types_here = [ma for ma, u in ML_FINAL.items() if u == name]
    units[name] = dict(kind="ml_group", source=f"experiments/ReAct-Calculator/KLTN_{name}_ReAct_Calculator.ipynb",
                       setup=setup, prompt=c[3], loop=loop, types=types_here,
                       prompt_md5={ma: md5(ns["TYPE_PROMPTS"][ma]["template"]) for ma in types_here},
                       max_tool_calls={ma: ns["TYPE_PROMPTS"][ma]["max_tool_calls"] for ma in types_here})

# ---------------- Mũ-Logarit ReAct: D79 ----------------
c = cells(os.path.join(ML_DIR, "KLTN_D79_ReAct_Calculator_full90.ipynb"))
setup = cut(c[2], r"^DATA_FILENAME = .*?^DATA_PATH = _matches\[0\]\n")
setup = cut(setup, r"^with open\(DATA_PATH.*\Z")
ns = {}
exec(c[3], ns)
units["D79"] = dict(kind="ml_single", source="experiments/ReAct-Calculator/KLTN_D79_ReAct_Calculator_full90.ipynb",
                    setup=setup, prompt=c[3], loop=c[5], types=["D79"], prompt_md5={"D79": md5(ns["PROMPT_TEMPLATE"])},
                    max_tool_calls={"D79": int(re.search(r"^MAX_TOOL_CALLS\s*=\s*(\d+)", c[5], re.M).group(1))})


# ---------------- Số phức ReAct: single-type notebooks ----------------
def sp_setup(text):
    text = cut(text, r"^DATA_PATH = .*?\n")
    text = cut(text, r"^OUT_PATH\s*= .*?\n")
    text = cut(text, r"^with open\(DATA_PATH, encoding='utf-8'\) as f:\n    records = json\.load\(f\)\nprint\('So cau:', len\(records\)\)\n")
    return cut(text, r"^tok = AutoTokenizer\.from_pretrained.*\Z")


for ma in SP_SINGLE:
    c = cells(os.path.join(SP_DIR, f"KLTN_{ma}_ReAct_Calculator_full90.ipynb"))
    assert len(c) == 5 and "df.to_csv(OUT_PATH" in c[4]
    ns = {}
    exec(c[3], ns)
    allc = "\n".join(c)
    units["SP_" + ma] = dict(kind="sp_single", source=f"so_phuc/experiments/Qwen3-4B/KLTN_{ma}_ReAct_Calculator_full90.ipynb",
                             setup=sp_setup(c[2]), prompt=c[3], loop=c[4], types=[ma],
                             prompt_md5={ma: md5(ns["PROMPT_TEMPLATE"])},
                             max_tool_calls={ma: int(re.search(r"^MAX_TOOL_CALLS\s*=\s*(\d+)", allc, re.M).group(1))})

# ---------------- Số phức ReAct: the two group notebooks (only the types they add) ----------------
for g, mas in SP_GROUP.items():
    c = cells(os.path.join(SP_DIR, SP_GROUP_NB[g]))
    setup = cut(c[2], r"^tok = AutoTokenizer\.from_pretrained.*\Z")
    type_cells, data_file, out_file, pm, mt = {}, {}, {}, {}, {}
    for s in c[4:]:
        ma = re.search(r"chay_mot_dang\(\s*ma_dang='(D\d+)'", s).group(1)
        if ma not in mas:
            continue
        type_cells[ma] = s
        data_file[ma] = re.search(r"data_path=f'\{DATA_DIR\}/([^']+)'", s).group(1)
        out_file[ma] = re.search(r"out_path=f'\{OUT_DIR\}/([^']+)'", s).group(1)
        cap = {}
        ns = {"chay_mot_dang": lambda **kw: cap.update(kw), "DATA_DIR": "", "OUT_DIR": ""}
        exec(s, ns)
        pm[ma], mt[ma] = md5(ns["PROMPT_TEMPLATE"]), ns["MAX_TOOL_CALLS"]
    assert sorted(type_cells) == sorted(mas), (g, sorted(type_cells))
    units["SP_" + g] = dict(kind="sp_group", source="so_phuc/experiments/Qwen3-4B/" + SP_GROUP_NB[g], setup=setup,
                            loop=c[3], type_cells=type_cells, data_file=data_file, out_file=out_file, types=mas,
                            prompt_md5=pm, max_tool_calls=mt)

# ---------------- Zero-shot, Mũ-Logarit ----------------
c = cells(ML_ZS_NB)
cfg = c[3]
setup = "\n".join([grab(cfg, r"\Aimport os.*?from vllm import LLM, SamplingParams\n").rstrip("\n"),
                   grab(cfg, r"^MODEL = .*?$"), grab(cfg, r"^MAX_MODEL_LEN, MAX_NEW_TOKENS = .*?$"),
                   grab(cfg, r"^TEMPERATURE, TOP_P, TOP_K, SEED = .*?$"), grab(cfg, r"^PRESENCE_PENALTY = .*?$"),
                   grab(cfg, r"^os\.environ\['TOKENIZERS_PARALLELISM'\] = 'false'$")]) + "\n"
sampling = grab(c[5], r"^sampling = SamplingParams\(.*\Z")
assert c[7].startswith("PROMPT_TEMPLATE = r'''") and "def get_letter" in c[8]
ns = {}
exec(c[7], ns)
units["ZS_ML"] = dict(kind="ml_zeroshot", source="experiments/Qwen3-4B/KLTN_mulogarit_zeroshot_full90_Qwen3-4B.ipynb",
                      setup=setup, sampling=sampling, prompt=c[7], loop=c[8], prompt_md5=md5(ns["PROMPT_TEMPLATE"]))

# ---------------- Zero-shot, Số phức ----------------
c = cells(SP_ZS_NB)
assert "ENABLE_THINKING = True" in c[2] and "PROMPT_TEMPLATE = \"\"\"" in c[5] and "def extract_choice" in c[8]
gen = (grab(c[7], r"^    from vllm import LLM, SamplingParams.*?$").strip() + "\n"
       + grab(c[7], r"^    sampling = SamplingParams\(temperature=TEMPERATURE.*?seed=SEED\)\n").replace("\n    ", "\n").strip() + "\n"
       + "outputs = llm.generate(prompts, sampling)\ntexts = [o.outputs[0].text for o in outputs]\n")
ns = {}
exec(grab(c[5], r"^PROMPT_TEMPLATE = \"\"\".*?^\"\"\"\n"), ns)
units["ZS_SP"] = dict(kind="sp_zeroshot", source="qwen_eval_kaggle.ipynb (Số phức, Qwen3-4B, thinking)",
                      setup=c[2], prompt=c[5], gen=gen, extract=c[8], prompt_md5=md5(ns["PROMPT_TEMPLATE"]))
zs_ml_same = units["ZS_ML"]["prompt_md5"] == units["ZS_SP"]["prompt_md5"]

# ---------------- The 142 dạng ----------------
unit_of = {}
for name, u in units.items():
    for ma in u.get("types", []):
        unit_of[("ML" if u["kind"].startswith("ml") else "SP", ma)] = name
types = []
for r in csv.DictReader(open(CATALOGUE, encoding="utf-8-sig")):
    so, ma_cu = int(r["so_dang"]), r["ma_cu"]
    topic, code = ma_cu.split("_")
    data_code = "D55" if (topic == "SP" and code == "D54") else code      # paper D54 = data D55
    name = unit_of.get((topic, data_code), "ZS_ML" if topic == "ML" else "ZS_SP")
    u = units[name]
    react = not name.startswith("ZS_")
    if topic == "ML":
        assert (r["cach_giai"] == "ReAct+Calculator") == react, (so, ma_cu)
    types.append(dict(so_dang=so, chu_de=r["chu_de"], ma_cu=ma_cu, ma_du_lieu=data_code,
                      cach_giai="ReAct+Calculator" if react else "zero-shot", unit=name, notebook_nguon=u["source"],
                      max_tool_calls=u["max_tool_calls"][data_code] if react else "",
                      prompt_md5=u["prompt_md5"][data_code] if react else u["prompt_md5"],
                      mo_ta=r["mo_ta_dang_moi"]))
assert len(types) == 142
assert sum(t["cach_giai"] == "ReAct+Calculator" for t in types) == 56

os.makedirs(BUNDLE, exist_ok=True)
json.dump(dict(types=types, units=units), open(os.path.join(BUNDLE, "pipeline_units.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(BUNDLE, "bang_dang_prompt.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[k for k in types[0] if k != "mo_ta"])
    w.writeheader()
    w.writerows([{k: v for k, v in t.items() if k != "mo_ta"} for t in types])
shutil.copy(QUESTIONS, os.path.join(BUNDLE, os.path.basename(QUESTIONS)))
shutil.copy(CANDIDATES, os.path.join(BUNDLE, "router_candidates.json"))
dst = os.path.join(BUNDLE, "router_lora")
assert os.path.realpath(ADAPTER) != os.path.realpath(dst), "the adapter must not be the bundle copy that is about to be replaced"
shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(ADAPTER, dst, ignore=shutil.ignore_patterns("training_run_v3"))     # the bundle copy is git-ignored

# ---------------- Notebook ----------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline_cells import CELLS  # noqa: E402

nb = {"cells": [], "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
for i, (kind, src) in enumerate(CELLS):
    cell = {"cell_type": kind, "id": f"c{i:02d}", "metadata": {}, "source": src.strip("\n").splitlines(True)}
    if kind == "code":
        cell.update(execution_count=None, outputs=[])
    nb["cells"].append(cell)
os.makedirs(os.path.dirname(NB_OUT), exist_ok=True)
json.dump(nb, open(NB_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("units:", len(units), "| ReAct dạng:", sum(t["cach_giai"] != "zero-shot" for t in types),
      "| zero-shot prompt identical in both topics:", zs_ml_same)
print("bundle:", BUNDLE)
print("notebook:", NB_OUT)
