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
- `Mu_Logarit_123_cau_goc.jsonl` / `.csv` / `.xlsx`: the 123 selected
  questions, manually transcribed from the rendered page images with their
  original question, four answer choices, correct answer, and solution.
  Seven questions required a correction relative to the source document
  (a wrong answer key or a printing error in an intermediate step); each
  correction is recorded in the `ghi_chu_sua` field / "Ghi chú sửa" column,
  and `doi_chieu_anh` / "Đối chiếu ảnh" states what the source document
  actually shows.
