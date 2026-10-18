import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'                   # ONE GPU. With two, Trainer doubles the batch (16 x 2 GPUs = 32 per step, 64 per update)
import transformers, peft, torch
print('transformers', transformers.__version__, '| peft', peft.__version__, '| torch', torch.__version__,
      '| GPUs:', torch.cuda.device_count())

import os, re, json, glob, copy, time, random
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')    # less memory fragmentation (must be set before torch is imported)
from collections import Counter
import numpy as np
import torch

# ------------------------------------------------------------------ configuration
MODEL = os.environ.get('ROUTER_MODEL', 'Qwen/Qwen3-0.6B')
QUICK_TEST = os.environ.get('ROUTER_QUICK', '0') == '1'    # True: a few steps and a few questions, only to check that everything runs

LOSS_ON = os.environ.get('ROUTER_LOSS', 'completion')      # 'completion' (recommended) or 'all'
USE_4BIT = False                                          # QLoRA (4-bit base model). False = LoRA on the 16-bit model
LORA_R, LORA_ALPHA, LORA_DROPOUT = 16, 32, 0.05
EPOCHS = 2
MAX_TRAIN_MINUTES = 270                                    # safety: training stops (and the adapter is saved) after this many minutes
SCORE_MAX_MINUTES = 200                                   # safety: scoring stops after this many minutes (the questions are scored in random order)
LEARNING_RATE = 2e-4
PER_DEVICE_BATCH, GRAD_ACCUM = int(os.environ.get('ROUTER_BS', '16')), int(os.environ.get('ROUTER_ACCUM', '2'))                      # effective batch: 32 sequences (the loss no longer builds the full logits, see RouterTrainer)
MAX_LEN = 512                                             # pairs longer than this are left out of training (1 of 12780: 726 tokens); it keeps the memory of a batch bounded
VAL_PER_TYPE = 3                                          # pairs of every type kept out of training to watch the loss (0 = none)
SEED = 42

# Evaluation (main): for every test question the probability of each of the 142 answers 'Dạng N: mô tả' is computed and the
# most probable one is the model's answer. Free generation is kept only as a comparison on a subset.
SCORE_CANDIDATES = os.environ.get('ROUTER_SCORE', '1') == '1'
SCORE_ALL = os.environ.get('ROUTER_SCORE_ALL', '1') == '1'                                          # score the whole test set (12951 questions: 172 source + 12779 variants)
SCORE_PER_TYPE = int(os.environ.get('ROUTER_SCORE_PER_TYPE', '20'))                                       # variants of every type in the sample (20 x 142 = 2840; all source questions are always included)
GREEDY_COMPARE = os.environ.get('ROUTER_GREEDY', '1') == '1'                                     # also let the model write its answer freely on that subset and read 'Dạng N' from it

assert LOSS_ON in ('completion', 'all')
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

def find(name):
    d = os.environ.get('ROUTER_DATA_DIR')
    if d:
        p = os.path.join(d, name)
        assert os.path.exists(p), p
        return p
    hits = glob.glob(f'/kaggle/input/**/{name}', recursive=True)
    assert hits, f'{name} not found under /kaggle/input: attach the dataset to the notebook first.'
    return hits[0]

TRAIN_PATH, EVAL_PATH, CAND_PATH = find('finetune_router.jsonl'), find('eval_set.jsonl'), find('candidates.json')
OUT_DIR = '/kaggle/working' if os.path.isdir('/kaggle/working') else os.environ.get('ROUTER_OUT', './router_out')
os.makedirs(OUT_DIR, exist_ok=True)
LORA_DIR = os.path.join(OUT_DIR, 'router_lora')
print('model:', MODEL, '| loss on:', LOSS_ON, '| quick test:', QUICK_TEST)
print('data :', TRAIN_PATH, EVAL_PATH, CAND_PATH, sep='\n       ')

# ------------------------------------------------------------------ data
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained(MODEL)
tok.padding_side = 'right'
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token
EOS = '<|im_end|>'

def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]

train_all = read_jsonl(TRAIN_PATH)
CANDS = json.load(open(CAND_PATH, encoding='utf-8'))
assert len(CANDS) == 142 and all(c.startswith(f'Dạng {i + 1}:') for i, c in enumerate(CANDS))
assert all(r['completion'] in set(CANDS) for r in train_all), 'a training answer is not one of the 142 candidates'

def type_of(completion):
    return int(re.match(r'Dạng (\d+):', completion).group(1))

# keep VAL_PER_TYPE pairs of every type out of the training set (only to watch the loss)
by_type = {}
for r in train_all:
    by_type.setdefault(type_of(r['completion']), []).append(r)
rng = random.Random(SEED)
train_rows, val_rows = [], []
for n, rs in sorted(by_type.items()):
    rs = rs[:]; rng.shuffle(rs)
    val_rows += rs[:VAL_PER_TYPE]
    train_rows += rs[VAL_PER_TYPE:]
rng.shuffle(train_rows)
if QUICK_TEST:
    train_rows, val_rows = train_rows[:160], val_rows[:40]
print('training pairs:', len(train_rows), '| validation pairs:', len(val_rows), '| types:', len(by_type))

def prompt_text(user):
    # chat template with the thinking block closed and empty: the answer starts right after it
    return tok.apply_chat_template([{'role': 'user', 'content': user}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)

def encode_pair(user, completion):
    p = tok(prompt_text(user), add_special_tokens=False).input_ids
    c = tok(completion + EOS, add_special_tokens=False).input_ids
    ids = p + c
    labels = ([-100] * len(p) + c) if LOSS_ON == 'completion' else list(ids)
    return {'input_ids': ids[:MAX_LEN], 'labels': labels[:MAX_LEN]}

train_ds = [encode_pair(r['prompt'], r['completion']) for r in train_rows]
n_before = len(train_ds)
train_ds = [x for x in train_ds if len(x['input_ids']) < MAX_LEN]            # a cut pair would lose the answer, so it is dropped instead
print(f'pairs left out because they are longer than {MAX_LEN} tokens: {n_before - len(train_ds)}')
val_ds = [encode_pair(r['prompt'], r['completion']) for r in val_rows]

lens = np.array([len(x['input_ids']) for x in train_ds])
n_loss = sum(sum(1 for t in x['labels'] if t != -100) for x in train_ds)
print(f'sequence length: mean {lens.mean():.0f}, p99 {np.percentile(lens, 99):.0f}, max {lens.max()} (MAX_LEN={MAX_LEN})')
print(f'tokens per epoch: {lens.sum():,} | tokens that carry loss: {n_loss:,} ({n_loss / lens.sum():.1%})')
assert lens.max() <= MAX_LEN
# look at one example: the part the loss is computed on
ex = train_ds[0]
print('--- loss is computed on ---')
print(tok.decode([t for t in ex['labels'] if t != -100]))

class DS(torch.utils.data.Dataset):
    def __init__(self, rows): self.rows = rows
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]

def collate(batch):
    m = max(len(b['input_ids']) for b in batch)
    ids = torch.full((len(batch), m), tok.pad_token_id, dtype=torch.long)
    lab = torch.full((len(batch), m), -100, dtype=torch.long)
    att = torch.zeros((len(batch), m), dtype=torch.long)
    for i, b in enumerate(batch):
        n = len(b['input_ids'])
        ids[i, :n] = torch.tensor(b['input_ids']); lab[i, :n] = torch.tensor(b['labels']); att[i, :n] = 1
    return {'input_ids': ids, 'labels': lab, 'attention_mask': att}

# ------------------------------------------------------------------ model: 4-bit base + LoRA adapters
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

HAS_CUDA = torch.cuda.is_available()
# A T4 (capability 7.5) has no bfloat16 tensor cores, yet torch.cuda.is_bf16_supported() answers True because it emulates them,
# which is several times slower. So bfloat16 is used only from capability 8.0 (Ampere) on; otherwise float16.
BF16 = HAS_CUDA and torch.cuda.get_device_capability()[0] >= 8 and os.environ.get('ROUTER_FP16', '0') != '1'
COMPUTE_DTYPE = torch.bfloat16 if BF16 else (torch.float16 if HAS_CUDA else torch.float32)
# float16 training: the weights stay in float32 (safe against overflow) and the matrix products run in float16 (autocast)
LOAD_DTYPE = torch.float32 if (HAS_CUDA and not BF16 and not USE_4BIT) else COMPUTE_DTYPE
print('GPUs visible:', torch.cuda.device_count(), '| bfloat16:', BF16, '| weights loaded as:', LOAD_DTYPE, '| matrix products in:', COMPUTE_DTYPE)
if USE_4BIT and not HAS_CUDA:
    USE_4BIT = False                                      # 4-bit needs a GPU
quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_use_double_quant=True,
                           bnb_4bit_compute_dtype=COMPUTE_DTYPE) if USE_4BIT else None
kw = dict(quantization_config=quant, device_map={'': 0} if HAS_CUDA else None)
try:
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=LOAD_DTYPE, **kw)
except TypeError:
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=LOAD_DTYPE, **kw)
model.config.use_cache = False
if USE_4BIT:
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                            gradient_checkpointing_kwargs={'use_reentrant': False})
else:
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    model.enable_input_require_grads()
lora = LoraConfig(r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT, bias='none', task_type='CAUSAL_LM',
                  target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'])
model = get_peft_model(model, lora)
model.print_trainable_parameters()
if HAS_CUDA:
    print(f'GPU memory after loading: {torch.cuda.memory_allocated() / 1e9:.1f} GB')

# ------------------------------------------------------------------ training
from transformers import Trainer, TrainingArguments

steps_per_epoch = max(1, len(train_ds) // (PER_DEVICE_BATCH * GRAD_ACCUM))
total_steps = int(os.environ.get('ROUTER_QUICK_STEPS', '12')) if QUICK_TEST else steps_per_epoch * EPOCHS
print(f'steps per epoch: {steps_per_epoch} | total optimizer steps: {total_steps}')

def make_args(**extra):
    base = dict(
        output_dir=os.path.join(OUT_DIR, 'router_ckpt'),
        per_device_train_batch_size=PER_DEVICE_BATCH if not QUICK_TEST else 4,
        per_device_eval_batch_size=PER_DEVICE_BATCH,
        gradient_accumulation_steps=GRAD_ACCUM if not QUICK_TEST else 2,
        max_steps=total_steps,
        learning_rate=LEARNING_RATE, lr_scheduler_type='cosine', weight_decay=0.0,
        logging_steps=5 if QUICK_TEST else 20,
        save_strategy='no' if QUICK_TEST else 'steps', save_steps=400, save_total_limit=2,
        bf16=BF16, fp16=(HAS_CUDA and not BF16),
        gradient_checkpointing=True, gradient_checkpointing_kwargs={'use_reentrant': False},
        optim='paged_adamw_8bit' if USE_4BIT else 'adamw_torch',
        report_to='none', prediction_loss_only=True, seed=SEED, remove_unused_columns=False, dataloader_num_workers=0 if (QUICK_TEST or not HAS_CUDA) else int(os.environ.get('ROUTER_WORKERS', '2')),
    )
    base.update(extra)
    return base

eval_kw = dict(eval_strategy='steps' if len(val_ds) else 'no', eval_steps=5 if QUICK_TEST else 200)
args = TrainingArguments(**make_args(**eval_kw, warmup_steps=max(1, int(0.03 * total_steps))))

from transformers import TrainerCallback

class Progress(TrainerCallback):
    """Prints the speed and the time left every 10 steps, writes the same to a file, and stops training after MAX_TRAIN_MINUTES."""
    def __init__(self):
        self.t0 = time.time()
        self.path = os.path.join(OUT_DIR, 'train_progress.log')
        self.time_up = False
        self.stop_at = None                                  # end of the current chunk: stop and save a checkpoint there
    def on_step_end(self, args, state, control, **kw):
        el = time.time() - self.t0
        if state.global_step % 10 == 0 or state.global_step == 1:
            rate = state.global_step / max(el, 1e-9)
            msg = f'step {state.global_step}/{state.max_steps} | {el / 60:.1f} min | {1 / max(rate, 1e-9):.1f} s/step | about {(state.max_steps - state.global_step) / max(rate, 1e-9) / 60:.0f} min left'
            print(msg, flush=True)
            open(self.path, 'a').write(msg + chr(10))
        if self.stop_at is not None and state.global_step >= self.stop_at:
            control.should_training_stop = True
            control.should_save = True
        if el > MAX_TRAIN_MINUTES * 60:
            print('time limit reached: training stops here', flush=True)
            self.time_up = True
            control.should_training_stop = True
            control.should_save = True

class RouterTrainer(Trainer):
    """Loss on the answer tokens only, WITHOUT building the logits of every position.
    The vocabulary has 151936 tokens, so the logits of a whole batch in float32 take several GB and overflowed a 16 GB T4
    (the answer is only about a fifth of each sequence). Here the last hidden states are taken, only the positions that
    predict an answer token go through the output layer, and the cross entropy is computed on those."""
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        if LOSS_ON != 'completion':
            return super().compute_loss(model, inputs, return_outputs=return_outputs, num_items_in_batch=num_items_in_batch)
        causal = self.accelerator.unwrap_model(model)
        causal = causal.get_base_model() if hasattr(causal, 'get_base_model') else causal      # Qwen3ForCausalLM inside the PEFT wrapper
        hidden = causal.model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'], use_cache=False).last_hidden_state
        target = inputs['labels'][:, 1:]
        take = target != -100
        logits = causal.lm_head(hidden[:, :-1][take]).float()                                  # only the answer positions
        loss = torch.nn.functional.cross_entropy(logits, target[take], reduction='sum')
        loss = loss / (num_items_in_batch if num_items_in_batch is not None else take.sum().clamp(min=1))
        return (loss, {'logits': logits}) if return_outputs else loss

PROG = Progress()
trainer = RouterTrainer(model=model, args=args, train_dataset=DS(train_ds),
                  eval_dataset=DS(val_ds) if len(val_ds) else None, data_collator=collate, callbacks=[PROG])
N_CHUNKS = 4                                             # the training is run by the next cells, one chunk each, so that every cell ends (and shows its log) in turn
TRAIN_T0 = time.time()

# ------------------------------------------------------------------ training, part 1 of 4
if trainer.state.global_step < total_steps and not PROG.time_up:
    PROG.stop_at = min(total_steps, -(-total_steps * 1 // N_CHUNKS))
    trainer.train(resume_from_checkpoint=None)
    print(f'part 1 of 4 done at step ' + str(trainer.state.global_step) + f' | {(time.time() - TRAIN_T0) / 60:.1f} min since the start of training')
else:
    print('nothing left to train')

# ------------------------------------------------------------------ training, part 2 of 4
if trainer.state.global_step < total_steps and not PROG.time_up:
    PROG.stop_at = min(total_steps, -(-total_steps * 2 // N_CHUNKS))
    trainer.train(resume_from_checkpoint=True)
    print(f'part 2 of 4 done at step ' + str(trainer.state.global_step) + f' | {(time.time() - TRAIN_T0) / 60:.1f} min since the start of training')
else:
    print('nothing left to train')

# ------------------------------------------------------------------ training, part 3 of 4
if trainer.state.global_step < total_steps and not PROG.time_up:
    PROG.stop_at = min(total_steps, -(-total_steps * 3 // N_CHUNKS))
    trainer.train(resume_from_checkpoint=True)
    print(f'part 3 of 4 done at step ' + str(trainer.state.global_step) + f' | {(time.time() - TRAIN_T0) / 60:.1f} min since the start of training')
else:
    print('nothing left to train')

# ------------------------------------------------------------------ training, part 4 of 4
if trainer.state.global_step < total_steps and not PROG.time_up:
    PROG.stop_at = min(total_steps, -(-total_steps * 4 // N_CHUNKS))
    trainer.train(resume_from_checkpoint=True)
    print(f'part 4 of 4 done at step ' + str(trainer.state.global_step) + f' | {(time.time() - TRAIN_T0) / 60:.1f} min since the start of training')
else:
    print('nothing left to train')

# ------------------------------------------------------------------ end of training: validation, save the adapter
print(f'training time: {(time.time() - TRAIN_T0) / 60:.1f} min')
if len(val_ds):
    print('final validation:', trainer.evaluate())

model.save_pretrained(LORA_DIR)
tok.save_pretrained(LORA_DIR)
print('adapter saved to', LORA_DIR, os.listdir(LORA_DIR))
import gc
del trainer
gc.collect()
if HAS_CUDA:
    torch.cuda.empty_cache()

# ------------------------------------------------------------------ inference helpers
model.eval()
if HAS_CUDA and not BF16 and not USE_4BIT:
    model.half()                                          # float32 weights were only needed for training; float16 is 2x lighter and faster for scoring
model.config.use_cache = True
if hasattr(model, 'base_model') and hasattr(model.base_model, 'model'):
    model.base_model.model.config.use_cache = True
DEV = next(model.parameters()).device

CAND_IDS = [tok(c + EOS, add_special_tokens=False).input_ids for c in CANDS]
COLON = tok(':', add_special_tokens=False).input_ids[0]
# number of tokens of each candidate up to and including the colon after "Dạng N" (the part that names the type)
LABEL_LEN = [ids.index(COLON) + 1 for ids in CAND_IDS]
print('example candidate tokens:', [tok.decode([t]) for t in CAND_IDS[16][:8]], '| label length:', LABEL_LEN[16])

def parse_type(text):
    m = re.search(r'D[ạa]ng\s*(\d+)', text)
    return int(m.group(1)) if m else None

@torch.no_grad()
def greedy_batch(prompts, max_new_tokens=100):
    tok.padding_side = 'left'
    enc = tok([prompt_text(p) for p in prompts], add_special_tokens=False, return_tensors='pt', padding=True).to(DEV)
    out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.pad_token_id)
    tok.padding_side = 'right'
    return [tok.decode(o[enc.input_ids.shape[1]:], skip_special_tokens=True) for o in out]

@torch.no_grad()
def prompt_state(user):
    """Run the question once. Returns its key/value cache, its length and the distribution of the first answer token."""
    p_ids = tok(prompt_text(user), add_special_tokens=False, return_tensors='pt').input_ids.to(DEV)
    out = model(input_ids=p_ids, use_cache=True)
    return out.past_key_values, p_ids.shape[1], torch.log_softmax(out.logits[0, -1].float(), -1)

@torch.no_grad()
def sum_logprob(state, token_lists, chunk=71):
    """Total log-probability of each token list as the answer, reusing the cache of the question."""
    cache, L, first = state
    res = torch.zeros(len(token_lists))
    for s in range(0, len(token_lists), chunk):
        part = token_lists[s:s + chunk]; n = len(part); m = max(len(x) for x in part)
        ids = torch.full((n, m), tok.pad_token_id, dtype=torch.long); msk = torch.zeros((n, m), dtype=torch.long)
        for i, x in enumerate(part):
            ids[i, :len(x)] = torch.tensor(x); msk[i, :len(x)] = 1
        c = copy.deepcopy(cache); c.batch_repeat_interleave(n)
        attn = torch.cat([torch.ones((n, L), dtype=torch.long), msk], 1).to(DEV)
        o = model(input_ids=ids.to(DEV), attention_mask=attn, past_key_values=c, use_cache=True)
        logp = torch.log_softmax(o.logits.float(), -1)                  # position j predicts token j+1 of the answer
        tgt = ids[:, 1:].to(DEV)
        tok_lp = logp[:, :-1].gather(2, tgt.unsqueeze(-1)).squeeze(-1) * msk[:, 1:].to(DEV)
        tok_lp = torch.cat([first[ids[:, 0].to(DEV)].unsqueeze(1), tok_lp], 1)   # log-prob of every answer token
        cum = tok_lp.cumsum(1)
        for i in range(n):
            res[s + i] = cum[i, len(part[i]) - 1].item()
        del o, logp, c
    return res

@torch.no_grad()
def score_candidates(user, top=5):
    """Stage 1: probability of the part that names the type ('Dạng N:') for all 142 candidates.
       Stage 2: probability of the whole text 'Dạng N: mô tả' for the `top` best of stage 1."""
    state = prompt_state(user)
    label = sum_logprob(state, [ids[:LABEL_LEN[i]] for i, ids in enumerate(CAND_IDS)])
    best = torch.topk(label, top).indices.tolist()
    full = sum_logprob(state, [CAND_IDS[i] for i in best], chunk=top)
    return label, best, full

# ------------------------------------------------------------------ check the optional candidate scoring against a plain forward pass
def check_scoring():
    q = val_rows[0]['prompt'] if len(val_rows) else train_rows[0]['prompt']
    label, best, full = score_candidates(q)
    ids_q = tok(prompt_text(q), add_special_tokens=False).input_ids
    def plain(tokens):
        with torch.no_grad():
            lp = torch.log_softmax(model(input_ids=torch.tensor([ids_q + tokens], device=DEV)).logits[0].float(), -1)
        return sum(lp[len(ids_q) - 1 + j, t].item() for j, t in enumerate(tokens))
    for k in (0, 16, 100):
        ref = plain(CAND_IDS[k][:LABEL_LEN[k]])
        print(f'label part of candidate {k + 1:3d}: cached {label[k].item():9.4f} | plain {ref:9.4f}')
        assert abs(label[k].item() - ref) < 0.3 + 0.02 * abs(ref), 'cached scoring disagrees with a plain forward pass'
    ref = plain(CAND_IDS[best[0]])
    print(f'full text of candidate {best[0] + 1:3d}: cached {full[0].item():9.4f} | plain {ref:9.4f}')
    assert abs(full[0].item() - ref) < 0.3 + 0.02 * abs(ref)    # fp16 / 4-bit noise grows with the length
    print('top candidate:', CANDS[best[0]][:80])

if SCORE_CANDIDATES:
    check_scoring()
else:
    print('candidate scoring is off (SCORE_CANDIDATES = False)')

# ------------------------------------------------------------------ evaluation on the existing dataset (the test set)
import pandas as pd

test = read_jsonl(EVAL_PATH)
src_rows = [r for r in test if r['nguon'] == 'Câu gốc']
var_rows = [r for r in test if r['nguon'] != 'Câu gốc']
rs = random.Random(SEED)
sample = []
for n in range(1, 143):
    vs = [r for r in var_rows if r['so_dang'] == n]
    sample += rs.sample(vs, min(SCORE_PER_TYPE, len(vs)))
if QUICK_TEST:
    src_rows, sample = src_rows[:6], sample[:6]
subset = src_rows + sample                                            # source questions + a sample of the variants
rest = random.Random(SEED).sample([r for r in test if r['nguon'] != 'Câu gốc'], len(var_rows))      # random order: a stopped run is still an unbiased sample
scored_rows = (src_rows + rest if (SCORE_ALL and not QUICK_TEST) else subset) if SCORE_CANDIDATES else []   # every source question is scored first
greedy_rows = subset if (GREEDY_COMPARE or not SCORE_CANDIDATES) else []
print(f'test questions: {len(test)} (source {len(src_rows)}) | scored over 142 candidates: {len(scored_rows)} | free generation: {len(greedy_rows)}')

# ---- method 2 (main): probability of each of the 142 answers
sc = {}
t0 = time.time()
for i, r in enumerate(scored_rows):
    label, best, full = score_candidates(r['prompt'])
    sc[r['id']] = dict(label=best[0] + 1, full=best[int(full.argmax())] + 1, top3=[t + 1 for t in best[:3]],
                       conf=float(torch.softmax(label, 0).max()))
    if i % 100 == 0:
        eta = (time.time() - t0) / (i + 1) * (len(scored_rows) - i - 1) / 60
        print(f'  scoring {i}/{len(scored_rows)}  ({(time.time() - t0) / 60:.1f} min, about {eta:.0f} min left)')
    if i % 2000 == 1999:
        json.dump(sc, open(os.path.join(OUT_DIR, 'router_scores_partial.json'), 'w'))
    if i == 19:
        print(f'  speed: {(time.time() - t0) / 20:.2f} s per question -> about {(time.time() - t0) / 20 * len(scored_rows) / 60:.0f} min for all', flush=True)
    if time.time() - t0 > SCORE_MAX_MINUTES * 60:
        print(f'time limit reached: {i + 1} of {len(scored_rows)} questions scored', flush=True)
        scored_rows = scored_rows[:i + 1]
        break
if scored_rows:
    print(f'scoring time: {(time.time() - t0) / 60:.1f} min')

# ---- comparison: free generation, 'Dạng N' read from the text
gen = {}
t0 = time.time()
order = sorted(greedy_rows, key=lambda r: len(r['prompt']))
BS = 32
for s in range(0, len(order), BS):
    batch = order[s:s + BS]
    for r, text in zip(batch, greedy_batch([r['prompt'] for r in batch])):
        gen[r['id']] = text
if greedy_rows:
    print(f'free generation time: {(time.time() - t0) / 60:.1f} min')

# ------------------------------------------------------------------ results
rows = []
for r in (scored_rows if scored_rows else greedy_rows):
    d = dict(id=r['id'], so_dang=r['so_dang'], ma_cu=r['ma_cu'], nguon=r['nguon'], chu_de=r['chu_de'])
    if r['id'] in sc:
        c = sc[r['id']]
        d.update(score_full_pred=c['full'], score_full_ok=(c['full'] == r['so_dang']),
                 score_label_pred=c['label'], score_label_ok=(c['label'] == r['so_dang']),
                 top3_ok=(r['so_dang'] in c['top3']), conf=c['conf'])
    if r['id'] in gen:
        pred = parse_type(gen[r['id']])
        d.update(greedy_pred=pred, greedy_ok=(pred == r['so_dang']), greedy_text=gen[r['id']].strip()[:160])
    rows.append(d)
# the questions answered freely but not scored (when only the generation is used)
if scored_rows:
    seen = {r['id'] for r in scored_rows}
    for r in greedy_rows:
        if r['id'] not in seen:
            pred = parse_type(gen[r['id']])
            rows.append(dict(id=r['id'], so_dang=r['so_dang'], ma_cu=r['ma_cu'], nguon=r['nguon'], chu_de=r['chu_de'],
                             greedy_pred=pred, greedy_ok=(pred == r['so_dang']), greedy_text=gen[r['id']].strip()[:160]))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT_DIR, 'router_eval_predictions.csv'), index=False, encoding='utf-8-sig')

def acc(frame, col):
    if col not in frame:
        return float('nan')
    x = frame[col].dropna()
    return float(x.astype(bool).mean()) if len(x) else float('nan')

main = 'score_full_ok' if scored_rows else 'greedy_ok'
summary = {'model': MODEL, 'loss_on': LOSS_ON, 'epochs': EPOCHS, 'quick_test': QUICK_TEST, 'main_metric': main}
groups = (('all', df), ('source', df[df.nguon == 'Câu gốc']), ('variants', df[df.nguon != 'Câu gốc']),
          ('mu_logarit', df[df.chu_de == 'Mũ-Logarit']), ('so_phuc', df[df.chu_de == 'Số phức']))
for name, frame in groups:
    scored_frame = frame[frame['score_full_ok'].notna()] if 'score_full_ok' in frame else frame.iloc[0:0]
    summary[f'n_{name}'] = len(scored_frame) if scored_rows else len(frame)
    if scored_rows:
        summary[f'score142_full_text_{name}'] = acc(scored_frame, 'score_full_ok')      # main result
        summary[f'score142_label_only_{name}'] = acc(scored_frame, 'score_label_ok')
        summary[f'score142_top3_{name}'] = acc(scored_frame, 'top3_ok')
    gframe = frame[frame['greedy_ok'].notna()] if 'greedy_ok' in frame else frame.iloc[0:0]
    if len(gframe):
        summary[f'free_generation_{name}'] = acc(gframe, 'greedy_ok')
        summary[f'free_generation_n_{name}'] = len(gframe)
if scored_rows:
    both = df[df['score_full_ok'].notna() & df['greedy_ok'].notna()] if 'greedy_ok' in df else df.iloc[0:0]
    if len(both):
        summary['on_the_same_subset_score142'] = acc(both, 'score_full_ok')
        summary['on_the_same_subset_free_generation'] = acc(both, 'greedy_ok')
    for t in (0.5, 0.8, 0.95):
        hi = df[df.conf >= t]
        summary[f'share_with_confidence_ge_{t}'] = len(hi) / max(1, df.conf.notna().sum())
        summary[f'accuracy_when_confidence_ge_{t}'] = acc(hi, 'score_full_ok')
json.dump(summary, open(os.path.join(OUT_DIR, 'router_eval_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in summary.items():
    print(f'{k:46s} {v:.4f}' if isinstance(v, float) else f'{k:46s} {v}')

wrong = df[df[main] == False]
text_of = {r['id']: r['prompt'] for r in test}
err = wrong.copy()
err['de_bai'] = err['id'].map(text_of)
err.to_csv(os.path.join(OUT_DIR, 'router_eval_errors.csv'), index=False, encoding='utf-8-sig')
print(f'wrong answers: {len(err)} (written with the question text to router_eval_errors.csv)')
pred_col = 'score_full_pred' if scored_rows else 'greedy_pred'
conf = Counter(zip(wrong.so_dang, wrong[pred_col]))
pd.DataFrame([dict(that_su=a, mo_hinh_tra_loi=b, so_cau=n) for (a, b), n in conf.most_common()]).to_csv(
    os.path.join(OUT_DIR, 'router_eval_confusions.csv'), index=False, encoding='utf-8-sig')
print('\ncác cặp bị nhầm nhiều nhất (Dạng đúng -> Dạng mô hình trả lời):')
for (a, b), n in conf.most_common(15):
    print(f'  Dạng {a} -> {b}: {n} câu')
print('\nđộ chính xác theo chủ đề và nguồn:')
print(df.groupby(['chu_de', 'nguon'])[main].agg(['mean', 'count']).round(4))

# ------------------------------------------------------------------ optional: merge the adapter into a 16-bit model (for serving with vLLM later)
MERGE_AND_SAVE = False
if MERGE_AND_SAVE and not QUICK_TEST:
    from peft import PeftModel
    base = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map={'': 0})
    merged = PeftModel.from_pretrained(base, LORA_DIR).merge_and_unload()
    merged.save_pretrained(os.path.join(OUT_DIR, 'router_merged_fp16')); tok.save_pretrained(os.path.join(OUT_DIR, 'router_merged_fp16'))
    print('merged model saved')
print('DONE:', sorted(os.listdir(OUT_DIR)))
