# -*- coding: utf-8 -*-
"""Cells of the pipeline notebook (used by build_pipeline_notebook.py)."""

MD_INTRO = r'''
# Chatbot Gia sư AI: chạy toàn bộ pipeline trên 100 câu thực tế

**Đề bài → bộ phân dạng (Qwen3-0.6B + LoRA) → dạng dự đoán → prompt của dạng đó + đề bài → Qwen3-4B (zero-shot, hoặc ReAct + Calculator) → đáp án.**

- Bộ phân dạng chấm xác suất 142 chuỗi "Dạng N: mô tả" và chọn dạng có xác suất cao nhất, giống hệt notebook huấn luyện.
- Cách giải và prompt được chọn **chỉ theo dạng dự đoán**. Cột `dang_dung` của bộ câu hỏi chỉ dùng ở bước đánh giá cuối.
- Mỗi dạng chạy đúng mã của notebook thử nghiệm cuối cùng của dạng đó (prompt, Calculator, vòng lặp ReAct, tham số sinh, cách trích đáp án), được chép nguyên văn vào `pipeline_units.json`. Chỉ bỏ các dòng nạp 90 câu và tạo tokenizer/LLM của notebook gốc; pipeline đưa vào các câu đã được định tuyến, một tokenizer và một engine vLLM dùng chung.
  - 56 dạng ReAct + Calculator (32 Mũ–Logarit, 24 Số phức): `temperature=0.3, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2`, tối đa 9216 token sinh, Calculator SymPy của chính notebook đó.
  - Mũ–Logarit zero-shot (56 dạng): `temperature=0.6, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2`, 9216 token, bật thinking.
  - Số phức zero-shot (30 dạng): `temperature=0.6, top_p=0.95, top_k=20, seed=42`, không có presence penalty, 9216 token, bật thinking.
- `dap_an_letter` được truyền vào mã gốc chỉ vì mã đó tự chấm điểm khi lưu CSV; đáp án không nằm trong prompt.

**Trước khi chạy:** gắn Dataset chứa thư mục `pipeline_bundle` (gồm `pipeline_units.json`, `cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv`, `router_candidates.json`, `router_lora/`), bật GPU T4 x2 và Internet, rồi **Save & Run All**. Kết quả nằm ở `/kaggle/working/pipeline/` và `pipeline_ket_qua.zip`.
'''

PIP = r'''
# Same order as the router training notebook, which ran on Kaggle without errors: torchao is removed BEFORE the installs.
# Kaggle ships torchao 0.10.0 and PEFT refuses it when it injects LoRA layers (ImportError: incompatible torchao).
!pip uninstall -y -q torchao
!pip install -q -U vllm
!pip uninstall -y -q torchcodec torchaudio
!pip install -q -U peft
# The installs above may bring torchao back as a dependency, so remove it once more.
!pip uninstall -y -q torchao
import importlib.util
assert importlib.util.find_spec('torchao') is None, 'torchao is still installed; PEFT will fail to load the router adapter'
import peft, transformers, torch, vllm
print('vllm', vllm.__version__, '| transformers', transformers.__version__, '| peft', peft.__version__, '| torch', torch.__version__)
'''

CONFIG = r'''
import os, re, sys, json, glob, time, types, shutil, hashlib, subprocess
import pandas as pd

_found = glob.glob('/kaggle/input/**/pipeline_units.json', recursive=True)
BUNDLE_DIR = os.environ.get('PIPELINE_BUNDLE_DIR') or (os.path.dirname(_found[0]) if _found else None)
assert BUNDLE_DIR, 'pipeline_units.json not found under /kaggle/input. Add the pipeline_bundle dataset first.'
WORK_DIR = os.environ.get('PIPELINE_WORK_DIR', '/kaggle/working/pipeline')
RAW_DIR = os.path.join(WORK_DIR, 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

QUESTIONS_CSV = os.path.join(BUNDLE_DIR, 'cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv')
ROUTER_ADAPTER = os.path.join(BUNDLE_DIR, 'router_lora')
ROUTER_CANDIDATES = os.path.join(BUNDLE_DIR, 'router_candidates.json')
ROUTER_OUT = os.path.join(WORK_DIR, 'router_predictions.csv')

PIPE = json.load(open(os.path.join(BUNDLE_DIR, 'pipeline_units.json'), encoding='utf-8'))
TYPE_BY_NO = {t['so_dang']: t for t in PIPE['types']}
UNITS = PIPE['units']
questions = pd.read_csv(QUESTIONS_CSV, encoding='utf-8-sig', dtype=str)
print(f"{len(questions)} questions | {len(TYPE_BY_NO)} dạng | {len(UNITS)} code units")
print(questions['topic'].value_counts().to_string())
'''

MD_ROUTER = r'''
## Bước 1. Phân dạng

Bộ phân dạng chạy trong một tiến trình con để giải phóng GPU trước khi nạp Qwen3-4B. Đề được đưa về đúng bố cục của dữ liệu huấn luyện (thân đề, một dòng trống, mỗi phương án một dòng); nội dung đề không đổi.
'''

ROUTER = r'''
ROUTER_PY = r"""
import copy, csv, json, re, sys, time
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

Q, ADAPTER, CAND, OUT = sys.argv[1:5]
PROMPT = ("Hãy xác định dạng bài của đề bài sau. Chỉ trả lời đúng một dòng theo mẫu "
          "\"Dạng N: mô tả dạng bài\", trong đó N là số thứ tự của dạng.\n\nĐề bài:\n")
EOS = "<|im_end|>"
CHUNK = 24
CANDS = json.load(open(CAND, encoding="utf-8"))
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float16, device_map={"": 0})
model = PeftModel.from_pretrained(model, ADAPTER).merge_and_unload().eval()
DEV = next(model.parameters()).device
CAND_IDS = [tok(c + EOS, add_special_tokens=False).input_ids for c in CANDS]
COLON = tok(":", add_special_tokens=False).input_ids[0]
LABEL_LEN = [ids.index(COLON) + 1 for ids in CAND_IDS]


def to_training_layout(q):
    parts = re.split(r"(?:^|\n|\s)(?=[A-D]\.\s)", q.strip())
    stem, opts = parts[0].strip(), [p.strip() for p in parts[1:]]
    if len(opts) != 4:
        return q.strip()
    fixed = []
    for o in opts:
        o = o.rstrip(";").rstrip()
        fixed.append(o if o.endswith(".") else o + ".")
    return stem + "\n\n" + "\n".join(fixed)


@torch.no_grad()
def prompt_state(user):
    text = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)
    p_ids = tok(text, add_special_tokens=False, return_tensors="pt").input_ids.to(DEV)
    out = model(input_ids=p_ids, use_cache=True)
    return out.past_key_values, p_ids.shape[1], torch.log_softmax(out.logits[0, -1].float(), -1)


@torch.no_grad()
def sum_logprob(state, token_lists, chunk):
    cache, L, first = state
    res = torch.zeros(len(token_lists))
    for s in range(0, len(token_lists), chunk):
        part = token_lists[s:s + chunk]
        n, m = len(part), max(len(x) for x in part)
        ids = torch.full((n, m), tok.pad_token_id, dtype=torch.long)
        msk = torch.zeros((n, m), dtype=torch.long)
        for i, x in enumerate(part):
            ids[i, :len(x)] = torch.tensor(x)
            msk[i, :len(x)] = 1
        c = copy.deepcopy(cache)
        c.batch_repeat_interleave(n)
        attn = torch.cat([torch.ones((n, L), dtype=torch.long), msk], 1).to(DEV)
        o = model(input_ids=ids.to(DEV), attention_mask=attn, past_key_values=c, use_cache=True)
        logp = torch.log_softmax(o.logits.float(), -1)
        tgt = ids[:, 1:].to(DEV)
        tok_lp = logp[:, :-1].gather(2, tgt.unsqueeze(-1)).squeeze(-1) * msk[:, 1:].to(DEV)
        tok_lp = torch.cat([first[ids[:, 0].to(DEV)].unsqueeze(1), tok_lp], 1)
        cum = tok_lp.cumsum(1)
        for i in range(n):
            res[s + i] = cum[i, len(part[i]) - 1].item()
    return res


rows = list(csv.DictReader(open(Q, encoding="utf-8-sig", newline="")))
out_rows, t0 = [], time.time()
for i, r in enumerate(rows):
    state = prompt_state(PROMPT + to_training_layout(r["question_markdown_latex"]))
    label = sum_logprob(state, [ids[:LABEL_LEN[k]] for k, ids in enumerate(CAND_IDS)], CHUNK)
    best = torch.topk(label, 5).indices.tolist()
    full = sum_logprob(state, [CAND_IDS[k] for k in best], 5)
    order = [best[j] for j in torch.argsort(full, descending=True).tolist()]
    out_rows.append(dict(id=r["id"], du_doan_dang=order[0] + 1, do_tin_cay=round(float(torch.softmax(label, 0).max()), 4),
                         top3="; ".join(str(k + 1) for k in order[:3])))
    if i % 10 == 0 or i == len(rows) - 1:
        print(f"router {i + 1}/{len(rows)} ({time.time() - t0:.0f}s)", flush=True)
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
    w.writeheader()
    w.writerows(out_rows)
"""
router_path = os.path.join(WORK_DIR, 'router_run.py')
open(router_path, 'w', encoding='utf-8').write(ROUTER_PY)
proc = subprocess.Popen([sys.executable, router_path, QUESTIONS_CSV, ROUTER_ADAPTER, ROUTER_CANDIDATES, ROUTER_OUT],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                        env=dict(os.environ, CUDA_VISIBLE_DEVICES='0'))
for line in proc.stdout:
    print(line, end='')
assert proc.wait() == 0, 'router failed (see the log above)'
'''

PLAN = r'''
def to_training_layout(q):
    """Same layout as the experiment data: the stem, a blank line, then one option per line (text unchanged)."""
    parts = re.split(r"(?:^|\n|\s)(?=[A-D]\.\s)", q.strip())
    stem, opts = parts[0].strip(), [p.strip() for p in parts[1:]]
    if len(opts) != 4:
        return q.strip()
    fixed = []
    for o in opts:
        o = o.rstrip(";").rstrip()
        fixed.append(o if o.endswith(".") else o + ".")
    return stem + "\n\n" + "\n".join(fixed)


pred = pd.read_csv(ROUTER_OUT, encoding='utf-8-sig', dtype={'id': str})
qs = questions.merge(pred, on='id', how='left', validate='one_to_one')
assert qs['du_doan_dang'].notna().all()
plan_rows = []
for i, r in qs.iterrows():
    t = TYPE_BY_NO[int(r['du_doan_dang'])]          # the prompt is chosen from the PREDICTED dạng only
    plan_rows.append(dict(STT=i + 1, id=r['id'], topic=r['topic'],
                          dang_du_doan=int(r['du_doan_dang']), do_tin_cay=float(r['do_tin_cay']), top3=r['top3'],
                          chu_de_du_doan=t['chu_de'], ma_du_lieu=t['ma_du_lieu'], cach_giai=t['cach_giai'],
                          unit=t['unit'], de_bai_mcq=to_training_layout(r['question_markdown_latex']),
                          dap_an_dung=r['answer_letter'], dang_dung=int(r['dang_dung'])))
plan = pd.DataFrame(plan_rows)
plan.drop(columns=['de_bai_mcq']).to_csv(os.path.join(WORK_DIR, 'ke_hoach_dinh_tuyen.csv'), index=False, encoding='utf-8-sig')
print(plan.groupby(['chu_de_du_doan', 'cach_giai']).size().to_string())
print('Code units used:', plan['unit'].nunique(), sorted(plan['unit'].unique()))
'''

MD_SETUP = r'''
## Bước 2. Nạp mã của từng dạng, rồi nạp Qwen3-4B

Mã của mỗi notebook gốc chạy trong một module riêng (mỗi notebook có Calculator, vòng lặp và hằng số riêng nên không được trộn lẫn). Phần cấu hình và Calculator của các notebook Số phức tạo tiến trình con giới hạn thời gian (`fork`), nên phải chạy **trước** khi CUDA khởi tạo, giống thứ tự trong notebook gốc.
'''

SETUP = r'''
MODS = {}


def run_code(mod, code):
    exec(compile(code, f'<{mod.__name__}>', 'exec'), mod.__dict__)


def new_module(unit):
    # A real module in sys.modules: functions sent to the Calculator's subprocess pool are pickled by module name.
    mod = types.ModuleType('unit_' + unit)
    sys.modules[mod.__name__] = mod
    return mod


needed = sorted(plan['unit'].unique())
for unit in needed:
    u = UNITS[unit]
    mod = new_module(unit)
    run_code(mod, u['setup'])
    if u['kind'] in ('ml_group', 'ml_single', 'sp_single', 'ml_zeroshot'):
        run_code(mod, u['prompt'])          # only string constants
    MODS[unit] = mod
    print(f"{unit:10s} {u['kind']:12s} <- {u['source']}")


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


# The prompts now in memory are the ones of the experiments (same md5 as recorded from the original notebooks).
for unit in needed:
    u, mod = UNITS[unit], MODS[unit]
    if u['kind'] == 'ml_group':
        for ma in sorted(set(plan.loc[plan.unit == unit, 'ma_du_lieu'])):
            assert md5(mod.TYPE_PROMPTS[ma]['template']) == u['prompt_md5'][ma], (unit, ma)
    elif u['kind'] in ('ml_single', 'sp_single'):
        assert md5(mod.PROMPT_TEMPLATE) == list(u['prompt_md5'].values())[0], unit
    elif u['kind'] == 'ml_zeroshot':
        assert md5(mod.PROMPT_TEMPLATE) == u['prompt_md5'], unit
print('Prompts checked.')
'''

ENGINE = r'''
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

MODEL, SEED = 'Qwen/Qwen3-4B', 42
tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)


def routed(unit, ma=None):
    sub = plan[plan.unit == unit]
    return sub if ma is None else sub[sub.ma_du_lieu == ma]


def ml_model_len(mod, pairs):
    """Cell 4 of the Mũ-Logarit ReAct notebooks: the longest prompt plus the whole generation budget."""
    prompt_tokens = 0
    for template, sub in pairs:
        longest = max(sub['de_bai_mcq'], key=len)
        prompt_tokens = max(prompt_tokens, len(tok(template.replace('{de_bai}', longest)).input_ids))
    return ((prompt_tokens + mod.MAX_NEW_TOKENS + 1500) // 1024 + 1) * 1024


for unit in needed:
    u, mod = UNITS[unit], MODS[unit]
    if u['kind'] == 'ml_group':
        mod.MAX_MODEL_LEN = ml_model_len(mod, [(mod.TYPE_PROMPTS[ma]['template'], routed(unit, ma))
                                               for ma in sorted(set(routed(unit).ma_du_lieu))])
    elif u['kind'] == 'ml_single':
        mod.MAX_MODEL_LEN = ml_model_len(mod, [(mod.PROMPT_TEMPLATE, routed(unit))])
    print(f'{unit:10s} MAX_MODEL_LEN={mod.MAX_MODEL_LEN}')
ENGINE_LEN = max(MODS[u].MAX_MODEL_LEN for u in needed)

N_GPU = torch.cuda.device_count()
TENSOR_PARALLEL = 2 if N_GPU >= 2 else 1
print(f'GPUs: {N_GPU} -> tensor_parallel_size={TENSOR_PARALLEL}, engine max_model_len={ENGINE_LEN}')
llm = LLM(model=MODEL, tensor_parallel_size=TENSOR_PARALLEL, dtype='float16',
          max_model_len=ENGINE_LEN, gpu_memory_utilization=0.90,
          trust_remote_code=True, enforce_eager=True, seed=SEED)
for mod in MODS.values():
    mod.tok, mod.llm = tok, llm
print('Ready.')
'''

MD_SOLVE = r'''
## Bước 3. Giải

Mỗi nhóm câu chạy bằng đúng mã của notebook gốc. Kết quả từng nhóm được lưu ngay vào `raw/` nên vẫn xem được nếu phiên bị dừng giữa chừng.
'''

SOLVE = r'''
OUTPUTS = {}          # STT -> answer and solution


def ml_records(sub):
    return [{'STT': int(r.STT), 'ma_dang': r.ma_du_lieu, 'dap_an_letter': r.dap_an_dung, 'de_bai_mcq': r.de_bai_mcq}
            for r in sub.itertuples()]


def sp_records(sub):
    return [{'STT': int(r.STT), 'loai_so': '', 'de_bai_mcq': r.de_bai_mcq, 'dap_an_letter': r.dap_an_dung}
            for r in sub.itertuples()]


def keep(df, unit, answer, text, tokens='token', calls=None, stop=None):
    df.to_csv(os.path.join(RAW_DIR, f'{unit}.csv' if 'ma' not in df.attrs else f"{unit}_{df.attrs['ma']}.csv"),
              index=False, encoding='utf-8-sig')
    for _, r in df.iterrows():
        OUTPUTS[int(r['STT'])] = dict(model_chon=r[answer] if isinstance(r[answer], str) else '',
                                      token=int(r[tokens]) if tokens else None,
                                      so_luot_goi_tool=int(r[calls]) if calls else 0,
                                      ly_do_dung=r[stop] if stop else '', loi_giai=r[text])


def move(path):
    df = pd.read_csv(path, encoding='utf-8-sig', keep_default_na=False)
    os.remove(path)
    return df


T0 = time.time()
for unit in needed:
    u, mod, sub = UNITS[unit], MODS[unit], routed(unit)
    t1 = time.time()
    print('#' * 72)
    print(f"{unit}: {len(sub)} questions, {u['kind']}  ({(t1 - T0) / 60:.1f} min so far)")
    print('#' * 72)
    if u['kind'] == 'ml_zeroshot':
        # One call for every Mũ-Logarit zero-shot question: same prompt and sampling for all these dạng.
        mod.TYPES = ['pipeline_ml']
        mod.ALL_RECORDS = {'pipeline_ml': ml_records(sub)}
        run_code(mod, u['sampling'])
        run_code(mod, u['loop'])
        df = move('/kaggle/working/pipeline_ml_zeroshot_full90_Qwen3-4B.csv')
        df['loi_giai'] = df['think'] + '</think>' + df['after']
        keep(df, unit, 'model_chon', 'loi_giai')
    elif u['kind'] == 'sp_zeroshot':
        mod.records = [dict(stt=int(r.STT), stt_goc=None, van_de=None, ma_dang=r.ma_du_lieu, muc_do=None, ten_dang=None,
                            nguon='Thực tế', loai_so=None, de_bai=r.de_bai_mcq, correct=r.dap_an_dung)
                       for r in sub.itertuples()]
        run_code(mod, u['prompt'])
        mod.tok = tok
        run_code(mod, u['gen'])
        run_code(mod, u['extract'])
        df = mod.res.rename(columns={'stt': 'STT'})
        df['token'] = [len(o.outputs[0].token_ids) for o in mod.outputs]
        keep(df, unit, 'qwen_chon', 'loi_giai_qwen')
    elif u['kind'] == 'ml_group':
        mod.ALL_RECORDS = {ma: ml_records(routed(unit, ma)) for ma in sorted(set(sub.ma_du_lieu))}
        run_code(mod, u['loop'])
        for ma in mod.ALL_RECORDS:
            mod.run_type(ma)
            df = move(f'/kaggle/working/{ma.lower()}_react_calculator_full90.csv')
            df.attrs['ma'] = ma
            keep(df, unit, 'model_chon', 'full_text', calls='tool_calls', stop='stop_reason')
    elif u['kind'] == 'ml_single':
        mod.records = ml_records(sub)
        mod.OUT_PATH = os.path.join(RAW_DIR, f'{unit}_out.csv')
        run_code(mod, u['loop'])
        keep(move(mod.OUT_PATH), unit, 'model_chon', 'full_text', calls='tool_calls', stop='stop_reason')
    elif u['kind'] == 'sp_single':
        mod.records = sp_records(sub)
        mod.OUT_PATH = os.path.join(RAW_DIR, f'{unit}_out.csv')
        run_code(mod, u['loop'])
        keep(move(mod.OUT_PATH), unit, 'model_chon', 'full_text', calls='so_luot_goi_tool', stop='ly_do_dung')
    elif u['kind'] == 'sp_group':
        unit_dir = os.path.join(WORK_DIR, 'data_' + unit)
        os.makedirs(unit_dir, exist_ok=True)
        mod.DATA_DIR = mod.OUT_DIR = unit_dir
        run_code(mod, u['loop'])                      # defines chay_mot_dang(...)
        for ma in sorted(set(sub.ma_du_lieu)):
            json.dump(sp_records(routed(unit, ma)), open(os.path.join(unit_dir, u['data_file'][ma]), 'w', encoding='utf-8'),
                      ensure_ascii=False)
            run_code(mod, u['type_cells'][ma])        # the cell of that dạng: its prompt, then chay_mot_dang(...)
            df = move(os.path.join(unit_dir, u['out_file'][ma]))
            df.attrs['ma'] = ma
            keep(df, unit, 'model_chon', 'full_text', calls='so_luot_goi_tool', stop='ly_do_dung')
    print(f'{unit} done in {(time.time() - t1) / 60:.1f} min; {len(OUTPUTS)}/{len(plan)} questions answered so far.')
print(f'All done in {(time.time() - T0) / 60:.1f} min.')
assert sorted(OUTPUTS) == sorted(plan.STT), 'some questions have no output'
'''

MD_REPORT = r'''
## Bước 4. Đánh giá

`dang_dung` chỉ được dùng từ đây. Ba loại lỗi: phân dạng sai; phân dạng đúng nhưng giải sai; không trích được đáp án.
'''

REPORT = r'''
res = plan.copy()
for k in ('model_chon', 'token', 'so_luot_goi_tool', 'ly_do_dung', 'loi_giai'):
    res[k] = res['STT'].map(lambda s: OUTPUTS[s][k])
res['dung_dang'] = res['dang_du_doan'] == res['dang_dung']
res['ket_qua'] = ['Không xác định' if c == '' else ('Đúng' if c == d else 'Sai')
                  for c, d in zip(res['model_chon'], res['dap_an_dung'])]
res['cach_giai_dang_dung'] = res['dang_dung'].map(lambda n: TYPE_BY_NO[n]['cach_giai'])
res.to_csv(os.path.join(WORK_DIR, 'ket_qua_pipeline_100cau.csv'), index=False, encoding='utf-8-sig')

lines = []


def out(s=''):
    print(s)
    lines.append(str(s))


def pct(a, b):
    return f'{a}/{b} ({a / b * 100:.1f}%)' if b else '0/0'


n = len(res)
out('=' * 72)
out(f"Phạm vi: {n} câu thực tế (đề thi thử / đề chính thức THPTQG), thuộc {res['dang_dung'].nunique()}/142 dạng; "
    + ', '.join(f'{k}: {v}' for k, v in res['topic'].value_counts().items()))
out('=' * 72)
out(f"Phân dạng đúng       : {pct(int(res['dung_dang'].sum()), n)}")
out(f"Đáp án đúng (cả hệ)  : {pct(int((res['ket_qua'] == 'Đúng').sum()), n)}")
out(f"Sai                  : {int((res['ket_qua'] == 'Sai').sum())}")
out(f"Không xác định       : {int((res['ket_qua'] == 'Không xác định').sum())}")
out()
out('--- Theo chuyên đề ---')
for topic, g in res.groupby('topic'):
    out(f"{topic:12s} phân dạng đúng {pct(int(g['dung_dang'].sum()), len(g))} | "
        f"đáp án đúng {pct(int((g['ket_qua'] == 'Đúng').sum()), len(g))}")
out()
out('--- Theo cách giải được chọn (theo dạng dự đoán) ---')
for k, g in res.groupby('cach_giai'):
    out(f"{k:18s} đáp án đúng {pct(int((g['ket_qua'] == 'Đúng').sum()), len(g))}")
out()
out('--- Phân dạng x kết quả ---')
out(pd.crosstab(res['dung_dang'].map({True: 'đúng dạng', False: 'sai dạng'}), res['ket_qua'], margins=True).to_string())
out()
cols = ['id', 'topic', 'dang_dung', 'dang_du_doan', 'do_tin_cay', 'cach_giai', 'dap_an_dung', 'model_chon', 'ket_qua']
out('--- (1) Phân dạng sai ---')
g = res[~res['dung_dang']]
out(g[cols].to_string(index=False) if len(g) else '(không có)')
out()
out('--- (2) Phân dạng đúng nhưng giải sai ---')
g = res[res['dung_dang'] & (res['ket_qua'] == 'Sai')]
out(g[cols + ['token', 'so_luot_goi_tool', 'ly_do_dung']].to_string(index=False) if len(g) else '(không có)')
out()
out('--- (3) Không trích được đáp án ---')
g = res[res['ket_qua'] == 'Không xác định']
out(g[cols + ['token', 'so_luot_goi_tool', 'ly_do_dung']].to_string(index=False) if len(g) else '(không có)')
open(os.path.join(WORK_DIR, 'bao_cao_pipeline.txt'), 'w', encoding='utf-8').write('\n'.join(lines))

zip_path = shutil.make_archive('/kaggle/working/pipeline_ket_qua', 'zip', WORK_DIR)
print('\nSaved:', zip_path)
'''

CELLS = [("markdown", MD_INTRO), ("code", PIP), ("code", CONFIG), ("markdown", MD_ROUTER), ("code", ROUTER),
         ("code", PLAN), ("markdown", MD_SETUP), ("code", SETUP), ("code", ENGINE), ("markdown", MD_SOLVE),
         ("code", SOLVE), ("markdown", MD_REPORT), ("code", REPORT)]
