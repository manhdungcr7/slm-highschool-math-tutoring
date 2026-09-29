# Data

## `questions/mu_logarit_extraction/`

Exponential and Logarithm equations/inequalities questions extracted from the
same source review document used for the Complex Numbers topic, produced with
[`../scripts/pdf_to_markdown/20_extract_mu_logarit.py`](../scripts/pdf_to_markdown/20_extract_mu_logarit.py).
The source PDF and the rendered page images used for transcription are not
included in this repository.

- `candidates_all.jsonl`, `review.csv`, `selected_no_visual.jsonl`,
  `summary.json`: output of the extraction script, recording which candidate
  questions were kept, which needed a figure/graph and were excluded, and
  which turned out to belong to a different topic.
- `Mu_Logarit_112_cau_goc.jsonl` / `.csv` / `.xlsx`: the 112 selected
  questions, manually transcribed from the rendered page images with their
  original question, four answer choices, correct answer, and solution.
  Eight questions required a correction relative to the source document (a
  wrong answer key, a printing error in an intermediate step, or content
  mismatched to the wrong question on the page); each correction is recorded
  in the `ghi_chu_sua` field / "Ghi chú sửa" column, and `doi_chieu_anh` /
  "Đối chiếu ảnh" states what the source document actually shows. The
  original extraction had selected 123 candidates; 2 exact duplicate
  questions (the same question appearing in two different source exams
  within the compiled document) and 9 real-world application word problems
  (compound interest, loan repayment, bacterial/population growth,
  ad-campaign and forest-area growth models — kept out to focus the scope on
  exponential/logarithmic equations and inequalities) were removed.
- `Mu_Logarit_112_cau_phan_dang.jsonl` / `.csv` / `.xlsx`: problem-type
  classification of the same 112 questions (columns: `Ma dang`, `Ten dang`,
  plus the question text and correct answer for reference). Grouping
  criterion: two questions share a Mã dạng only when they share the same
  given-data form, the same thing to compute/decide, and the same solution
  method. 93 unique problem types; 11 of them group 2-4 questions, the
  remaining 82 are singletons. (A classification error found during variant
  generation — D03 and D53 had the identical criterion and should have been
  one type — was fixed by merging D03 into D53; this dropped the count from
  the earlier 94 to 93.)
- `Mu_Logarit_112_cau_goc_ket_qua_mo_hinh.csv` / `.xlsx`: ChatGPT (`gpt-4o`)
  and Gemini (`gemini-2.5-flash`) zero-shot answers on the 112 questions,
  produced with
  [`../scripts/pdf_to_markdown/21_solve_mu_logarit_with_models.py`](../scripts/pdf_to_markdown/21_solve_mu_logarit_with_models.py)
  and graded with
  [`../scripts/pdf_to_markdown/22_grade_mu_logarit_answers.py`](../scripts/pdf_to_markdown/22_grade_mu_logarit_answers.py).

- `bien_the/D01_bien_the.json`, `D12_bien_the.json`, `D18_bien_the.json`,
  `D53_bien_the.json`: SymPy-generated numerical variants for a first pilot
  batch of 4 problem types (the ones with the most source questions: D01, 5
  questions; D12, 4; D18, 3; D53, 4 — 16 source questions total), produced
  with the scripts in
  [`../scripts/generate_questions/`](../scripts/generate_questions/). Each
  source question gets 6 variants (2 per parameter bucket x 3 buckets), for
  96 variants total. Every variant's answer is checked by an independent
  verifier (`20_verify_pilot.py`) that re-derives the answer through a
  different symbolic path than the generator used; all 96 currently pass.
  The remaining 89 problem types have not been covered yet.
- `Mu_Logarit_thi_diem_4dang_bien_the.csv` / `.xlsx`: the same 16 source
  questions plus their 96 generated variants combined into one file
  (produced by `21_export_pilot.py`).

## `results/qwen3_4b_zeroshot/`

- `ketqua_Qwen3-4B_think_mulogarit112.csv` / `.xlsx`: Qwen3-4B zero-shot
  answers on the same 112 questions, run on Kaggle (2×T4 GPU, vLLM) with the
  same prompt and generation settings used for the Complex Numbers topic
  (`ENABLE_THINKING=True`, temperature 0.6, top_p 0.95, top_k 20, seed 42,
  max_new_tokens 9216).
