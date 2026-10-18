# Router fine-tuning

Kaggle notebook that fine-tunes Qwen3-0.6B (LoRA) to recognise the dạng of a question, and evaluates it by scoring the 142
candidate strings. The finished router is in [`../../models/router_lora/`](../../models/router_lora/).

| File | What it is |
|---|---|
| `KLTN_router_finetune_qlora.ipynb` | The notebook (training, evaluation, adapter merge). Its first cell explains inputs, outputs and how to run (GPU T4, Save & Run All; `QUICK_TEST` for a 5-minute check) |
| `router_finetune_cells.py` | The code cells of the notebook as one Python script (used for local dry runs). Both files are written by `scripts/router/build_finetune_notebook.py`; edit that builder, not the generated files |
| `router_sweep.py`, `sweep_w1.log` | One experiment of the sweep used to choose the settings (model size, epochs, LoRA rank, learning rate, loss) before the final run, and the log of one such run |

Inputs (a Kaggle Dataset made from a bundle folder): `data/router_train/kaggle_bundle_v3/` for the run that reached 100%
(`finetune_router.jsonl`, `eval_set.jsonl`, `candidates.json`). How that training data and the catalogue were built:
[`data/router_train/README.md`](../../data/router_train/README.md) and [`scripts/router/`](../../scripts/router/).

To retrain after adding data: regenerate the bundle with `scripts/router/make_kaggle_bundle.py`, upload it, run the notebook,
then copy the resulting `router_lora/` over `models/router_lora/` and rebuild the pipeline bundle
(`python scripts/pipeline/build_pipeline_notebook.py`). Evaluate on **questions that are not variants of the training templates**
(see the real-world set), because the built-in evaluation set is written like the training data.
