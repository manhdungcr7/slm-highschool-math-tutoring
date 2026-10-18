# Thirty additional application and advanced mathematics questions

The 30-question selection contains 17 exponential/logarithmic questions and 13
complex-number questions, assigned to 12 entries of the existing 142-type
catalogue. These are transcriptions of published questions, not newly generated
numerical variants. The earlier nine-question shortlist was not accepted as
verified ground truth; this selection was reviewed afresh.

## Deliverables

- `../questions/cau_hoi_VD_VDC_30_cau_THPT.csv`: the 30 new questions, four choices,
  independently derived answer, numeric type label, difficulty, and source.
- `cau_hoi_VD_VDC_30_cau_THPT.md`: readable questions and checking notes.
- `../questions/cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv`: 70 unchanged rows from
  the approved 100-question set plus these 30 questions. The topic totals remain
  75 exponential/logarithmic questions and 25 complex-number questions.
- `30_cau_thay_the.csv`: exact list of the 30 simple questions replaced.
- `kiem_tra_30_cau.csv`: a derivation and scope rationale for every new question.
- `30_cau_nguon_va_kiem_tra.json`: transcription, checking notes, and parameters
  for reproducible arithmetic checks.
- `overlap_review.json`: comparison of the mathematical givens against the
  approved 100 questions, the previous router evaluation data (including source
  questions), and the router fine-tuning data available locally.

## Source and review

The source is the publicly available compilation *Chuyên đề trong đề thi tốt
nghiệp THPT Quốc gia môn Toán 2017–2021*:

https://file.montoan.com.vn/file-pdf/chuyen-de-trong-de-thi-tot-nghiep-thpt-quoc-gia-mon-toan-2017-2021.pdf

The PDF was kept locally in `sources/thpt_2017_2021.pdf` (not committed, see "Regenerating"). Each row records chapter,
question number, PDF page, and printed page. Selected pages were rendered and
read visually, because text extraction drops conjugation bars in complex-number
formulas. Mathematical givens and option order were preserved. Formula syntax
and spacing were normalized to Markdown LaTeX. No question requires a figure.

All 30 questions have a written derivation. The collection script also checks
answers using symbolic or numerical calculations, as appropriate. The written
arguments establish the domains, completeness of the case splits, and existence;
numerical checks alone are not treated as proofs. In particular, the review
accounts for the excluded pole in the circle-intersection question, roots from
the vanishing radical, open endpoints in integer counts, and both real and
conjugate roots of real-coefficient polynomials.

Two initially selected public questions were removed because their complete
mathematical givens matched earlier local data: complex-number chapter question
154 (modulus 8) matched router training row `135-44`; question 159 (modulus 6)
matched evaluation variant `12293`. They are not in the final 30.

Independent rechecking found and corrected an algebra error in the first D126 derivation: isolating z must retain the real numerator term cr. For the three source questions (c=4, 5, and 6), the resulting radius polynomial has three positive roots, so the correct answer is B (3) in each case. The source PDF confirms those option labels; the generator, exact-root verifier, question files, and audit records now agree.

The final overlap scan found no matches. This is a comparison of normalized
formula fragments and relevant bounds; it is not a universal semantic-duplicate
detector or a claim about model pretraining data. Some retained questions share
the same template with different numerical values, including questions from
parallel examination versions. The 30 questions represent 12 types, not 30
different types. Questions 166/178/184, for example, vary the coefficient of az.

Difficulty labels are reviewer assessments, not labels printed in the source.
Type labels are reasoned assignments to the catalogue, not router predictions.
The original approved 100-question CSV was not changed. The other 70 questions
were carried over from the existing review and were not solved again in this
collection pass. The original pipeline results must not be reported as results
for the new 100-question file; run the pipeline again on that file.

## Reproduction

From `F:/Math`:

```text
python scripts/collect_hard_realworld_20261015.py
python scripts/check_hard_question_overlap_20261015.py
```

The scripts read local source documents and catalogue/data files. They do not
change the thesis repository, the approved original 100-question CSV, the model,
or the prompt catalogue.

## Regenerating

The compilation is not stored in the repository (third-party document). Download it from the URL above to
`sources/thpt_2017_2021.pdf` (this folder is git-ignored), then run
`python scripts/realworld_eval/hard30/collect_hard_questions.py` from the repository root. The script transcribes the 30 questions,
recomputes each answer with SymPy/mpmath, and rewrites the files of this folder and of `../questions/`; with the original PDF the
output is identical to what is committed. `python scripts/realworld_eval/hard30/check_overlap.py` rewrites `overlap_review.json`.

Note: the keys of three questions (VD-019 to VD-021, dạng 126) were wrong in the first transcription and were corrected to B (three
solutions); the script contains the corrected derivation.
