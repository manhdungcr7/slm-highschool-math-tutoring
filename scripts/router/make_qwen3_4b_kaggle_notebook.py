# -*- coding: utf-8 -*-
"""Copy the Kaggle notebook of the Qwen3-0.6B router run and change only what Qwen3-4B needs.

python make_qwen3_4b_kaggle_notebook.py
Input : experiments/Router-Finetune/KLTN_router_finetune_qlora.ipynb   (the run that reached 100%)
Output: experiments/Router-Finetune-4B/KLTN_router_finetune_Qwen3-4B_Kaggle.ipynb

Changes (the training data and all training settings stay as in the 0.6B notebook):
  1. MODEL = Qwen/Qwen3-4B
  2. Dạng 122 (Số phức D34, removed from the thesis) is left out of the training pairs and of the candidates (141)
  3. weights loaded in float16 on a T4: the float32 weights of the 0.6B run would take 16 GB for 4B, a whole T4
  4. MAX_TRAIN_MINUTES 270 -> 680 (almost the whole 12 h Kaggle session)
  5. training only: the evaluation cells are left out (the evaluation runs in a separate notebook)
  6. the training data is downloaded from GitHub at a fixed commit, checked by its git hash (no Kaggle Dataset)
"""
import difflib
import json
import os

from common import REPO

SRC = os.path.join(REPO, "experiments", "Router-Finetune", "KLTN_router_finetune_qlora.ipynb")
DST = os.path.join(REPO, "experiments", "Router-Finetune-4B", "KLTN_router_finetune_Qwen3-4B_Kaggle.ipynb")

COMMIT = "b213dc43036660918fc860f5df02b61ac30a9a16"

EDITS = [
    ("MODEL = os.environ.get('ROUTER_MODEL', 'Qwen/Qwen3-0.6B')",
     "MODEL = os.environ.get('ROUTER_MODEL', 'Qwen/Qwen3-4B')"),

    ("MAX_TRAIN_MINUTES = 270                                    # safety: training stops (and the adapter is saved) after this many minutes",
     "MAX_TRAIN_MINUTES = 680                                    # Kaggle stops a session at 12 h (720 min); the rest is for setup, the final validation and saving"),

    ("TRAIN_PATH, EVAL_PATH, CAND_PATH = find('finetune_router.jsonl'), find('eval_set.jsonl'), find('candidates.json')",
     "# the training data is downloaded from the repo at a fixed commit (no Kaggle Dataset needed; Internet must be On)\n"
     "import hashlib, urllib.request\n"
     f"RAW = 'https://raw.githubusercontent.com/manhdungcr7/slm-highschool-math-tutoring/{COMMIT}/data/router_train/kaggle_bundle_v3/'\n"
     "DATA_DIR = '/tmp/router_data' if os.path.isdir('/kaggle/working') else os.environ.get('ROUTER_DATA_TMP', './router_data')\n"
     "os.makedirs(DATA_DIR, exist_ok=True)\n"
     "def fetch(name, sha):\n"
     "    path = os.path.join(DATA_DIR, name)\n"
     "    for attempt in range(3):\n"
     "        try:\n"
     "            urllib.request.urlretrieve(RAW + name, path); break\n"
     "        except Exception as e:\n"
     "            print('retry', name, repr(e)[:80]); time.sleep(5)\n"
     "    data = open(path, 'rb').read()\n"
     "    assert hashlib.sha1(b'blob %d\\0' % len(data) + data).hexdigest() == sha, f'{name} is not the expected version'\n"
     "    return path\n"
     "TRAIN_PATH = fetch('finetune_router.jsonl', '80e65d755380c47595906479b9ef4d21b10b220c')\n"
     "CAND_PATH = fetch('candidates.json', '75b57b65e9fa19dc6e6d9895fab15bb8c49f9308')\n"
     "EVAL_PATH = None                                           # training only: the evaluation runs in a separate notebook"),

    ("assert all(r['completion'] in set(CANDS) for r in train_all), 'a training answer is not one of the 142 candidates'\n",
     "assert all(r['completion'] in set(CANDS) for r in train_all), 'a training answer is not one of the 142 candidates'\n"
     "# Dạng 122 (Số phức D34) is removed from the thesis: left out of the training pairs and of the candidates\n"
     "REMOVED = {122}\n"
     "CANDS = [c for c in CANDS if int(re.match(r'Dạng (\\d+):', c).group(1)) not in REMOVED]\n"
     "CAND_NUM = [int(re.match(r'Dạng (\\d+):', c).group(1)) for c in CANDS]      # candidate index -> type number (122 is skipped)\n"
     "train_all = [r for r in train_all if r['completion'] in set(CANDS)]\n"
     "assert len(CANDS) == 141 and len(train_all) == 12690\n"),

    ("LOAD_DTYPE = torch.float32 if (HAS_CUDA and not BF16 and not USE_4BIT) else COMPUTE_DTYPE",
     "LOAD_DTYPE = COMPUTE_DTYPE                                 # Qwen3-4B: float32 weights (16 GB) do not fit a T4, so float16"),

    ("sc[r['id']] = dict(label=best[0] + 1, full=best[int(full.argmax())] + 1, top3=[t + 1 for t in best[:3]],",
     "sc[r['id']] = dict(label=CAND_NUM[best[0]], full=CAND_NUM[best[int(full.argmax())]], top3=[CAND_NUM[t] for t in best[:3]],"),

    ("print(f'label part of candidate {k + 1:3d}:", "print(f'label part of candidate {CAND_NUM[k]:3d}:"),
    ("print(f'full text of candidate {best[0] + 1:3d}:", "print(f'full text of candidate {CAND_NUM[best[0]]:3d}:"),
]

MD_NEW = """# Router: fine-tune Qwen3-4B (LoRA) để nhận ra dạng của một đề bài (chỉ huấn luyện)

Bản sao notebook huấn luyện Qwen3-0.6B (bản đạt 100%), giữ nguyên dữ liệu và mọi thiết lập huấn luyện. Chỉ khác:

1. `MODEL = Qwen/Qwen3-4B`.
2. Bỏ Dạng 122 (Số phức D34) khỏi dữ liệu huấn luyện và danh sách dạng: còn 141 dạng, 12690 cặp.
3. Trên T4 nạp trọng số float16 thay cho float32 (float32 của 4B chiếm khoảng 16 GB, bằng cả bộ nhớ T4).
4. `MAX_TRAIN_MINUTES = 680` (bản cũ 270): dùng gần hết 12 giờ của một phiên Kaggle.
5. Chỉ huấn luyện và lưu adapter; phần đánh giá chạy ở notebook riêng.
6. Dữ liệu huấn luyện tự tải từ GitHub (commit cố định, có kiểm tra mã băm): không cần gắn Dataset.

## Cách chạy

1. **Settings**: Accelerator = **GPU T4 x2** (notebook dùng 1 GPU, như lần chạy 0.6B); **Internet = On**.
2. Chạy thử: đặt `QUICK_TEST = True` ở ô cấu hình (đổi `'0'` thành `'1'` ở dòng `QUICK_TEST`), **Run All**. Dòng
   `step … s/step` cho tốc độ; chạy thử dùng 8 câu mỗi bước, chạy thật 32 câu mỗi bước.
3. Chạy thật: `QUICK_TEST = False`, **Save Version → Save & Run All (Commit)**.
4. Kết quả trong **Output**: `router_lora/` (adapter), `train_progress.log`, `router_ckpt/` (checkpoint).
   Nếu log có dòng `time limit reached`, huấn luyện chưa đủ số bước và adapter chưa phải bản cuối.
"""

DROP_FROM = "# ------------------------------------------------------------------ inference helpers"


def main():
    nb = json.load(open(SRC, encoding="utf-8"))
    before = ["".join(c["source"]) for c in nb["cells"]]
    after = list(before)
    for old, new in EDITS:
        hits = [i for i, s in enumerate(after) if old in s]
        assert len(hits) == 1 and after[hits[0]].count(old) == 1, old
        after[hits[0]] = after[hits[0]].replace(old, new)
    assert nb["cells"][0]["cell_type"] == "markdown"
    after[0] = MD_NEW
    for c, s in zip(nb["cells"], after):
        c["source"] = s.splitlines(keepends=True)
        if c["cell_type"] == "code":
            c["outputs"], c["execution_count"] = [], None
    # training only: the cells from the inference helpers on (scoring, evaluation, results, merge) are left out
    cut = next(i for i, s in enumerate(after) if s.startswith(DROP_FROM))
    print(f"cells left out (evaluation): {len(nb['cells']) - cut}")
    nb["cells"], before, after = nb["cells"][:cut], before[:cut], after[:cut]
    before[0] = after[0]
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    json.dump(nb, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for a, b in zip(before, after):
        for line in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0):
            if not line.startswith(("---", "+++")):
                print(line)
    print("written:", DST)


if __name__ == "__main__":
    main()
