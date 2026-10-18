# -*- coding: utf-8 -*-
"""Run the pipeline notebook end to end WITHOUT a GPU, with a fake vLLM, to check the plumbing before using Kaggle.

python scripts/pipeline/dry_run_pipeline.py

What is real: the notebook cells, the code units of every dạng (exec'd verbatim), the Calculator backends, the routing
plan, the loops and the report. What is fake: the router predictions (each of the 36 code units gets at least one
question) and vLLM (answers are canned, the Calculator is called with two trivial commands). The accuracy it prints is
meaningless; it only proves that nothing crashes and that every unit can be run. Needs `transformers` (the Qwen tokenizer is
downloaded once), pandas, sympy.

Note: the units write to /kaggle/working (hard-coded in the original experiment notebooks). On Windows this resolves to
<current drive>:\\kaggle\\working; the script creates it and removes it again when it is empty.
"""
import csv
import json
import os
import pickle
import shutil
import sys
import tempfile
import types

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NB = os.path.join(REPO, "experiments", "Pipeline", "KLTN_Pipeline_GiaSu_100cau.ipynb")
BUNDLE = os.path.join(REPO, "data", "pipeline_bundle")
WORK = tempfile.mkdtemp(prefix="pipeline_dry_run_")
KAGGLE = os.path.abspath("/kaggle/working")
made_kaggle = not os.path.exists(KAGGLE)
os.makedirs(KAGGLE, exist_ok=True)
os.environ["PIPELINE_BUNDLE_DIR"] = BUNDLE
os.environ["PIPELINE_WORK_DIR"] = WORK

# ---- fake vllm ----
import transformers  # noqa: E402

_tok = transformers.AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
transformers.AutoTokenizer.from_pretrained = staticmethod(lambda *a, **k: _tok)


class SamplingParams:
    def __init__(self, **kw):
        self.kw = kw


class _O:
    def __init__(self, text, stop_reason):
        self.text, self.stop_reason, self.finish_reason = text, stop_reason, "stop"
        self.token_ids = list(range(max(1, len(text) // 4)))


class LLM:
    def __init__(self, **kw):
        print("[fake LLM]", kw)

    def generate(self, prompts, sp, use_tqdm=True):
        outs = []
        for i, p in enumerate(prompts):
            s = sp[i] if isinstance(sp, list) else sp
            for k in ("temperature", "top_p", "top_k", "seed"):
                assert k in s.kw, k            # every generation call must carry the experiment parameters
            letter = "ABCD"[len(p) % 4]
            if "<think>\nThought:" not in p:   # zero-shot prompt
                outs.append(types.SimpleNamespace(outputs=[_O("<think>\nfake reasoning\n</think>\n\nĐáp án đúng: " + letter, None)]))
                continue
            n_obs = p.split("<|im_start|>assistant\n")[-1].count("Observation:")
            if s.kw.get("stop") is None or n_obs >= 2:
                outs.append(types.SimpleNamespace(outputs=[_O(" all checked.\nFinal Answer: \\boxed{" + letter + "}", None)]))
            else:
                expr = "val_one = 2 + 3" if n_obs == 0 else "Eq(val_one, 5)"
                outs.append(types.SimpleNamespace(outputs=[_O(f" step.\nAction: Calculator\nAction Input: {expr}\n", "Observation:")]))
        return outs


vllm = types.ModuleType("vllm")
vllm.LLM, vllm.SamplingParams = LLM, SamplingParams
sys.modules["vllm"] = vllm

# ---- fake router output: every code unit gets one question, the others keep their true dạng ----
pipe = json.load(open(os.path.join(BUNDLE, "pipeline_units.json"), encoding="utf-8"))
qs = list(csv.DictReader(open(os.path.join(BUNDLE, "cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv"), encoding="utf-8-sig")))
first_type = {}
for t in pipe["types"]:
    first_type.setdefault(t["unit"], t["so_dang"])
forced = list(first_type.values())
rows = []
for i, q in enumerate(qs):
    d = forced[i] if i < len(forced) else int(q["dang_dung"])
    rows.append(dict(id=q["id"], du_doan_dang=d, do_tin_cay=0.9, top3=f"{d}; 1; 2"))
with open(os.path.join(WORK, "router_predictions.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("code units forced to run:", len(forced))

cells = ["".join(c["source"]) for c in json.load(open(NB, encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
g = {"__name__": "__main__"}
for i, src in enumerate(cells):
    if "!pip" in src or "ROUTER_PY = r" in src:        # installs and the real router subprocess are skipped
        print(f"--- skip cell {i}")
        continue
    src = src.replace("shutil.make_archive('/kaggle/working/pipeline_ket_qua'", "shutil.make_archive(os.path.join(WORK_DIR, '..', 'zip_dry_run')")
    print(f"--- run cell {i}")
    exec(compile(src, f"<cell{i}>", "exec"), g)
    if "def new_module" in src:                          # the Calculator functions must be picklable by module name
        for unit, mod in g["MODS"].items():
            for fn in ("fast_simplify", "is_zero"):
                if hasattr(mod, fn):
                    pickle.dumps(getattr(mod, fn))
        print("pickle by module name: ok")
res = g["res"]
print("\nDRY RUN OK:", len(res), "questions,", res["unit"].nunique(), "code units ran, answers:", res["ket_qua"].value_counts().to_dict())
print("(the numbers are fake; this only checks the plumbing)")

# ---- clean up what this script created ----
shutil.rmtree(WORK, ignore_errors=True)
zip_path = os.path.join(os.path.dirname(WORK), "zip_dry_run.zip")
if os.path.exists(zip_path):
    os.remove(zip_path)
if made_kaggle:
    for d in (KAGGLE, os.path.dirname(KAGGLE)):
        try:
            os.rmdir(d)
        except OSError:
            print("left in place (not empty):", d)
