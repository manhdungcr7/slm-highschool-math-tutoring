# Router on benchmark v2: results

2,070 questions (23 types, Complex Numbers D34 excluded), router Qwen3-0.6B + LoRA (the 100% model), run on 3 Kaggle accounts.

* Final answer (the whole string `Dạng N: description` scored): **1,929/2,070 (93.19%)**.
* First stage only (the label `Dạng N:`): 1,434/2,070 (69.28%); the second stage corrected 495 questions the first stage got wrong and never made a first-stage-correct question wrong.
* For the 141 wrong questions, the correct dạng is not among the router's top 3.
* Median confidence of the wrong predictions: 0.54.

For comparison, the same router scores 100% on its own test questions (`models/README.md`); benchmark v2 rewords the questions of the 23 types. The earlier 89.03% was measured on a flawed first version of v2 and must not be used.

| Type | Correct |
|---|---|
| D28 | 58/90 |
| D49 | 60/90 |
| D44 | 76/90 |
| D14 | 79/90 |
| D38 | 81/90 |
| D45 | 82/90 |
| D48 | 83/90 |
| D39 | 85/90 |
| D51 | 85/90 |
| D40 | 86/90 |
| D32 | 86/90 |
| D42 | 86/90 |
| D53 | 86/90 |
| D52 | 87/90 |
| D37 | 89/90 |
| D33 | 90/90 |
| D47 | 90/90 |
| D46 | 90/90 |
| D35 | 90/90 |
| D36 | 90/90 |
| D04 | 90/90 |
| D50 | 90/90 |
| D54 | 90/90 |

Most frequent confusions: Dạng 116 → Dạng 118 (14); Dạng 132 → Dạng 128 (12); Dạng 137 → Dạng 133 (9); Dạng 102 → Dạng 104 (7); Dạng 116 → Dạng 120 (6).

Files: `router_v2_ket_qua_2070_cau.csv` (every question: `so_dang` correct, `pred_v2` predicted, `pred_buoc1_v2` first stage, `top3_v2`, `conf_v2`, `dung_v2`), `router_v2_141_cau_sai.csv` (the wrong questions with their text), `router_summary_shard*of3.json`.
