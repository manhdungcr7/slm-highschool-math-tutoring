# Models

## `router_lora/` - the router that reached 100%

LoRA adapter on **Qwen/Qwen3-0.6B** that reads a question and says which of the 142 dạng it is. It is the router of the
whole pipeline (`experiments/Pipeline/`).

| | |
|---|---|
| Base model | `Qwen/Qwen3-0.6B` (downloaded from Hugging Face; not stored here) |
| LoRA | r = 16, alpha = 32, dropout 0.05, on all attention and MLP projections (`q,k,v,o,gate,up,down_proj`) |
| Training | 2 epochs (772 steps, about 2.8 hours on one Kaggle T4), learning rate 2e-4, effective batch 32, loss on the answer only |
| Training data | `data/router_train/kaggle_bundle_v3/finetune_router.jsonl`: 12,780 pairs, 90 new variants for each of the 142 dạng. (`kaggle_bundle/` holds the training set of the earlier run; both bundles have the same evaluation set) |
| Notebook | `experiments/Router-Finetune/KLTN_router_finetune_qlora.ipynb` |

### How it answers

It does not generate text. For a question it computes the probability of each of the 142 strings `Dạng N: description`
(`data/catalogue/danh_muc_trong_prompt.txt`) and returns the most probable one. To keep memory small, this is done in two
stages: the probability of the part `Dạng N:` for all 142 candidates, then the probability of the whole string for the best 5.
The chat template is used with `enable_thinking=False`. The implementation is `scripts/router/run_router_real.py`:

```bash
python scripts/router/run_router_real.py questions.csv models/router_lora routed.csv
# questions.csv: columns id, topic, question_markdown_latex  (options written inline "A. ... B. ..." are accepted)
# routed.csv   : id, du_doan_dang (predicted dạng), do_tin_cay (confidence), top3, mo_ta_du_doan
```

The question must have the layout of the training data: the stem, a blank line, then one option per line (`run_router_real.py`
converts inline options). On a Kaggle T4 it takes about 0.7 s per question. Loading the adapter with a PEFT older than the one that
saved it prints a warning about `kasa_config`; it is harmless. Uninstall `torchao` first on Kaggle (PEFT rejects the preinstalled
version).

### Evaluation of this run (`training_run_v3/`)

* `router_eval_summary.json`: on the 12,860 questions of the existing data in the 141 scored dạng (8,026 Exponential/Logarithm, 4,834
  Complex Numbers; 170 of them are the source questions, the others are generated variants), scoring the 142 whole strings gives
  **12,860/12,860**. Scoring only the label part `Dạng N:` gives 99.99% (169/170 on the source questions). Letting the model write its
  answer freely gives 99.97%. Complex Numbers D34 (Dạng 122) is not scored: its answer key counted $z = 0$ as purely imaginary. The
  model was trained on all 142 dạng and still chooses among the 142 strings.
* `router_eval_predictions.csv`: the prediction for every evaluation question. `trainer_state.json`, `train_progress.log`: the training run.
* **This number is for questions written like the training data.** On 63 real questions from the internet the same router is right on
  74.6%; see `data/results/pipeline_realworld/`.

### What is not here

The earlier Kaggle outputs (`FinetuneMath_v2.zip`, `FinetuneMath_v3.zip`, 300 MB each with checkpoints and optimizer states) are not
stored; this folder is the final adapter of v3. An older adapter that was trained before v3 is not kept on purpose, so that the
only router in the repository is the one that was evaluated.
