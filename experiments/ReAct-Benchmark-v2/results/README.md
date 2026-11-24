# ReAct + Calculator on benchmark v2: results

2,070 questions (23 types, D34 excluded), Qwen3-4B, the code of each type taken from the notebook that reached 90/90 on v1,
no router. Run on Kaggle (T4 x2) in 5 shards on 2026-11-24.

* Correct: **2019/2,070 (97.54%)**. Wrong: 47. No answer: 4.
* 21 of the 23 types: 1,881/1,890 (99.52%). Of these, 17 types are 90/90.
* D35: 72/90 and D44: 66/90. They account for 42 of the 51 questions that are not correct.

## Where D35 and D44 lose points

In v1, 30 of the 90 questions of D35 and 30 of the 90 of D44 contain a nested fraction, for example
`\dfrac{z}{z+\dfrac{22}{5}}` or `w=\dfrac{\dfrac{23}{3}+iz}{1+z}`. Benchmark v2 writes them as the equal simple
fraction (`\dfrac{5z}{5z+22}`, `w=\dfrac{23+3iz}{3(1+z)}`).

| | questions with a nested fraction in v1 | all other questions |
|---|---|---|
| D35 | 12/30 | 60/60 |
| D44 | 6/30 | 60/60 |

All 42 wrong answers of the two types are among those 60 questions. The same code scored 90/90 on v1 for both types. The answer
key of all 180 questions of D35 and D44 was checked independently (number of intersection points for D35; the radius of the
circle through three image points for D44) and is correct, and v1 and v2 give the same value.

Example (STT 1293, `2z/(2z+15)`): the model wrote the conjugate of the denominator as `(2x+15) - y*i` instead of
`(2x+15) - 2y*i`, so the real part was not `x²+y²+...` and the step "subtract the two equations to eliminate the x²+y² cluster"
produced a system with no solution; it answered A (the key is B). The data cannot separate the effect of the new fraction form
from the effect of the new wording, but no wrong answer of these two types is outside the rewritten questions.

## Other wrong answers

9 of the 1,890 questions of the other 21 types: D53 (3), D38 (2), D04, D36, D39, D50 (1 each). The 4 questions without an
answer ran out of the 9,216-token budget (D04: 1, D44: 3). 17 questions used the whole tool-call limit.

## Per type

| Type | Correct | Mean tokens |
|---|---|---|
| D44 | 66.0/90.0 | 1551 |
| D35 | 72.0/90.0 | 808 |
| D53 | 87.0/90.0 | 347 |
| D38 | 88.0/90.0 | 1303 |
| D50 | 89.0/90.0 | 1913 |
| D36 | 89.0/90.0 | 1387 |
| D39 | 89.0/90.0 | 951 |
| D04 | 89.0/90.0 | 707 |
| D46 | 90.0/90.0 | 1763 |
| D52 | 90.0/90.0 | 1731 |
| D47 | 90.0/90.0 | 1165 |
| D37 | 90.0/90.0 | 1101 |
| D49 | 90.0/90.0 | 1070 |
| D48 | 90.0/90.0 | 955 |
| D32 | 90.0/90.0 | 911 |
| D45 | 90.0/90.0 | 830 |
| D54 | 90.0/90.0 | 820 |
| D42 | 90.0/90.0 | 813 |
| D51 | 90.0/90.0 | 799 |
| D40 | 90.0/90.0 | 784 |
| D33 | 90.0/90.0 | 751 |
| D14 | 90.0/90.0 | 679 |
| D28 | 90.0/90.0 | 647 |

Files: `react_v2_ket_qua_2070_cau.csv` (every question with the model's answer, the number of tool calls, the stop reason and the
whole solution), `react_v2_summary_shard*of5.json`.
