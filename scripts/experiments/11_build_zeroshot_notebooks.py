# -*- coding: utf-8 -*-
"""
Builds the 10 Kaggle notebooks that run Qwen3-4B zero-shot over the
Mu-Logarit evaluation set (91 problem types, 90 variants each, 8,190
questions total), one notebook per group so the run can be split across
10 separate Kaggle accounts/GPU quotas.

Prompt, decoding settings, grading regex, and notebook cell structure are
copied unchanged from the Complex Numbers (so_phuc) Qwen3 zero-shot
full-90 experiments (see so_phuc/experiments/*/KLTN_*_zeroshot_full90_*.ipynb) -
only the model name, dataset path, and output filenames differ.

Run scripts/experiments/10_prepare_zeroshot_data.py first to produce
plan_solve_prompts_mulogarit_merged.json and mulogarit_group_split.json.
"""
import json

SPLIT_INFO = "scripts/experiments/mulogarit_group_split.json"
OUT_DIR = "experiments/Qwen3-4B"
MODEL = "Qwen/Qwen3-4B"
# Kaggle dataset path for the merged JSON once uploaded - SUA NEU KHAC.
KAGGLE_DATA_PATH = "/kaggle/input/datasets/ggducky/mulogarit-full/plan_solve_prompts_mulogarit_merged.json"

MAX_MODEL_LEN = 11264
MAX_NEW_TOKENS = 9216
TEMPERATURE, TOP_P, TOP_K, SEED = 0.6, 0.95, 20, 42
PRESENCE_PENALTY = 1.2

PROMPT_TEMPLATE = r'''Bạn hãy giải bài toán trắc nghiệm sau đây.

Yêu cầu trình bày:
- Giải chi tiết từng bước bằng tiếng Việt.
- Viết dưới dạng Markdown, dùng LaTeX cho công thức toán (đặt công thức trong dấu $...$).
- Không xuống dòng quá nhiều lần trong một biểu thức (ví dụ ngoặc vuông, phân số) vì sẽ khó đọc.
- Sau khi giải xong, kết luận rõ ràng ở dòng cuối cùng: "Đáp án đúng: X" (X là A, B, C hoặc D).

Đề bài:
{de_bai}
'''


def md_cell(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def code_cell(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": src.splitlines(keepends=True)}


def setup_cell(group_name, first_type, is_first):
    lines = [
        f"MERGED_DATA_PATH = '{KAGGLE_DATA_PATH}'  # SUA NEU KHAC\n",
        f"OUT_PATH  = '/kaggle/working/{first_type.lower()}_zeroshot_full90_Qwen3-4B.csv'\n",
        "\n",
        f"MODEL = '{MODEL}'\n",
        f"MAX_MODEL_LEN, MAX_NEW_TOKENS = {MAX_MODEL_LEN}, {MAX_NEW_TOKENS}\n",
        f"TEMPERATURE, TOP_P, TOP_K, SEED = {TEMPERATURE}, {TOP_P}, {TOP_K}, {SEED}\n",
        f"PRESENCE_PENALTY = {PRESENCE_PENALTY}\n",
        "os.environ['TOKENIZERS_PARALLELISM'] = 'false'\n",
        "\n",
        "with open(MERGED_DATA_PATH, encoding='utf-8') as f:\n",
        "    _all_records = json.load(f)\n",
        f"records = _all_records['{first_type}']\n",
        "print('So cau:', len(records))\n",
        "\n",
    ]
    if is_first:
        lines += [
            "tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)\n",
            "N_GPU = torch.cuda.device_count()\n",
            "TENSOR_PARALLEL = 2 if N_GPU >= 2 else 1\n",
            "llm = LLM(model=MODEL, tensor_parallel_size=TENSOR_PARALLEL, dtype='float16',\n",
            "          max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.90,\n",
            "          trust_remote_code=True, enforce_eager=True, seed=SEED)\n",
            "print('San sang.')\n",
        ]
    else:
        lines += [
            "# KHONG nap lai tok/llm - dung lai bien da nap tu khoi dau tien cua\n",
            "# notebook nay. Nap lai LLM(...) nhieu lan hay gay loi GPU het bo nho.\n",
            "print('Dung lai tok/llm da nap san.')\n",
        ]
    lines += [
        "sampling = SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, top_k=TOP_K,\n",
        "                          presence_penalty=PRESENCE_PENALTY,\n",
        "                          max_tokens=MAX_NEW_TOKENS, seed=SEED)\n",
    ]
    return "".join(lines)


def gen_cell():
    lines = [f"PROMPT_TEMPLATE = r'''{PROMPT_TEMPLATE}'''\n", "\n"]
    lines += [
        "prompts = []\n",
        "for r in records:\n",
        "    txt = PROMPT_TEMPLATE.replace('{de_bai}', r['de_bai_mcq'])\n",
        "    prompts.append(tok.apply_chat_template(\n",
        "        [{'role': 'user', 'content': txt}],\n",
        "        tokenize=False, add_generation_prompt=True, enable_thinking=True))\n",
        "\n",
        "t0 = time.time()\n",
        "outputs = llm.generate(prompts, sampling)\n",
        "print(f'Sinh xong {len(outputs)} cau, mat {(time.time()-t0)/60:.1f} phut.')\n",
    ]
    return "".join(lines)


def grade_cell(dang):
    return (
        "def get_letter(t):\n"
        "    m = re.findall(r'[Đđ]áp\\s*án[^A-D]{0,15}([A-D])\\b', t)\n"
        "    if m:\n"
        "        return m[-1]\n"
        "    m = re.findall(r'\\\\boxed\\{([A-D])\\}', t)\n"
        "    return m[-1] if m else ''\n"
        "\n"
        "rows = []\n"
        "for r, out in zip(records, outputs):\n"
        "    txt = out.outputs[0].text\n"
        "    ntok = len(out.outputs[0].token_ids)\n"
        "    think = txt.split('</think>')[0] if '</think>' in txt else txt\n"
        "    after = txt.split('</think>')[-1] if '</think>' in txt else ''\n"
        "    het_ngan_sach = ntok >= MAX_NEW_TOKENS - 1\n"
        "\n"
        "    chon = get_letter(after)\n"
        "\n"
        "    rows.append({\n"
        "        'STT': r['STT'], 'ma_dang': r['ma_dang'],\n"
        "        'dap_an_dung': r['dap_an_letter'], 'model_chon': chon,\n"
        "        'DUNG': chon == r['dap_an_letter'],\n"
        "        'token': ntok, 'het_ngan_sach': het_ngan_sach,\n"
        "        'think': think, 'after': after,\n"
        "    })\n"
        "\n"
        "df = pd.DataFrame(rows)\n"
        "df.to_csv(OUT_PATH, index=False, encoding='utf-8-sig')\n"
        "\n"
        "print('='*70)\n"
        f"print('KET QUA TONG (ZERO-SHOT, {dang}, Qwen3-4B):', df['DUNG'].sum(), '/', len(df), 'DUNG',\n"
        "      f\"({df['DUNG'].mean()*100:.1f}%)\")\n"
        "print('='*70)\n"
        "print()\n"
        "print('--- Cac cau SAI ---')\n"
        "print(df[~df['DUNG']][['STT', 'dap_an_dung', 'model_chon', 'het_ngan_sach']])\n"
    )


def build_notebook(group_name, types):
    cells = [md_cell(
        f"# Mu-Logarit - {group_name} ({types[0]}-{types[-1]}, {len(types)} dạng) - "
        f"FULL90 - ZERO-SHOT - Qwen3-4B\n\n"
        "Dùng đúng PROMPT_TEMPLATE tiếng Việt, cách chấm điểm, và các tham số sinh "
        "(`temperature=0.6, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2, "
        "max_new_tokens=9216, enable_thinking=True`) giống hệt bản Qwen3-4B zero-shot "
        "đã dùng cho bộ Số phức - không đổi chữ nào ngoài tên model (giữ nguyên) và "
        "nguồn dữ liệu.\n\n"
        f"**CẦN UPLOAD** `plan_solve_prompts_mulogarit_merged.json` lên Kaggle, đường dẫn "
        f"`{KAGGLE_DATA_PATH}`.\n"
    )]
    cells.append(code_cell(
        "!pip install -q -U vllm\n"
        "!pip uninstall -y -q torchcodec\n"
        "import vllm; print('vLLM:', vllm.__version__)\n"
    ))
    cells.append(code_cell(
        "import os, json, re, time\n"
        "import pandas as pd\n"
        "import torch\n"
        "from transformers import AutoTokenizer\n"
        "from vllm import LLM, SamplingParams\n"
    ))
    for i, dang in enumerate(types):
        cells.append(md_cell(f"## Dạng {dang} - zero-shot"))
        cells.append(code_cell(setup_cell(group_name, dang, is_first=(i == 0))))
        cells.append(code_cell(gen_cell()))
        cells.append(code_cell(grade_cell(dang)))
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main():
    split_info = json.load(open(SPLIT_INFO, encoding="utf-8"))
    for group_name, types in split_info.items():
        nb = build_notebook(group_name, types)
        out_path = f"{OUT_DIR}/KLTN_{group_name}_zeroshot_full90_Qwen3-4B.ipynb"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"Wrote {out_path} ({len(types)} dang: {types[0]}..{types[-1]})")


if __name__ == "__main__":
    main()
