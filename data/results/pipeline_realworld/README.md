# Whole-pipeline test on real-world questions

The full tutor pipeline was run end to end on questions collected from the internet. For each question it routes the
question to a dạng, loads that dạng's prompt and solves the question with Qwen3-4B. The notebook is
[`experiments/Pipeline/KLTN_Pipeline_GiaSu_100cau.ipynb`](../../../experiments/Pipeline/KLTN_Pipeline_GiaSu_100cau.ipynb).
It was run once on Kaggle (2 x T4) on 2026-10-16.

- **Router:** Qwen3-0.6B + LoRA. It scores the 142 strings "Dạng N: mô tả" and keeps the most probable one.
- **Choice of prompt:** taken from the predicted dạng only. The column `dang_dung` is used for evaluation only.
- **Solver:** every dạng runs the code of its final experiment notebook, copied verbatim. This includes the prompt,
  the Calculator, the ReAct loop, the generation parameters and the answer extraction.

## Evaluation set: 93 questions

| | Router (dạng correct) | Final answer correct |
|---|---|---|
| All 93 questions | 77/93 (82.8%) | 89/93 (95.7%) |
| 63 questions from web pages and mock exams | 47/63 (74.6%) | 63/63 |
| 30 questions from official exams (application level) | 30/30 | 26/30 (86.7%) |
| Mũ-Logarit (68) | 55/68 (80.9%) | 64/68 (94.1%) |
| Số phức (25) | 22/25 (88.0%) | 25/25 |
| Solved with ReAct + Calculator (35) | | 31/35 (88.6%) |
| Solved zero-shot (58) | | 58/58 |

The 93 questions cover 49 of the 142 dạng. No answer was missing. All 16 questions sent to a wrong dạng were still
answered correctly, and 15 of them were sent to a zero-shot dạng. Details are in
[`bao_cao_93_cau.txt`](bao_cao_93_cau.txt), produced by `scripts/pipeline/report_93.py`.

### The four wrong answers

All four were routed to the correct dạng.

- **VD-012, VD-013, VD-014** (dạng 69, data code D75):
  - One option is "Vô số". The prompt stores every option in the Calculator as a number.
  - The model repeated `option_c = "Vô số"` until it reached the limit of 25 tool calls, then had to answer and chose D.
  - None of the 90 experiment variants of this dạng has a non-numeric option.
- **VD-005** (dạng 63, data code D68):
  - The question writes $4a^2$. The model took the coefficient as 4 instead of $(2a)^2$, so 2.
  - None of the four options matched its result, and it still answered B.

## Changes to the question set

1. **Original set:** 100 questions (75 Mũ-Logarit, 25 Số phức) from mock exams and official exam papers. Each was kept
   only if it belongs to one of the 142 dạng. The texts of the questions were not edited.
2. **First run, before this one:** 98/100 correct and router 70/100. Most questions were easy and only 13 needed ReAct.
3. **Harder questions:**
   - 30 recognition-level questions were replaced by 30 application-level questions from official exams (2017-2021).
   - They were transcribed from the compilation *Chuyên đề trong đề thi tốt nghiệp THPT Quốc gia môn Toán 2017-2021*.
     The numbers and the order of the options are kept; the formulas were normalised to Markdown LaTeX.
   - Every answer key was recomputed independently with a program.
   - The keys of the three dạng 126 questions (VD-019 to VD-021) were wrong in the first transcription and were
     corrected to B (3 solutions). The source PDF agrees.
   - None of the 30 questions is identical to a question of the experiment data, the router training data or the
     router evaluation data. 16 of them share a template with experiment variants but use other numbers.
4. **Run on the 100 questions:** 96/100 correct and router 77/100, with 47/70 on the web questions.
   See [`kaggle_run_20261016/bao_cao_pipeline.txt`](kaggle_run_20261016/bao_cao_pipeline.txt).
5. **Seven questions removed:** SRC-09, SRC-02, SRC-22, WEB-026, WEB-044, BS-008 and CR-9.
   - The first six belong to the dạng named in the catalogue, but are a sub-case of its template, for example the
     other inequality sign or two different constants.
   - CR-9 could be read as dạng 11 or dạng 49. The catalogue's distinction (dạng 11: both sides are logarithms)
     decides it as dạng 11.
   - They were removed to keep only unambiguous labels. All seven had been routed to a wrong dạng, so removing them
     raises the router score. Both numbers (with and without them) should be reported.
   - The review of the 23 questions routed differently from their label is in
     [`ra_soat_nhan_dang_23_cau_phan_sai.csv`](ra_soat_nhan_dang_23_cau_phan_sai.csv).

## Limitations

- **Single run:** zero-shot answers can change between runs. With seed 42 the batch composition still changes
  sampling: question BS-011 was wrong in the first run and right in the second.
- **Labels:** `dang_dung` was assigned and reviewed by hand against the catalogue names, not by independent annotators.
- **Official-exam questions:** the 30 questions come from the same families the catalogue was built from (other exam
  codes). Their 30/30 router score therefore says little about generalisation. The 63 web questions (74.6%) are the
  more independent measure.
- **Small ReAct sample:** only 35 questions were solved with ReAct + Calculator.

## Files

| File | Content |
|---|---|
| `questions/cau_hoi_thuc_te_93_cau.csv` | The 93-question evaluation set: question, answer, `dang_dung`, source |
| `questions/cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv` | The 100 questions of the Kaggle run |
| `questions/cau_hoi_VD_VDC_30_cau_THPT.csv` | The 30 application-level questions |
| `questions/kiem_tra_30_cau.csv` | The 30 questions with source page, derivation of the answer and reason for the dạng |
| `ket_qua_pipeline_93cau_7cot.csv` / `.xlsx` | Results for the 93 questions, described below |
| `ket_qua_pipeline_100cau_7cot.csv` | Same columns for the 100 questions |
| `ra_soat_nhan_dang_23_cau_phan_sai.csv` | Label review of the questions routed differently from their label |
| `bao_cao_93_cau.txt` | Report on the 93 questions |
| `kaggle_run_20261016/` | Raw output of the Kaggle run: report, per-question results with full solutions, router output, routing plan, outputs of each code unit (`raw/`) |

The results files have seven columns:

| Column | Content |
|---|---|
| Đề bài | The question |
| Đáp án đúng | The correct answer |
| Dạng đúng | The labelled dạng |
| Dạng dự đoán | The dạng predicted by the router |
| Response của mô hình | The model's full response |
| Đáp án mô hình chọn | The answer the model chose |
| Đúng/Sai | Correct or wrong |

## Reproducing the run

1. Build the Kaggle bundle and the notebook with
   `python scripts/pipeline/build_pipeline_notebook.py <router_adapter_dir>`. The adapter (`router_lora`, 40 MB) is not
   stored in this repository.
2. Upload `data/pipeline_bundle/` (with `router_lora/`) as a Kaggle Dataset.
3. Run the notebook with GPU T4 x2 and internet access.
