# Scripts

Run everything from the repository root (paths are relative to it).

## `pipeline/` - the whole system

| Script | Purpose |
|---|---|
| `build_pipeline_notebook.py` | Builds `experiments/Pipeline/KLTN_Pipeline_GiaSu_100cau.ipynb` and the Kaggle bundle `data/pipeline_bundle/`. For each of the 142 dạng it takes the code of that dạng's final experiment notebook verbatim (table `ML_FINAL` and the Complex Numbers lists inside the script) |
| `pipeline_cells.py` | The cells of the pipeline notebook (install, router, routing plan, loading the code units, solving, report) |
| `dry_run_pipeline.py` | Runs the notebook without GPU using a fake vLLM; use it after every change to the builder or the cells |
| `analyze_pipeline_errors.py` | Recomputes the numbers quoted in `data/results/pipeline_realworld/PHAN_TICH_LOI.md` from a run |
| `report_93.py` | The report on the 93 questions of the evaluation (the 100 of the run minus 7) |

## `realworld_eval/` - collecting real questions

| Script | Purpose |
|---|---|
| `crawl_loigiaihay.py` | Downloads the exam pages of loigiaihay.com ("đề thi thử THPT Quốc gia môn Toán") by listing or by id range |
| `parse_exam_pages.py` | Turns the pages into a pool of questions with answer keys (formulas kept as `$...$`) |
| `filter_candidates.py` | Keeps new Exponential/Logarithm and Complex Numbers questions (optionally application level) and removes the ones already used |
| `hard30/collect_hard_questions.py` | Transcribes 30 application-level questions from a public compilation of exam papers and **recomputes every answer** with SymPy/mpmath; `check_overlap.py` compares them with the router data |

## `router/` - catalogue, training data and router tools

The catalogue of the 142 dạng (`build_catalogue.py`, `catalogue_ml.py`, `catalogue_sp.py`, `descriptions.py`, checks), the
generators of the 12,780 training questions (`gen_ml_extra.py`, `gen_sp_new.py`, `ml_passes/`, `so_phuc_generators/`), the assembly and
audit of the training set (`assemble_train.py`, `audit_train.py`, `augment_train.py`), the builder of the training notebook
(`build_finetune_notebook.py`), the Kaggle bundle maker (`make_kaggle_bundle.py`) and `run_router_real.py`, which runs the finished
router on a CSV of questions. How the training data were made: `data/router_train/README.md`.

## `experiments/` - Exponential/Logarithm experiments

`10_`-`15_*.py` prepare the data and build the zero-shot notebooks, merge and re-grade their results. `react/` builds the
ReAct + Calculator notebooks (`framework.py`, `calculator_backend.py`, `part_tool.py`, `part_kienthuc.py`, one `dang_Dxx.py` per dạng,
`build_multi_notebook.py`) and summarises their results (`summarize_results.py`, `show_fail.py`, `show_response.py`). See
`experiments/ReAct-Calculator/README.md`.

## `generate_questions/` - variants of the Exponential/Logarithm questions

Generators and verifiers of the 90 variants per dạng; see its own README.

## `pdf_to_markdown/` - source extraction

| Script | Purpose |
|---|---|
| `20_extract_mu_logarit.py` | Extract candidate Exponential/Logarithm questions from the source PDF and render the relevant pages for transcription |

The source review PDF is in `data/source_documents/DAP AN.pdf` (the default of `--pdf`); see the README there for its origin.
