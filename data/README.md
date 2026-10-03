# Data

## `questions/mu_logarit_extraction/`

Exponential and Logarithm equations/inequalities questions extracted from the
same source review document used for the Complex Numbers topic, produced with
[`../scripts/pdf_to_markdown/20_extract_mu_logarit.py`](../scripts/pdf_to_markdown/20_extract_mu_logarit.py).
The source PDF and the rendered page images used for transcription are not
included in this repository.

`Mu_Logarit_112_*` files are preserved as pre-exclusion snapshots for provenance. The `Mu_Logarit_107_*` files below are the retained evaluation set; D09, D11, D31 and D32 are not included. The original 112-question model-result files are archival as well. D31 (two answer options that were the same set in 9 of 90 variants) and D32 (variants whose options are numerically equal) were then dropped after a Qwen3-4B zero-shot audit and are treated as non-existent; they remain only in the archival 112-question snapshot files and in git history.

- `candidates_all.jsonl`, `review.csv`, `selected_no_visual.jsonl`,
  `summary.json`: output of the extraction script, recording which candidate
  questions were kept, which needed a figure/graph and were excluded, and
  which turned out to belong to a different topic.
- `Mu_Logarit_107_cau_goc.jsonl` / `.csv` / `.xlsx`: the 107 retained
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
- `Mu_Logarit_107_cau_phan_dang.jsonl` / `.csv` / `.xlsx`: problem-type
  classification of the same 107 retained questions (columns: `Ma dang`, `Ten dang`,
  plus the question text and correct answer for reference). Grouping
  criterion: two questions share a problem type only when their given-data form,
  requested task, and solution method match. The retained 107-question set has
  89 types. A manual audit split D36 into D36a (select a universally true
  logarithm proposition) and D36b (evaluate a logarithm of a power), and split
  D50 into D50a (difference of logarithms, using the quotient rule) and D50b
  (sum of logarithms, using the product rule). These groups differ in the
  requested task or solution method and are kept separate. The 112-question
  classification has 93 types; excluding D09 and D11 leaves 91 types, and dropping D31 and D32 leaves 89 retained types.
- `Mu_Logarit_107_cau_goc_ket_qua_mo_hinh.csv`: ChatGPT (`gpt-4o`)
  and Gemini (`gemini-2.5-flash`) zero-shot answers on the 107 retained questions,
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
  **Coverage: all 89 retained problem types, 90 variants each** (8,010
  variants total). D43 uses additional exact
  rational thresholds in the same inequality. D51 uses additional coefficients
  selected so the quadratic factors at integer powers of 2; the original
  inequality was checked by direct enumeration for each generated variant.
  D09 and D11 are excluded because they are symbolic questions without numbers
  to vary. Each type's variants are checked with a method independent of the
  generation formula, and global scans reject repeated question statements
  and answer choices. D84's variants use an independent endpoint-sign
  verifier. A Windows-encoding bug (UTF-8 mis-decoded as Windows-1252)
  that corrupted Vietnamese diacritics in several thousand rows while
  expanding some batches to 90 variants was found and fixed; every row was
  re-scanned afterward and confirmed clean. See the generator README for
  details.
- `Mu_Logarit_bien_the_full.csv` / `.xlsx`: the 107 retained source questions plus
  8,010 generated variants combined into one file (8,117 rows), produced
  by `22_export_all.py`.

## `results/qwen3_4b_zeroshot/`

- `ketqua_Qwen3-4B_think_mulogarit107.csv`: Qwen3-4B zero-shot
  answers on the same 107 retained questions, run on Kaggle (2×T4 GPU, vLLM) with the
  same prompt and generation settings used for the Complex Numbers topic
  (`ENABLE_THINKING=True`, temperature 0.6, top_p 0.95, top_k 20, seed 42,
  max_new_tokens 9216).
