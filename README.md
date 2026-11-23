# Applying Small Language Models in High-School Mathematics Tutoring

This repository accompanies an undergraduate thesis studying whether a small
language model (SLM) can be guided to answer every multiple-choice
high-school mathematics question correctly, across more than one topic. The
long-term goal is an **AI tutor whose whole chain, from the question text to the final answer, is 100% correct**.

The canonical, actively-maintained repository for each topic's own paper
submission stays separate (see below); this repository consolidates a copy
of the data, scripts, and results from every topic in one place, **plus the whole-system work (router, pipeline and its
real-world test)**, so a new contributor can pick up the work from here.

> Vietnamese notes for the next steps: [`data/results/pipeline_realworld/VAN_DE_HIEN_TAI.md`](data/results/pipeline_realworld/VAN_DE_HIEN_TAI.md)
> (the open problems, short) and [`PHAN_TICH_LOI.md`](data/results/pipeline_realworld/PHAN_TICH_LOI.md) (the detailed error analysis).

## The system

```
question ──► Router ──────────► "Dạng N" ──► prompt of dạng N ──► Solver ───────────────────► answer (A/B/C/D)
             Qwen3-0.6B + LoRA              (catalogue of 142)    Qwen3-4B, either
             scores the 142 strings                               · zero-shot, or
             "Dạng N: description"                                · ReAct + Calculator (SymPy tool)
```

* **142 dạng** (problem types): Dạng 1-88 are Exponential/Logarithm, Dạng 89-142 are Complex Numbers. **141 of them are
  scored**: Complex Numbers D34 (Dạng 122 in the catalogue) was removed from the evaluation: its answer key counted $z = 0$ as purely imaginary in 4 questions, while the convention of this work is that 0 is not purely imaginary. The router still chooses among all 142 strings (it was trained on them). The catalogue
  ([`data/catalogue/`](data/catalogue/)) holds the name, description, example and recognition hints of each dạng, and the
  old code (`ma_cu`, e.g. `ML_D20`, `SP_D55`) used by the experiments.
* **Router:** fine-tuned Qwen3-0.6B (LoRA). It scores all 142 strings and takes the most probable one. See
  [`models/`](models/) and [`experiments/Router-Finetune/`](experiments/Router-Finetune/).
* **Solver:** Qwen3-4B on vLLM. 55 dạng (32 Exponential/Logarithm, 23 Complex Numbers) use **ReAct + Calculator**, the other
  87 are solved **zero-shot** (including the removed Complex Numbers D34, should the router pick it). Each dạng uses exactly the prompt, tool and generation parameters of its final experiment.
* **Figures:** [`docs/figures/`](docs/figures/) (draw.io sources + PNG, Vietnamese and English; to be refined).

## Key results so far

| Stage | Result |
|---|---|
| Router, on its test set (12,860 questions of the existing data in the 141 scored dạng; 100% when the whole string is scored) | 12,860/12,860; on the 170 source questions 100% with full-text scoring, 99.4% with the label part only |
| Each ReAct dạng on its 90 generated variants (Qwen3-4B) | 90/90 for all 32 Exponential/Logarithm dạng and all 23 Complex Numbers dạng |
| **Whole pipeline on 93 real questions** (49 of the 142 dạng, one Kaggle run, 2026-10-16) | router 77/93 (82.8%), final answer 89/93 (95.7%) |

The last row is the first test outside the generated data. Details, the 100-question set it comes from and the reasons why
7 questions were left out are in [`data/results/pipeline_realworld/`](data/results/pipeline_realworld/). The router is far from
perfect on real questions, and the ReAct answers are less reliable than 95.7% suggests; see "Open problems" below.

## Repository map

| Path | What it is |
|---|---|
| [`data/catalogue/`](data/catalogue/) | The 142-dạng catalogue (CSV/JSON), the text used in the router prompt, and the audit of the names |
| [`models/router_lora/`](models/router_lora/) | The router adapter that reached 100% (LoRA on Qwen3-0.6B), with its evaluation and training log |
| [`data/router_train/`](data/router_train/) | Router training data (12,780 pairs = 142 dạng × 90 new variants) and the Kaggle bundles (`kaggle_bundle`, `kaggle_bundle_v3`) |
| [`experiments/Router-Finetune/`](experiments/Router-Finetune/), [`scripts/router/`](scripts/router/) | Router training notebook and every script that built the catalogue and the training data |
| [`experiments/ReAct-Calculator/`](experiments/ReAct-Calculator/), [`scripts/experiments/react/`](scripts/experiments/react/) | ReAct + Calculator notebooks for the 32 Exponential/Logarithm dạng, their prompts, and the code that builds them |
| [`experiments/Qwen3-4B/`](experiments/Qwen3-4B/) | The zero-shot notebooks: Exponential/Logarithm, and the Complex Numbers baseline (`qwen_eval_kaggle_sophuc_zeroshot.ipynb`) |
| [`so_phuc/`](so_phuc/) | Complex Numbers data, ReAct notebooks and results for the 23 ReAct dạng, and the reworded benchmark v2 (2,070 questions) |
| [`experiments/Pipeline/`](experiments/Pipeline/), [`scripts/pipeline/`](scripts/pipeline/), [`data/pipeline_bundle/`](data/pipeline_bundle/) | **The whole-system notebook**, the scripts that build and analyse it, and its Kaggle bundle |
| [`data/results/pipeline_realworld/`](data/results/pipeline_realworld/) | Real-world test: question sets, results of the Kaggle run, error analysis, open problems |
| [`scripts/realworld_eval/`](scripts/realworld_eval/), [`data/questions/realworld_pool/`](data/questions/realworld_pool/) | Crawl, parse and filter scripts to collect new real questions, and the pool already collected (3,111 + 258 parsed questions, nearly all with their answer key) |
| [`data/questions/mu_logarit_extraction/`](data/questions/mu_logarit_extraction/), [`data/source_documents/`](data/source_documents/) | The 107 source Exponential/Logarithm questions, and the PDF they were extracted from |
| [`scripts/generate_questions/`](scripts/generate_questions/), [`scripts/pdf_to_markdown/`](scripts/pdf_to_markdown/) | Generators of the variants (8,010 for Exponential/Logarithm) and the PDF extractor |
| [`data/results/`](data/results/) | Zero-shot and ReAct results of the dạng experiments (ChatGPT, Gemini, Qwen3-4B) |

## How to continue

```bash
# 1. See what each dạng uses (solving mode, source notebook, prompt md5) and rebuild the pipeline notebook + Kaggle bundle
python scripts/pipeline/build_pipeline_notebook.py          # uses models/router_lora and the 100-question set
# 2. Check the plumbing locally, without GPU (fake vLLM)
python scripts/pipeline/dry_run_pipeline.py
# 3. Run on Kaggle: upload data/pipeline_bundle as a Dataset, import experiments/Pipeline/KLTN_Pipeline_GiaSu_100cau.ipynb,
#    GPU T4 x2 + internet, Save & Run All.  Results: /kaggle/working/pipeline_ket_qua.zip
# 4. Analyse a run (reproduces every number of PHAN_TICH_LOI.md)
python scripts/pipeline/analyze_pipeline_errors.py
# 5. Collect new real questions for a harder / larger evaluation set
python scripts/realworld_eval/crawl_loigiaihay.py --out pages --ids 47800 51500
python scripts/realworld_eval/parse_exam_pages.py pages pool.json
python scripts/realworld_eval/filter_candidates.py pool.json candidates --min-num 36 --exclude <existing question CSVs>
#    then run the router on candidates.csv:  python scripts/router/run_router_real.py candidates.csv models/router_lora routed.csv
#    and decide the dạng of each question BY HAND against the catalogue (most application-level questions fit none).
```

Reference documents: [`experiments/Pipeline/README.md`](experiments/Pipeline/README.md) (how the notebook is built and which
notebook each dạng comes from), [`models/README.md`](models/README.md), [`scripts/README.md`](scripts/README.md).

## Things that will surprise you

* **Two numberings of the dạng.** The catalogue and the router use "Dạng 1...142". The experiment notebooks, prompts and
  result files use the **old codes** (`D79`, `D55`, ...), which are different for Exponential/Logarithm and Complex Numbers.
  The mapping is the `ma_cu` column of [`data/catalogue/danh_muc_dang_bai.csv`](data/catalogue/danh_muc_dang_bai.csv) and
  [`data/pipeline_bundle/bang_dang_prompt.csv`](data/pipeline_bundle/bang_dang_prompt.csv). The Complex Numbers dạng that is
  `D54` in the paper is `D55` in the data files.
* **Several prompt versions exist for some dạng.** The final one is the newest: R (`R01`, `R04`) over H (`H01`-`H05`) over G
  (`G01`-`G10`); the final choice for every dạng is the table `ML_FINAL` in
  [`scripts/pipeline/build_pipeline_notebook.py`](scripts/pipeline/build_pipeline_notebook.py). For Complex Numbers D04 the final
  prompt is the one in `KLTN_Nhom1_...`, not in the stand-alone `KLTN_D04_...` notebook (older).
* **The pipeline does not re-implement anything.** It runs the code of each dạng's final notebook verbatim (prompt, Calculator
  backend, ReAct loop, parameters, answer extraction) and checks the prompt md5. Do not "clean up" those code units; if you change
  a prompt, change it in the experiment notebook and re-run that dạng's 90 variants first.
* **Generation parameters differ by mode.** ReAct: temperature 0.3, top-p 0.95, top-k 20, presence penalty 1.2, 9,216 new tokens.
  Zero-shot Exponential/Logarithm: temperature 0.6, presence penalty 1.2. Zero-shot Complex Numbers: temperature 0.6, **no** presence penalty.
  All with seed 42 and thinking enabled.
* **Same prompt, same seed, different result.** Results depend on which questions share a batch, so a single run is not
  conclusive (one zero-shot question was wrong in one run and right in the next). Repeat runs before drawing conclusions.
* **Kaggle environment.** `pip install -U vllm`, uninstall `torchaudio`/`torchcodec`, and uninstall `torchao` (PEFT rejects the
  preinstalled version when loading the router). The experiment notebooks write to `/kaggle/working`.
* **Labels of the real-world set are manual.** Each question was assigned to a dạng by reading it against the catalogue
  names; 7 questions whose label was uncertain were removed (see the README of `data/results/pipeline_realworld/`).

## Open problems (the research to do next)

A problem is recorded when it is the main cause of a wrong result, even in one question. Behaviours that are frequent but
harmless are recorded only if they stop a later pipeline version from reaching 100%. Plan: this pipeline is version 1; version 2
fixes the problems below; the same evaluation set then shows which problems remain, which become version 3.

**Router**
* The training data are numeric variants of very few question templates (median 3 templates per dạng), so a new way of writing the
  same dạng is often misrouted. All 16 wrong cases had a template not seen in training; the 17 seen ones were all right.
* Dạng with the same opening phrase ("Tìm tập xác định của...", "Tập nghiệm của...") are confused with each other.
* There is no mechanism for questions outside the 142 dạng, and the confidence does not flag errors (6 of 16 wrong cases had confidence ≥ 0.9).

**Solver, causing wrong answers**
* With ReAct, the model does not detect and repair a broken intermediate step: it misreads a parameter ($4a^2$ as $(4a)^2$), or the tool
  keeps failing (a non-numeric option such as "Vô số"), and it still commits to an answer instead of re-reading the question or changing approach.
* With zero-shot, the model can compute the right result and still match it to the wrong option: in one run it copied an option wrongly
  and did not see that another option was equal to its result ($\ln 4 = 2\ln 2$). The same question was right in the next run, so this
  is an unreliable step, not a rule.

**Solver, answers right but not because of the solving process**
* ReAct applies a recipe that no longer fits the question (letters instead of numbers, a different sign, a parameter in another position, or the prompt of a neighbouring dạng) and still commits to an answer; four such answers were right by chance (no step of the trace leads to the final letter).

## Not in this repository

* `FinetuneMath_v2.zip` / `FinetuneMath_v3.zip` (300 MB each: Kaggle outputs with optimizer states and checkpoints). Everything needed from the v3 run
  (adapter, evaluation, log) is in `models/router_lora/`. The older adapter in `experiments/Router-Finetune/router_out/` is not tracked.
* The third-party exam compilation used for the 30 application-level questions (`hard30/sources/`, git-ignored); its URL is in
  `data/results/pipeline_realworld/hard30/README.md`.
* Raw HTML of the crawled exam pages (re-crawl with `scripts/realworld_eval/`).
* Thesis and paper drafts.

## Details per topic

(The sections below are the original description of the two topics.)

### Topics

### 1. Complex Numbers (published as a SoICT 2026 submission)

Canonical repository:
[react-calculator-complex-numbers](https://github.com/manhdungcr7/react-calculator-complex-numbers).
A full copy of that repository's tracked files (data, scripts, experiment
results) is mirrored here under [`so_phuc/`](so_phuc/) so both topics can be
browsed side by side. `so_phuc/README.md` is that repository's own README.

### 2. Exponential and Logarithm equations and inequalities

This is the second topic, extracted from the same source review document
used for Complex Numbers. Its data and scripts live at the top level of
this repository (this is the canonical location for this topic — there is
no separate dedicated repository for it).

| Directory | Contents |
|---|---|
| [`scripts/pdf_to_markdown/`](scripts/pdf_to_markdown/) | Script that extracts candidate questions from the source PDF |
| [`scripts/generate_questions/`](scripts/generate_questions/) | Scripts that generate numerical variants of the source questions per problem type |
| [`data/questions/mu_logarit_extraction/`](data/questions/mu_logarit_extraction/) | The extracted/transcribed question set, its problem-type classification, and generated variants |
| [`data/results/`](data/results/) | Model-solving results (ChatGPT, Gemini, Qwen3-4B zero-shot) |

Each directory has its own README with further details.

## Status

**Exponential and Logarithm**: 112 questions were transcribed, then D09 and D11 were excluded because they are general symbolic questions without numeric inputs to vary. A manual audit split D36 into D36a (selecting a universally true logarithm proposition) and D36b (evaluating a logarithm of a power), and split D50 into D50a (difference-to-quotient rule) and D50b (sum-to-product rule), because the questions differ in their data, requested task, or solution method. From the 123 originally selected candidates, 2 exact duplicates and 9 real-world
application questions (compound interest, loan repayment,
bacterial/population growth, ad-campaign and forest-area growth models)
were removed to keep the scope to exponential/logarithmic equations and
inequalities. D31 (two answer options that were the same set in 9 of 90 variants) and D32 (variants whose options are numerically equal) were then dropped after a Qwen3-4B zero-shot audit and are treated as non-existent; they remain only in the archival 112-question snapshot files and in git history. The retained set therefore has 107 questions across 89 problem types. On the retained 107-question set, zero-shot results are: ChatGPT 87 correct / 18 incorrect / 2 undetermined, Gemini 106 correct / 1 incorrect, and Qwen3-4B 97 correct / 10 undetermined.

Evaluation-variant generation covers all 89 retained problem types, each with 90 independently verified variants (8,010 variants; 8,117 retained source and variant rows). D43 was expanded with exact rational thresholds in the same logarithmic inequality. D51 was expanded by choosing coefficients whose quadratic factors at integer powers of 2, preserving the original question form and solution method; every generated case was checked by direct enumeration of the original inequality. Each batch also passes repository-wide scans for duplicate question statements and answer choices.
symbolic relations with no numeric values to vary. D84 has 90 independently
verified variants; its source answer 14 remains in the retained set. A
Windows-encoding bug introduced while expanding some batches to 90
variants (UTF-8 text mis-decoded as Windows-1252, corrupting Vietnamese
diacritics in several thousand rows) was found and corrected; every row
was re-scanned afterward and is clean. See
[`scripts/generate_questions/README.md`](scripts/generate_questions/README.md)
for the generation and verification methods.
