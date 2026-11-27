# Router fine-tuning with Qwen3-4B

Kaggle notebook that trains the router (type-identification module) on **Qwen3-4B**. It is a copy of the notebook of the
Qwen3-0.6B run ([`../Router-Finetune/`](../Router-Finetune/)) with the smallest set of changes; the finished adapter is in
[`../../models/router_lora_qwen3_4b/`](../../models/router_lora_qwen3_4b/).

| File | What it is |
|---|---|
| `KLTN_router_finetune_Qwen3-4B_Kaggle.ipynb` | The notebook (training only). Written by `scripts/router/make_qwen3_4b_kaggle_notebook.py`, which copies the 0.6B notebook and applies the changes below; edit that script, not the notebook |

## Changes from the Qwen3-0.6B notebook

1. `MODEL = Qwen/Qwen3-4B`.
2. Dạng 122 (Complex Numbers D34, removed from the thesis) is left out of the training pairs and of the candidates: 141 dạng, 12690 pairs.
3. Weights loaded in float16 on a T4 (float32 weights of 4B take about 16 GB, the whole memory of a T4).
4. `MAX_TRAIN_MINUTES` 270 -> 680 (almost the whole 12-hour Kaggle session). The run needed about 307 minutes.
5. Training only: the evaluation cells are left out.
6. The training data is downloaded from this repository at commit `b213dc4` and checked by its git hash, so no Kaggle Dataset is attached.

Unchanged: LoRA r 16, alpha 32, dropout 0.05 on q, k, v, o, gate, up, down; 2 epochs; lr 2e-4 cosine, 3% warmup; batch 16 x 2
on one GPU; MAX_LEN 512; loss on the answer only; 3 pairs per dạng held out for the validation loss; seed 42.

To run: Settings -> GPU T4 x2 (one is used), Internet On, then Save Version -> Save & Run All. The output folder `router_lora/` is the adapter.
