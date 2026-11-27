# -*- coding: utf-8 -*-
"""Write the Kaggle notebook that evaluates the Qwen3-4B router (the published Qwen3-0.6B numbers are printed beside it).

python build_eval_4b_kaggle.py
Output: experiments/Router-Finetune-4B/KLTN_router_eval_Kaggle.ipynb
        experiments/Router-Finetune-4B/router_eval_cells.py   (the code cells as one script, for a local dry run)

The router is scored with the scoring of the 0.6B evaluation (finetune notebook): the probability of "Dạng N:" for every
candidate, then the probability of the whole answer "Dạng N: mô tả" for the 5 best; fp16 weights, adapter not merged.
The candidates are the 141 dạng without Dạng 122 (Số phức D34).
Sets: the test set (12860), the 93 real-world questions (pipeline layout), benchmark v2 (2070).
"""
import json
import os

from common import REPO

OUT_DIR = os.path.join(REPO, "experiments", "Router-Finetune-4B")
COMMIT = "c628e1d5ecaaf4d69d1553de61b6715d26a7fe5f"

MD = r'''# Đánh giá mô-đun xác định dạng: Qwen3-4B

Chấm **adapter Qwen3-4B** vừa huấn luyện, cùng cách chấm với lần đánh giá Qwen3-0.6B: xác suất của "Dạng N:" cho mọi ứng
viên, rồi xác suất của cả câu "Dạng N: mô tả" cho 5 ứng viên đứng đầu; trọng số float16. Mô hình chọn trong **141 dạng**
(đã bỏ Dạng 122). Số liệu đã công bố của Qwen3-0.6B được in kèm để so sánh.

| Tập | Số câu |
|---|---|
| Tập kiểm tra | 12860 (170 câu gốc) |
| Câu thực tế từ Internet | 93 (trình bày đề như pipeline) |
| Bộ dữ liệu phiên bản thứ 2 | 2070 (23 dạng Số phức) |

Mô hình, adapter và dữ liệu tự tải từ GitHub và Hugging Face (commit cố định, có kiểm tra mã băm): không cần gắn Dataset.

## Cách chạy

1. **Settings**: Accelerator = **GPU T4 x2** (mỗi GPU chấm một nửa số câu); **Internet = On**.
2. Chạy thử: đặt `QUICK_TEST = True` ở ô cấu hình, **Run All**: vài câu mỗi tập, in tốc độ và thời gian ước tính.
3. Chạy thật: `QUICK_TEST = False`, **Save Version → Save & Run All (Commit)**.
4. Kết quả trong **Output**, thư mục `results/`: `summary.json` (mọi số liệu, kèm số đã công bố của 0.6B), và cho mỗi mô hình
   `test_predictions.csv`, `realworld93_predictions.csv`, `benchmark_v2_predictions.csv`.
'''

CELLS = []

CELLS.append(r'''!pip uninstall -y -q torchao
!pip install -q -U transformers peft accelerate''')

CELLS.append(r'''# ================= Cấu hình =================
QUICK_TEST = False          # True: vài câu mỗi tập, chỉ để kiểm tra notebook chạy được
RUN_MODELS = ['qwen3_4b']   # ('qwen3_06b' is only for a local dry run on a small GPU)
SETS_TO_RUN = ['benchmark_v2']   # tập test và 93 câu đã có kết quả từ lần chạy trước; thêm 'test', 'realworld93' nếu muốn chấm lại

import os, sys, json, csv, re, time, hashlib, random, subprocess, threading, urllib.request
from collections import Counter, defaultdict
QUICK_TEST = os.environ.get('ROUTER_QUICK', str(int(QUICK_TEST))) == '1'
RUN_MODELS = os.environ.get('ROUTER_RUN_MODELS', ','.join(RUN_MODELS)).split(',')
SETS_TO_RUN = os.environ.get('ROUTER_SETS', ','.join(SETS_TO_RUN)).split(',')
WORK = '/kaggle/working' if os.path.isdir('/kaggle/working') else os.environ.get('ROUTER_OUT', './router_eval')
DATA = '/tmp/router_eval_data' if os.path.isdir('/kaggle/working') else os.path.join(WORK, 'data')
RES = os.path.join(WORK, 'results' + ('_quick' if QUICK_TEST else ''))
os.makedirs(DATA, exist_ok=True); os.makedirs(RES, exist_ok=True)
import torch
T_START = time.time()
MAX_HOURS = float(os.environ.get('ROUTER_MAX_HOURS', 11.0))   # a Kaggle session stops at 12 h: scoring stops cleanly after this many hours
N_GPU = max(1, torch.cuda.device_count())

# continue an earlier run: attach its Output as an input (Add Input -> Your Work -> Notebooks); its scored questions are copied
# here and are not scored again
import glob, shutil
if os.path.isdir('/kaggle/input'):
    for src in glob.glob('/kaggle/input/**/' + os.path.basename(RES) + '/*/shards', recursive=True):
        dst = os.path.join(RES, src.replace(chr(92), '/').split('/' + os.path.basename(RES) + '/', 1)[1])      # results/<model>/shards
        os.makedirs(dst, exist_ok=True)
        for fn in os.listdir(src):
            if not os.path.exists(os.path.join(dst, fn)):
                shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn)); print('copied from the earlier run:', fn)
print('GPUs:', N_GPU, [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], '| quick test:', QUICK_TEST, '| models:', RUN_MODELS)''')

CELLS.append(r'''# ------------------------------------------------------------------ download (fixed commit, checked by hash)
REPO = 'manhdungcr7/slm-highschool-math-tutoring'
COMMIT = '__COMMIT__'
RAW = f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/'
LFS = f'https://media.githubusercontent.com/media/{REPO}/{COMMIT}/'
FILES = {   # local path: (url, kind of hash, hash)
    'eval_set.jsonl': (RAW + 'data/router_train/kaggle_bundle_v3/eval_set.jsonl', 'git', 'a30dda736eccc1b809bb295eef130f259df5f36d'),
    'candidates.json': (RAW + 'data/router_train/kaggle_bundle_v3/candidates.json', 'git', '75b57b65e9fa19dc6e6d9895fab15bb8c49f9308'),
    'benchmark_v2.csv': (RAW + 'so_phuc/data/questions/benchmark_so_phuc_v2_23dang_2070cau.csv', 'git', 'f624e77751d1302c4a94ae32ec95a450d9ec4645'),
    'realworld_93.csv': (RAW + 'data/results/pipeline_realworld/questions/cau_hoi_thuc_te_93_cau.csv', 'git', 'ebefb7e289d05a90f3852fb95434c38d14a0cd01'),
    # published results of the 0.6B router (142 candidates), for comparison, and to take the same free-generation subset
    'pub06b_test.csv': (RAW + 'models/router_lora/training_run_v3/router_eval_predictions.csv', 'git', '3ae94fd5bd90084585cb56b961184a9ea8c37099'),
    'pub06b_realworld93.csv': (RAW + 'data/results/pipeline_realworld/kaggle_run_20261016/router_predictions.csv', 'git', '9cfef8084dc5b34ffa079d7de77bb0a569191723'),
    'pub06b_benchmark_v2.csv': (RAW + 'experiments/Router-Benchmark-v2/results/router_v2_ket_qua_2070_cau.csv', 'git', 'cea60c8c45dc67e1706ffa6476392c00268cf78c'),
    # adapters
    'lora_06b/adapter_config.json': (RAW + 'models/router_lora/adapter_config.json', 'git', 'b559039e16eb97a4e85e5f99c84de7057ec97e61'),
    'lora_06b/adapter_model.safetensors': (RAW + 'models/router_lora/adapter_model.safetensors', 'git', '7ca685f36307a552836cc5b23f8b991bfd108180'),
    'lora_4b/adapter_config.json': (RAW + 'models/router_lora_qwen3_4b/adapter_config.json', 'git', 'ca56bd7330e68fcd09bce5537620412f3664c9a5'),
    'lora_4b/adapter_model.safetensors': (LFS + 'models/router_lora_qwen3_4b/adapter_model.safetensors', 'sha256', 'd1bf4823158672dfc99d61f3544586074b80d8d75b3e603f47696cb14ac29c6e'),
}

def file_hash(path, kind):
    data = open(path, 'rb').read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() if kind == 'git' else hashlib.sha256(data).hexdigest()

for name, (url, kind, h) in FILES.items():
    if (name.startswith('lora_06b/') and 'qwen3_06b' not in RUN_MODELS) or (name.startswith('lora_4b/') and 'qwen3_4b' not in RUN_MODELS):
        continue
    path = os.path.join(DATA, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not (os.path.exists(path) and file_hash(path, kind) == h):
        for attempt in range(3):
            try:
                urllib.request.urlretrieve(url, path); break
            except Exception as e:
                print('retry', name, repr(e)[:80]); time.sleep(5)
    assert file_hash(path, kind) == h, f'{name} is not the expected version'
    print(f'{os.path.getsize(path):>11,}  {name}')

MODELS = {'qwen3_4b': ('Qwen/Qwen3-4B', os.path.join(DATA, 'lora_4b')),
          'qwen3_06b': ('Qwen/Qwen3-0.6B', os.path.join(DATA, 'lora_06b'))}''')

CELLS.append(r'''# ------------------------------------------------------------------ the questions of every set
import pandas as pd

def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]

PROMPT = ('Hãy xác định dạng bài của đề bài sau. Chỉ trả lời đúng một dòng theo mẫu '
          '"Dạng N: mô tả dạng bài", trong đó N là số thứ tự của dạng.\n\nĐề bài:\n')
REMOVED = {122}
CANDS = [c for c in json.load(open(os.path.join(DATA, 'candidates.json'), encoding='utf-8'))
         if int(re.match(r'Dạng (\d+):', c).group(1)) not in REMOVED]
assert len(CANDS) == 141

def to_training_layout(q):
    """The step the pipeline applies before the router: the stem, a blank line, one option per line (text unchanged)."""
    parts = re.split(r'(?:^|\n|\s)(?=[A-D]\.\s)', q.strip())
    stem, opts = parts[0].strip(), [p.strip() for p in parts[1:]]
    if len(opts) != 4:
        return q.strip()
    fixed = []
    for o in opts:
        o = o.rstrip(';').rstrip()
        fixed.append(o if o.endswith('.') else o + '.')
    return stem + '\n\n' + '\n'.join(fixed)

test = read_jsonl(os.path.join(DATA, 'eval_set.jsonl'))
assert len(test) == 12860 and not {r['so_dang'] for r in test} & REMOVED
rw = pd.read_csv(os.path.join(DATA, 'realworld_93.csv'), encoding='utf-8-sig')
assert len(rw) == 93
bench = list(csv.DictReader(open(os.path.join(DATA, 'benchmark_v2.csv'), encoding='utf-8-sig')))
assert len(bench) == 2070
label_of = {}
for e in test:
    label_of.setdefault(e['prompt'], set()).add(int(e['so_dang']))
v2_label = {}
for r in bench:
    lab = label_of.get(PROMPT + r['de_bai_v1'])                    # the label of the v1 wording of the same question
    assert lab and len(lab) == 1, r['stt']
    v2_label[r['stt']] = next(iter(lab))
pub_test = pd.read_csv(os.path.join(DATA, 'pub06b_test.csv'), encoding='utf-8-sig')

SETS = {
    'test': [dict(key=str(r['id']), prompt=r['prompt']) for r in test],
    'realworld93': [dict(key=r.id, prompt=PROMPT + to_training_layout(r.question_markdown_latex)) for r in rw.itertuples()],
    'benchmark_v2': [dict(key=r['stt'], prompt=PROMPT + r['de_bai']) for r in bench],
}
SETS = {k: v for k, v in SETS.items() if k in SETS_TO_RUN}
if QUICK_TEST:
    SETS = {k: v[::max(1, len(v) // 6)][:6] for k, v in SETS.items()}
json.dump(dict(cands=CANDS, sets=SETS, models=MODELS), open(os.path.join(DATA, 'jobs.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print({k: len(v) for k, v in SETS.items()})''')

CELLS.append(r'''# ------------------------------------------------------------------ the scoring worker (one process per GPU)
WORKER = r"""
import os, sys, json, csv, copy, time
MODEL_KEY, SHARD, NSH, JOBS, OUTD = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
DEADLINE = float(os.environ['ROUTER_DEADLINE'])           # epoch seconds: stop cleanly before the session ends
def time_up():
    if time.time() > DEADLINE:
        open(os.path.join(OUTD, f'time_up_shard{SHARD}'), 'w').write('1')
        print(f'[{MODEL_KEY} gpu{SHARD}] time budget reached: stopping (the scored questions are saved)', flush=True)
        return True
    return False
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
try:
    import peft.import_utils as _pi
    _pi.is_torchao_available = lambda: False
except Exception:
    pass
from peft import PeftModel
J = json.load(open(JOBS, encoding='utf-8'))
BASE, ADAPTER = J['models'][MODEL_KEY]
CANDS = J['cands']
CAND_NUM = [int(c.split(':')[0].split()[1]) for c in CANDS]
EOS = '<|im_end|>'
tok = AutoTokenizer.from_pretrained(BASE)
try:
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float16, device_map={'': 0})
except TypeError:
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float16, device_map={'': 0})
model = PeftModel.from_pretrained(model, ADAPTER)
model.half(); model.eval()
model.config.use_cache = True
DEV = next(model.parameters()).device
CAND_IDS = [tok(c + EOS, add_special_tokens=False).input_ids for c in CANDS]
COLON = tok(':', add_special_tokens=False).input_ids[0]
LABEL_LEN = [ids.index(COLON) + 1 for ids in CAND_IDS]
NO_CACHE = False

def prompt_text(user):
    return tok.apply_chat_template([{'role': 'user', 'content': user}], tokenize=False, add_generation_prompt=True, enable_thinking=False)

@torch.no_grad()
def prompt_state(user):
    p_ids = tok(prompt_text(user), add_special_tokens=False, return_tensors='pt').input_ids.to(DEV)
    out = model(input_ids=p_ids, use_cache=True)
    return out.past_key_values, p_ids.shape[1], torch.log_softmax(out.logits[0, -1].float(), -1), p_ids

@torch.no_grad()
def sum_logprob(state, token_lists, chunk=71):
    global NO_CACHE
    cache, L, first, p_ids = state
    res = torch.zeros(len(token_lists))
    for s in range(0, len(token_lists), chunk):
        part = token_lists[s:s + chunk]; n = len(part); m = max(len(x) for x in part)
        ids = torch.full((n, m), tok.pad_token_id, dtype=torch.long); msk = torch.zeros((n, m), dtype=torch.long)
        for i, x in enumerate(part):
            ids[i, :len(x)] = torch.tensor(x); msk[i, :len(x)] = 1
        if not NO_CACHE:
            try:
                c = copy.deepcopy(cache); c.batch_repeat_interleave(n)
                attn = torch.cat([torch.ones((n, L), dtype=torch.long), msk], 1).to(DEV)
                o = model(input_ids=ids.to(DEV), attention_mask=attn, past_key_values=c, use_cache=True)
                logp = torch.log_softmax(o.logits.float(), -1)
                tok_lp = logp[:, :-1].gather(2, ids[:, 1:].to(DEV).unsqueeze(-1)).squeeze(-1) * msk[:, 1:].to(DEV)
                tok_lp = torch.cat([first[ids[:, 0].to(DEV)].unsqueeze(1), tok_lp], 1)
                del o, logp, c
            except Exception as e:
                print('cache reuse failed, scoring without the cache:', repr(e)[:100], flush=True); NO_CACHE = True
        if NO_CACHE:
            full = torch.cat([p_ids.repeat(n, 1), ids.to(DEV)], 1)
            attn = torch.cat([torch.ones((n, L), dtype=torch.long), msk], 1).to(DEV)
            logp = torch.log_softmax(model(input_ids=full, attention_mask=attn).logits[:, L - 1:-1].float(), -1)
            tok_lp = logp.gather(2, ids.to(DEV).unsqueeze(-1)).squeeze(-1) * msk.to(DEV)
            del logp
        cum = tok_lp.cumsum(1)
        for i in range(n):
            res[s + i] = cum[i, len(part[i]) - 1].item()
    return res

@torch.no_grad()
def predict(user, top=5):
    state = prompt_state(user)
    label = sum_logprob(state, [ids[:LABEL_LEN[i]] for i, ids in enumerate(CAND_IDS)])
    best = torch.topk(label, top).indices.tolist()
    full = sum_logprob(state, [CAND_IDS[i] for i in best], chunk=top)
    order = [best[j] for j in torch.argsort(full, descending=True).tolist()]
    return dict(pred=CAND_NUM[order[0]], pred_label=CAND_NUM[best[0]],
                top3_label=' '.join(str(CAND_NUM[i]) for i in best[:3]),
                top3_full=' '.join(str(CAND_NUM[i]) for i in order[:3]),
                conf=round(float(torch.softmax(label, 0).max()), 6))

def done_keys(path):
    if not os.path.exists(path):
        return set()
    return {r['key'] for r in csv.DictReader(open(path, encoding='utf-8-sig'))}

for name, items in J['sets'].items():
    items = [it for i, it in enumerate(items) if i % NSH == SHARD]
    path = os.path.join(OUTD, f'{name}_shard{SHARD}.csv')
    done = done_keys(path)
    todo = [it for it in items if it['key'] not in done]
    new = not os.path.exists(path)
    f = open(path, 'a', encoding='utf-8-sig', newline='')
    w = csv.DictWriter(f, fieldnames=['key', 'pred', 'pred_label', 'top3_label', 'top3_full', 'conf'])
    if new:
        w.writeheader()
    t0 = time.time()
    for i, it in enumerate(todo):
        if time_up():
            f.close(); sys.exit(0)
        w.writerow(dict(key=it['key'], **predict(it['prompt'])))
        if i % 25 == 24 or i == len(todo) - 1:
            f.flush()
            el = time.time() - t0
            if i == 24 or i % 500 == 499 or i == len(todo) - 1:
                print(f'[{MODEL_KEY} gpu{SHARD}] {name}: {i + 1}/{len(todo)} | {el / (i + 1):.2f} s/question | about {el / (i + 1) * (len(todo) - i - 1) / 60:.0f} min left', flush=True)
    f.close()

print(f'[{MODEL_KEY} gpu{SHARD}] done', flush=True)
"""
WORKER_PATH = os.path.join(DATA, 'eval_worker.py')
open(WORKER_PATH, 'w', encoding='utf-8').write(WORKER)

def run_model(key):
    outd = os.path.join(RES, key, 'shards')
    os.makedirs(outd, exist_ok=True)
    for fn in os.listdir(outd):
        if fn.startswith('time_up_'):
            os.remove(os.path.join(outd, fn))
    procs = []
    for g in range(N_GPU):
        p = subprocess.Popen([sys.executable, WORKER_PATH, key, str(g), str(N_GPU), os.path.join(DATA, 'jobs.json'), outd],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g), PYTHONIOENCODING='utf-8', ROUTER_DEADLINE=str(T_START + MAX_HOURS * 3600)))
        procs.append(p)
    logs = [[] for _ in procs]
    def pump(i, p):
        for line in p.stdout:
            logs[i].append(line)
            if line.startswith('[') or 'Error' in line or 'Traceback' in line:
                print(line, end='', flush=True)
    threads = [threading.Thread(target=pump, args=(i, p)) for i, p in enumerate(procs)]
    for t in threads: t.start()
    for t in threads: t.join()
    for i, p in enumerate(procs):
        if p.wait() != 0:
            print(''.join(logs[i][-40:]))
            raise RuntimeError(f'{key}: worker on GPU {i} failed')''')

CELLS.append(r'''# ------------------------------------------------------------------ run (both GPUs, one model after the other)
T0 = time.time()
for key in RUN_MODELS:
    t = time.time()
    run_model(key)
    print(f'{key}: {(time.time() - t) / 60:.1f} min', flush=True)
print(f'total: {(time.time() - T0) / 60:.1f} min')
INCOMPLETE = any(fn.startswith('time_up_') for k in RUN_MODELS for fn in os.listdir(os.path.join(RES, k, 'shards')))
if INCOMPLETE:
    print('The time budget ended before everything was scored. Save this version, then Add Input -> Your Work -> Notebooks -> '
          'the Output of this version, and Save & Run All again: only the questions not scored yet are done.')''')

CELLS.append(r'''# ------------------------------------------------------------------ results (only when every question is scored)
def parse_type(text):
    m = re.search(r'D[ạa]ng\s*(\d+)', str(text))
    return int(m.group(1)) if m else None

def merged(key, name):
    parts = [pd.read_csv(os.path.join(RES, key, 'shards', f'{name}_shard{g}.csv'), encoding='utf-8-sig', dtype={'key': str})
             for g in range(N_GPU)]
    df = pd.concat(parts, ignore_index=True)
    assert df.key.is_unique
    return df

def acc(x):
    return round(float(x.astype(bool).mean()), 6) if len(x) else None

SUMMARY = {}
for key in RUN_MODELS:
    S = SUMMARY[key] = {'base_model': MODELS[key][0], 'n_candidates': len(CANDS)}
    if 'test' in SETS:
        # --- test set, in the columns of the 0.6B evaluation (router_eval_predictions.csv)
        sc = merged(key, 'test').set_index('key')
        rows = []
        for r in test:
            k = str(r['id'])
            if k not in sc.index:
                continue
            c = sc.loc[k]
            d = dict(id=r['id'], so_dang=r['so_dang'], ma_cu=r['ma_cu'], nguon=r['nguon'], chu_de=r['chu_de'],
                     score_full_pred=int(c.pred), score_full_ok=int(c.pred) == r['so_dang'],
                     score_label_pred=int(c.pred_label), score_label_ok=int(c.pred_label) == r['so_dang'],
                     top3_ok=str(r['so_dang']) in str(c.top3_label).split(), conf=c.conf)
            rows.append(d)
        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(RES, key, 'test_predictions.csv'), index=False, encoding='utf-8-sig')
        T = S['test'] = {}
        for name, fr in (('all', df), ('source', df[df.nguon == 'Câu gốc']), ('variants', df[df.nguon != 'Câu gốc']),
                         ('mu_logarit', df[df.chu_de == 'Mũ-Logarit']), ('so_phuc', df[df.chu_de == 'Số phức'])):
            T[f'n_{name}'] = len(fr)
            T[f'correct_{name}'] = int(fr.score_full_ok.sum())
            T[f'score_full_text_{name}'] = acc(fr.score_full_ok)
            T[f'score_label_only_{name}'] = acc(fr.score_label_ok)
            T[f'score_top3_{name}'] = acc(fr.top3_ok)
        for t in (0.5, 0.8, 0.95):
            hi = df[df.conf >= t]
            T[f'share_with_confidence_ge_{t}'] = round(len(hi) / max(1, len(df)), 6)
            T[f'accuracy_when_confidence_ge_{t}'] = acc(hi.score_full_ok)
        wrong = df[~df.score_full_ok]
        T['confusions'] = [dict(dang_dung=a, mo_hinh=b, so_cau=n) for (a, b), n in Counter(zip(wrong.so_dang, wrong.score_full_pred)).most_common()]
    if 'realworld93' in SETS:
        # --- 93 real-world questions, in the columns of the pipeline router (router_predictions.csv)
        p93 = merged(key, 'realworld93').set_index('key')
        rows = []
        for r in rw.itertuples():
            if r.id not in p93.index:
                continue
            c = p93.loc[r.id]
            rows.append(dict(id=r.id, topic=r.topic, dang_dung=int(r.dang_dung), du_doan_dang=int(c.pred), do_tin_cay=c.conf,
                             top3='; '.join(str(c.top3_full).split()), dung=int(c.pred) == int(r.dang_dung)))
        d93 = pd.DataFrame(rows)
        d93.to_csv(os.path.join(RES, key, 'realworld93_predictions.csv'), index=False, encoding='utf-8-sig')
        S['realworld93'] = dict(n=len(d93), correct=int(d93.dung.sum()), accuracy=acc(d93.dung),
                                by_topic={t: f'{int(g.dung.sum())}/{len(g)}' for t, g in d93.groupby('topic')})
    if 'benchmark_v2' in SETS:
        # --- benchmark v2, in the columns of the v2 evaluation (router_v2_ket_qua_2070_cau.csv)
        pv2 = merged(key, 'benchmark_v2').set_index('key')
        rows = []
        for r in bench:
            if r['stt'] not in pv2.index:
                continue
            c = pv2.loc[r['stt']]
            lab = v2_label[r['stt']]
            rows.append(dict(stt=int(r['stt']), ma_dang=r['ma_dang_bai_bao'], bien_the=int(r['bien_the']), so_dang=lab,
                             pred_v2=int(c.pred), pred_buoc1_v2=int(c.pred_label), top3_v2=c.top3_full, conf_v2=c.conf,
                             dung_v2=int(c.pred) == lab))
        dv2 = pd.DataFrame(rows)
        dv2.to_csv(os.path.join(RES, key, 'benchmark_v2_predictions.csv'), index=False, encoding='utf-8-sig')
        S['benchmark_v2'] = dict(n=len(dv2), correct=int(dv2.dung_v2.sum()), accuracy=acc(dv2.dung_v2),
                                 first_stage_correct=int((dv2.pred_buoc1_v2 == dv2.so_dang).sum()),
                                 by_type={k: f'{int(g.dung_v2.sum())}/{len(g)}' for k, g in dv2.groupby('ma_dang')})

# the published numbers of the 0.6B router (142 candidates), for comparison
pub93 = pd.read_csv(os.path.join(DATA, 'pub06b_realworld93.csv'), encoding='utf-8-sig').set_index('id')
pubv2 = pd.read_csv(os.path.join(DATA, 'pub06b_benchmark_v2.csv'), encoding='utf-8-sig')
SUMMARY['published_qwen3_06b_142_candidates'] = dict(
    test=f"{int(pub_test.score_full_ok.sum())}/{len(pub_test)}",
    realworld93=f"{int(sum(pub93.loc[r.id, 'du_doan_dang'] == int(r.dang_dung) for r in rw.itertuples()))}/93",
    benchmark_v2=f"{int(pubv2.dung_v2.sum())}/{len(pubv2)}")
SUMMARY['settings'] = dict(quick_test=QUICK_TEST, gpus=N_GPU, commit=COMMIT, weights='float16, adapter not merged',
                           scoring='label "Dạng N:" for all candidates, whole answer for the 5 best', removed_types=sorted(REMOVED),
                           versions=dict(torch=torch.__version__, transformers=__import__('transformers').__version__, peft=__import__('peft').__version__))
json.dump(SUMMARY, open(os.path.join(RES, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(f"{'':28s}" + ''.join(f'{k:>16s}' for k in RUN_MODELS) + f"{'0.6B published':>18s}")
P = SUMMARY['published_qwen3_06b_142_candidates']
line = lambda label, f, pub: print(f'{label:28s}' + ''.join(f'{f(SUMMARY[k]):>16s}' for k in RUN_MODELS) + f'{pub:>18s}')
if 'test' in SETS:
    line('test set', lambda s: f"{s['test']['correct_all']}/{s['test']['n_all']}", P['test'])
    line('  source questions', lambda s: f"{s['test']['correct_source']}/{s['test']['n_source']}", '')
if 'realworld93' in SETS:
    line('93 real-world', lambda s: f"{s['realworld93']['correct']}/{s['realworld93']['n']}", P['realworld93'])
if 'benchmark_v2' in SETS:
    line('benchmark v2', lambda s: f"{s['benchmark_v2']['correct']}/{s['benchmark_v2']['n']}", P['benchmark_v2'])
    print('\nbenchmark v2 by type (0.6B published in brackets):')
    pub_by = {k: f"{int(g.dung_v2.sum())}/{len(g)}" for k, g in pubv2.groupby('ma_dang')}
    for t in sorted(SUMMARY[RUN_MODELS[0]]['benchmark_v2']['by_type']):
        print(f'  {t}: ' + ' | '.join(f"{k} {SUMMARY[k]['benchmark_v2']['by_type'].get(t, '-')}" for k in RUN_MODELS) + f'  ({pub_by.get(t, "-")})')
print('\nresults in', RES)''')


def build():
    cells = [dict(cell_type="markdown", metadata={}, source=MD.strip().splitlines(keepends=True))]
    code = [c.replace("__COMMIT__", COMMIT).strip() for c in CELLS]
    # the results cell runs only when every question is scored (otherwise the run is continued in the next session)
    i = next(i for i, c in enumerate(code) if c.startswith("# ------------------------------------------------------------------ results"))
    body = "\n".join(("    " + l) if l.strip() else "" for l in code[i].splitlines())
    code[i] = "if INCOMPLETE:\n    print('not every question is scored yet: no summary in this session')\nelse:\n" + body
    code = [c + "\n" for c in code]
    for c in code:
        cells.append(dict(cell_type="code", metadata={}, execution_count=None, outputs=[], source=c.splitlines(keepends=True)))
    nb = dict(cells=cells, nbformat=4, nbformat_minor=5,
              metadata=dict(kernelspec=dict(name="python3", display_name="Python 3", language="python"),
                            language_info=dict(name="python")))
    p = os.path.join(OUT_DIR, "KLTN_router_eval_Kaggle.ipynb")
    json.dump(nb, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # local dry run: the pip cell is left out
    open(os.path.join(OUT_DIR, "router_eval_cells.py"), "w", encoding="utf-8").write("\n\n".join(code[1:]))
    print("written:", p)


if __name__ == "__main__":
    build()
