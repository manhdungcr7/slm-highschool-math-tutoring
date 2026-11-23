# ReAct + Calculator on benchmark v2

`KLTN_ReAct_v2_Kaggle.ipynb` runs Qwen3-4B with ReAct + Calculator on the reworded Complex Numbers benchmark
[`so_phuc/data/questions/benchmark_so_phuc_v2_23dang_2070cau.csv`](../../so_phuc/data/questions/benchmark_so_phuc_v2_23dang_2070cau.csv)
(2,070 questions, 23 types; D34 is not included).

* Each type runs the code of its final notebook, the one that reached 90/90 on v1: the prompt, the Calculator, the
  ReAct loop, the generation parameters and the answer extraction. The code is taken verbatim from
  [`data/pipeline_bundle/pipeline_units.json`](../../data/pipeline_bundle/pipeline_units.json). The cells that load and
  run it are those of the pipeline notebook.
* There is no router: every question is solved with the prompt of its own type.
* The notebook downloads its two input files from a fixed commit and checks their md5.
* It runs in 5 shards on Kaggle (GPU T4 x2, Internet on). Set `SHARD_ID` to 0-4 in the first cell. Each type runs
  whole, as one batch, inside one shard.
