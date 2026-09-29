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
  method. 91 unique problem types (11 of them group 2-4 questions, the rest
  are singletons). Two classification errors found while writing variant
  generators — D03/D53 and, separately, D26/D36/D70 — were each merging two
  or three problem types that had turned out to share the identical
  criterion; fixing them dropped the count from the original 94 to 91.
- `Mu_Logarit_112_cau_goc_ket_qua_mo_hinh.csv` / `.xlsx`: ChatGPT (`gpt-4o`)
  and Gemini (`gemini-2.5-flash`) zero-shot answers on the 112 questions,
  produced with
  [`../scripts/pdf_to_markdown/21_solve_mu_logarit_with_models.py`](../scripts/pdf_to_markdown/21_solve_mu_logarit_with_models.py)
  and graded with
  [`../scripts/pdf_to_markdown/22_grade_mu_logarit_answers.py`](../scripts/pdf_to_markdown/22_grade_mu_logarit_answers.py).

- `bien_the/*.json`: SymPy-generated numerical variants, one file per
  generator batch (see
  [`../scripts/generate_questions/README.md`](../scripts/generate_questions/README.md)
  for which problem types each batch covers). Every variant's answer is
  checked by an independent verifier that re-derives the answer through a
  different method than the generator used (symbolic re-solving, direct
  numeric substitution for identities, or brute-force integer enumeration
  for counting problems), and a repo-wide scan rejects any question whose
  four answer choices are not all distinct after rendering.
  **Coverage: 88 of 91 problem types**, 607 generated variants.
  The three uncovered types are D09 and D11 (symbolic relations without
  numerical inputs to vary) and D84 (the source answer appears inconsistent
  with its equation and needs source-page verification). Round 8 added D08,
  D23, D47, D52, D57, and D78 using independent verifiers; see the generator
  README for each method.
- `Mu_Logarit_bien_the_full.csv` / `.xlsx`: the 112 source questions plus
  607 generated variants combined into one file (719 rows), produced
  by `22_export_all.py`.

## `results/qwen3_4b_zeroshot/`

- `ketqua_Qwen3-4B_think_mulogarit112.csv` / `.xlsx`: Qwen3-4B zero-shot
  answers on the same 112 questions, run on Kaggle (2×T4 GPU, vLLM) with the
  same prompt and generation settings used for the Complex Numbers topic
  (`ENABLE_THINKING=True`, temperature 0.6, top_p 0.95, top_k 20, seed 42,
  max_new_tokens 9216).
