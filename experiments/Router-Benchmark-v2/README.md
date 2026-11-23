# Router on benchmark v2

`KLTN_Router_v2_Kaggle.ipynb` runs the router (Qwen3-0.6B + LoRA) on the reworded Complex Numbers benchmark
[`so_phuc/data/questions/benchmark_so_phuc_v2_23dang_2070cau.csv`](../../so_phuc/data/questions/benchmark_so_phuc_v2_23dang_2070cau.csv)
(2,070 questions, 23 types; Complex Numbers D34 is not included). The router still chooses among 142 dạng.
The notebook downloads everything from GitHub and splits the questions into 7 shards (set `SHARD_ID` 0-6 in the first cell).
